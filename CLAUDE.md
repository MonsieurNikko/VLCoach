# Agent rules for this repo

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
- Ponytail: stdlib before dependencies, fewest files, no speculative abstractions.
  Mark deliberate shortcuts with a `# ponytail:` comment naming the ceiling.
- Plans in `docs/superpowers/plans/`, design specs in `docs/superpowers/specs/`.

## Hard limits (spec §3.2, §5.3)
- Scrapling `DynamicFetcher` only. Never `StealthyFetcher`, proxies, CAPTCHA handling,
  fingerprint spoofing, or Tracker Network internal API calls.
- Fail closed on any access block. No retry escalation.
- Never fabricate a missing value. Never infer a match result the page did not state.

## Environment
- Windows venv is `.venv`, Mac venv is `.venv-mac`. Both git-ignored, both iCloud-synced,
  each machine uses only its own.
- `PLAYWRIGHT_BROWSERS_PATH` and `OLLAMA_MODELS` are per-machine user env vars, not project
  config. On the PC both point to D:.
- `.git` lives inside iCloud Drive: commit and push from one machine at a time.
- Line endings are LF everywhere (`.gitattributes`).

## Language
- Code, comments, commits, docs: English.
- Coaching report: `--lang fr|en`, default `en`.
