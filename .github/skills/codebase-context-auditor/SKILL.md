---
name: codebase-context-auditor
description: 'Examine the repository, map components and tech stack, and draft/refresh Agent.md for upcoming planning phases.'
argument-hint: 'Which folders or modules need to be profiled?'
---

# Codebase Context Auditor

## Outcomes
- Repository topology map covering directories, services, tools, and data assets
- Component relationship summary that calls out integration points, contracts, and risks
- Fresh `Agent.md` briefing that future agents use as context for planning and implementation

## When to Use
- Kicking off a new development phase or onboarding a contributor
- Validating that the documented architecture still matches the actual code
- Before writing or refreshing `Agent.md` so downstream agents inherit accurate context

## Required Inputs
- **Scope**: repo root or specific subdirectories to audit
- **Concerns** (optional): questions, TODOs, or suspected gaps that deserve extra scrutiny
- **Output path**: default `Agent.md` at repository root (override if needed)

## Procedure
1. **Stabilize workspace**
   - Sync main, run `git status`, ensure no unrelated changes.
   - Skim `README.md`, `Docs/` roadmaps, and `norsk_praksis/README.md` to capture declared goals.
2. **Inventory structures**
   - List top-level directories plus any language-specific folders (`norsk_praksis/`, `Docs/`, `tests/`).
   - Record for each: purpose, primary languages, notable dependencies, and entry points.
3. **Deep-dive components**
   - For every scoped directory, read exported classes/functions (e.g., `norsk_agent/agent.py`, `tools.py`).
   - Note: responsibilities, key abstractions, contracts, data models, external APIs, storage, and side effects.
4. **Map interactions**
   - Trace how modules call each other. Capture import graphs, shared utilities, configuration flow, and test coverage links.
   - Highlight coupling/potential seams for extension, plus undocumented conventions or implicit state.
5. **Assess tech stack**
   - Summarize runtimes (Python version, frameworks, tooling), data formats (`vocabulary.json`, prompts, MCP servers), and infra assumptions.
   - Document setup commands (venv activation, `pip install -r requirements.txt`, `pytest`).
6. **Capture risks & opportunities**
   - List performance hotspots, missing tests, brittle integrations, and modernization ideas.
   - Tie observations back to roadmap phases in `Docs/SPEC_N_ROADMAPs/` when relevant.
7. **Author `Agent.md`**
   - Use the template below; fill each section with findings.
   - Store at repo root (or agreed location) and link to supporting files (diagrams, specs, TODOs).
   - Re-run lint/tests if recommendations add code changes, then commit alongside `Agent.md`.

## Agent.md Template
```markdown
# Agent Brief

## Mission Snapshot
- Project purpose, stakeholders, current phase
- Key dependencies (models, services, datasets)

## Tech Stack & Tooling
- Languages, frameworks, build/test commands
- External services and credentials

## Core Components
| Area | Role | Key Files | Notes |
|------|------|-----------|-------|

## Data & Knowledge Assets
- Schemas, vocabularies, prompt stores, diagrams

## Integration & Flows
- How modules interact, event/data pipelines, contracts

## Risks & Gaps
- Testing debt, coupling, unknowns, blocked items

## Next-Step Recommendations
- High-priority investigations or tasks for the next dev stage
```

## Quality Checks
- Every major directory mentioned with purpose + owner modules
- Interactions cite concrete files/functions, not vague descriptions
- Agent.md references current tech stack, setup steps, and risk list
- Findings trace back to docs or code snippets for verification

## Follow-Up
- If scope exceeds timebox, split into multiple Agent.md updates (per subsystem)
- Schedule recurring audits (per roadmap phase) so Agent.md stays fresh
