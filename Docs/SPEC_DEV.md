# SPEC_DEV: NorskPraksis — Norwegian Roleplay Agent

## Document Purpose

This specification is the single source of truth for building NorskPraksis, a voice-first Norwegian language practice application. Each phase below maps 1:1 to a `ROAD_MAP_PHASE<n>.md` file that provides coding directives.

No code appears in this document. Each phase states exactly what to build, what concepts it teaches, and what the acceptance criteria are.

---

## Application Scope (Fixed)

NorskPraksis does one thing: it simulates real-world Norwegian roleplay scenarios through voice conversation. A user picks a scenario (ordering coffee, checking into a hotel, buying a train ticket), and the agent adopts the corresponding Norwegian persona. The user practices speaking Norwegian. The agent responds in Norwegian. That is the entire application.

There are no plans to extend capabilities beyond roleplay scenarios.

---

## Tech Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Agent framework | Google Agent Development Kit (ADK) for Python | Abstracts Gemini Live API complexity |
| Real-time voice | ADK Gemini Live API Toolkit (`LiveRequestQueue`) | Bidirectional audio streaming |
| Model | `gemini-2.0-flash-live` (or latest Live-capable model) | Required for real-time voice I/O |
| Frontend | `adk web` (development UI) | No custom frontend needed |
| Session storage | `InMemorySessionService` → `DatabaseSessionService` (SQLite) | Progressive complexity |
| Memory | `InMemoryMemoryService` | Cross-session vocabulary tracking |
| Language | Python 3.11+ | ADK requirement |
| Package | `google-adk` (single pip install) | Includes FastAPI, uvicorn, google-genai |

---

## Project Structure (Final State)

```
norsk_praksis/
├── norsk_agent/
│   ├── __init__.py
│   ├── agent.py
│   ├── scenarios.py
│   ├── tools.py
│   └── prompts.py
├── tests/
│   └── test_agent.py
├── .env
├── requirements.txt
├── SPEC_DEV.md
└── ROAD_MAP_PHASE<n>.md
```

This structure grows incrementally. Phase 1 starts with three files.

---

## Reference Codebase

The attached codebase (`main.py`, `gemini_live.py`, `config_utils.py`, `simple_tracker.py`, `recaptcha_validator.py`, `fingerprint.py`) is a standalone FastAPI application that talks directly to the Gemini Live API via `google.genai`. It manually manages WebSocket lifecycle, audio chunking, tool dispatch, and session timeouts.

This codebase is **not used directly**. It serves as a reference for understanding what the ADK abstracts away. Specific correspondences are noted in each phase so the learner can compare hand-rolled vs. framework approaches.

---

## Learning Objectives by Phase

| Phase | Builds | Teaches |
|-------|--------|---------|
| 1 | Minimal talking agent | Agent anatomy, operational loop, `adk web` |
| 2 | Scenario selection via tools | Tool design, function-as-tool pattern, taxonomy of capability |
| 3 | Session persistence and state | Session management, state scopes, context engineering |
| 4 | Cross-session memory | Memory architecture (declarative vs. procedural), memory ETL |
| 5 | MCP integration | MCP architecture, transport primitives, interoperability |

---

## Phase 1 — The Talking Agent

### What You Build

A single ADK agent that speaks Norwegian. When the user opens `adk web` and talks, the agent responds as a friendly Norwegian conversation partner. There is one hardcoded persona: a café server in Oslo.

### Project Structure at End of Phase

```
norsk_praksis/
├── norsk_agent/
│   ├── __init__.py
│   └── agent.py
├── .env
└── requirements.txt
```

### Specification

**File: `requirements.txt`**
- Single dependency: `google-adk`

**File: `.env`**
- `GOOGLE_GENAI_USE_VERTEXAI=TRUE` (or `FALSE` for Google AI Studio key)
- `GOOGLE_CLOUD_PROJECT=<project-id>` (if Vertex AI)
- `GOOGLE_CLOUD_LOCATION=us-central1` (if Vertex AI)
- `GOOGLE_API_KEY=<key>` (if Google AI Studio)

**File: `norsk_agent/__init__.py`**
- Exports the `root_agent` symbol from `agent.py`

**File: `norsk_agent/agent.py`**
- Defines a single `LlmAgent` named `root_agent`
- Model: a Gemini model that supports the Live API (e.g., `gemini-2.0-flash-live`)
- `instruction`: A Norwegian-language system prompt that establishes the café server persona. The instruction must:
  - Declare the persona in Norwegian (servitør på en kafé i Oslo)
  - Instruct the agent to speak only Norwegian
  - Instruct the agent to greet the user first and ask what they would like to order
  - Instruct the agent to gently correct pronunciation or grammar mistakes
  - Instruct the agent to keep responses short (1-2 sentences) so the user practices more

