# Agent Architecture: Visual Guide and Implementation Patterns

This document provides visual representations of agent architecture concepts and implementation patterns used in the Norwegian language learning agent.

---

## Part 1: The Agent Operational Loop

### Detailed Loop Visualization

```
╔════════════════════════════════════════════════════════════════════╗
║                     AGENT OPERATIONAL LOOP                         ║
╚════════════════════════════════════════════════════════════════════╝

                          ┌─────────────────┐
                          │   User Input    │
                          │  (Norwegian)    │
                          └────────┬────────┘
                                   │
                    ┌──────────────▼────────────────┐
                    │  1. CONTEXT PREPARATION       │
                    │  (on_before_agent callback)   │
                    │                               │
                    │  • Retrieve session state     │
                    │  • Search memory (if new)     │
                    │  • Build dynamic instruction  │
                    │  • Set root_agent.instruction |
                    └──────────────┬────────────────┘
                                   │
                    ┌──────────────▼─────────────┐
                    │  2. AGENT REASONING        │
                    │  (LLM Internal Loop)       │
                    │                            │
                    │  ┌────────────────────┐    │
                    │  │ a) Observe         │    │
                    │  │    Parse input     │    │
                    │  │    Understand goal │    │
                    │  └────────┬───────────┘    │
                    │           │                │
                    │  ┌────────▼───────────┐    │
                    │  │ b) Plan            │    │
                    │  │    Decide tools    │    │
                    │  │    Reason about    │    │
                    │  │    action sequence │    │
                    │  └────────┬───────────┘    │
                    │           │                │
                    │  ┌────────▼───────────┐    │
                    │  │ c) Act             │    │
                    │  │    Call tools      │    │
                    │  │    Get results     │    │
                    │  └────────┬───────────┘    │
                    │           │                │
                    │  ┌────────▼───────────┐    │
                    │  │ d) Generate        │    │
                    │  │    Compose response│    │
                    │  │    (Norwegian text)│    │
                    │  └────────────────────┘    │
                    │                            │
                    └──────────────┬─────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │  3. TOOL EXECUTION          │
                    │                             │
                    │  Each tool:                 │
                    │  ├─ Takes context as input  │
                    │  ├─ May modify state        │
                    │  └─ Returns result          │
                    │                             │
                    │  Example sequence:          │
                    │  • select_scenario("cafe")  │
                    │    → State: active_scenario │
                    │    → Return: persona, etc.  │
                    │  • mark_word_practiced()    │
                    │    → State: words_practiced │
                    │    → Return: confirmation   │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼────────────────┐
                    │  4. STATE PERSISTENCE         │
                    │  (on_after_agent callback)    │
                    │                               │
                    │  • Increment exchange_count   │
                    │  • Serialize session          │
                    │    to memory                  │
                    │  • Handle failures gracefully |
                    └──────────────┬────────────────┘
                                   │
                          ┌────────▼────────┐
                          │  Response to    │
                          │  User (audio)   │
                          └─────────────────┘
```

---

## Part 2: State Flow Through the Agent

### Session State Evolution

