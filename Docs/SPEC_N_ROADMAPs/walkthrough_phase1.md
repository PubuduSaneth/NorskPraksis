# Phase 1 Walkthrough: The Talking Agent (V2)

## Changes Made
- Scaffolded the project directory `norsk_praksis/norsk_agent/` replacing the previous nested structure.
- Created `requirements.txt` containing `google-adk`.
- Created `.env` with the Google API Key configuration.
- Instantiated the `LlmAgent` in `norsk_agent/agent.py` using `from google.adk.agents import LlmAgent`. 
- Set the model to `gemini-2.0-flash-exp` to correctly connect with the Live API endpoints provided by the current `google-genai` pip package.
- Defined the system instruction to force the agent into the Norwegian "café server in Oslo" persona, demanding short NORSK only replies.
- Exported the agent in `norsk_agent/__init__.py`.
- Started the `uv run adk web norsk_praksis` development server.

## What Was Tested
- ADK web server startup and correct module loading of the `norsk_agent`.

## Validation Results
- The Uvicorn web server loaded the agent properly from the exact directory spec and launched on `http://127.0.0.1:8000`. No validation errors or module load errors occurred.

## Next Steps
Navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. 
1. Select the `norsk_agent` from the agent dropdown.
2. Click the microphone icon to connect.
3. Verify that the agent immediately greets you as a Norwegian café server and only responds in Norwegian to your spoken audio!
