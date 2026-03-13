# Agent Development Deep Dive: Annotated Code Walkthrough

This document provides line-by-line analysis of the Norwegian language learning agent, showing how architectural concepts translate to actual implementation.

---

## Module 1: Core Agent Setup (agent.py)

### The System Instruction (Lines 14-33)

```python
SYSTEM_INSTRUCTION = """
Du er en vennlig og tålmodig norsk språkpartner.
Bruk alltid norsk.

Du befinner deg først i en "meny"-modus.
Hovedoppgaven din her er å hjelpe brukeren med å velge et praksis-scenario.
Bruk `list_scenarios`-verktøyet for å fortelle brukeren hvilke scenarioer de kan øve på.

Når brukeren har valgt et scenario, eller du forstår hvilket de vil bruke, bruk `select_scenario`-verktøyet for å bytte rolle.
Etter å ha byttet rolle, ta umiddelbart på deg den nye personligheten (persona) og start samtalen med 'opening_line' fra scenarioet.
Hold deg i denne rollen og svar utelukkende på norsk.
Hold svarene dine svært korte (1-2 små setninger).
Dersom brukeren gjør grammatikkfeil eller uttaler noe feil, gi en rask og vennlig korreksjon på norsk.

Hvis brukeren står fast eller ber om hjelp til noen ord ("hva sier jeg?", "trenger vokabular"), bruk `get_vocabulary`-verktøyet for det valgte scenarioet og foreslå 2-3 relevante norske uttrykk med engelsk oversettelse.

VIKTIG: Hvis brukeren spør om betydningen eller definisjonen av et ord ("hva betyr", "definer", "hva er"), MÅ du bruke `lookup_word` verktøyet fra det eksterne registeret. Hvis MCP-serveren ikke svarer eller feiler, bruk den lokale kunnskapen din som fallback.

Dersom brukeren sier "bytt scenario" eller "new scenario", gå ut av rollen din og tilbake til "meny"-modus for å velge et nytt scenario.
"""
```

**Architectural Analysis:**

This static instruction is the **default instruction** when no scenario is active. It:
1. **Establishes role**: Agent is a "Norwegian language partner"
2. **Defines mode states**: Menu mode vs. scenario mode
3. **Specifies tool usage**: When to use which tool (list_scenarios, select_scenario, get_vocabulary)
4. **Delegates authority**: Tells agent to consult MCP service for word definitions
5. **Handles fallback**: "If MCP fails, use fallback knowledge" ← graceful degradation

**Key insight**: The instruction is a form of **context engineering**. Rather than hardcoding behavior in code, the behavior is specified in natural language and interpreted by the LLM.

---

### The Before-Agent Callback (Lines 35-56)

```python
async def on_before_agent(callback_context: CallbackContext):
    state = callback_context.state                          # [1] Access session state
    scenario_id = state.get("active_scenario_id")          # [2] Check active scenario

    memory_info = ""
    # Search memory if no active scenario yet to personalize greeting
    if not scenario_id:                                     # [3] Only search when needed
        try:
            memories = await callback_context.search_memory("scenario fullført")  # [4] Query long-term memory
            if memories and memories.memories:
                memory_info = "\n\nKontekst fra tidligere samtaler:\n"
                for mem in memories.memories[-3:]:          # [5] Take last 3 memories
                    memory_info += f"- {mem.content.parts[0].text if mem.content and mem.content.parts else ''}\n"
        except Exception:
            pass                                            # [6] Graceful degradation

    if scenario_id and scenario_id in SCENARIOS:           # [7] Scenario is active
        scenario = SCENARIOS[scenario_id]
        new_instruction = build_instruction(scenario, state)  # [8] Dynamic instruction
        root_agent.instruction = new_instruction
    else:
        root_agent.instruction = SYSTEM_INSTRUCTION + memory_info  # [9] Default + context
```

**Step-by-step breakdown:**