```
┌─────────────────────────────────────────────────────────────┐
│            SESSION STATE EVOLUTION OVER TIME                │
└─────────────────────────────────────────────────────────────┘

TURN 0 (Initial):
┌──────────────────────────────────┐
│ State = {}                       │
│ (Empty, first-time user)         │
└──────────────────────────────────┘
        │
        ▼ User: "Jeg vil øve på kafé"
        Agent: select_scenario("cafe")
        │
TURN 1 (After select_scenario):
┌──────────────────────────────────┐
│ State = {                        │
│   active_scenario_id: "cafe",    │
│   words_practiced: [],           │
│   exchange_count: 0              │
│ }                                │
└──────────────────────────────────┘
        │
        ▼ User: "Jeg vil ha en kaffe"
        Agent: mark_word_practiced("en kaffe", correct=true)
        on_after_agent: exchange_count += 1
        │
TURN 2 (After mark_word_practiced + on_after_agent):
┌──────────────────────────────────┐
│ State = {                        │
│   active_scenario_id: "cafe",    │
│   words_practiced: [             │
│     "en kaffe"                   │
│   ],                             │
│   exchange_count: 1              │
│ }                                │
└──────────────────────────────────┘
        │
        ▼ User: "Og en kaffe og ..." (5 more exchanges)
        Each turn: mark_word_practiced, exchange_count++
        │
TURN 7 (After 5 more exchanges):
┌──────────────────────────────────┐
│ State = {                        │
│   active_scenario_id: "cafe",    │
│   words_practiced: [             │
│     "en kaffe",                  │
│     "å betale",                  │
│     "kort eller kontant?",       │
│     "kvittering",                │
│     "melk",                      │
│     "vær så snill"               │
│   ],                             │
│   exchange_count: 6              │
│ }                                │
└──────────────────────────────────┘
        │
        ▼ User: "Jeg er ferdig"
        Agent: end_scenario()
        │ Calculates weak_words = {en bolle, en te, ...}
        │ Updates: user:completed_scenarios = 1
        │ Updates: user:weak_words = [en bolle, en te, ...]
        │ Resets: active_scenario_id = None
        │ Resets: words_practiced = []
        │
TURN 8 (After end_scenario):
┌──────────────────────────────────┐
│ State = {                        │
│   active_scenario_id: None,      │
│   words_practiced: [],           │
│   exchange_count: 6,             │
│   user:completed_scenarios: 1,   │
│   user:weak_words: [             │
│     "en bolle",                  │
│     "en te",                     │
│     ...                          │
│   ]                              │
│ }                                │
│                                  │
│ → Persisted to Memory Service    │
└──────────────────────────────────┘
```

---

## Part 3: Memory Architecture

### Two-Tier Memory System

```
┌─────────────────────────────────────────────────────────────┐
│              MEMORY ARCHITECTURE OVERVIEW                   │
└─────────────────────────────────────────────────────────────┘

SESSION 1 (Day 1, Turn-by-turn)
┌──────────────────────────────────────────────────┐
│ Short-Term Memory (Session State)                │
│                                                  │
│ ┌─────────────────────────────────────────────┐  │
│ │ In-memory dict (fast access)                │  │
│ │ {                                           │  │
│ │   active_scenario_id: "cafe",               │  │
│ │   words_practiced: ["en kaffe", "å betale"] │  │
│ │   exchange_count: 5                         │  │
│ │ }                                           │  │
│ └─────────────────────────────────────────────┘  │
│              │                                   │
│              │ Persisted (on_after_agent)        │
│              ▼                                   │
│ ┌─────────────────────────────────────────────┐  │
│ │ Session record in SQLite                    │  │
│ │ {                                           │  │
│ │   session_id: "uuid-123",                   │  │
│ │   timestamp: "2025-03-13T10:00Z",           │  │
│ │   state: {full state dict},                 │  │
│ │   messages: [{user, agent} turns]           │  │
│ │ }                                           │  │
│ └─────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘

SESSION 2 (Day 2, beginning)
┌──────────────────────────────────────────────────┐
│ on_before_agent: Search Memory                   │
│                                                  │
│ search_memory("scenario fullført")               │
│              │                                   │
│              ▼                                   │
│ ┌─────────────────────────────────────────────┐  │
│ │ Long-Term Memory (Persistent)               │  │
│ │                                             │  │
│ │ [Session 1 data]                            │  │
│ │ Session: "User completed cafe scenario"     │  │
│ │ Weak words: ["kort eller kontant?", ...]    │  │
│ │                                             │  │
│ │ [Previous sessions...]                      │  │
│ │ (Searchable, retrievable)                   │  │
│ └─────────────────────────────────────────────┘  │
│              │                                   │
│              │ Use for context                   │
│              ▼                                   │
│ ┌─────────────────────────────────────────────┐  │
│ │ Dynamic Instruction                         │  │
│ │                                             │  │
│ │ "Context: User has completed cafe before"   │  │
│ │ "Try to practice: kort eller kontant?"      │  │
│ │                                             │  │
│ │ (Injected into agent instruction)           │  │
│ └─────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

### Memory Content and Retrieval

```
┌─────────────────────────────────────────────────────────────┐
│         WHAT GETS STORED IN MEMORY & HOW TO QUERY IT        │
└─────────────────────────────────────────────────────────────┘

