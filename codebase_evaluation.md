# Codebase Evaluation Report

## Architecture & Functionality Overview

The `norsk_agent` codebase implements a Norwegian language learning AI agent, constructed using the `google.adk` framework. Through this framework, the agent leverages the `LlmAgent` and is powered by a Gemini language model (`gemini-2.5-flash`).

The primary goal of the system is to provide an interactive dialogue for practicing Norwegian in various real-world scenarios, while tracking the user's progress and vocabulary mastery.

### Core Components

- **[agent.py](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/norsk_agent/agent.py)**: The entrypoint for defining the ADK agent.
  - Exposes the main `root_agent` (`LlmAgent`).
  - Implements session and memory persistence using `SqliteSessionService` and `InMemoryMemoryService`.
  - Defines pre- and post-generation lifecycle callbacks ([on_before_agent](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/norsk_agent/agent.py#30-52), [on_after_agent](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/norsk_agent/agent.py#53-61)) to inject dynamic context, track usage statistics (`exchange_count`), and save sessions.

- **[tools.py](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/norsk_agent/tools.py)**: Contains all functional tools mapped to the LLM agent to interact with the learning experience.
  - Features robust state tracking within the context (`tool_context.state`) for active scenarios, vocabulary practice tracking, and tracking long-term user profile statistics (e.g. `user:completed_scenarios`, `user:weak_words`).
  - Exposes tools like [select_scenario](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/norsk_agent/tools.py#23-51), [get_vocabulary](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/norsk_agent/tools.py#52-65), [mark_word_practiced](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/norsk_agent/tools.py#66-86), [end_scenario](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/norsk_agent/tools.py#114-148), and [get_user_profile](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/norsk_agent/tools.py#149-163).

- **[prompts.py](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/norsk_agent/prompts.py)**: Manages dynamic prompt creation.
  - The [build_instruction](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/norsk_agent/prompts.py#1-35) function weaves together the persona of the chosen scenario with the current session state, selectively injecting the user's `weak_words` or active [vocabulary](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/norsk_agent/tools.py#52-65) constraints to ensure tailored practice.

- **[scenarios.py](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/norsk_agent/scenarios.py)**: Acts as the data source for the language situations.
  - Includes scenarios like "cafe", "hotel", "train", "grocery", and "doctor".
  - Each provides a thematic persona, an opening line, and specialized Norwegian-English vocabulary lists to test the user against.

## Python Dependency Environment

The Python environment setup relies on `uv` to create a virtual environment and manage dependencies. It is currently very lightweight, relying strictly on:
- `google-adk`

### Setup Execution Status
- The environment has been fully initialized with `uv venv`.
- All required packages from [requirements.txt](file:///Users/pubuduss/Developer/com/NorskPraksis/norsk_praksis/requirements.txt) were successfully installed via `uv pip install`.