| Line | Action | Purpose |
|------|--------|---------|
| 1 | `state = callback_context.state` | Get current session state from the session service |
| 2 | `scenario_id = state.get("active_scenario_id")` | Check if user is in a scenario or menu mode |
| 3-4 | `if not scenario_id: ... search_memory(...)` | Only look up memory if not in active scenario (optimization) |
| 5 | `memories.memories[-3:]` | Take most recent 3 memories (recency weighting) |
| 6 | `except Exception: pass` | Don't fail if memory service unavailable |
| 7-9 | Conditional instruction assignment | Dynamically choose instruction based on state |

**Architectural principle: Layered Context**

```
Base Instruction (static)
    ↓
+ Memory Info (dynamic, from long-term storage)
    ↓
OR
    ↓
Scenario-Specific Instruction (dynamic, from current state + history)
```

---

### The After-Agent Callback (Lines 58-65)

```python
async def on_after_agent(callback_context: CallbackContext):
    count = callback_context.state.get("exchange_count", 0)       # [1] Get current count
    callback_context.state["exchange_count"] = count + 1           # [2] Increment

    try:
        await callback_context.add_session_to_memory()             # [3] Persist session
    except Exception:
        pass                                                       # [4] Graceful degradation
```

**What this does:**
1. **Conversation Depth Tracking**: Counts how many back-and-forths have happened
2. **Memory Persistence**: After each turn, the entire session is serialized to long-term memory
3. **Non-Blocking**: If memory service fails, conversation continues (no user-facing interruption)

**Why after-agent and not before?**
- **Causal correctness**: The agent has already responded to the user
- **Complete state**: Everything that happened in this turn is now finalized
- **Non-blocking**: Persistence doesn't delay response to user

---

### Service Initialization (Lines 67-80)

```python
session_service = SqliteSessionService("sessions.db")             # [1] Ephemeral sessions
memory_service = InMemoryMemoryService()                          # [2] Long-term memory

MODEL_ID = "gemini-live-2.5-flash-native-audio"                  # [3] Model selection

from mcp import StdioServerParameters

mcp_toolset = McpToolset(                                         # [4] MCP integration
    connection_params=StdioServerParameters(
        command="uv",                                              # [5] Use uv package manager
        args=["run", os.path.join(os.path.dirname(os.path.dirname(__file__)), "mcp_vocab_server.py")],
    ),
    use_mcp_resources=True                                         # [6] Enable resource discovery
)
```

**Architectural decisions:**

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Session Service | SQLite | Persistent across restarts, local storage |
| Memory Service | In-Memory | Simpler setup for demo; in production would be vector DB |
| Model | Gemini 2.5 Flash | Multimodal, low-latency, live audio support |
| MCP Transport | Stdio | Cross-platform, no network required, secure |
| MCP Resources | Enabled | Allows service to expose data resources (e.g., vocabulary lists) |

---

### Root Agent Creation (Lines 82-89)

```python
root_agent = LlmAgent(
    name="norsk_agent",                                            # [1] Identifiable name
    model=MODEL_ID,                                                # [2] Which LLM to use
    instruction=SYSTEM_INSTRUCTION,                                # [3] Initial instruction
    tools=[list_scenarios, select_scenario, get_vocabulary,        # [4] Local tools
           mark_word_practiced, get_progress, end_scenario,
           get_user_profile, mcp_toolset],                         # [5] MCP tools
    before_agent_callback=on_before_agent,                         # [6] Context preparation
    after_agent_callback=on_after_agent,                           # [7] State persistence
)
```

**Agent Construction:**

```
Agent = {
  name: Identifiable in logs
  model: LLM backend
  instruction: Initial behavior specification
  tools: {
    Local tools: Direct access to state/scenarios
    MCP tools: Remote access to external services
  }
  Callbacks: {
    before: Prepare context (memory, instruction)
    after: Persist state
  }
}
```

---

## Module 2: Tools (tools.py)