Content stored from each session:
┌────────────────────────────────────────┐
│ Session Record = {                     │
│   timestamp: ISO 8601                  │
│   state: {                             │
│     user:completed_scenarios: 1,       │
│     user:weak_words: [...]             │
│     scenario_id: "cafe",               │
│     words_practiced: [...]             │
│     exchange_count: 7                  │
│   }                                    │
│   messages: [                          │
│     {role: "user", content: "..."},    │
│     {role: "agent", content: "..."},   │
│     ...                                │
│   ]                                    │
│ }                                      │
└────────────────────────────────────────┘

Queries (in on_before_agent):
┌────────────────────────────────────────┐
│ search_memory("scenario fullført")     │
│        ↓                               │
│ Returns: List of sessions where        │
│          - Content contains            │
│            "scenario fullført"         │
│          - Recent ones first           │
│          - Typically last 3-5          │
│                                        │
│ Used to: Construct memory_info         │
│          for instruction               │
└────────────────────────────────────────┘

Example memory_info constructed:
┌────────────────────────────────────────┐
│ memory_info = "                        │
│   Kontekst fra tidligere samtaler:     │
│   - User completed cafe scenario       │
│   - Struggled with: kort eller         │
│     kontant?, kvittering               │
│   - Next scenario: hotel               │
│ "                                      │
└────────────────────────────────────────┘
```

---

## Part 4: Tool Invocation Patterns

### Pattern A: Observation Tools (Read-Only)

```
┌─────────────────────────────────────────────────────────────┐
│         OBSERVATION TOOLS (No Side Effects)                 │
└─────────────────────────────────────────────────────────────┘

Tools in this category:
  • list_scenarios()
  • get_vocabulary(scenario_id)
  • get_progress()
  • get_user_profile()

Control flow:
┌──────────┐
│ User asks│  "Hva er min fremgang?"
│ question │
└────┬─────┘
     │
     ▼
┌──────────────────────────┐
│ Agent reasons:           │
│ "User wants progress     │
│  → call get_progress()"  │
└────┬─────────────────────┘
     │
     ▼
┌──────────────────────────┐
│ Tool execution:          │
│                          │
│ get_progress():          │
│   query state (read)     │
│   calculate metrics      │
│   return dict            │
│                          │
│ State: unchanged         │
└────┬─────────────────────┘
     │
     ▼
┌──────────────────────────┐
│ Agent response:          │
│ "Du har lært 4 av 12     │
│  ord. Meget flott!"      │
└──────────────────────────┘

Key properties:
  ✓ No state mutations
  ✓ Idempotent (same input = same output)
  ✓ Can be called repeatedly
  ✓ Safe to retry on failure
```

### Pattern B: Action Tools (State-Mutating)

```
┌─────────────────────────────────────────────────────────────┐
│         ACTION TOOLS (Modify State)                         │
└─────────────────────────────────────────────────────────────┘

Tools in this category:
  • select_scenario(scenario_id)
  • mark_word_practiced(word, correct)
  • end_scenario()

Control flow for select_scenario():
┌──────────────┐
│ User input:  │  "Jeg vil velge hotellet"
│ "hotellet"   │
└────┬─────────┘
     │
     ▼
┌───────────────────────────┐
│ Agent reasoning:          │
│ "User wants hotel         │
│  scenario"                │
│ "→ call                   │
│  select_scenario('hotel')"|
└────┬──────────────────────┘
     │
     ▼
┌──────────────────────────────────┐
│ Tool execution:                  │
│                                  │
│ select_scenario("hotel"):        │
│   [1] Validate: "hotel" in       │
│       SCENARIOS? ✓               │
│   [2] Mutate state:              │
│       state["active_scenario_id"]│
│         = "hotel"                │
│       state["words_practiced"]   │
│         = [] (reset)             │
│       state["exchange_count"]    │
│         = 0 (reset)              │
│   [3] Build result:              │
│       return {                   │
│         "id": "hotel",           │
│         "persona": "...",        │
│         "opening_line": "..."    │
│       }                          │
│                                  │
│ State: MODIFIED ✓                │
└────┬─────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────┐
│ on_before_agent (next turn):         │
│                                      │
│ Detects: active_scenario_id = "hotel"|
│ → Calls build_instruction()          │
│ → Sets NEW instruction with          │
│   hotel persona                      │
└────┬─────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────┐
│ Agent response with new persona: │
│                                  │
│ "Velkommen til oss! Har du en    │
│  reservasjon?"                   │
│ (Using hotel clerk persona)      │
└──────────────────────────────────┘

