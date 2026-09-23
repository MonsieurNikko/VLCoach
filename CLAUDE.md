# Agent rules for this repo

**Read `AGENTS.md` before editing anything.** It is the shared contract for every agent on this
project: the invariants you must obey, and the canonical source for each kind of project fact.
This file adds only what is specific to Claude Code, and must never contradict it.

## Pace
- One file per step. Before writing a file, say what it does and why in five lines or fewer. Wait for "ok" before the next file.
- After every edit, show the diff, or the whole file if new.
- No batch writes, no parallel file creation.
- Before any install, download, delete or move, say what and why, then wait.
- After each completed step, append an entry to `HISTORY.md`: `## YYYY-MM-DD HH:MM — title`, then **Changed** and **Next** lists. Newest at the bottom.
- Tick the matching box in `ROADMAP.md` when a sub-step is done.

## Workflow (spec §11)
- Superpowers: `brainstorming` before design changes, `writing-plans` before multi-step work,
  `test-driven-development` for all behaviour (RED → GREEN → REFACTOR),
  `systematic-debugging` for any failure, `verification-before-completion` before any "done".
- Ponytail: follow the minimalism ladder in `AGENTS.md`. Plugin `ponytail@ponytail` 4.10.0 is
  installed at user scope; `/ponytail lite|full|ultra` sets the intensity, default `full`.
- Plans in `docs/superpowers/plans/`, design specs in `docs/superpowers/specs/`.

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
