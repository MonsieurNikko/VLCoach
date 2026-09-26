# Agent rules for this repo

**Read `AGENTS.md` before editing anything.** It is the shared contract for every agent on this
project: the invariants you must obey, and the canonical source for each kind of project fact.
This file adds only what is specific to Claude Code, and must never contradict it.

## Pace
- Approval is per task, not per file. Before starting one, say in five lines or fewer what it
  changes and why. Run it end to end, then show the full diff and the `pytest` output, and wait
  for "ok". One task is one commit, so `git revert` undoes a bad one.
- High blast radius keeps the stricter rule — one file per step, wait for "ok" before the next:
  `collect.py`, anything touching the network, the hard limits in `AGENTS.md`, or the other machine.
- Before any install, download, delete or move, say what and why, then wait. No exception.
- Tick each sub-step box in `ROADMAP.md` as it is done, so progress stays visible between approvals.
- After each completed task, append an entry to `HISTORY.md`: `## YYYY-MM-DD HH:MM — title`, then **Changed** and **Next** lists. Newest at the bottom.

## Workflow (spec §11)
- Superpowers: `brainstorming` before design changes, `writing-plans` before multi-step work,
  `test-driven-development` for all behaviour (RED → GREEN → REFACTOR),
  `systematic-debugging` for any failure, `verification-before-completion` before any "done".
- Ponytail: follow the minimalism ladder in `AGENTS.md`. Plugin `ponytail@ponytail` 4.10.0 is
  installed at user scope; `/ponytail lite|full|ultra` sets the intensity, default `full`.
- Plans in `docs/superpowers/plans/`, design specs in `docs/superpowers/specs/`.

## Graphify
- Graph rules are in `AGENTS.md` (Knowledge graph). This section adds the Claude Code side.
- For a question that spans files, start with `graphify-out/GRAPH_REPORT.md` or `graphify query`.
- First build on a machine: `/graphify .` from the repo root.
- At the end of each task, after the `HISTORY.md` entry: run `graphify update .` if code changed,
  and `/graphify . --update` if any document changed, `HISTORY.md` and `ROADMAP.md` included.
  Only changed files are re-extracted, but each one costs LLM tokens.
- Post-commit hook: `graphify hook install`, once per machine, after the install rule above. It
  refreshes code only. Documents still need `/graphify . --update`.

## Environment
- Windows venv is `.venv`, Mac venv is `.venv-mac`. Both git-ignored, each machine uses only
  its own. Python is 3.13 on the PC, 3.12 on the Mac.
- `PLAYWRIGHT_BROWSERS_PATH` and `OLLAMA_MODELS` are per-machine user env vars, not project
  config. On the PC both point to D:.
- On the PC the repo sits inside iCloud Drive: commit and push from one machine at a time, and
  avoid `git checkout` there — the file storm locked `.git/index` once (`HISTORY.md`, 2026-09-22 01:09).
  The Mac clone is outside iCloud, so switching branches on it is safe.
- Line endings are LF everywhere (`.gitattributes`).

## Language
- Coaching report: `--lang fr|en`, default `en`.
