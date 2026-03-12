from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.sessions.sqlite_session_service import SqliteSessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from .tools import list_scenarios, select_scenario, get_vocabulary, mark_word_practiced, get_progress, end_scenario, get_user_profile
from .prompts import build_instruction
from .scenarios import SCENARIOS

SYSTEM_INSTRUCTION = """
Du er en vennlig og tålmodig norsk språkpartner. 
Bruk alltid norsk.

Du befinner deg først i en "meny"-modus. 
Hovedoppgaven din her er å hjelpe brukeren med å velge et praksis-scenario.
Bruk `list_scenarios`-verktøyet for å fortelle brukeren hvilke scenarioer (situasjoner) de kan øve på.

Når brukeren har valgt et scenario, eller du forstår hvilket de vil bruke, bruk `select_scenario`-verktøyet for å bytte rolle.
Etter å ha byttet rolle, ta umiddelbart på deg den nye personligheten (persona) og start samtalen med 'opening_line' fra scenarioet.
Hold deg i denne rollen og svar utelukkende på norsk.
Hold svarene dine svært korte (1-2 små setninger).
Dersom brukeren gjør grammatikkfeil eller uttaler noe feil, gi en rask og vennlig korreksjon på norsk.

Hvis brukeren står fast eller ber om hjelp til noen ord ("hva sier jeg?", "trenger vokabular"), bruk `get_vocabulary`-verktøyet for det valgte scenarioet og foreslå 2-3 relevante norske uttrykk med engelsk oversettelse.

Dersom brukeren sier "bytt scenario" eller "new scenario", gå ut av rollen din og tilbake til "meny"-modus for å velge et nytt scenario.
"""

async def on_before_agent(callback_context: CallbackContext):
    state = callback_context.state
    scenario_id = state.get("active_scenario_id")
    
    memory_info = ""
    # Search memory if no active scenario yet to personalize greeting
    if not scenario_id:
        try:
            memories = await callback_context.search_memory("scenario fullført")
            if memories and memories.memories:
                memory_info = "\n\nKontekst fra tidligere samtaler:\n"
                for mem in memories.memories[-3:]: # last 3 memories
                    memory_info += f"- {mem.content.parts[0].text if mem.content and mem.content.parts else ''}\n"
        except Exception:
            pass

    if scenario_id and scenario_id in SCENARIOS:
        scenario = SCENARIOS[scenario_id]
        new_instruction = build_instruction(scenario, state)
        root_agent.instruction = new_instruction
    else:
        root_agent.instruction = SYSTEM_INSTRUCTION + memory_info

async def on_after_agent(callback_context: CallbackContext):
    count = callback_context.state.get("exchange_count", 0)
    callback_context.state["exchange_count"] = count + 1
    
    try:
        await callback_context.add_session_to_memory()
    except Exception:
        pass

session_service = SqliteSessionService("sessions.db")
memory_service = InMemoryMemoryService()

root_agent = LlmAgent(
    name="norsk_agent",
    model="gemini-2.5-flash",
    instruction=SYSTEM_INSTRUCTION,
    tools=[list_scenarios, select_scenario, get_vocabulary, mark_word_practiced, get_progress, end_scenario, get_user_profile],
    before_agent_callback=on_before_agent,
    after_agent_callback=on_after_agent,
)