### How to Run

```
adk web
```

Then select `norsk_agent` from the agent dropdown in the browser UI.

### Acceptance Criteria

1. `adk web` launches without errors
2. `norsk_agent` appears in the agent dropdown
3. Clicking the microphone and speaking English triggers a Norwegian response
4. The agent responds with voice audio (not just text)
5. The agent stays in character as the café server

### What This Teaches

**The Core Anatomy of an Agent:**
- An agent is an `LlmAgent` with a `name`, `model`, and `instruction`
- The `instruction` is the system prompt — the single most important design decision
- The agent has no tools yet; it is a pure LLM wrapper

**The Operational Loop:**
- User speaks → audio captured by `adk web` UI → sent to ADK via `LiveRequestQueue` → forwarded to Gemini Live API → model generates Norwegian audio → streamed back to browser → played through speakers
- This is the Perceive → Reason → Act loop in its simplest form

**Reference Codebase Comparison:**
- The entire `gemini_live.py` (280 lines) is replaced by ADK's toolkit
- The WebSocket management in `main.py` (lines 211-318) is replaced by `adk web`
- The `config_utils.py` pattern is replaced by `.env` + ADK's automatic credential resolution

---

## Phase 2 — Scenarios and Tools

### What You Build

The agent can now switch between multiple roleplay scenarios. The user says "I want to practice ordering food" or "I want to check into a hotel," and the agent adopts the matching persona. Scenario switching is implemented as an ADK tool.

### Project Structure at End of Phase

```
norsk_praksis/
├── norsk_agent/
│   ├── __init__.py
│   ├── agent.py
│   ├── scenarios.py
│   └── tools.py
├── .env
└── requirements.txt
```

### Specification

**File: `norsk_agent/scenarios.py`**
- A Python dictionary mapping scenario IDs to scenario definitions
- Each scenario definition contains:
  - `id`: string identifier (e.g., `"cafe"`, `"hotel"`, `"train"`, `"grocery"`, `"doctor"`)
  - `title_no`: Norwegian title (e.g., `"På kafeen"`)
  - `title_en`: English title (e.g., `"At the café"`)
  - `persona`: Norwegian-language persona description for the system prompt
  - `opening_line`: The Norwegian sentence the agent says to start the scenario
  - `vocabulary`: List of 10-15 key Norwegian words/phrases relevant to this scenario, each with Norwegian term and English translation
- Minimum five scenarios:
  1. Café (ordering coffee and pastries)
  2. Hotel (checking in, asking about facilities)
  3. Train station (buying tickets, asking about departures)
  4. Grocery store (asking for items, understanding prices)
  5. Doctor's office (describing symptoms, understanding instructions)

**File: `norsk_agent/tools.py`**
- Three Python functions, each with full docstrings and type hints:

  1. `list_scenarios() -> dict`: Returns all available scenarios with their IDs and titles (both Norwegian and English). No parameters.

  2. `select_scenario(scenario_id: str) -> dict`: Accepts a scenario ID string. Returns the full scenario definition including persona, opening line, and vocabulary list. If the ID is invalid, returns an error message.

  3. `get_vocabulary(scenario_id: str) -> dict`: Accepts a scenario ID string. Returns just the vocabulary list for that scenario. The agent uses this when the user asks "what words should I know?" or similar.

**File: `norsk_agent/agent.py`** (updated)
- The `root_agent` now includes `tools=[list_scenarios, select_scenario, get_vocabulary]`
- The `instruction` is updated to:
  - Start in a "menu" mode: greet the user in Norwegian and offer to list available scenarios
  - When a scenario is selected via the tool, adopt that scenario's persona
  - Use the vocabulary list to guide conversation toward practicing those specific words
  - If the user says "bytt scenario" (switch scenario) or "new scenario," return to menu mode
  - Continue to correct mistakes gently and keep responses short

### Acceptance Criteria

1. User can say "what scenarios do you have?" and the agent calls `list_scenarios` and reads them out
2. User can say "I want to practice at the hotel" and the agent calls `select_scenario("hotel")` and switches persona
3. The agent's persona, opening line, and vocabulary change when switching scenarios
4. User can ask "what words should I know?" and the agent calls `get_vocabulary` and reads key terms
5. User can say "bytt scenario" to return to the menu

### What This Teaches

**Taxonomy of Capability — Tools:**
- Tools extend what an agent can do beyond pure conversation
- ADK tools are plain Python functions with docstrings — the framework introspects the signature and docstring to create the function schema automatically
- The agent decides when to call a tool based on user intent (no explicit routing code)

