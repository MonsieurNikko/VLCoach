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

---

## 2026-09-21 23:40 — Task 1: skeleton, config, dependencies

**Changed**
- Branch `feat/v0.2` created off `main`.
- Design doc renamed to `2026-09-21-vlcoach-design.md`, `vcoach` -> `vlcoach` everywhere, addendum §9 added (stats/coaching review). Old draft plan removed. `ROADMAP.md` added with a `CLAUDE.md` rule to tick it.
- `pyproject.toml`: package `vlcoach`, entry point `vlcoach = vlcoach.cli:main`, Scrapling pinned to git commit `2b160ee`.
- Installed into `.venv`: numpy 2.5.3, scipy 1.18.1, scikit-learn 1.9.1, pytest 9.1.1.
- `vlcoach/config.py`: all constants, `FIELDS` bounds table (16 fields incl. `acs_rank_in_team`, `rr_change`), `CONTEXT`, `DIFF_FIELDS`, `riot_id()`.
- `tests/test_config.py`: 3 tests, RED then GREEN.

**Next**
- Task 2: `stats.py` — Wilson, Jeffreys, shrinkage, TDD.

---

## 2026-09-22 00:54 — Task 2: stats proportions

**Changed**
- `vlcoach/stats.py`: `wilson` (closed form), `jeffreys` (scipy Beta), `shrink` (pseudo-count, k=10). `LEAKAGE_WARNING` constant.
- `tests/test_stats.py`: 3 tests. Wilson checked against Newcombe 1998 values.
- Debugging: first shrink assertion was wrong — it demanded 3-0 rank below 55-45, but spec §7.3 only demands 3-0 not be reported as 100%. Root-caused via systematic-debugging, test corrected to pin the formula value (8/13) and the displacement inequality. Plan file synced.

**Next**
- Task 3: `robust_z`, `ewma`, `bootstrap_diff`.

---

## 2026-09-22 01:09 — README, logo, and an iCloud incident

**Changed**
- `README.md` written: badges, mermaid pipeline, methods table, collapsible setup, access notice, status. Pushed to `main` and `feat/v0.2`.
- `assets/logo.svg`: first a card-style logo, then replaced by a minimal wordmark at the user's request (`vl` red, `coach` gray, transparent).
- Incident: `git checkout main` inside the iCloud folder died with `fatal: unable to write new index file` mid-switch. HEAD stayed on `feat/v0.2`, working tree was half `main`. Nothing lost — the commit was already pushed. Recovered with `git checkout -- .` after the lock cleared.
- Fix: `main` now lives in a git worktree at `D:\vlcoach-main`. This folder never switches branches again. Rule added to `CLAUDE.md`.

**Next**
- Delete two stray files left by the failed checkout (untracked, asked user).
- Task 3: `robust_z`, `ewma`, `bootstrap_diff`.