### Tool 1: List Scenarios (Lines 4-21)

```python
def list_scenarios() -> list[dict[str, str]]:
    """
    Returns the list of available practice scenarios.
    """
    return [
        {
            "id": s["id"],
            "title_no": s["title_no"],
            "title_en": s["title_en"]
        }
        for s in SCENARIOS.values()
    ]
```

**Pattern: Observation tool (no side effects)**

```python
# Input: none (agent discovers available scenarios)
# Output: structured list (allows agent to reason about options)
# Side effects: none (read-only)
```

**Why this pattern?**
- Agent can ask "what scenarios are available?" without committing to one
- Output is structured (dictionary list) so agent can parse reliably
- Tool is deterministic (same input = same output always)

---

### Tool 2: Select Scenario (Lines 23-50)

```python
def select_scenario(tool_context: Context, scenario_id: str) -> dict:
    """
    Selects a scenario by ID and returns its context, triggering a persona switch.
    """
    if scenario_id not in SCENARIOS:                              # [1] Validation
        return {"error": f"Beklager, jeg kjenner ikke til scenarioet '{scenario_id}'."}

    # Initialize state                                             # [2] Reset scenario state
    tool_context.state["active_scenario_id"] = scenario_id
    tool_context.state["words_practiced"] = []
    tool_context.state["exchange_count"] = 0

    scenario = SCENARIOS[scenario_id]                             # [3] Retrieve scenario data
    return {                                                       # [4] Return complete context
        "id": scenario["id"],
        "title_no": scenario["title_no"],
        "title_en": scenario["title_en"],
        "persona": scenario["persona"],
        "opening_line": scenario["opening_line"]
    }
```

**Pattern: Stateful action tool**

```
Input:  scenario_id (e.g., "cafe")
        ↓
[1] Validate
        ↓
[2] Modify state
     - active_scenario_id = "cafe"
     - words_practiced = [] (reset)
     - exchange_count = 0 (reset)
        ↓
[3] Prepare response
        ↓
Output: Complete scenario context (persona, opening_line)

Side effect: Next call to on_before_agent will see updated state
             and switch the agent's instruction dynamically
```

**Why return the full context?**
- Agent sees the persona and opening_line in tool output
- Agent can decide whether to use them (though instruction says to)
- Human-readable feedback confirms what scenario was selected

---

### Tool 3: Get Vocabulary (Lines 52-64)

```python
def get_vocabulary(scenario_id: str) -> dict:
    """
    Retrieves the vocabulary list for a given scenario.
    """
    if scenario_id not in SCENARIOS:
        return {"error": f"Beklager, jeg kan ikke finne vokabular for '{scenario_id}'."}
    return {"vocabulary": SCENARIOS[scenario_id]["vocabulary"]}
```

**Pattern: Lookup tool (read-only, with error handling)**

```python
Input:  scenario_id
Output: {"vocabulary": [{"no": "en kaffe", "en": "a coffee"}, ...]}
        OR
        {"error": "..."}
```

**When is this called?**
- User: "Jeg trenger hjelp med ord" (I need help with words)
- Agent reasons: "User needs vocabulary → call get_vocabulary"
- Agent presents: "Her er noen nyttige ord: en kaffe, å betale, ..."

---

### Tool 4: Mark Word Practiced (Lines 66-85)

```python
def mark_word_practiced(tool_context: Context, word: str, correct: bool) -> str:
    """
    Marks a vocabulary word as practiced by the user.
    """
    practiced = tool_context.state.get("words_practiced", [])     # [1] Get current list
    if correct and word not in practiced:                         # [2] Check if new and correct
        practiced.append(word)
        tool_context.state["words_practiced"] = practiced         # [3] Update state
        return f"Flott! '{word}' er markert som lært."
    elif not correct:
        return f"Notert at '{word}' trenger mer øving."
    return f"'{word}' er allerede lært."
```

**Pattern: State-mutating tool with context-aware responses**