**Tool Design Best Practices:**
- Each tool does one thing (list, select, get vocabulary)
- Return types are always `dict`
- Docstrings are the "API documentation" the model reads to decide when and how to call the tool
- Type hints on parameters generate the JSON schema the model uses for arguments

**Reference Codebase Comparison:**
- The manual `tool_mapping` dict and `FunctionDeclaration` construction in `gemini_live.py` (lines 98-111) is replaced by passing Python functions to `tools=[...]`
- The manual `FunctionResponse` construction (lines 219-257) is replaced by ADK's automatic tool dispatch and response handling

---

## Phase 3 — Session Persistence and State

### What You Build

The agent now remembers what happened within a single conversation session. It tracks which scenario the user selected, how many exchanges have occurred, and which vocabulary words the user has used correctly. When the session resumes (same session ID), the agent picks up where it left off.

### Project Structure at End of Phase

```
norsk_praksis/
├── norsk_agent/
│   ├── __init__.py
│   ├── agent.py
│   ├── scenarios.py
│   ├── tools.py
│   └── prompts.py
├── tests/
│   └── test_agent.py
├── .env
└── requirements.txt
```

### Specification

**File: `norsk_agent/prompts.py`**
- A function `build_instruction(scenario: dict, session_state: dict) -> str` that constructs the full Norwegian system prompt dynamically
- The prompt incorporates:
  - The current scenario's persona
  - The count of exchanges so far (from state)
  - Which vocabulary words the user has successfully used (from state)
  - Which vocabulary words remain unpracticed
  - Adaptive difficulty: if the user has used most words correctly, the agent uses more complex sentences

**File: `norsk_agent/tools.py`** (updated)
- `select_scenario` now writes to session state:
  - `state["current_scenario_id"]` = the selected scenario ID
  - `state["exchange_count"]` = 0
  - `state["words_practiced"]` = empty list
  - `state["words_correct"]` = empty list
- New tool: `mark_word_practiced(word: str, correct: bool) -> dict`
  - The agent calls this after each user utterance to record which vocabulary words appeared and whether they were used correctly
  - Updates `state["words_practiced"]` and `state["words_correct"]`
  - Returns a summary of progress (e.g., "5 of 12 words practiced, 4 correct")
- New tool: `get_progress() -> dict`
  - Returns the current session progress: scenario, exchange count, words practiced, accuracy percentage

**File: `norsk_agent/agent.py`** (updated)
- Uses `InMemorySessionService` initially
- Includes `before_agent_callback` that:
  - Reads `state["current_scenario_id"]` to determine the active scenario
  - Calls `build_instruction()` with the current scenario and state to produce a dynamic system prompt
- Includes `after_agent_callback` that:
  - Increments `state["exchange_count"]` after each agent turn
- `output_key` is set to `"last_response"` so the agent's text output is saved to state

**Session service upgrade path** (documented in the ROAD_MAP, not in code yet):
- Replace `InMemorySessionService()` with `DatabaseSessionService(db_url="sqlite+aiosqlite:///norsk_sessions.db")`
- This single-line change makes all state persist across server restarts

**File: `tests/test_agent.py`**
- A test that creates a session, selects a scenario, verifies state was written, simulates a few exchanges, and verifies progress tracking works
- Uses `InMemoryRunner` for non-streaming testing

### Acceptance Criteria

1. After selecting a scenario, `state["current_scenario_id"]` is set
2. The agent tracks vocabulary usage across the conversation
3. `get_progress` returns accurate counts
4. Replacing `InMemorySessionService` with `DatabaseSessionService` (SQLite) persists state across restarts
5. The dynamic prompt adapts based on which words have been practiced

### What This Teaches

**Session Management — Workbench vs. Filing Cabinet:**
- `InMemorySessionService` is the workbench: fast, ephemeral, good for active work
- `DatabaseSessionService` is the filing cabinet: persistent, slower, good for long-term storage
- Switching between them is a one-line change — the agent code doesn't know or care

**State Scopes:**
- Session-scoped state (no prefix): lives for one conversation (exchange count, current scenario)
- User-scoped state (`user:` prefix): lives across sessions for one user (introduced in Phase 4)
- Application-scoped state (`app:` prefix): lives across all users (not needed for this app)

**Context Engineering:**
- The `before_agent_callback` demonstrates dynamic prompt construction — the system prompt is not static, it adapts to the current session state
- This is the foundation of context engineering: what goes into the context window determines what comes out

