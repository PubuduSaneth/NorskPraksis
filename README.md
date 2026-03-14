# NorskPraksis - Norwegian Language Learning Agent

This repository contains a real-world agent implementation designed to teach agent development concepts using the Google Agent Development Kit (ADK).

## Overview

The **Norwegian Language Learning Agent** is a multi-turn conversational agent that:

- Guides users through language practice scenarios (café, hotel, train station, etc.)
- Dynamically tracks vocabulary mastery
- Learns from user mistakes and focuses on weak areas
- Maintains persistent user profiles across sessions
- Integrates external tools via the Model Context Protocol (MCP)

## Architecture

The system is built on the Google Agent Development Kit (ADK) and centers on a single `LlmAgent` that orchestrates the entire learning flow:

- **Operational loop.** The agent lifecyle (detailed in `Docs/Agent_Architecture_Diagrams.md`) cycles through context preparation (`on_before_agent`), LLM reasoning, MCP/local tool invocation, and state persistence (`on_after_agent`). This separation keeps instruction assembly, tool planning, and response generation loosely coupled and easy to test.
- **State and memory.** Short-term state lives in an ADK session service (SQLite), while long-term conversation summaries are stored via the memory service. Before each turn the agent can retrieve the three most recent memories to personalize the current instruction; after each turn it increments `exchange_count` and persists the transcript so progress survives restarts.
- **Scenario-driven prompts.** When a scenario is active, `prompts.build_instruction()` injects persona, vocabulary goals, and learner weaknesses into the system instruction so the LLM always role-plays the correct situation. When no scenario is active the agent falls back to the default Norwegian “menu mode” instruction augmented with retrieved memory snippets.
- **Tool ecosystem.** Local tools (listing/selecting scenarios, tracking vocabulary, progress, and user profile) manage structured application state, while an MCP toolset (backed by `mcp_vocab_server.py`) adds external vocabulary lookup capability. The ADK planner can mix these tool types in a single reasoning loop.
- **Design choices.** Leveraging callbacks and MCP keeps the agent modular: scenarios can evolve without touching tool code, and additional MCP servers can be registered without changing the core agent. Using SQLite for sessions offers persistence without extra infrastructure, and Gemini Live models provide low-latency, speech-capable interactions suited for language learning.

## Codebase Structure

- `norsk_praksis/norsk_agent/agent.py` – Declares the root `LlmAgent`, configures callbacks, registers local and MCP tools, and wires session/memory services.
- `norsk_praksis/norsk_agent/prompts.py` – Builds dynamic instructions for each scenario, embedding persona, opening lines, and learner focus areas.
- `norsk_praksis/norsk_agent/scenarios.py` – Defines the catalog of practice scenarios, their vocabularies, personas, and opening lines that drive role-play.
- `norsk_praksis/norsk_agent/tools.py` – Implements the ADK tools the agent can call (scenario selection, vocabulary lookup, progress tracking, marking practiced words, ending scenarios, user profile access).
- `norsk_praksis/mcp_vocab_server.py` – Stdio-based MCP server exposing vocabulary lookup/definition capabilities consumed through the MCP toolset.
- `tests/test_agent.py` – Smoke tests for the agent setup and scenario behaviors.
- `Docs/` – Deep architecture references (`Agent_Architecture_Diagrams.md`), annotated walkthroughs (`Agent_Deep_Dive.md`), and roadmap/spec files for each delivery phase.
- `vocabulary.json` – Shared vocabulary data backing scenarios and MCP resources.

## Project Setup

1. **Clone and enter the repo.**

    ```bash
    git clone https://github.com/PubuduSaneth/NorskPraksis.git
    cd NorskPraksis
    ```

2. **Install Python 3.11+.** The project targets `requires-python = ">=3.11"` (see `pyproject.toml`).
3. **Create the environment and install dependencies via uv.**

    ```bash
    cd norsk_praksis
    uv sync
    ```

    - `uv sync` inspects `pyproject.toml`, creates `.venv` automatically (Python 3.11+), and installs all declared dependencies.
    - If you still track additional packages in `requirements.txt`, run `uv add -r requirements.txt` once to import them into `pyproject.toml`, then delete the file or keep it for reference.

4. **(Optional) Re-sync or check the environment.**

    ```bash
    uv sync --frozen  # repeat only when you suspect drift or after editing pyproject.toml
    ```

5. **Configure credentials.** Create a `.env` (use `Docs/SPEC_N_ROADMAPs/SPEC_DEV.md` as a template) and set the required Google ADK keys, for example `GOOGLE_API_KEY` or Vertex AI credentials.

6. **Start the ADK web UI through uv.**

    ```bash
    uv run adk web . --no-reload
    ```

    Running through `uv run` guarantees the correct virtual environment and launches the Agent Dev Kit interface exposing the `norsk_agent` profile.

7. **Smoke test.** Connect to `norsk_agent` in the UI (or via `adk cli run norsk_agent`) and ensure the agent greets you in Norwegian, listing available scenarios. If MCP vocabulary lookups fail, confirm that `uv run ... mcp_vocab_server.py` can start on your machine.

## User Guide

- **Launching the tutor.** Run `uv run adk web . --no-reload` from the `norsk_praksis` directory, open the browser UI that ADK prints (usually `http://localhost:8000`), and select `norsk_agent`. Ensure your microphone is granted access if you want voice mode.

- **Selecting a scenario.** Start in “menu mode”: ask “Hva kan jeg øve på?” or click the tool shortcut so the agent calls `list_scenarios`. Say the scenario name (e.g., “Jeg vil øve på kafé”), and the agent will call `select_scenario` to switch personas and start the role-play with the appropriate opening line.

- **Practicing vocabulary.** During the scenario, request help (“Jeg trenger vokabular”) so the agent invokes `get_vocabulary` for focused phrases. As you speak, the agent uses `mark_word_practiced` to note words you mastered; you can ask “Hvordan går det?” to trigger `get_progress` for completion stats.

- **Managing sessions and memory.** Each exchange updates `exchange_count` and saves a session record. If you say “Jeg er ferdig” the agent calls `end_scenario`, resets state, and stores weak words for the next session. On the next visit the agent may remind you of unfinished vocabulary using the retrieved memory snippets.

- **Troubleshooting tips.**
  - If tool calls fail, confirm the MCP vocabulary server is running (ADK spawns it through `uv`; installing `uv` via `pip install uv` may be necessary).
  - If the agent stays in menu mode, verify that `scenarios.py` includes the scenario ID you requested.
  - To reset progress, delete `norsk_praksis/sessions.db` (clears session history) or remove the corresponding rows via the SQLite CLI.