```
Input:  word="kort eller kontant?", correct=True

State before: words_practiced = ["en kaffe"]

[1] Check: Is word new and correct?
[2] Update: words_practiced = ["en kaffe", "kort eller kontant?"]
[3] Return: Positive feedback in Norwegian

Output:  "Flott! 'kort eller kontant?' er markert som lært."

State after: words_practiced = ["en kaffe", "kort eller kontant?"]
```

**Why this matters:**
- Tool is **idempotent** for correct words (calling twice = same result)
- Tool provides **feedback** (not silent state updates)
- Tool tracks **learner progress** in real-time

---

### Tool 5: Get Progress (Lines 87-112)

```python
def get_progress(tool_context: Context) -> dict:
    """
    Returns the user's progress in the current scenario.
    """
    active_scenario_id = tool_context.state.get("active_scenario_id")  # [1] Check state
    if not active_scenario_id or active_scenario_id not in SCENARIOS:
        return {"error": "Ingen aktivt scenario for å vise fremgang."}

    scenario = SCENARIOS[active_scenario_id]
    total_words = len(scenario.get("vocabulary", []))              # [2] Calculate total
    practiced = tool_context.state.get("words_practiced", [])
    practiced_count = len(practiced)                               # [3] Calculate practiced

    return {                                                       # [4] Return metrics
        "scenario_id": active_scenario_id,
        "words_practiced": practiced,
        "practiced_count": practiced_count,
        "total_words": total_words,
        "completion_percentage": (practiced_count / total_words) * 100 if total_words > 0 else 0
    }
```

**Pattern: Metrics tool (read-only observation)**

```
State: {
  active_scenario_id: "cafe",
  words_practiced: ["en kaffe", "å betale"]
}

Scenarios: {
  "cafe": {
    vocabulary: [12 words total]
  }
}

Calculation:
  practiced_count = 2
  total_words = 12
  completion_percentage = 16.67%

Output: {
  scenario_id: "cafe",
  words_practiced: [...],
  practiced_count: 2,
  total_words: 12,
  completion_percentage: 16.67
}
```

**Why return both count AND percentage?**
- **Count**: Agent can reason about absolute progress ("3 more words to learn")
- **Percentage**: Agent can assess relative progress ("User is 75% done")
- Both allow different types of feedback

---

### Tool 6: End Scenario (Lines 114-147)

```python
def end_scenario(tool_context: Context) -> str:
    """
    Ends the current practice scenario, calculating accuracy and saving progress.
    """
    active_scenario_id = tool_context.state.get("active_scenario_id")  # [1] Verify state
    if not active_scenario_id or active_scenario_id not in SCENARIOS:
        return "Bruk 'select_scenario' for å velge et scenario først."

    scenario = SCENARIOS[active_scenario_id]
    vocab = scenario.get("vocabulary", [])
    words_practiced = tool_context.state.get("words_practiced", [])     # [2] Get session data

    # Calculate weak words                                         # [3] Analysis
    target_words = {item["norwegian"] for item in vocab}
    practiced_set = set(words_practiced)
    weak_words = target_words - practiced_set

    # Update cross-session profile                                # [4] Update profile
    completed = tool_context.state.get("user:completed_scenarios", 0)
    tool_context.state["user:completed_scenarios"] = completed + 1

    all_weak_words = set(tool_context.state.get("user:weak_words", []))
    all_weak_words.update(weak_words)
    tool_context.state["user:weak_words"] = list(all_weak_words)

    # Reset scenario state                                        # [5] Clean up
    tool_context.state["active_scenario_id"] = None
    tool_context.state["words_practiced"] = []

    weak_str = ', '.join(weak_words) if weak_words else 'Ingen'
    return f"Scenario fullført! Du klarte {len(practiced_set)} av {len(target_words)} ord. ..."
```

**Pattern: Orchestration tool (complex state mutations)**