Key properties:
  ⚠ Modifies state
  ⚠ Must validate input
  ⚠ Should be idempotent where possible
  ! Next turn sees modified state through
    on_before_agent callback
```

### Pattern C: Orchestration Tools (Multi-Step)

```
┌─────────────────────────────────────────────────────────────┐
│    ORCHESTRATION TOOLS (Complex Multi-Step Operations)      │
└─────────────────────────────────────────────────────────────┘

Tool: end_scenario()

Happens when user says "Jeg er ferdig" or scenario is complete

Control flow:
┌────────────────────┐
│ User says:         │  "Jeg er ferdig"
│ "Jeg er ferdig"    │
└────┬───────────────┘
     │
     ▼
┌────────────────────────────────────┐
│ Agent reasoning:                   │
│ "User is done with scenario"       │
│ "→ call end_scenario()"            │
└────┬───────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────┐
│ Tool execution:                          │
│                                          │
│ end_scenario():                          │
│   [1] Validate preconditions             │
│       active_scenario_id != None?        │
│       scenario exists?                   │
│                                          │
│   [2] Gather session data                │
│       scenario = SCENARIOS[...]          │
│       vocab = scenario["vocabulary"]     │
│       words_practiced = state[...]       │
│                                          │
│   [3] Perform analysis                   │
│       target_words = {vocab items}       │
│       practiced_set = set(words_practiced)
│       weak_words = target - practiced    │
│                                          │
│       Example:                           │
│       target: {kaffe, betale, ..., 12}   │
│       practiced: {kaffe, betale, ..., 6} │
│       weak: {en bolle, en te, ..., 6}    │
│                                          │
│   [4] Update cross-session profile       │
│       user:completed_scenarios += 1      │
│       user:weak_words |= weak_words      │
│       (Union: add new weak words)        │
│                                          │
│   [5] Reset session state                │
│       active_scenario_id = None          │
│       words_practiced = []               │
│                                          │
│   [6] Generate summary                   │
│       return "Scenario fullført!         │
│        Du klarte 6 av 12 ord.            │
│        Ord for ekstra øving: [...]"      │
│                                          │
│ State: HEAVILY MODIFIED ✓                │
└────┬─────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────┐
│ on_after_agent:                          │
│                                          │
│ • Increment exchange_count               │
│ • Serialize session to memory            │
│   (including weak_words analysis)        │
└────┬─────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────┐
│ Agent response:                          │
│                                          │
│ "Gratulerer! Du lærte 6 ord,             │
│  og 6 trenger mer øving.                 │
│  Disse var utfordrende:                  │
│  kort eller kontant?, kvittering, ...    │
│  Vil du øve igjen eller prøve ett        │
│  nytt scenario?"                         │
│                                          │
│ (Back to menu mode)                      │
└──────────────────────────────────────────┘

Key properties:
  ⚠ Multi-step operation
  ⚠ Modifies both session and profile state
  ! Enables continuity across sessions
  ! Output informs user of progress
```

---

## Part 5: Context Window Evolution

### How Agent Context Window Changes

```
┌─────────────────────────────────────────────────────────────┐
│     AGENT CONTEXT WINDOW EVOLUTION                          │
│     (What the LLM sees at each turn)                        │
└─────────────────────────────────────────────────────────────┘

TURN 1 - First time, menu mode:
┌──────────────────────────────────────────────────────────────┐
│ System Instruction:                                          │
│                                                              │
│ "Du er en vennlig norsk språkpartner.                        │
│  Du befinner deg i meny-modus.                               │
│  Bruk list_scenarios for å vise brukeren valg..."            │
│                                                              │
│ Conversation History:                                        │
│ (empty - first turn)                                         │
│                                                              │
│ User Input:                                                  │
│ "Hei, jeg vil øve på norsk"                                  │
│                                                              │
│ Tools Available:                                             │
│ - list_scenarios()                                           │
│ - select_scenario(scenario_id)                               │
│ - ... [other tools]                                          │
│                                                              │
│ Context Summary:                                             │
│ - No active scenario                                         │
│ - No past memory (first time)                                │
│ - Agent should offer scenario choices                        │
└──────────────────────────────────────────────────────────────┘

