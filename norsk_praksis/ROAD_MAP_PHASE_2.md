# ROAD MAP — Phase 2: Scenarios & Tools

## Goal
Expand the agent so it can list scenarios, switch personas via tool calls, and surface vocabulary for each scenario while remaining entirely voice-driven through ADK.

## Deliverables
1. New module files `norsk_agent/scenarios.py` and `norsk_agent/tools.py` populated per spec.
2. Updated `norsk_agent/agent.py` wiring all tools and refreshed instructions to support scenario selection flow.
3. Verified runtime behavior showing tool invocation for listing, selecting, and retrieving vocabulary.

## Tasks for Coding Agent
1. **Scenario Catalog**
   - Implement `scenarios.py` with a dict containing at least the five required scenarios (café, hotel, train, grocery, doctor).
   - Each entry must provide: `id`, `title_no`, `title_en`, `persona`, `opening_line`, and a 10–15 item vocabulary list of `{norwegian, english}` pairs.
2. **Tooling Layer**
   - In `tools.py`, implement `list_scenarios()`, `select_scenario(scenario_id: str)`, and `get_vocabulary(scenario_id: str)`.
   - Add precise docstrings describing intent and return shapes; ensure type hints use `dict` return types.
   - Handle invalid IDs gracefully with informative Norwegian error messaging.
3. **Agent Wiring**
   - Update `norsk_agent/agent.py` so `root_agent` imports the new tools and passes them via the `tools=[...]` argument.
   - Revise the instruction so the agent:
     - Opens in a scenario "menu" greeting and offers to describe choices.
     - Calls `list_scenarios` when asked about available practice options.
     - Invokes `select_scenario` when the user names one, then adopts its persona plus `opening_line`.
     - Leans on `get_vocabulary` to weave required terms into dialogue and when the user explicitly requests vocabulary help.
     - Recognizes commands like "bytt scenario" or "new scenario" to return to menu mode.
4. **Behavior Verification**
   - Manually exercise flows via `adk web`: ask for scenarios, pick one, request vocabulary, and trigger scenario switching.

## Acceptance Checklist
- Asking for available scenarios produces a tool-driven list readout.
- Selecting any of the five scenarios triggers persona change and uses the specified opening line.
- `get_vocabulary` is callable both proactively and on demand, with vocab reflecting the active scenario.
- "bytt scenario" resets the agent to menu mode without restarting the session.
- Persona, vocabulary, and corrections all stay in Norwegian and align with the chosen setting.
