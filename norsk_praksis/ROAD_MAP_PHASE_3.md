# ROAD MAP — Phase 3: Session Persistence & State

## Goal
Give the agent session awareness: remember the current scenario, exchange counts, and vocabulary performance within a session, and generate dynamic prompts based on that evolving state.

## Deliverables
1. New module `norsk_agent/prompts.py` housing `build_instruction()` logic.
2. Enhanced `norsk_agent/tools.py` with session-mutating behavior plus `mark_word_practiced()` and `get_progress()`.
3. Updated `norsk_agent/agent.py` wiring callbacks, session service, and stateful prompt handling.
4. Test coverage via `tests/test_agent.py` using `InMemoryRunner` to validate state transitions.

## Tasks for Coding Agent
1. **Dynamic Prompt Builder**
   - Implement `build_instruction(scenario: dict, session_state: dict) -> str` in `prompts.py`.
   - Prompt must inject persona, exchange count, practiced vs. remaining vocabulary, and adaptive difficulty messaging.
2. **Stateful Tools**
   - Update `select_scenario` to write `current_scenario_id`, reset `exchange_count`, `words_practiced`, and `words_correct` in session state.
   - Add `mark_word_practiced(word: str, correct: bool)` to log usage and accuracy, returning a summary of progress.
   - Add `get_progress()` to surface scenario, exchange count, practiced words, and accuracy percentage.
3. **Agent Callbacks & Session Service**
   - Configure `root_agent` to use `InMemorySessionService()` initially.
   - Add `before_agent_callback` that looks up the active scenario from state, calls `build_instruction`, and sets the instruction each turn.
   - Add `after_agent_callback` to increment `exchange_count` and capture any other bookkeeping like last response.
   - Set `output_key="last_response"` so responses persist in state.
   - Document the single-line change needed to swap in `DatabaseSessionService(db_url="sqlite+aiosqlite:///norsk_sessions.db")` later.
4. **Testing**
   - Create `tests/test_agent.py` verifying: scenario selection writes state; `mark_word_practiced` updates counts; `get_progress` reflects reality; callbacks honor state mutations.
5. **Manual Verification**
   - Run `adk web`, select a scenario, speak multiple turns, and confirm state-driven adaptation (forces prompts to mention unpracticed vocab, etc.).

## Acceptance Checklist
- Scenario selections persist in state for the session.
- `mark_word_practiced` and `get_progress` provide accurate metrics available to the agent mid-dialogue.
- Dynamic prompts reflect practiced vs. remaining vocabulary and adjust difficulty accordingly.
- Switching to `DatabaseSessionService` enables persistence across restarts without further code changes.
- Test suite passes locally, proving state bookkeeping works deterministically outside the live UI.
