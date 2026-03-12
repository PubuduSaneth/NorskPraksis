# Phase 2 Walkthrough: Scenarios and Tools

## Changes Made
- Created [norsk_agent/scenarios.py](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/norsk_agent/scenarios.py) defining 5 separate environments: Café, Hotel, Train, Grocery, Doctor.
- Created [norsk_agent/tools.py](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/norsk_agent/tools.py) with three strongly-typed and documented utility functions:
  - [list_scenarios()](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/norsk_agent/tools.py#3-21): Exposes scenario titles to the LLM.
  - [select_scenario()](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/norsk_agent/tools.py#22-44): Returns full persona and opening lines, allowing the LLM to switch its internal context.
  - [get_vocabulary()](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/norsk_agent/tools.py#45-58): Selectively injected translation aids triggered upon user request.
- Updated [norsk_agent/agent.py](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/norsk_agent/agent.py):
  - Expanded the `SYSTEM_INSTRUCTION` into a robust "Menu Mode" router.
  - Passed `[list_scenarios, select_scenario, get_vocabulary]` into the `LlmAgent` initialization.

## What Was Tested
- Server restart and agent discovery under the new tool configuration.

## Next Steps
Navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.
1. Connect via the Microphone.
2. Ask the agent: *"Hvilke scenarioer har du?"* (Which scenarios do you have?)
3. The ADK network log on the right side of the screen should indicate a [list_scenarios](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/norsk_agent/tools.py#3-21) Tool Call execution. The agent will then read the 5 scenarios aloud to you in Norwegian.
4. Tell the agent which one you want, e.g., *"Jeg vil øve på hotellet"* (I want to practice at the hotel). The agent will use [select_scenario](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/norsk_agent/tools.py#22-44) and seamlessly adopt the Hotel Receptionist persona immediately!