**Callbacks and Lifecycle:**
- `before_agent_callback` fires before every agent turn — opportunity to reshape the prompt
- `after_agent_callback` fires after every agent turn — opportunity to update bookkeeping state

**Reference Codebase Comparison:**
- The existing codebase has no session persistence at all — the `valid_tokens` dict in `main.py` is a simple expiring cache, not a session store
- The session timeout in `main.py` (line 306, `asyncio.wait_for`) is a blunt instrument; ADK manages session lifecycle through services

---

## Phase 4 — Cross-Session Memory

### What You Build

The agent now remembers the user across sessions. When a user returns tomorrow, the agent knows which scenarios they've completed, which words they struggle with, and their overall proficiency level. This is built on ADK's memory service and user-scoped state.

### Specification

**State additions (user-scoped, persist across sessions):**
- `user:completed_scenarios` — list of scenario IDs the user has completed (defined as: all vocabulary words practiced with >70% accuracy)
- `user:weak_words` — list of `{word, scenario_id, attempts, correct}` entries for words the user struggles with
- `user:total_sessions` — count of sessions completed
- `user:proficiency_level` — one of `"beginner"`, `"intermediate"`, `"advanced"`, calculated from completed scenarios and accuracy

**New tool: `end_scenario() -> dict`**
- Called when the user finishes a scenario (either explicitly or when all vocabulary is practiced)
- Calculates accuracy for the scenario
- Updates `user:completed_scenarios` if accuracy >70%
- Extracts weak words (accuracy <50%) and appends to `user:weak_words`
- Updates `user:proficiency_level` based on new totals
- Returns a Norwegian-language summary of the session results

**New tool: `get_user_profile() -> dict`**
- Returns the user's cross-session profile: completed scenarios, weak words, proficiency level, total sessions
- The agent calls this at the start of a new session to personalize the greeting

**Updated prompt engineering:**
- The `build_instruction` function now incorporates the user profile
- If the user has weak words from previous sessions, the agent weaves those words into the current scenario's conversation
- The greeting changes based on proficiency: beginners get more English mixed in, advanced users get pure Norwegian

**Memory service integration:**
- `InMemoryMemoryService` is configured on the runner
- At the end of each session, a summary is stored as a memory entry
- At the start of each session, the agent searches memory for relevant past interactions using `search_memory`

### Acceptance Criteria

1. A returning user (same `user_id`, new `session_id`) sees their previous progress
2. Weak words from previous sessions appear in new scenarios
3. Proficiency level updates correctly as the user completes more scenarios
4. The greeting is personalized based on history
5. Memory search retrieves relevant past interactions

### What This Teaches

**Memory Architecture — Declarative vs. Procedural:**
- Declarative memory: "This user has completed the café and hotel scenarios" (facts about the user stored in `user:` state)
- Procedural memory: "When this user struggles with pronunciation, slow down and repeat" (behavioral patterns encoded in the prompt based on proficiency level)
- The distinction matters: declarative memory is stored explicitly, procedural memory emerges from how you use declarative facts in prompt construction

**The Memory ETL Pipeline:**
- **Extract**: At end of session, extract key facts (words practiced, accuracy, scenario completed)
- **Transform**: Calculate derived metrics (proficiency level, weak word patterns)
- **Load**: Write to user-scoped state and memory service
- This pipeline runs inside `end_scenario()` and `after_agent_callback`

**Compaction Strategies:**
- Session history grows with each exchange. The `build_instruction` function must summarize, not replay
- Instead of stuffing 50 past exchanges into the prompt, the function extracts: "User has practiced 8 of 12 words, struggles with 'regning' and 'kvittering'"
- This is compaction: reducing raw history to a compact, useful summary

**Reference Codebase Comparison:**
- The existing codebase has zero memory capability — every WebSocket connection starts fresh
- The BigQuery tracker in `simple_tracker.py` logs events but never reads them back — it is write-only analytics, not memory

---

## Phase 5 — MCP Integration

### What You Build

The agent connects to an external vocabulary resource via the Model Context Protocol (MCP). Instead of hardcoded vocabulary lists in `scenarios.py`, the agent queries an MCP server that serves Norwegian vocabulary data. This introduces interoperability with external systems without changing the agent's core logic.

### Specification

**MCP Server (standalone process):**
- A minimal MCP server that exposes Norwegian vocabulary data
- Implements one MCP tool: `lookup_word(norwegian_word: str) -> dict`
  - Returns: definition, example sentence, pronunciation guide, difficulty level
- Implements one MCP resource: `vocabulary://{scenario_id}`
  - Returns the full vocabulary list for a scenario
- Transport: stdio (simplest for local development)
- The server reads vocabulary data from a single JSON file

