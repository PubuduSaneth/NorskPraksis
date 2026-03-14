# Documentation Structure

This documentation set explains agent development concepts through concrete code examples from this implementation.

### 1. **Agent_Development_Guide.md** - Main Concepts
Start here. This document explains:
- **Core Anatomy and Taxonomy of Agents**
  - The agent's operational loop (perceive → reason → act → persist)
  - Taxonomy of agent capabilities (observation, action, communication, memory, tool integration)

- **Tools, Interoperability, and MCP**
  - Tool design best practices
  - The Model Context Protocol architecture
  - Transport mechanism (stdio-based JSON-RPC)

- **Context Engineering – Sessions and Persistent Memory**
  - Session management and state evolution
  - Two-tier memory architecture (short-term + long-term)
  - How memory informs agent behavior

### 2. **Agent_Deep_Dive.md** - Code Walkthrough
Detailed line-by-line analysis of each component:
- **agent.py**: Agent setup, callbacks, service initialization
- **tools.py**: Seven tool implementations with architectural patterns
- **scenarios.py**: Scenario data structures as configuration
- **prompts.py**: Dynamic instruction generation
- Concrete state evolution example showing the learning journey

### 3. **Agent_Architecture_Diagrams.md** - Visual Guides
ASCII diagrams and visual representations:
- Detailed operational loop with all four phases
- Session state evolution over time
- Two-tier memory system (short-term vs. long-term)
- Tool invocation patterns (observation vs. action vs. orchestration)
- Context window evolution as conversation progresses
- Complete system architecture overview

## Codebase Structure

```
norsk_praksis/norsk_agent
├── agent.py              # Agent initialization, callbacks, services
├── tools.py              # Seven tool implementations
├── scenarios.py          # Scenario definitions (configuration data)
├── prompts.py            # Dynamic instruction building
├── mcp_vocab_server.py   # (Not shown) MCP service for vocabulary lookup
└── sessions.db           # SQLite database for session persistence
```

### agent.py (89 lines)
Initializes the root agent with:
- **System instruction**: Agent behavior specification
- **Before-agent callback**: Context preparation (memory search, instruction building)
- **After-agent callback**: State persistence (session serialization)
- **Service initialization**: Session storage + memory service
- **Tool registration**: Local tools + MCP toolset

### tools.py (163 lines)
Seven tools demonstrating different patterns:

| Tool | Pattern | Purpose |
|------|---------|---------|
| `list_scenarios()` | Observation | Discover available scenarios |
| `select_scenario()` | Action | Switch to new scenario, reset state |
| `get_vocabulary()` | Observation | Retrieve vocabulary for scenario |
| `mark_word_practiced()` | Action | Track learned words |
| `get_progress()` | Observation | Query session metrics |
| `end_scenario()` | Orchestration | Multi-step scenario completion, analysis, profile update |
| `get_user_profile()` | Observation | Cross-session user statistics |

### scenarios.py (107 lines)
Scenario definitions as data:
- Five scenarios (café, hotel, train station, grocery store, doctor)
- Each with: persona, opening_line, vocabulary list
- Configuration-driven: new scenarios need no code changes

### prompts.py (35 lines)
Dynamic instruction builder:
- Takes scenario + state
- Marks learned words with `[LÆRT]`
- Includes weak words from long-term memory
- Adds continuity cue (exchange count)

## Key Architectural Patterns

### 1. Dynamic Context Engineering
Instead of a static system prompt, the agent's instruction is dynamically constructed based on:
- Current state (active scenario)
- User progress (words practiced, completion percentage)
- Historical data (weak words from previous sessions)

**Benefits**: Agent behavior adapts without retraining; context window optimized per-turn.

### 2. Callback-Driven Lifecycle
Agent behavior is shaped by callbacks, not hardcoded logic:
```
on_before_agent() → Prepare context (memory + instruction)
                  ↓
             Agent reasoning
                  ↓
on_after_agent() → Persist state (session + memory)
```

**Benefits**: Clean separation of concerns; extensible without modifying agent.

### 3. Tool-Based State Mutation
All state changes happen through tools, never directly:
```python
# ✓ Tool modifies state
def select_scenario(tool_context, scenario_id):
    tool_context.state["active_scenario_id"] = scenario_id

# ✗ Not directly in callbacks
```

**Benefits**: Auditability; consistency; understandability.

### 4. Two-Tier Memory
- **Short-term**: Session state (in-memory, fast)
- **Long-term**: Persistent storage (database, queryable)

