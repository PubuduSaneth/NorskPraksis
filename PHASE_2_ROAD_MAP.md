### ROAD_MAP_PHASE_2.md: Scenarios and Tools

**Goal:** Enable the agent to switch roles using function-as-tool patterns.

1. **Data Layer:**
- Create `norsk_agent/scenarios.py`. Define the 5 scenarios (Café, Hotel, Train, Grocery, Doctor) with metadata, personas, and vocabulary.

2. **Tool Development:**
- Create `norsk_agent/tools.py`.
- Implement `list_scenarios()`: Return IDs and titles.
- Implement `select_scenario(scenario_id)`: Return the full dictionary.
- Implement `get_vocabulary(scenario_id)`: Return word lists.
- *Note:* Ensure all functions have clear docstrings and type hints.

3. **Agent Integration:**
- Update `norsk_agent/agent.py`.
- Import tools and add to the `root_agent`'s `tools` list.
- Update system instructions to explain how to use these tools and return to "Menu Mode."

4. **Validation:**
- Test via `adk web`: Ask "Hvilke scenarioer har du?" or "What scenarios can we practice?" Expected Behavior: The agent will call the `list_scenarios` tool and read out the options
