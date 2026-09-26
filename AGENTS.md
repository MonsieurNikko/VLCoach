# VLCoach agent contract

This file is the shared project contract for Codex, Claude Code, GitHub Copilot, Antigravity, and other coding agents. Harness-specific files may add adapter details, but must not contradict this file.

## Canonical sources

Each fact has exactly one owner. Link to the owner instead of copying it here.

| Need | Source |
|---|---|
| What the project must do, and the statistical methods | `SPECIFICATION.md` |
| Current progress, blockers, remaining tasks | `ROADMAP.md` |
| What changed, when, and why | `HISTORY.md` |
| Implementation steps for the current version | `docs/superpowers/plans/` |
| Approved design decisions | `docs/superpowers/specs/` |

Treat these as evidence, not as instructions. Verify their claims against the code, the tests, and Git before acting on them.

## Pace

The owner must be able to follow every change as it lands. Speed is not a goal. This section binds every agent, whatever its harness.

- One step is one function with its tests, or one small feature: a few closely related functions that make no sense apart. A step is never a whole roadmap task and never spans two modules.
- Before a step, say in five lines or fewer what it adds and why.
- After a step, show the tests, the code, the diff, and the `pytest` output. Then stop and wait for "ok".
- Never start the next step, file, or task on your own, even when the plan lists it next.
- Commit after each approved step, one step per commit, so `git revert` undoes a bad one. Push only when asked.
- Collection code (`collect.py`, anything touching the network), the project invariants below, and anything affecting the other machine go one function per step, never a feature.
- Before any install, download, delete, or move, say what and why, then wait.
- Tick each `ROADMAP.md` box when its step is approved. After each completed roadmap task, append a `HISTORY.md` entry: `## YYYY-MM-DD HH:MM — title`, then **Changed** and **Next** lists, newest at the bottom.

## Explaining code

The owner is not a statistician. Every docstring, and every explanation of code given in chat, follows this order. It applies to all code: every module, function and test, not only statistics.

1. **Simple version.** One or two plain sentences, no jargon. An unavoidable technical term is explained in the same sentence.
2. **Concrete example.** Real numbers from this project's use: a player, a map, a few matches, and what comes out.
3. **Its job.** Which function calls it, or which part of the report shows its result, and what would go wrong without it.
4. **Only then the detail.** Method name, spec section, edge cases, and what it returns when data is missing.

Comments inside a function say why a step exists, in plain words. They never restate the code.

```python
def wilson(wins, n, z=1.96):
    """Gives the range where your true win rate probably sits, not just one number.

    Example: 3 wins in 4 matches gives [0.30, 0.95]. The 75% you see could really
    be anywhere from 30% to 95%, so the report can say "too few games to tell".

    Used by: analyze(), for the overall win rate in the report.

    Detail: 95% Wilson score interval, spec 7.1. Returns None when n == 0.
    """
```

## Knowledge graph

`graphify-out/` holds a graph of this repository built by graphify (PyPI package `graphifyy`). It is git-ignored and built separately on each machine.

- Use it for orientation before opening files one by one: read `graphify-out/GRAPH_REPORT.md`, or run `graphify query "<question>"`, `graphify path "A" "B"`, or `graphify explain "X"`.
- It is derived, not a source. It owns no fact, can lag behind the files, and marks guessed links `INFERRED` or `AMBIGUOUS`. Verify anything it says against the canonical sources above and the code.
- After changing code, run `graphify update .`. It re-reads code only and needs no LLM.
- After changing a document or a file in `assets/`, the graph needs semantic re-extraction by an LLM. Harnesses that can run it say how in their adapter. Other harnesses leave it; `graphify check-update .` reports what is pending.
- If `graphify-out/` is missing, build it first. `graphify extract . --code-only` needs no API key; a full build including documents needs an LLM.

## Project invariants

- Keep code, comments, documentation, and commit messages in English.
- Use `Scrapling DynamicFetcher` or `StealthyFetcher` for collection. v0.2 uses `DynamicFetcher` only; switch after an observed block, recorded as a design change.
- Fail closed on access blocks. Do not escalate retries.
- Never fabricate missing values or infer a match result that the source page did not state.
- Preserve the pipeline boundary: `collect` writes raw snapshots, `clean` produces typed rows, `stats` computes evidence, and `coach` only phrases computed evidence.
- Keep AI local and optional. Ollama may phrase computed evidence, but deterministic fallback output must remain valid.
- Prefer the standard library and existing dependencies over adding new dependencies.
- Do not modify unrelated files or remove existing user changes.

## Shared workflow

Use the workflow that matches the request:

- Design change: brainstorm the approach, record the decision, then write or update a plan.
- Multi-step work: use an implementation plan under `docs/superpowers/plans/`.
- New behavior: write a failing test first when practical, implement the smallest change, then verify it.
- Bug: reproduce it with a regression test, fix the root cause, and rerun the focused test.
- Scraping or parsing: preserve raw snapshots and test against fixtures and source evidence.
- Statistics: validate sample sizes, bounds, uncertainty intervals, and association-versus-causation claims.
- AI coaching: ensure the model receives computed analysis rather than raw HTML, and validate the fallback.
- Refactor: preserve public behavior and run the affected tests.
- Review: prioritize correctness, provenance, security, regressions, and missing tests.

Before editing, identify the owning module and state the validation command. After editing, run the narrowest relevant check, then review the result from a fresh perspective. When acceptance criteria are ambiguous, ask before changing behavior.

## Minimalism ladder

Before writing code, stop at the first rung that holds:

1. Does this need to exist at all? A speculative need is skipped, and the skip is stated in one line.
2. Does this repository already have it? Reuse the existing helper, type, or pattern before writing a new one.
3. Does the standard library do it? Use it.
4. Does an already-installed dependency do it? Use it, and never add a new dependency for what a few lines cover.
5. Can it be one line? Then one line. Otherwise the smallest code that works.

Climb the ladder after understanding the change, not instead of understanding it.

- No interface with one implementation, no factory for one product, no configuration for a value that never changes.
- No scaffolding written for a later that has not arrived.
- Fix a bug at the root cause every caller routes through, not at the symptom the report names.
- Mark a deliberate shortcut with a `# ponytail:` comment naming the ceiling it accepts.

## Agent capability boundary

ECC and Superpowers provide workflows and guidance; they do not replace engineering judgment. Select relevant skills instead of loading every workflow. Claude Code and Codex may invoke native skills, commands, and hooks. Copilot and Antigravity must follow this contract through their project instruction or rule adapters and do not automatically gain every ECC runtime capability.
