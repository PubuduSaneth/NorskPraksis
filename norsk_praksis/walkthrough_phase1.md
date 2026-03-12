# Phase 1 Walkthrough: Talking Agent

## Changes Made
- Scaffolded project directories for the `norsk_agent`.
- Created [src/norsk_praksis/norsk_agent/agent.py](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/src/norsk_praksis/norsk_agent/agent.py) to define the minimalist `LlmAgent` powered by `gemini-2.0-flash-live`.
- Programmed a custom system instruction specifying the persona (Oslo café server, Norwegian-only output, grammar corrections, brief answers).
- Exported the agent properly into the `norsk_praksis` Python module via [__init__.py](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/src/norsk_praksis/__init__.py).
- Verified [.env](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/.env) configuration (ensuring VertexAI routing is `FALSE` and using standard Developer API with `GOOGLE_API_KEY`).

## What Was Tested
- Executed `uv run adk web` to confirm the application begins smoothly.
- The Uvicorn web server loaded the agent properly and launched on `http://127.0.0.1:8000`.

## Validation Results
- The `google-adk` backend starts correctly and exposes the `adk web` interface exactly as requested in Phase 1 of the roadmap.

## Next Steps
Please navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. 
1. Select the `root_agent` from the agent dropdown.
2. Click the microphone icon or "Connect" button.
3. Try speaking to the agent in English or broken Norwegian (e.g. "I want to order coffee please").
4. The agent is strictly commanded to reply solely in spoken Norwegian as a café server and offer gentle correction if you make mistakes.
