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

## Workflow (spec §11)
- Superpowers: `brainstorming` before design changes, `writing-plans` before multi-step work,
  `test-driven-development` for all behaviour (RED → GREEN → REFACTOR),
  `systematic-debugging` for any failure, `verification-before-completion` before any "done".
- Ponytail: follow the minimalism ladder in `AGENTS.md`. Plugin `ponytail@ponytail` 4.10.0 is
  installed at user scope; `/ponytail lite|full|ultra` sets the intensity, default `full`.
- Plans in `docs/superpowers/plans/`, design specs in `docs/superpowers/specs/`.

## Environment
- Windows venv is `.venv`, Mac venv is `.venv-mac`. Both git-ignored, both iCloud-synced,
  each machine uses only its own.
- `PLAYWRIGHT_BROWSERS_PATH` and `OLLAMA_MODELS` are per-machine user env vars, not project
  config. On the PC both point to D:.
- `.git` lives inside iCloud Drive: commit and push from one machine at a time.
- Line endings are LF everywhere (`.gitattributes`).

## Language
- Coaching report: `--lang fr|en`, default `en`.
