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

---

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

## 2026-09-22 15:26 — Ponytail installed on the Mac, ladder made portable

**Changed**
- Installed `ponytail@ponytail` 4.10.0 at user scope on the Mac. It had only ever been
  installed on the PC; plugins live in `~/.claude`, so the clone carried nothing.
  Marketplace `DietrichGebert/ponytail` added (third non-official one).
- `AGENTS.md`: new Minimalism ladder section, so Codex, Copilot and Antigravity get the
  principles without the plugin. Recovered two rungs the old paraphrase had dropped —
  "does this need to exist at all" and "does this repository already have it" — plus the
  root-cause bugfix rule.
- `CLAUDE.md`: Ponytail paraphrase replaced by a pointer to that section, plus the
  Claude Code specifics (`/ponytail lite|full|ultra`, default `full`).

**Next**
- `/reload-plugins` or a new session: the six ponytail skills are not invocable in the
  session that installed them.
- Same two install commands on the PC are not needed — it already has 4.10.0.
- Resume ROADMAP Task 4 onward. Still no project code written.

## 2026-09-23 13:51 — feat/v0.2 merged into main, Mac environment built

**Changed**
- Merged `feat/v0.2` into `main` (`fb5256b`). `main` had only cherry-picked documentation;
  Tasks 1 and 2 lived on the branch and had never been ported. One conflict, `HISTORY.md`,
  resolved chronologically. Backup ref kept at `backup/main-before-merge`.
- `.venv-mac` created, Python 3.12.13, `uv pip install -e ".[dev]"`: numpy 2.5.3, scipy 1.18.1,
  scikit-learn 1.9.1, pytest 9.1.1, scrapling 0.4.15 at the pinned commit.
- `pytest -v`: **6 passed**. Wilson checked against Newcombe 1998.
- `SPECIFICATION.md`: CLI examples renamed `vcoach` -> `vlcoach`, matching the entry point.
- `CLAUDE.md`: the worktree rule is gone, the merge ended that convention. The iCloud warning
  stays for the PC; the Mac clone is outside iCloud, verified, so branch switching is safe there.
  Corrected the false claim that both venvs are iCloud-synced.

**Next**
- Task 3: `robust_z`, `ewma`, `bootstrap_diff`, TDD.
- 17 commits ahead of `origin/main`, nothing pushed. Confirm the PC is idle before pushing.
- Delete `origin/feat/v0.2` and the local backup ref once the push lands.

## 2026-09-23 13:53 — Task 3: stats per-match series

**Changed**
- `tests/test_stats.py`: 3 tests appended, RED confirmed (`AttributeError`, as the plan predicted).
- `vlcoach/stats.py`: `robust_z` (median/MAD, 0.67449 scaling, MAD=0 -> all None),
  `ewma` (a None carries the previous value), `bootstrap_diff` (2000 resamples, seed 42).
- Debugging: `ewma([3,3,3]) == [3,3,3]` failed. Root cause was the update form, not the test —
  `alpha*x + (1-alpha)*s` gives 3.0000000000000004 on a constant series. Replaced with the
  algebraically identical `s + alpha*(x - s)`, which is exact when `x == s`. Plan file synced.
- `pytest -v`: **9 passed**.

**Next**
- Task 4: `logistic` with `auc_std`, `categorical_used`, `MIN_CATEGORICAL_ROWS` gate.

## 2026-09-23 14:06 — Pace rule graduated by blast radius

**Changed**
- `CLAUDE.md` pace: approval moves from per-file to per-task, with the full diff and the
  `pytest` output shown before the gate. One task is one commit, so `git revert` is the recovery.
- Per-file approval kept where the blast radius is real: `collect.py`, the network, the hard
  limits, the other machine. Installs, downloads, deletions and moves still always wait.
- ROADMAP sub-step boxes are still ticked as they go, so progress stays visible between gates.
- Rationale: professional practice grades oversight by risk rather than applying maximum
  vigilance uniformly (arXiv 2512.14012). `AGENTS.md` unchanged — pace is harness-specific.

**Next**
- Task 4 under the new regime: `logistic` with `auc_std`, `categorical_used`, `MIN_CATEGORICAL_ROWS`.

## 2026-09-23 14:11 — Task 4: regularized logistic regression

**Changed**
- `tests/test_stats.py`: 3 tests appended (skip under 40 rows / single class, fit with signal
  and missing values, categoricals only at 100 rows). RED confirmed.
- `vlcoach/stats.py`: `logistic()` — sklearn pipeline (impute, scale, L2), stratified CV AUC
  with `auc_std`, one-hot map/agent gated at `MIN_CATEGORICAL_ROWS`, odds ratios per feature.
- Deviation from the plan: `penalty="l2"` raised 12 `FutureWarning`s — deprecated in sklearn 1.8,
  removed in 1.10, and we run 1.9.1. Replaced with the documented equivalent `l1_ratio=0`.
  Same regularization, no warnings, no breakage at the next minor. Plan file synced.
- `pytest -q`: **12 passed**, no warnings.

**Next**
- Task 5: `analyze()` assembles the analysis JSON.

## 2026-09-23 14:24 — stats.py rewritten for a junior reader

**Changed**
- `vlcoach/stats.py`: 108 -> 248 lines, behaviour identical. Every docstring now states the
  question the function answers, what it returns, and when it returns None. Single-letter names
  replaced (`w`/`l` -> `wins`/`losses`, `p` -> `observed_rate`, `rs` -> `scored_rows`).
  The bootstrap and the feature matrix are explicit loops instead of dense comprehensions.
- Comments explain decisions, not syntax: why median/MAD over mean/std, why the EWMA update is
  written as a step, why sklearn is imported inside the function, why 100 rows gate the one-hot.
- No logic touched. The 12 existing tests are the proof: **12 passed**, unchanged.
- Ponytail tension, noted on purpose: the file more than doubled. Every added line is a comment
  or a docstring, no logic was added, and the owner could not read his own statistics module.

**Next**
- Task 5: `analyze()` assembles the analysis JSON. Written in this style from the start.