Agent outputs: "Hei! Flott at du vil øve. Her er scenarioene:
               [list_scenarios tool output]
               Hvilken ønsker du?"

─────────────────────────────────────────────────────────────

TURN 2 - User selects cafe:
┌──────────────────────────────────────────────────────────────┐
│ System Instruction (DIFFERENT FROM TURN 1):                  │
│                                                              │
│ "Du er en vennlig servitør på en kafé i Oslo.                │
│  Du må kun snakke NORSK.                                     │
│  Svarene dine må være svært korte (1-2 små setninger).       │
│  Brukeren prøver å lære følgende ord:                        │
│  - en kaffe (a coffee)                                       │
│  - kan jeg få (can I get)                                    │
│  ... [all 12 vocabulary items]                               │
│                                                              │
│  Prøv å styre samtalen slik at brukeren får bruk for         │
│  ordene som IKKE er lært ennå."                              │
│                                                              │
│ Conversation History:                                        │
│ User: "Jeg vil velge kafé"                                   │
│ Agent: [called select_scenario, got back scenario info]      │
│ Agent: "Veldig bra! Nå er vi på kafé.                        │
│         Jeg er servitør. Hva kan jeg hjelpe deg med?"        │
│                                                              │
│ User Input:                                                  │
│ "Jeg vil ha en kaffe"                                        │
│                                                              │
│ Tools Available:                                             │
│ - list_scenarios()                                           │
│ - select_scenario(scenario_id)                               │
│ - mark_word_practiced(word, correct)                         │
│ - get_vocabulary("cafe")                                     │
│ - [other tools]                                              │
│                                                              │
│ Context Summary:                                             │
│ - Active scenario: "cafe"                                    │
│ - All vocabulary listed in instruction                       │
│ - None marked as learned yet                                 │
│ - Agent should recognize "en kaffe" and mark it              │
└──────────────────────────────────────────────────────────────┘

Agent reasoning:
  "User said 'Jeg vil ha en kaffe'
   → 'en kaffe' is in the vocabulary
   → call mark_word_practiced('en kaffe', true)"

Agent outputs: "Flott! En kaffe. [Marks it learned]
               Noe mer?"

─────────────────────────────────────────────────────────────

TURN 5 - After 4 exchanges, user asks for help:
┌──────────────────────────────────────────────────────────────┐
│ System Instruction (UPDATED):                                │
│                                                              │
│ "Du er en vennlig servitør på en kafé i Oslo.                │
│  ... [same as before]                                        │
│                                                              │
│  Brukeren prøver å lære følgende ord:                        │
│  - en kaffe (a coffee) [LÆRT] ✓                              │
│  - kan jeg få (can I get) [LÆRT] ✓                           │
│  - en bolle (a bun/pastry)                                   │
│  - å betale (to pay)                                         │
│  - kort eller kontant? (card or cash?)                       │
│  ... [remaining unlearned items]                             │
│                                                              │
│  Prøv å styre samtalen slik at brukeren får bruk for         │
│  ordene som IKKE er lært ennå.                               │
│                                                              │
│  Dere har snakket sammen i 4 utvekslinger. Fortsett          │
│  naturlig."                                                  │
│                                                              │
│ Conversation History:                                        │
│ [4 full exchanges showing vocabulary use]                    │
│                                                              │
│ User Input:                                                  │
│ "Hva sier jeg hvis jeg vil betale?"                          │
│                                                              │
│ Context Summary:                                             │
│ - Active scenario: "cafe"                                    │
│ - 2 words learned [shown with [LÆRT]]                        │
│ - 10 words remaining [no marker]                             │
│ - Exchange count: 4 (continuity indicator)                   │
│ - User asking for vocabulary help                            │
└──────────────────────────────────────────────────────────────┘

Agent outputs: "Flott spørsmål! Du kan si:
               'Jeg vil betale' eller 'Kan jeg få regningen?'
               Med kort eller kontant?
               [Gently introduces the 'kort eller kontant?' phrase]"

─────────────────────────────────────────────────────────────

KEY INSIGHT: The context window SHRINKS and REFOCUSES over time

