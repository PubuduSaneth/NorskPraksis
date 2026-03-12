### ROAD_MAP_PHASE_1.md: The Talking Agent

**Goal:** Initialize the project and build a minimal voice-enabled agent.

1. **Project Setup:**
- Create directory structure: `norsk_praksis/norsk_agent/`.
- Create `requirements.txt` with `google-adk`.
- Create `.env` based on the `SPEC_DEV` template (ensure `GOOGLE_API_KEY` or Vertex AI variables are set).

2. **Implementation:**
- In `norsk_agent/agent.py`:
    - Import `LlmAgent` from `google_adk`.
    - Define `root_agent` using `gemini-2.0-flash-live`.
    - Set the `instruction` to the "Oslo Café Server" persona in Norwegian.
- In `norsk_agent/__init__.py`:
    - Expose `root_agent`.

3. **Validation:**
- Run `adk web` in the root.
- Connect to `norsk_agent` and verify the agent initiates the conversation with a Norwegian greeting.
