# Agent Brief

## Mission Snapshot
- Build a Norwegian language tutor that guides learners through realistic role-play scenarios while reinforcing weak vocabulary using Google ADK.
- Primary users are agent developers learning ADK patterns; stakeholders are the edukit maintainers planning phased deliveries described in Docs/SPEC_N_ROADMAPs.
- Current state: single LlmAgent running Gemini Live 2.5 Flash with MCP-assisted vocabulary lookup, backed by SQLite sessions and in-memory long-term memory.
- Key dependencies: Google ADK runtime/services, uv-managed Python 3.11 environment, external MCP vocab server (FastMCP), vocabulary.json data store.

## Tech Stack & Tooling
- Python 3.11+, Google ADK (>=1.27.0), FastMCP (from mcp>=1.26.0), Gemini Live 2.5 Flash audio model.
- Dependency management via uv (`uv sync`, `uv run ...`).
- Local agent run: `cd norsk_praksis && uv run adk web . --no-reload` to launch the ADK UI (or `uv run adk cli run norsk_agent`).
- MCP vocab server auto-spawned via uv when the toolset is first invoked; can also be run manually with `uv run mcp_vocab_server.py`.
- Tests: `cd norsk_praksis && uv run pytest` (see tests/test_agent.py).

## Core Components
| Area | Role | Key Files | Notes |
|------|------|-----------|-------|
| Agent orchestration | Defines the `LlmAgent`, lifecycle callbacks, session/memory services, MCP toolset | norsk_praksis/norsk_agent/agent.py | `on_before_agent` swaps instructions per scenario and injects memory context; `on_after_agent` increments `exchange_count` and syncs sessions. |
| Prompting | Builds dynamic instructions per scenario with weak-word emphasis and `[LÆRT]` markers | norsk_praksis/norsk_agent/prompts.py | `build_instruction()` tailors persona, vocabulary focus, and conversation length awareness. |
| Scenario catalog | Provides role-play metadata and vocabulary lists | norsk_praksis/norsk_agent/scenarios.py | Five scenarios today (cafe, hotel, train, grocery, doctor); structure allows drop-in additions. |
| Local tools | ADK tools for listing/selecting scenarios, tracking vocab progress, ending sessions, showing profile | norsk_praksis/norsk_agent/tools.py | Tool context stores both session (`active_scenario_id`, `words_practiced`) and longitudinal stats (`user:*`). |
| MCP vocabulary | FastMCP stdio server exposing `lookup_word` + resource endpoint over vocabulary.json | norsk_praksis/mcp_vocab_server.py | Consumed via `McpToolset` with `use_mcp_resources=True` so words also appear in Tool/Resource lists. |
| Data assets | Vocabulary store backing MCP + docs/roadmaps describing phases | vocabulary.json, Docs/** | `vocabulary.json` holds Norwegian/English pairs plus usage examples. |
| Tests | Async pytest smoke tests for lifecycle + memory behaviors | norsk_praksis/tests/test_agent.py | Uses InMemoryRunner; validates exchange counter, scenario selection, cross-session weak-word carryover. |

## Data & Knowledge Assets
- vocabulary.json: canonical list of Norwegian words with translations, example sentences, pronunciations; used by both scenarios and MCP resources.
- Docs/Agent_Development_Guide.md + Agent_Deep_Dive.md: conceptual + line-by-line walkthroughs for onboarding.
- Docs/SPEC_N_ROADMAPs/*: phase-by-phase roadmap, specs, and walkthroughs that describe desired behaviors and delivery milestones.
- Docs/Agent_Architecture_Diagrams.md: ASCII sequence/state diagrams of the perception→reason→act→persist loop and memory tiers.

## Integration & Flows
- `on_before_agent` loads recent memories (when in menu mode) and rebuilds instructions from `prompts.build_instruction()` whenever a scenario is active.
- Scenario selection + progress tracking happen exclusively through tools (`select_scenario`, `mark_word_practiced`, `end_scenario`), keeping callbacks side-effect free.
- MCP toolset launches FastMCP via uv, exposing `lookup_word` plus `vocabulary://{word}` resources; fallback logic in SYSTEM_INSTRUCTION directs the agent to use local knowledge if MCP fails.
- Sessions persist through `SqliteSessionService`, while long-term stats (weak words) are maintained in state and optionally promoted into `InMemoryMemoryService` via `add_session_to_memory()`.
- Tests rely on `InMemoryRunner` to simulate exchanges and validate that callbacks mutate state as intended.

## Risks & Gaps
- `end_scenario()` builds `target_words` using a non-existent `"norwegian"` key; vocabulary entries use `"no"`, so weak word tracking never records anything (see norsk_praksis/norsk_agent/tools.py).
- `norsk_praksis/README.md` is empty; developers must rely on the root README for setup, which may cause confusion when running commands inside the package folder.
- Only three async smoke tests exist; no direct tool unit tests or MCP server coverage, so regressions in tool logic will go undetected.
- Long-term memory service is in-memory only; restarts wipe weak-word history despite documentation claiming persistence.
- No CI configuration in repo; `uv sync`/pytest instructions rely on manual execution.

## Next-Step Recommendations
1. Fix `end_scenario()` to read vocabulary entries via `v["no"]` (or `v.get("norwegian")`) so weak-word tracking works; add unit tests for this flow.
2. Flesh out `norsk_praksis/README.md` with run/test instructions scoped to the package directory and clarify uv usage.
3. Add tooling/tests around MCP server (e.g., contract test that `lookup_word()` returns expected JSON) and around each ADK tool to ensure state mutations remain correct.
4. Persist long-term memory to durable storage (SQLite table or vector store) so weak words survive process restarts, aligning with documentation claims.
5. Wire CI (GitHub Actions) to run `uv sync --frozen` + `uv run pytest` on pull requests for early regression detection.