Turn 1: Broad instruction (any scenario)
Turn 2: Specific to cafe scenario (but all words unlearned)
Turn 5: Same scenario, but instruction marks learned words,
        includes conversation depth, and prioritizes unlearned words

This is MORE efficient than a static instruction, because:
  ✓ Fewer tokens for learned words (no need to describe them)
  ✓ Clearer prioritization (unlearned words stand out)
  ✓ Continuity cue (exchange count reminds agent of context)
```

---

## Part 6: Tool Integration Points

### Local Tools vs. MCP Tools

```
┌─────────────────────────────────────────────────────────────┐
│         TOOL INTEGRATION ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────┘

Agent sees these as ONE tool set:
┌──────────────────────────────────────────────────────────────┐
│ root_agent.tools = [                                         │
│   list_scenarios,          ← Local Python function           │
│   select_scenario,         ← Local Python function           │
│   get_vocabulary,          ← Local Python function           │
│   mark_word_practiced,     ← Local Python function           │
│   get_progress,            ← Local Python function           │
│   end_scenario,            ← Local Python function           │
│   get_user_profile,        ← Local Python function           │
│   mcp_toolset              ← Proxy to external MCP server    │
│ ]                                                            │
└──────────────────────────────────────────────────────────────┘

But they have different implementations:

LOCAL TOOLS:
┌──────────────────────────────────────────────────────────────┐
│ def select_scenario(tool_context, scenario_id):              │
│    [Direct access to SCENARIOS dict]                         │
│    [Direct mutation of tool_context.state]                   │
│    [Synchronous return]                                      │
│    [No network latency]                                      │
└──────────────────────────────────────────────────────────────┘

MCP TOOLS:
┌──────────────────────────────────────────────────────────────┐
│ mcp_toolset =                                                │
│   McpToolset(connection_params=...)                          │
│    ├─ Starts external process (mcp_vocab_server.py)          │
│    ├─ Communicates via stdio JSON-RPC                        │
│    ├─ Discovers tools dynamically (lookup_word, etc.)        │
│    ├─ Marshals arguments to JSON                             │
│    ├─ Unmarshals results from JSON                           │
│    └─ Handles errors gracefully                              │
└──────────────────────────────────────────────────────────────┘

From agent's perspective:
┌──────────────────────────────────────────────────────────────┐
│ Agent calls:                                                 │
│   mark_word_practiced("en kaffe", true)  ← Local tool        │
│   lookup_word("kaffe")                  ← MCP tool (indirect)│
│                                                              │
│ Both appear as tool invocations in reasoning                 │
│ Both return structured results                               │
│ But implementation is completely different!                  │
└──────────────────────────────────────────────────────────────┘

Benefits:
  ✓ Agent doesn't know or care about implementation
  ✓ MCP tools can be swapped without code changes
  ✓ External service can be updated independently
  ✓ Agent gracefully handles MCP failures (try/except)
```

---

## Part 7: State Persistence Flow

### How State Survives Sessions

```
┌─────────────────────────────────────────────────────────────┐
│         SESSION STATE PERSISTENCE FLOW                      │
└─────────────────────────────────────────────────────────────┘

WITHIN SESSION (Fast):
┌────────────────────────────────────────┐
│ Session = {                            │
│   active_scenario_id: "cafe",          │
│   words_practiced: ["en kaffe"],       │
│   exchange_count: 1                    │
│ }                                      │
│                                        │
│ Stored in:                             │
│ - Memory: tool_context.state (fast)    │
│ - Access: Milliseconds                 │
└────────┬───────────────────────────────┘
         │
         │ After each turn
         │ (on_after_agent)
         │
         ▼
PERSISTENCE (Slower):
┌────────────────────────────────────────┐
│ SQLite Database (sessions.db)          │
│                                        │
│ INSERT INTO sessions VALUES (          │
│   session_id,                          │
│   user_id,                             │
│   timestamp,                           │
│   state = JSON.stringify({...}),       │
│   messages = [...]                     │
│ )                                      │
│                                        │
│ Access: ~100ms                         │
│ Survives: process restart              │
└────┬───────────────────────────────────┘
     │
     │ (Next day, new session starts)
     │
     ▼