```
This tool does multiple things:

[1] Validates preconditions
    if no active scenario: error out

[2] Gathers data
    Get session vocabulary and practiced words

[3] Performs analysis
    weak_words = target_words - practiced_words

    Example:
    target:    {kaffe, betale, kort_eller_kontant, kvittering}
    practiced: {kaffe, betale}
    weak:      {kort_eller_kontant, kvittering}

[4] Updates persistent profile
    - Increment completed_scenarios counter
    - Add newly identified weak words to user:weak_words

[5] Resets session state
    - Clear active_scenario_id (back to menu mode)
    - Clear words_practiced (next scenario starts fresh)

[6] Returns summary
    "Scenario fullført! Du klarte 2 av 4 ord.
     Ord for ekstra øving: kort eller kontant?, kvittering."
```

**Architectural insight:**
This tool demonstrates how **session-level state** (active_scenario_id) transitions to **user-level profile** (user:completed_scenarios, user:weak_words).

```
Session-level (ephemeral):
  - active_scenario_id
  - words_practiced
  - exchange_count

User-level (persistent):
  - user:completed_scenarios (across all sessions)
  - user:weak_words (aggregate from all scenarios)
```

---

### Tool 7: Get User Profile (Lines 149-162)

```python
def get_user_profile(tool_context: Context) -> dict:
    """
    Retrieves the user's cross-session practice profile and statistics.
    """
    return {
        "completed_scenarios": tool_context.state.get("user:completed_scenarios", 0),
        "weak_words": tool_context.state.get("user:weak_words", [])
    }
```

**Pattern: Profile query tool (cross-session view)**

```
Input:  none (profile is keyed by current user/session)

Output: {
  completed_scenarios: 5,
  weak_words: [
    "kort eller kontant?",
    "heisen",
    "frokost inkludert"
  ]
}
```

**Use case:**
- Agent: "Flott! Du har nå fullført 5 scenarioer! 🎉"
- Agent: "Jeg merker du sliter med disse ordene: kort eller kontant?, heisen. Vil du øve på dem igjen?"

---

## Module 3: Scenario Definitions (scenarios.py)

### Scenario Structure

```python
SCENARIOS = {
    "cafe": {
        "id": "cafe",
        "title_no": "På kafé",
        "title_en": "At the café",
        "persona": "Du er en vennlig servitør på en kafé i Oslo.",
        "opening_line": "Hei! Hva kan jeg friste med i dag?",
        "vocabulary": [
            {"no": "en kaffe", "en": "a coffee"},
            {"no": "kan jeg få", "en": "can I get"},
            # ... more vocabulary
        ]
    },
    # ... more scenarios
}
```

**Key fields:**

| Field | Purpose | Example |
|-------|---------|---------|
| `id` | Machine-readable identifier | "cafe" |
| `title_no` / `title_en` | Display names | "På kafé" / "At the café" |
| `persona` | Agent's role instruction | "Du er en vennlig servitør..." |
| `opening_line` | Initial greeting | "Hei! Hva kan jeg friste med i dag?" |
| `vocabulary` | Learning goals | List of no/en word pairs |

**Scenario as configuration:**
Rather than hardcoding behavior for each scenario, the scenario is a **data structure** that the agent interprets. This allows:
- Adding new scenarios without code changes
- Testing different personas quickly
- Analyzing which vocabulary is hardest (statistics on vocabulary usage)

---

## Module 4: Dynamic Instruction Building (prompts.py)

