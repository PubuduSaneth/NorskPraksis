### ROAD_MAP_PHASE_4.md: Cross-Session Memory

**Goal:** Personalize the experience using user-scoped state and memory search.

1. **User Profiling Tools:**
- Update `tools.py`:
    - Implement `end_scenario()`: Calculate accuracy, update `user:completed_scenarios` and `user:weak_words`.
    - Implement `get_user_profile()`: Retrieve cross-session stats.

2. **Memory Integration:**
- Configure `InMemoryMemoryService` on the agent runner.
- In `after_agent_callback`, logic to `search_memory` for previous session summaries to inform the current greeting.


3. **Prompt Personalization:**
- Update `build_instruction` in `prompts.py` to accept the user profile.
- Inject "weak words" from previous sessions into the current scenario's instruction.


4. **Validation:**
- Run two separate sessions with the same `user_id`. Verify the agent mentions a word the user failed in the previous session.