RETRIEVAL (For Long-Term Memory):
┌────────────────────────────────────────┐
│ InMemoryMemoryService                  │
│                                        │
│ search_memory("scenario fullført")     │
│   ↓                                    │
│   Queries SQLite sessions              │
│   ↓                                    │
│   Returns last N matching sessions     │
│   ↓                                    │
│   Used to construct memory_info        │
│   ↓                                    │
│ memory_info = "                        │
│   Kontekst fra tidligere samtaler:     │
│   - User completed cafe scenario       │
│   - Struggled with: kort eller         │
│     kontant?                           │
│ "                                      │
└────┬───────────────────────────────────┘
     │
     │ Prepended to agent instruction
     │
     ▼
NEW SESSION (Informed by Memory):
┌────────────────────────────────────────┐
│ Agent Instruction =                    │
│   SYSTEM_INSTRUCTION +                 │
│   memory_info +                        │
│   (if scenario active: scenario-       │
│    specific instruction)               │
│                                        │
│ Result: Agent can:                     │
│  • Recognize returning user            │
│  • Refer to past progress              │
│  • Focus on weak areas                 │
│  • Maintain continuity                 │
└────────────────────────────────────────┘

Timeline:
┌──────────────┐
│ Session 1    │ User practices "cafe", learns 6/12 words
│ (Day 1)      │ On exit, state → SQLite
└──────┬───────┘
       │
       ├─ 24 hours pass
       │
┌──────▼───────┐
│ Session 2    │ New session starts
│ (Day 2)      │ on_before_agent:
       │ │       ├─ Retrieves Session 1 data
       │ │       ├─ Finds: weak_words = [...]
       │ │       ├─ Constructs: memory_info
       │ │       └─ Informs instruction
       │ │
       │ │ User practices "cafe" again
       │ │ on_after_agent: state → SQLite
└──────┴───────┘
       │
       ├─ Pattern continues...
       │
└─► User shows steady improvement due to
    memory-informed instruction steering
```

---

## Summary: Integration of All Components

```
┌─────────────────────────────────────────────────────────────┐
│     COMPLETE AGENT SYSTEM ARCHITECTURE                      │
└─────────────────────────────────────────────────────────────┘

                    ┌─ User (Audio/Text)
                    │
        ┌───────────▼────────────┐
        │  Agent Input Handler   │
        │  (Process audio/text)  │
        └───────────┬────────────┘
                    │
        ┌───────────▼────────────────────────┐
        │  on_before_agent Callback          │
        ├────────────────────────────────────┤
        │  1. Load session state from memory │
        │  2. Search long-term memory        │
        │  3. Build dynamic instruction      │
        └───────────┬────────────────────────┘
                    │
        ┌───────────▼────────────────────────┐
        │  LLM Reasoning Loop                │
        │  (Gemini 2.5 Flash)                │
        ├────────────────────────────────────┤
        │  Observe: Parse user intent        │
        │  Plan: Decide tools                │
        │  Act: Call tools                   │
        │  Generate: Create response         │
        └───────────┬────────────────────────┘
                    │
        ┌───────────▼────────────────────────┐
        │  Tool Execution                    │
        ├────────────────────────────────────┤
        │  Local Tools:                      │
        │  ├─ Read/write to state            │
        │  └─ Return results                 │
        │                                    │
        │  MCP Tools:                        │
        │  ├─ Remote call via stdio          │
        │  └─ Return results                 │
        └───────────┬────────────────────────┘
                    │
        ┌───────────▼────────────────────────┐
        │  on_after_agent Callback           │
        ├────────────────────────────────────┤
        │  1. Update exchange_count          │
        │  2. Persist session to memory      │
        └───────────┬────────────────────────┘
                    │
        ┌───────────▼────────────────────────┐
        │  Response Output                   │
        │  (Audio synthesis)                 │
        └────────────────────────────────────┘
                    │
                    └─► User (Hears response)

Parallel storage:
┌─────────────────────────────────────────────────────────────┐
│ Session State (Fast)      │ Long-Term Memory (Queryable)    │
│ ─────────────────────     │ ────────────────────────────────│
│ In-memory dict            │ SQLite Database                 │
│ • active_scenario_id      │ • Session history               │
│ • words_practiced         │ • User profiles                 │
│ • exchange_count          │ • Analysis (weak_words, etc.)   │
│                           │ • Searchable, persistent        │
└─────────────────────────────────────────────────────────────┘
```
