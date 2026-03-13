### ROAD_MAP_PHASE_3.md: Session Persistence and State

**Goal:** Add dynamic prompt engineering and within-session progress tracking.

1. **State Logic:**
- Create `norsk_agent/prompts.py`. Implement `build_instruction(scenario, state)` to generate a system prompt that adapts based on `words_practiced`.


2. **Tool & Lifecycle Updates:**
- Update `tools.py`
    - Modify `select_scenario` to initialize session state keys.
    - Implement `mark_word_practiced(word, correct)`.
    - Implement `get_progress()`.

- Update `agent.py`:
    - Implement `before_agent_callback` to call `build_instruction`.
    - Implement `after_agent_callback` to increment `exchange_count`.
    - Configure `InMemorySessionService`.


3. **Testing:**
- Create `tests/test_agent.py`. Use `InMemoryRunner` to simulate a session and assert that `state["exchange_count"]` increases.


4. **Persistence Upgrade:**
- Switch `InMemorySessionService` to `DatabaseSessionService` using SQLite.
