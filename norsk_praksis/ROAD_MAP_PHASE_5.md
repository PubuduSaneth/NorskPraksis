# ROAD MAP — Phase 5: MCP Vocabulary Integration

## Goal
Replace hardcoded vocabulary lookups with an MCP-connected vocabulary service so the agent can query external data sources transparently through ADK.

## Deliverables
1. Standalone MCP server (stdio transport) exposing the `lookup_word` tool and `vocabulary://{scenario_id}` resource backed by a JSON data file.
2. Shared `vocabulary.json` containing all scenario vocab plus additional standalone entries.
3. ADK agent updates that register MCP tools/resources alongside native Python tools and prefer MCP lookups when available.

## Tasks for Coding Agent
1. **Vocabulary Data Store**
   - Create `vocabulary.json` with structure `{ "words": [ { "norwegian", "english", "example_no", "example_en", "pronunciation", "difficulty", "scenario_id"? } ] }`.
   - Ensure every scenario has a corresponding slice plus some extra words for ad-hoc lookups.
2. **MCP Server Implementation**
   - Build a lightweight MCP server process (can live in `mcp_vocabulary_server.py` or similar) that:
     - Loads `vocabulary.json` at startup.
     - Implements tool `lookup_word(norwegian_word: str) -> dict` returning definition, example sentence, pronunciation guidance, and difficulty tier.
     - Implements resource `vocabulary://{scenario_id}` returning the full vocab list for that scenario.
     - Communicates over stdio transport per MCP conventions.
3. **ADK Integration**
   - Update agent startup to spawn/connect to the MCP server via ADK's MCP client utilities.
   - Register the MCP-provided tool/resource in the agent's `tools` array alongside local functions.
   - Modify instructions so the agent:
     - Prefers `lookup_word` when a user asks for meanings, pronunciation, or usage of a specific Norwegian word.
     - Falls back to local `scenarios.py` vocabulary if the MCP server is offline, logging the degradation but keeping UX steady.
4. **Runtime Validation**
   - Launch MCP server, start `adk web`, and verify that asking "Hva betyr <word>?" triggers MCP tool calls seen in logs.
   - Stop the MCP server and confirm the agent gracefully uses the built-in vocabulary without user-visible errors.
5. **Documentation**
   - Add run instructions describing how to start the MCP server before `adk web` and how to troubleshoot connection failures.

## Acceptance Checklist
- MCP server responds to `lookup_word` and `vocabulary://{scenario_id}` requests over stdio.
- Live sessions show the agent invoking MCP tools automatically for word queries.
- Removing or stopping the MCP server reverts to local vocabulary with clear logging but uninterrupted UX.
- No behavioral difference is visible to users between MCP and local tool invocations aside from richer data.