```python
def build_instruction(scenario: dict, state: dict) -> str:
    """
    Builds a dynamic system instruction based on the scenario and the user's progress.
    """
    persona = scenario.get("persona", "")
    vocabulary = scenario.get("vocabulary", [])

    words_practiced = state.get("words_practiced", [])
    exchange_count = state.get("exchange_count", 0)
    weak_words = state.get("user:weak_words", [])

    # Base setup
    instruction = f"{persona}\n\nDu må kun snakke NORSK til enhver tid.\n"
    instruction += "Svarene dine må være svært korte (1-2 små setninger).\n"
    instruction += "Dersom brukeren gjør feil, rett dem raskt og vennlig på norsk.\n\n"

    # Include weak words if any
    if weak_words:
        instruction += f"VIKTIG: I tidligere samtaler har brukeren hatt problemer med disse ordene: {', '.join(weak_words)}.\nPrøv å flette dem inn i samtalen hvis det passer.\n\n"

    # Inject vocabulary status
    if vocabulary:
        instruction += "Brukeren prøver å lære følgende vokabular:\n"
        for v in vocabulary:
            status = " [LÆRT]" if v["no"] in words_practiced else ""
            instruction += f"- {v['no']} ({v['en']}){status}\n"

        instruction += "\nPrøv å styre samtalen slik at brukeren får bruk for ordene som IKKE er lært ennå.\n"

        if exchange_count > 0:
            instruction += f"Dere har snakket sammen i {exchange_count} utvekslinger. Fortsett naturlig.\n"

    return instruction
```

**Instruction evolution:**

Example progression for "cafe" scenario:

**Turn 1 (Fresh start):**
```
Du er en vennlig servitør på en kafé i Oslo.
Du må kun snakke NORSK til enhver tid.
Svarene dine må være svært korte (1-2 små setninger).

Brukeren prøver å lære følgende vokabular:
- en kaffe (a coffee)
- kan jeg få (can I get)
- en bolle (a bun/pastry)
- å betale (to pay)
- kort eller kontant? (card or cash?)
... [all vocabulary]

Prøv å styre samtalen slik at brukeren får bruk for ordene som IKKE er lært ennå.
```

**Turn 3 (User has practiced 2 words):**
```
Du er en vennlig servitør på en kafé i Oslo.
Du må kun snakke NORSK til enhver tid.

VIKTIG: I tidligere samtaler har brukeren hatt problemer med disse ordene: kort eller kontant?, kvittering.
Prøv å flette dem inn i samtalen hvis det passer.

Brukeren prøver å lære følgende vokabular:
- en kaffe (a coffee) [LÆRT]
- kan jeg få (can I get) [LÆRT]
- en bolle (a bun/pastry)
- å betale (to pay)
- kort eller kontant? (card or cash?)
... [rest]

Prøv å styre samtalen slik at brukeren får bruk for ordene som IKKE er lært ennå.

Dere har snakket sammen i 2 utvekslinger. Fortsett naturlig.
```

**Key insight: The instruction is a form of in-context learning.**

Rather than training the model to learn Norwegian-teaching strategies, we encode that strategy in the instruction:
1. **Persona**: Sets role (servitør/waiter)
2. **Vocabulary tracking**: Marks which words are learned with `[LÆRT]`
3. **Prioritization**: "Focus on unlearned words"
4. **Weak words**: "These words are hard for this user"
5. **Continuity**: "You've been talking for N exchanges"

---

## Memory in Action: A Concrete Example

### Scenario: User's Learning Journey

**Day 1, Session 1:**

```
User: "Jeg vil øve på norsk"
Agent (on_before_agent):
  - Searches memory for "scenario fullført"
  - Memory is empty (first time)
  - Uses default SYSTEM_INSTRUCTION

User: "Kan jeg velge kafé?"
Agent: Calls select_scenario("cafe")
  - State: active_scenario_id = "cafe", words_practiced = []

Conversation:
  Agent: "Hei! Hva kan jeg friste med i dag?"
  User: "Jeg vil ha en kaffe"
  Agent: "Flott! En kaffe?" [marks "en kaffe" as learned]
  ...

After 5 exchanges, user says: "Jeg er ferdig"
Agent: Calls end_scenario()
  - Analyzes: User learned 6/12 words
  - Weak words identified: ["kort eller kontant?", "kvittering", ...]
  - Updates state: user:completed_scenarios = 1, user:weak_words = [...]

on_after_agent:
  - Serializes entire session to memory
  - Memory now contains: "User completed cafe scenario, struggled with payment terms"
```

