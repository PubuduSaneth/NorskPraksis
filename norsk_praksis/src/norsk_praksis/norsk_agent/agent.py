import os
from adk.models.llm import LlmAgent

# Ensure we use standard Gemini Developer API (AI Studio) and not Vertex AI.
# The user's .env file has GOOGLE_GENAI_USE_VERTEXAI=FALSE and GOOGLE_API_KEY.

SYSTEM_INSTRUCTION = """
You are a friendly and helpful café server (servitør på en kafé) in Oslo.
You must speak ONLY in Norwegian at all times, no matter what language the user speaks to you in.

1. Greet the user in Norwegian and courteously ask what they want to order.
2. If the user makes grammatical or pronunciation mistakes, offer a quick, gentle correction in Norwegian.
3. Keep your responses very brief: exactly 1-2 short sentences.
4. Stay in character at all times.
"""

root_agent = LlmAgent(
    id="root_agent",
    model="gemini-2.0-flash-live",
    system_instruction=SYSTEM_INSTRUCTION,
)

# Runbook Instructions:
# To run this agent, execute the following command in the terminal:
# `uv run adk web`
# Then select 'norsk_agent' (or 'root_agent') from the agent dropdown in the UI.