Memory informs behavior during context preparation, not during reasoning.

### 5. MCP Integration
External tools are accessed through the Model Context Protocol:
```python
mcp_toolset = McpToolset(
    connection_params=StdioServerParameters(
        command="uv",
        args=["run", "mcp_vocab_server.py"]
    )
)
```

**Benefits**: Decoupling; extensibility; tool swappability.

## Learning Outcomes

After studying this agent and documentation, you should understand:

1. **How agents work**
   - Perception → Reasoning → Action → Persistence loop
   - Tool invocation and state management
   - Callback-driven lifecycle

2. **Tool design**
   - Single responsibility principle
   - Observation vs. action vs. orchestration tools
   - Error handling and validation

3. **Context engineering**
   - Dynamic instruction generation
   - State evolution and queries
   - Session vs. user-level concerns

4. **Memory architectures**
   - Short-term (session) vs. long-term (persistent)
   - Memory-informed behavior
   - Cross-session continuity

5. **Interoperability**
   - Model Context Protocol basics
   - Tool discovery and composition
   - Graceful degradation

## Running the Agent

(Assuming Google ADK environment is set up)

```bash
python -m agent
```

The agent will:
1. Load scenarios from `scenarios.py`
2. Initialize SQLite session storage
3. Start listening for user input
4. On each turn:
   - Search memory for personalization
   - Build dynamic instruction
   - Call Gemini 2.5 Flash for reasoning
   - Execute tools as needed
   - Persist session to memory

## Key Files for Understanding

| Document | Best for | Time |
|----------|----------|------|
| Agent_Development_Guide.md | Concepts + examples | 30-45 min |
| Agent_Deep_Dive.md | Line-by-line code analysis | 45-60 min |
| Agent_Architecture_Diagrams.md | Visual understanding | 20-30 min |

**Suggested reading order:**
1. Start with **Agent_Development_Guide.md** to understand concepts
2. Review **Agent_Architecture_Diagrams.md** for visual intuition
3. Deep dive into **Agent_Deep_Dive.md** for implementation details
4. Reference the actual code as you read each section

## Architectural Decisions and Rationales

### Why SQLite for Sessions?
- Persistent across process restarts
- Simple setup (no external database)
- Good enough for single-user demo
- (Production would use managed database)

### Why InMemoryMemoryService for Long-Term Memory?
- Demonstrates memory pattern without complexity
- (Production would use vector database for semantic search)

### Why Callbacks Instead of Direct State Management?
- Separates concerns (context ≠ reasoning ≠ persistence)
- Easier to test and extend
- Agent core unchanged when adding new behavior

### Why Dynamic Instructions?
- Context-aware behavior without retraining
- Efficient (no need to include irrelevant information)
- Enables in-context learning (marking `[LÆRT]` words)

### Why MCP for External Tools?
- Standard protocol (not proprietary)
- Decoupled (external service independent)
- Composable (multiple MCP servers)
- Accessible (JSON-RPC over stdio)

## Extending the Agent

### Add a New Scenario
1. Edit `scenarios.py`: Add entry to `SCENARIOS` dict
2. Done! No code changes needed.

### Add a New Tool
1. Create function in `tools.py` following tool patterns
2. Register in `agent.py`: Add to `tools=[]` list
3. Update instruction to mention when to use it

### Change Agent Behavior
1. Edit `prompts.py`: Modify `build_instruction()` to add new context
2. Agent automatically uses enhanced instruction
3. No retraining needed!

### Integrate New MCP Service
1. Create MCP server (follows server spec)
2. Create McpToolset with connection params
3. Register in agent tools list
4. Done! Tools automatically discovered.

## Troubleshooting

**Agent doesn't remember previous sessions?**
- Check that `sessions.db` is being persisted
- Verify `on_after_agent` is being called
- Check memory service implementation

**Agent ignores vocabulary status `[LÆRT]`?**
- Verify `build_instruction()` is marking words
- Check agent instruction actually includes vocabulary list
- Agent might not be looking at words (confirm in instruction)

**MCP tool not available?**
- Verify external server is running: `uv run mcp_vocab_server.py`
- Check stdio connection params match server expectations
- Examine agent logs for MCP connection errors

## References

- **Google ADK Documentation**: ADK concepts and API
- **Model Context Protocol (MCP)**: Tool protocol specification
- **Anthropic Agents Documentation**: Building agents with Claude
- **This codebase**: Real-world implementation example

---

**Last Updated**: March 2025
**Version**: 1.0
**Author**: Educational example using Google ADK