**ADK agent update:**
- The agent's tool list now includes the MCP-connected tools alongside native Python tools
- ADK provides MCP client integration — the agent treats MCP tools identically to local Python tools
- The `instruction` is updated to prefer the MCP vocabulary lookup when the user asks about a specific word's meaning or pronunciation

**Vocabulary JSON file:**
- A single `vocabulary.json` that contains all scenario vocabularies plus additional words not in any scenario
- This file is the "database" the MCP server reads from
- Structured as: `{ "words": [ { "norwegian": "...", "english": "...", "example_no": "...", "example_en": "...", "pronunciation": "...", "difficulty": "A1|A2|B1|B2" } ] }`

### Acceptance Criteria

1. The MCP server starts and responds to tool calls over stdio
2. The ADK agent can call `lookup_word` through MCP and get vocabulary data
3. When the user asks "hva betyr regning?" (what does regning mean?), the agent uses the MCP tool to provide definition, example, and pronunciation
4. Removing the MCP server gracefully degrades — the agent falls back to the hardcoded vocabulary in `scenarios.py`
5. The agent does not distinguish between MCP tools and local tools in its behavior

### What This Teaches

**The MCP Architecture:**
- MCP is a protocol for connecting AI agents to external data and tools
- It defines a client-server model: the ADK agent is the MCP client, the vocabulary server is the MCP server
- The protocol standardizes how tools and resources are discovered and invoked

**Technical Primitives and Transport:**
- MCP uses JSON-RPC 2.0 as its message format
- Transport options: stdio (local, process-based) and SSE (remote, HTTP-based)
- This phase uses stdio: the ADK agent spawns the MCP server as a subprocess and communicates over stdin/stdout
- The learner sees that the same tool interface works regardless of whether the tool is a local Python function or a remote MCP server

**Interoperability:**
- The agent's `tools` list mixes local Python functions and MCP-connected tools
- The model does not know or care about the difference — it sees a unified tool schema
- This is the key insight: MCP provides interoperability without changing the agent's core logic

**Reference Codebase Comparison:**
- The existing codebase's tool system (`tool_mapping` in `gemini_live.py`) only supports local Python functions
- MCP would require significant custom code in the existing architecture
- ADK provides MCP integration out of the box

---

## Phase Dependency Map

```
Phase 1 ──→ Phase 2 ──→ Phase 3 ──→ Phase 4
   (agent)    (tools)    (sessions)   (memory)
                              │
                              └──→ Phase 5
                                    (MCP)
```

Phase 5 depends on Phase 3 (needs session state), not Phase 4 (does not need cross-session memory). Phases 4 and 5 can be done in either order.

---

## Non-Goals (Explicit Exclusions)

These items are deliberately excluded from all phases:

1. **Custom frontend** — `adk web` is sufficient; no React/Vue/SPA
2. **Production deployment** — no Docker, Cloud Run, or Kubernetes
3. **Authentication** — no reCAPTCHA, no user login (the existing codebase's `recaptcha_validator.py` and `fingerprint.py` are not used)
4. **Rate limiting** — no Redis, no SlowAPI (the existing codebase's rate limiting in `main.py` is not used)
5. **Analytics** — no BigQuery tracking (the existing codebase's `simple_tracker.py` is not used)
6. **Multi-agent orchestration** — single agent throughout
7. **Image/video input** — voice-only
8. **Translation service** — the agent handles translation inline
9. **Grading/scoring UI** — progress is tracked in state but not displayed in a dashboard
10. **Multiple languages** — Norwegian only

---

## Glossary

| Term | Definition |
|------|-----------|
| **ADK** | Google Agent Development Kit — Python framework for building AI agents |
| **LlmAgent** | ADK's primary agent class, wrapping a language model with instructions and tools |
| **LiveRequestQueue** | ADK's async queue for bidirectional audio/video streaming with Gemini Live API |
| **`adk web`** | ADK's built-in development web UI with microphone and audio playback |
| **Session** | A single conversation between user and agent, identified by session ID |
| **State** | Key-value data attached to a session, readable/writable by tools and callbacks |
| **Memory** | Cross-session knowledge store, searchable by the agent |
| **MCP** | Model Context Protocol — standard for connecting agents to external tools and data |
| **ToolContext** | Object passed to tool functions, providing access to state, artifacts, and memory |
| **CallbackContext** | Object passed to lifecycle callbacks, providing access to state and invocation info |
| **Operational Loop** | The Perceive → Reason → Act cycle that defines agent behavior |
| **Compaction** | Reducing raw conversation history to a concise summary for the context window |
