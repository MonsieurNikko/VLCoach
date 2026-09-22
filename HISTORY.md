# History

Running log. Newest entry at the bottom. Every entry: when, what changed, what comes next.

---

## 2026-09-21 00:52 — Spec dropped in

**Changed**
- `SPECIFICATION.md` placed in an empty folder. No code, no git.

**Next**
- Read it, plan.

---

## 2026-09-21 01:10 — Environment measured, plan drafted

**Changed**
- Machine probed: Python 3.13.2, RTX 4070 SUPER with 12 GB VRAM (not 16), Ollama 0.5.7 (too old), C: at 9.8 GB free, D: at 103 GB free.
- Tracker.gg `robots.txt` checked: disallows `/*/profile/*` and `/*/matches/*` for all agents. User chose live crawl anyway.
- Model chosen: `qwen3:14b` (9.3 GB, fits 12 GB on-GPU). User declined three-way benchmark.
- Plugins installed: `superpowers@claude-plugins-official` 6.3.0, `ponytail@ponytail` 4.10.0.

**Next**
- Provision venv, Scrapling, disk reclaim.

---

## 2026-09-21 01:35 — Provisioning and disk reclaim

**Changed**
- `.venv` created (CPython 3.13.2). `scrapling==0.4.15` installed from `git+https://github.com/D4Vinci/Scrapling.git@2b160ee`.
- `PLAYWRIGHT_BROWSERS_PATH=D:\playwright` set at user scope. All 18 browser versions from `C:\...\ms-playwright` moved there, nothing left on C:.
- `OLLAMA_MODELS=D:\ollama\models` set at user scope. 13.01 GB store moved, Ollama restarted, all five old models verified present.
- C: reclaimed from 2.3 GB free to 25.99 GB: pip/uv caches purged, temp cleared, 3.89 GB of runaway iCloud logs deleted, `AMD\PPC\sdkusage.csv` (0.57 GB) deleted.
- Rename of `.venv` to `.venv-win` failed: iCloud sync agent holds the directory. PC keeps `.venv`; Mac will use `.venv-mac`.

**Next**
- Brainstorm design with Superpowers, apply ponytail.

---

## 2026-09-21 01:56 — Design approved and committed (`d0d7151`)

**Changed**
- `git init`. `.gitignore` covers `.venv*/`, `data/`, fixtures. `.gitattributes` pins LF for PC/Mac.
- `CLAUDE.md` written: pace rule (one file per step, explain first, wait for ok), Superpowers + ponytail workflow, hard scraping limits, per-machine env notes, `--lang fr|en` default `en`.
- Brainstorming run through all four sections, each approved. Approach A chosen: stdlib-first, six modules (`cli` `config` `collect` `clean` `stats` `coach`), four deps (`scrapling[fetchers]` `numpy` `scipy` `scikit-learn`) plus `pytest`. No `typer` `httpx` `pandas` `statsmodels`.
- Design spec written to `docs/superpowers/specs/2026-09-21-vcoach-design.md`. Self-review fixed one contradiction (import direction).
- Commit `d0d7151` holds spec, rules, design, and the earlier draft plan `docs/superpowers/plans/001-v0.2-implementation-plan.md`, which is now superseded.

**Next**
- User reviews the design spec.
- On approval: `superpowers:writing-plans` produces the implementation plan; old draft plan gets deleted (ask first).
- Then Phase 0 remainder: Python deps into `.venv`, Ollama upgrade, `ollama pull qwen3:14b`.
- Then code, one file per step, TDD.

---

## 2026-09-21 20:54 — Pushed to GitHub

**Changed**
- Branch renamed `master` -> `main`. Remote `origin` = `https://github.com/MonsieurNikko/VLCoach.git`. Both commits pushed, `main` tracks `origin/main`.
- Git author identity passed per-commit so far. Set `git config --global user.name` and `user.email` on both machines.

**Next**
- User reviews design spec.
- `superpowers:writing-plans` on approval.
- README with bootstrap commands is required by spec §11/§12 — not written yet.

## 2026-09-22 13:50 — Agent tooling configured

**Changed**
- Claude Code: ECC `v2.2.1` installed globally with standard hooks.
- Codex: native `ecc@ecc` plugin installed and enabled from the official ECC marketplace.
- GitHub Copilot: added `.github/copilot-instructions.md` with VLCoach constraints and dynamic workflow guidance.

**Next**
- Restart Claude Code and run `/reload-plugins`, or start a new session.
- Use Codex through `npx -y @openai/codex` unless the CLI is added to the global npm path.

## 2026-09-22 14:39 — One canonical source per agent fact

**Changed**
- `AGENTS.md` committed and promoted to the single constitution: added a Canonical sources
  table (SPECIFICATION / ROADMAP / HISTORY / plans / specs) and restored the explicit
  `StealthyFetcher` ban.
- `.github/copilot-instructions.md` committed.
- `CLAUDE.md` reduced to a Claude Code adapter: Hard limits and the English rule removed,
  replaced by a read-`AGENTS.md`-first pointer. Pace, Workflow, Environment kept.

**Next**
- Copilot still carries its own copy of the invariants; add a generation step only if Copilot
  is actually used to write project code.
- `docs/MAP.md` once modules exist; a ROADMAP delete-zone once something is deliberately removed.
- Resume the real work: ROADMAP Task 4 onward, no project code written yet.
