# ROAD MAP — Phase 4: Cross-Session Memory

## Goal
Extend the agent with user-scoped memory so returning learners receive personalized greetings, proficiency tracking, and targeted reinforcement of weak vocabulary across sessions.

## Deliverables
1. User-scoped state keys (`user:completed_scenarios`, `user:weak_words`, `user:total_sessions`, `user:proficiency_level`).
2. New tools `end_scenario()` and `get_user_profile()` handling memory ETL and personalization reads.
3. Updated `build_instruction()` to blend user profile data with session context.
4. Memory service integration (`InMemoryMemoryService`) plus logic to store/search memories at session boundaries.

## Tasks for Coding Agent
1. **State Schema**
   - Initialize and document the user-scoped keys listed above; ensure defaults exist when values are absent.
   - Define criteria for "completed scenario" (>70% accuracy) and "weak words" (<50% accuracy) within shared utility helpers if needed.
2. **Tooling Enhancements**
   - Implement `end_scenario()` to:
     - Compute per-scenario accuracy from session stats.
     - Update `user:completed_scenarios`, `user:weak_words`, `user:total_sessions`, and `user:proficiency_level`.
     - Produce a Norwegian summary describing performance and recommendations.
   - Implement `get_user_profile()` to expose the user-scoped snapshot for prompts and conversation.
3. **Prompt Personalization**
   - Update `build_instruction()` so it:
     - Personalizes greetings by proficiency tier (beginner: allow occasional English hints; intermediate: mostly Norwegian; advanced: fully Norwegian with faster pace).
     - Surfaces weak words from prior sessions and encourages revisiting them inside current scenarios.
     - Mentions completed scenarios to reinforce progress.
4. **Memory Service Wiring**
   - Configure the agent runner to attach `InMemoryMemoryService`.
   - After each session (e.g., inside `end_scenario()` or `after_agent_callback` when session concludes), store a concise memory entry summarizing scenario, accuracy, and standout issues.
   - At session start, run `search_memory` keyed by user ID and feed relevant snippets into the prompt or state.
5. **Validation**
   - Simulate multiple sessions (same `user_id`, different `session_id`s) ensuring greetings adapt, weak words resurface, and proficiency ladder steps correctly.
   - Confirm graceful handling when user history is empty.

## Acceptance Checklist
- Returning users hear greetings referencing past accomplishments and weak areas.
- Weak vocabulary from prior sessions appears organically in new conversations.
- Proficiency levels update based on completed scenarios and accuracy thresholds.
- Memory search retrieves past summaries and influences the prompt.
- User-scoped state persists across sessions regardless of session service backing.
