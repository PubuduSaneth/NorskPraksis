# ROAD MAP — Phase 1: Talking Agent

## Goal
Stand up the minimal NorskPraksis agent that speaks Norwegian via ADK, using a single café-server persona and running entirely through `adk web`.

## Deliverables
1. Project skeleton: `norsk_praksis/`, `norsk_agent/`, `.env`, `requirements.txt`.
2. Functional `root_agent` exposed via `norsk_agent/__init__.py` and defined in `norsk_agent/agent.py`.
3. Verified microphone-to-audio response loop in `adk web` with Norwegian-only voice replies.

## Tasks for Coding Agent
1. **Scaffold**
   - Create `norsk_praksis/` and nested `norsk_agent/` with `__init__.py` and `agent.py`.
   - Ensure package init re-exports `root_agent`.
2. **Dependencies**
   - Write `requirements.txt` containing only `google-adk`.
3. **Environment Configuration**
   - Populate `.env` with the exact variables from SPEC_DEV (project, location, key). Leave placeholder values but document where real credentials go.
4. **Agent Implementation**
   - In `agent.py` define a single `LlmAgent` named `root_agent` targeting `gemini-2.0-flash-live` (or the latest Live-capable model).
   - Craft the Norwegian system instruction that:
     - Establishes the persona (servitør på en kafé i Oslo).
     - Forces Norwegian-only output.
     - Greets first and asks what the user wants to order.
     - Promises gentle pronunciation/grammar corrections.
     - Keeps responses to 1–2 sentences.
5. **Runbook Instructions**
   - Document in comments or module docstring that the app is launched via `adk web` and the agent is selected from the UI.

## Acceptance Checklist
- `adk web` starts cleanly.
- `norsk_agent` appears in the agent dropdown.
- Speaking English through the mic yields a Norwegian audio reply.
- Persona stays consistent with the café server role.
- Responses are short and include pronunciation or grammar coaching as needed.
