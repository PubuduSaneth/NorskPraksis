### ROAD_MAP_PHASE_5.md: MCP Integration

**Goal:** Decouple vocabulary data using the Model Context Protocol.

1. **MCP Server Construction:**
- Create a standalone script `mcp_vocab_server.py`.
- Implement an MCP server that reads `vocabulary.json`.
- Expose tool `lookup_word` and resource `vocabulary://{id}`.

2. **ADK Connection:**
- In `agent.py`, configure the ADK agent to connect to the MCP server via `stdio` transport.
- Add MCP tools to the agent's toolset.

3. **Hybrid Logic:**
- Update system instructions: "If a user asks for a definition, use the `lookup_word` tool from the external registry."
- Implement graceful fallback: if the MCP server is unreachable, the agent should use the local `scenarios.py` data.

4. **Validation:**
- Start the MCP server.
- Ask the agent: "Hva betyr ordet 'regning'?" and verify it provides the definition from the JSON file via MCP.
