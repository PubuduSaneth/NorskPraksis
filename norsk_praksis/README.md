# Norsk Praksis Package Guide

This README covers everything you need when working **inside** the `norsk_praksis/` package directory—environment creation, local runs, tests, and troubleshooting that assumes paths relative to this folder.

## Prerequisites
- Python 3.11 or newer (matches `requires-python = ">=3.11"` in `pyproject.toml`).
- `uv` package manager installed globally (`pip install uv`).
- A `.env` file with your Google ADK / Gemini credentials (follow `Docs/SPEC_N_ROADMAPs/SPEC_DEV.md`).

## Environment Setup (package-scoped)
```bash
cd norsk_praksis
uv sync            # Creates .venv/ and installs google-adk, mcp, etc.
uv sync --frozen   # Repeat when you change pyproject.toml or need reproducibility
source .venv/bin/activate  # Optional; uv run automatically uses the env
```

`uv sync` inspects `pyproject.toml`, installs dependencies, and pins them in `uv.lock`. The `requirements.txt` is legacy—`uv add -r requirements.txt` once imports any stragglers.

## Running the Agent
From `norsk_praksis/`:

```bash
# Launch the ADK browser UI (default http://localhost:8000)
uv run adk web . --no-reload

# CLI-only run if you do not need the UI
uv run adk cli run norsk_agent
```

During startup the agent will spawn the MCP vocab server automatically using the same `uv` environment. If you need to run it manually (for debugging):

```bash
uv run mcp_vocab_server.py
```

## Running Tests
```bash
cd norsk_praksis
uv run pytest              # Full suite (currently async smoke tests)
uv run pytest tests/test_agent.py -k scenario  # Focus on scenario-related tests
```

Tests leverage `InMemoryRunner`, so no external services are required. Aim to add new tests next to `tests/test_agent.py` and run them through `uv run pytest` to ensure the virtual environment is honored.

## Useful Paths
- `norsk_agent/agent.py` — Defines the `LlmAgent`, callbacks, and tool registration.
- `norsk_agent/tools.py` — Scenario selection, vocabulary tracking, user profile tools.
- `norsk_agent/prompts.py` — Dynamic instruction builder (injects weak words / learned vocab).
- `norsk_agent/scenarios.py` — Scenario metadata and vocabulary lists.
- `mcp_vocab_server.py` — FastMCP server providing the `lookup_word` tool.
- `tests/test_agent.py` — Async smoke tests for lifecycle and memory behavior.

## Troubleshooting Checklist
- **`ImportError` for google.adk** → Ensure `uv sync` completed successfully and you are running commands via `uv run` (which activates `.venv` automatically).
- **MCP tool missing** → Start `uv run mcp_vocab_server.py` in a separate terminal to confirm the server runs; the agent invokes it through stdio so any exceptions appear in this terminal.
- **State not persisting** → Delete `sessions.db` (in this folder) to reset, then rerun; verify `SqliteSessionService` has write permission to the directory.
- **Credential errors** → Double-check `.env` values (e.g., `GOOGLE_API_KEY`) and reload your shell so `uv run` inherits them.

For deeper architecture guidance, see the repo-level `README.md` plus `Docs/Agent_Development_Guide.md` and the Phase roadmaps in `Docs/SPEC_N_ROADMAPs/`.