**Day 2, Session 2:**

```
User: "Hei, jeg er tilbake!"
Agent (on_before_agent):
  - Searches memory for "scenario fullført"
  - Finds: "User completed cafe scenario" ← HIT!
  - memory_info = "Kontekst fra tidligere samtaler:\n- User completed cafe scenario"
  - Builds instruction: SYSTEM_INSTRUCTION + memory_info

Agent greeting: "Kjempe! Jeg ser du var her forrige gang og fullførte kafé-scenarioet. Vil du continue med det eller prøve noe nytt?"

User: "Jeg vil gjøre det igjen"
Agent: Calls select_scenario("cafe")
  - on_before_agent detects active_scenario_id = "cafe"
  - Calls build_instruction(scenario, state)
  - State includes: user:weak_words = ["kort eller kontant?", "kvittering"]
  - Instruction includes: "VIKTIG: Brukeren har problemer med: kort eller kontant?, kvittering"

Conversation:
  Agent: "Hei! Hva kan jeg friste med i dag?"
  User: "En kaffe, vær så snill"
  Agent: "En kaffe! [Naturally steers toward payment] Kort eller kontant?"
  User: "Kort, takk" ← EXCELLENT - practicing weak word!
  Agent: Marks "kort eller kontant?" as learned

on_after_agent:
  - Session persisted to memory with new learning
  - user:weak_words reduced (payment phrase now practiced)
```

**Cross-session continuity demonstrated:**

```
Session 1:
  New scenario → identify weak words → persist to memory

Session 2:
  Load memory → customize instruction → focus on weak words → improve
```

---

## State Schema Complete Reference

### Session-Level State

```python
{
    # Immediate context
    "active_scenario_id": "cafe",              # Current practice scenario ID
    "words_practiced": [                        # Words learned this session
        "en kaffe",
        "å betale"
    ],
    "exchange_count": 5,                        # Number of agent-user exchanges

    # Cross-session profile (stored in state, persisted to memory)
    "user:completed_scenarios": 3,              # Total scenarios completed
    "user:weak_words": [                        # Words struggling with
        "kort eller kontant?",
        "heisen"
    ]
}
```

### State Mutations by Tool

| Tool | Mutations | Scope |
|------|-----------|-------|
| `select_scenario` | active_scenario_id, words_practiced, exchange_count | Session reset |
| `mark_word_practiced` | words_practiced | Session-specific |
| `end_scenario` | active_scenario_id, user:completed_scenarios, user:weak_words | Cross-session |
| `get_vocabulary` | None (read-only) | - |
| `get_progress` | None (read-only) | - |
| `get_user_profile` | None (read-only) | - |
| `list_scenarios` | None (read-only) | - |

### Memory Persistence Points

Memory is added at two moments:

1. **In on_after_agent**: Entire session serialized
   ```python
   await callback_context.add_session_to_memory()
   ```

2. **Memory search in on_before_agent**: Queried for personalization
   ```python
   memories = await callback_context.search_memory("scenario fullført")
   ```

---

## Summary: Architectural Patterns in Action

| Pattern | Implementation | Benefit |
|---------|----------------|---------|
| **Dynamic Instructions** | `on_before_agent` rebuilds instruction based on state | Agent adapts to context without retraining |
| **Callback Hooks** | `on_before_agent` and `on_after_agent` | Clean separation of concerns |
| **Tool-Based Mutations** | All state changes go through tools | Auditability, consistency |
| **Layered State** | Session state + user profile | Short-term responsiveness + long-term learning |
| **Memory-Informed Behavior** | Memory queried before reasoning | Context awareness without explicit prompting |
| **MCP Integration** | External tools via stdio JSON-RPC | Decoupling, extensibility |
| **Graceful Degradation** | Try/except around external calls | Robustness |

