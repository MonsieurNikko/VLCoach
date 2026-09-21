# Roadmap — vlcoach v0.2

Checklist view of `docs/superpowers/plans/2026-09-21-vlcoach-v0.2.md`. Tick as you go. Details, code and commands live in the plan.

Legend: `[ ]` todo · `[x]` done · `[~]` in progress

---

## Phase 0 — Environment

- [x] Superpowers plugin installed and verified (6.3.0)
- [x] Ponytail plugin installed (4.10.0)
- [x] `.venv` created, Python 3.13.2
- [x] Scrapling 0.4.15 installed from pinned git commit
- [x] Playwright browsers on `D:\playwright`, `PLAYWRIGHT_BROWSERS_PATH` set
- [x] Ollama store on `D:\ollama\models`, `OLLAMA_MODELS` set, five old models verified
- [x] C: reclaimed 2.3 → 26 GB
- [x] `git init`, `.gitignore`, `.gitattributes` (LF), pushed to `MonsieurNikko/VLCoach`
- [x] `CLAUDE.md` agent rules, `HISTORY.md` log
- [x] Design spec written, reviewed, approved, committed
- [x] Implementation plan written, approved, committed
- [ ] Ollama upgraded ≥ 0.6.6 → Task 11
- [ ] `qwen3:14b` pulled → Task 11

## Task 1 — Skeleton, config, dependencies

- [x] `git mv` design doc to `2026-09-21-vlcoach-design.md`; rename `vcoach` → `vlcoach` in it and in `CLAUDE.md`
- [x] Append addendum §9 (statistics review) to design doc
- [x] `git rm docs/superpowers/plans/001-v0.2-implementation-plan.md`
- [x] `pyproject.toml`
- [x] `uv pip install -e ".[dev]"` — numpy, scipy, scikit-learn, pytest
- [x] `tests/test_config.py` — RED
- [x] `vlcoach/__init__.py`, `vlcoach/config.py` — GREEN
- [x] `HISTORY.md` entry, commit

## Task 2 — stats: proportions

- [x] `tests/test_stats.py` — Wilson vs literature, Jeffreys extremes, shrink inequality — RED
- [x] `vlcoach/stats.py` — `wilson`, `jeffreys`, `shrink` — GREEN
- [x] `HISTORY.md` entry, commit

## Task 3 — stats: per-match series

- [ ] Tests — robust_z None/MAD=0, ewma constant/gaps, bootstrap identical/separated — RED
- [ ] `robust_z`, `ewma`, `bootstrap_diff` — GREEN
- [ ] `HISTORY.md` entry, commit

## Task 4 — stats: logistic regression

- [ ] Tests — skipped <40, skipped one class, fits with signal, categoricals only at 100 — RED
- [ ] `logistic` with `auc_std`, `categorical_used`, `MIN_CATEGORICAL_ROWS` gate — GREEN
- [ ] `HISTORY.md` entry, commit

## Task 5 — stats: analyze()

- [ ] Tests — shape, small sample, signal needs CI and MAD, margins, empty rows — RED
- [ ] `analyze` with `signal`, `comparisons`, `margins`, `form[*].mad` — GREEN
- [ ] `HISTORY.md` entry, commit

## Task 6 — clean

- [ ] `tests/test_clean.py` — percent/bounds, dedup, result never inferred, derived+sorted, quality — RED
- [ ] `vlcoach/clean.py` — `clean` (incl. `round_diff`, `acs_rank_in_team`, `rr_change`), `quality` — GREEN
- [ ] `HISTORY.md` entry, commit

## Task 7 — coach: fallback

- [ ] `tests/test_coach.py` — five headings en/fr, small sample wording, empty analysis — RED
- [ ] `vlcoach/coach.py` — `HEADINGS`, templates, `fallback` using `signal`, margins, consistency, team rank, comparisons — GREEN
- [ ] `HISTORY.md` entry, commit

## Task 8 — coach: Ollama client

- [ ] Test — dead port returns None — RED
- [ ] `GUARDRAILS`, `ask_ollama` — GREEN
- [ ] `HISTORY.md` entry, commit

## Task 9 — cli: offline pipeline

- [ ] `vlcoach/cli.py` — `paths`, `analyze`, `coach`, `collect` stub, `main`
- [ ] `vlcoach --help` resolves
- [ ] Synthetic `data/raw/Demo_TAG.json`, run `analyze` then `coach --lang fr` → fallback file with five headings
- [ ] `HISTORY.md` entry, commit

## Task 10 — collect: the only network task

- [ ] Capture `tests/fixtures/profile.html` and `match.html` from own profile (ask first); make `damaged.html`
- [ ] Inspect fixtures, fill `SELECTORS` (cells, team block, map/agent/result/scores/timestamp, optional RR/lobby rank)
- [ ] `tests/test_collect.py` — structural tests, no network — RED
- [ ] `vlcoach/collect.py` — `BlockedError`, `ParseError`, `parse_profile`, `parse_match` with team rank, `fetch_all` — GREEN
- [ ] Live run `vlcoach collect "Name#TAG" --matches 10` (ask first), then `analyze`, `coach`
- [ ] `HISTORY.md` entry, commit

## Task 11 — Ollama, model, README

- [ ] `winget upgrade Ollama.Ollama`, verify ≥ 0.6.6 and five models still listed (ask first)
- [ ] `ollama pull qwen3:14b` (ask first, 9.3 GB to D:)
- [ ] Measure: quantization, VRAM 100% GPU, wall time, headings kept
- [ ] `README.md` — access notice, Windows + Mac setup, usage, measured model table, methods
- [ ] `HISTORY.md` entry, commit

## Task 12 — Verification (spec §12)

- [ ] `pytest -v` all green, ≥ 22 tests
- [ ] `vlcoach --help`
- [ ] Small-sample run: wide interval, model skipped, no confident wording
- [ ] Ollama stopped → fallback file produced
- [ ] Ollama running → `ollama ->`, five headings, no invented claims
- [ ] Full `vlcoach run` → four artifacts, or clean `BlockedError` exit
- [ ] `grep -rn "StealthyFetcher\|proxy" vlcoach/` → nothing
- [ ] README measured cells filled
- [ ] Final `HISTORY.md` entry, commit, push

---

## After v0.2 (not planned, spec §3.3 / §13)

- Round-level data source (attack/defense, economy, trades, clutch) — only if a lawful source exists
- Mixed-effects / WPA — only once round-level data exists
