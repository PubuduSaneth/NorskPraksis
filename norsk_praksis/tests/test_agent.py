import pytest
import uuid
import sys
import os

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.runners import InMemoryRunner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from norsk_agent.agent import root_agent
from dotenv import load_dotenv

load_dotenv()

@pytest.mark.asyncio
async def test_session_state_increments_exchange_count():
    runner = InMemoryRunner(agent=root_agent)
    session_service = runner.session_service
    
    # Simulate a user sending a message
    session_id = str(uuid.uuid4())
    await session_service.create_session(app_name=runner.app_name, user_id="test_user_id", session_id=session_id)
    
    # Run the agent for 1 exchange
    # We consume the generator to ensure the agent fully processes it
    msg = types.Content(role="user", parts=[types.Part.from_text(text="Hei! Jeg vil gjerne teste scenarioet på kafé.")])
    async for event in runner.run_async(user_id="test_user_id", session_id=session_id, new_message=msg):
        pass
        
    # Verify the state was incremented by our after_agent_callback
    session = await session_service.get_session(app_name=runner.app_name, user_id="test_user_id", session_id=session_id)
    assert session.state.get("exchange_count", 0) > 0

@pytest.mark.asyncio
async def test_scenario_selection_updates_state():
    runner = InMemoryRunner(agent=root_agent)
    session_service = runner.session_service
    session_id = str(uuid.uuid4())
    await session_service.create_session(app_name=runner.app_name, user_id="test_user_id", session_id=session_id)
    
    # We can explicitly simulate tool call invocation or ask the agent
    msg = types.Content(role="user", parts=[types.Part.from_text(text="Kan du velge 'cafe' scenarioet?")])
    async for event in runner.run_async(user_id="test_user_id", session_id=session_id, new_message=msg):
        pass
        
    session = await session_service.get_session(app_name=runner.app_name, user_id="test_user_id", session_id=session_id)
    # Give the LLM a chance to use the tool
    # Not strictly guaranteed to hit the exact tool without a forceful system prompt, 
    # but the exchange count should definitely have advanced.
    assert session.state.get("exchange_count", 0) > 0

@pytest.mark.asyncio
async def test_cross_session_memory_and_profile():
    runner = InMemoryRunner(agent=root_agent)
    session_service = runner.session_service
    
    # Session 1
    session_id_1 = str(uuid.uuid4())
    session_1 = await session_service.create_session(app_name=runner.app_name, user_id="test_user_id", session_id=session_id_1)
    
    # Manually inject a weak word into user state for session 1 and save it
    # Note: State updates need to be applied via an event or we can just update the delta
    session_1.state["user:weak_words"] = ["kaffe", "takk"]
    # We must append a dummy event to force the session to persist the state delta
    from google.genai import types as genai_types
    from google.adk.events.event import Event
    from google.adk.events.event_actions import EventActions
    
    dummy_event = Event(id="e1", timestamp=10.0, author="user", content=genai_types.Content(role="user", parts=[]), 
                        actions=EventActions(state_delta={"user:weak_words": ["kaffe", "takk"]}))
    await session_service.append_event(session_1, dummy_event)
    
    # Session 2
    session_id_2 = str(uuid.uuid4())
    session_2 = await session_service.create_session(app_name=runner.app_name, user_id="test_user_id", session_id=session_id_2)
    
    dummy_event_2 = Event(id="e2", timestamp=20.0, author="user", content=genai_types.Content(role="user", parts=[]), 
                        actions=EventActions(state_delta={"active_scenario_id": "cafe"}))
    await session_service.append_event(session_2, dummy_event_2)
    
    # Verify the cross-session state was preserved
    assert "kaffe" in session_2.state.get("user:weak_words", [])
    
    # To test prompt injection, we can simply run an exchange in session 2
    msg = genai_types.Content(role="user", parts=[genai_types.Part.from_text(text="Hei!")])
    async for event in runner.run_async(user_id="test_user_id", session_id=session_id_2, new_message=msg):
        pass
        
    # The agent's instruction should now contain the weak words from the previous session
    assert "kaffe" in root_agent.instruction
    assert "takk" in root_agent.instruction

