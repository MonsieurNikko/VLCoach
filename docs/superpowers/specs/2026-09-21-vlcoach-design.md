# vlcoach — technical design

Date: 2026-09-21
Requirements: `SPECIFICATION.md` (v0.2). This document is the technical design that satisfies it.
Status: approved section by section in brainstorming; implementation plan follows.

## 1. Decisions that shape everything

**Collection is a live Scrapling crawl of Tracker.gg.** `https://tracker.gg/robots.txt` disallows `/*/profile/*` and `/*/matches/*` for all user agents, and spec §5.3 itself states Tracker Network does not permit scraping. The user was shown this and chose to proceed. The build stays inside the spec's own limits: `DynamicFetcher` on real Playwright Chromium only, no stealth, no proxies, no CAPTCHA handling, no fingerprint spoofing, no internal API calls, fail closed on any block. The README says plainly that the tool requests disallowed paths and is meant for the operator's own profile.

**Local model is `qwen3:14b`.** 9.3 GB, 40K context, verified on the Ollama registry. Fits the machine's real 12 GB VRAM fully on-GPU. Chosen for thinking mode (the model's only input is a nested analysis JSON), for French and English, and for instruction following. `phi4:14b` is English-centric; `gemma3:12b` is weaker on structured numeric input; 24B-class models need ~14 GB and would force CPU offload. One model, measured once, documented in the README — the user declined a three-way benchmark.

**Stdlib first, six modules, four dependencies.** `scrapling[fetchers]`, `numpy`, `scipy`, `scikit-learn` (the last three are one install), plus `pytest` for tests. `argparse`, `urllib.request`, `csv`, `json` cover the rest. No `typer`, `httpx`, `pandas`, `statsmodels`: each would do in one line what stdlib does in three, at the cost of a dependency in a venv that iCloud syncs.

**Report language is a flag.** `--lang fr|en`, default `en`. Code, comments, commits and docs are English.

**Build order is deterministic-core-first.** Stats, cleaning and coaching are built against fixtures before the scraper is wired in. The scraper is the only component whose success depends on a third party, so a block or DOM change can never leave the project with nothing working.

## 2. Modules

```
vlcoach/
  cli.py       argparse. Subcommands run|collect|analyze|coach. Flags --matches --model --headed --lang.
               Calls the other modules in order. No logic of its own.
  config.py    Constants only: K=10, ALPHA=0.20, N_BOOT=2000, SEED=42, OLLAMA_URL,
               AUTO_MODEL="qwen3:14b", DATA_DIR. FIELDS: the one table of
               field name -> (type, min, max) from spec §4. riot_id(): parses
               "Name#TAG" -> (name, tag, url_path, file_stem).
  collect.py   parse_profile(html) -> list of match URLs.
               parse_match(html, riot_id) -> dict of raw string values for that player's row.
               fetch_all(riot_id, n, headed) -> uses DynamicFetcher, calls the two parsers,
               writes data/raw/<stem>.json + one .html snapshot per page before parsing.
               Two exceptions: BlockedError (halt) and ParseError (log, continue).
  clean.py     clean(raw_rows) -> list of dicts typed per FIELDS, implausible -> None,
               dedup on match_id, derived columns. Writes data/clean/<stem>.csv.
               quality(rows) -> the §6.3 completeness block.
  stats.py     wilson, jeffreys, shrink, robust_z, ewma, bootstrap_diff, logistic.
               analyze(rows) -> dict with all results + quality + leakage warning.
               Writes data/analysis/<stem>.json.
  coach.py     ask_ollama(analysis, model, lang) -> markdown or None on any failure.
               fallback(analysis, lang) -> markdown from templates.
               Both produce the five §8.3 sections. Writes data/analysis/<stem>_coach.md.
```

Dependencies point strictly downward: `config` imports nothing from the package; `collect`, `clean`, `stats` and `coach` import only `config`; `cli` imports all of them. No module imports a sibling. `collect` is the only module that touches the network. Changing the scraping strategy means editing `collect.py` and nothing else — that module boundary is the interface spec §5.2.5 asks for. There is no `Protocol` class because there is only one live implementation; the snapshot path in tests calls the same `parse_*` functions on a file's contents.

`config.FIELDS` is the single source of truth for field names, types and plausibility bounds. `clean`, the CSV writer, `quality` and the logistic feature list all read from it, so they cannot drift apart.

## 3. Data flow

```
"Name#TAG"
   | config.riot_id()
   v
collect.fetch_all --> data/raw/<stem>.json        list of {url, match_id, fields: {str: str}, error: str|None}
                  --> data/raw/<stem>/*.html      one snapshot per page, written BEFORE parse
   |
   v
clean.clean       --> data/clean/<stem>.csv       one row per match, typed, None for missing/implausible
   |
   v
stats.analyze     --> data/analysis/<stem>.json
   |
   v
coach.ask_ollama  --> data/analysis/<stem>_coach.md
   +- None --> coach.fallback --> same file
```

Each stage reads only the previous stage's file, so `vlcoach analyze` and `vlcoach coach` rerun without re-scraping. Raw JSON keeps every value as the string the page showed; cleaning is the only place typing happens. A parser change never needs a re-crawl and a cleaning bug never needs a re-parse.

Analysis JSON shape, fixed because both `coach.py` paths read it:

```
quality:         {discovered, with_result, completeness: {field: pct}}
winrate:         {n, wins, p, wilson: [lo, hi], jeffreys: {mean, ci: [lo, hi]}}
by_map/by_agent: {name: {n, wins, raw, shrunk}}
form:            {field: {ewma: [...], last: x}}       ACS, ADR, KAST, DD-delta
outliers:        {field: {z: [...]}}                   same fields, robust z per match
win_vs_loss:     {field: {diff, ci: [lo, hi], uncertain: bool}}
model:           {skipped: reason|None, auc, odds_ratios: {feature: x}}
leakage_warning: "<spec §7.7 text>"
```

## 4. Statistical methods

| Spec | Function | Implementation |
|---|---|---|
| 7.1 | `wilson(w, n)` | closed form; tested against literature values |
| 7.2 | `jeffreys(w, l)` | `scipy.stats.beta(w+0.5, l+0.5)` -> mean, ppf(0.025), ppf(0.975) |
| 7.3 | `shrink(wins_g, n_g, p_global, k=K)` | `(wins_g + k*p_global)/(n_g + k)`; caller reports raw and shrunk |
| 7.4 | `robust_z(xs)` | `scipy.stats.median_abs_deviation`; `0.67449*(x-med)/MAD`; MAD==0 -> None |
| 7.5 | `ewma(xs, alpha=ALPHA)` | three-line loop |
| 7.6 | `bootstrap_diff(win_vals, loss_vals)` | `numpy.random.default_rng(SEED)`, N_BOOT resamples, percentiles 2.5/97.5 |
| 7.7 | `logistic(rows)` | sklearn `Pipeline`: `SimpleImputer` + `StandardScaler` on continuous, `OneHotEncoder(handle_unknown="ignore")` on map/agent, `LogisticRegression(penalty="l2")`; `StratifiedKFold` + `cross_val_score(scoring="roc_auc")` |

Continuous features for 7.7: DD-delta, KAST%, ACS, opening balance, HS%. Categorical: map, agent. Minimum 40 rows with a parsed result and both classes present; otherwise `skipped` with the reason.

## 5. Error handling

Two exception classes, both in `collect.py`.

`BlockedError` — Cloudflare challenge, 403, 429, or login wall. `fetch_all` stops at once, writes the raw JSON it has, exits with a message naming the cause. No retry, no backoff escalation, no automatic `--headed` fallback; the user chooses `--headed` (spec §9), and if headed is also blocked that is the answer.

`ParseError` — `parse_profile` or `parse_match` cannot find what it expects. `fetch_all` catches per match, records `{url, error}` in the raw JSON, continues (spec §5.3). The snapshot is already on disk, so the failure is debuggable offline.

Downstream is None-tolerant instead of raising:

- `clean`: a value that fails type or bounds becomes `None`. Never fabricated, never inferred.
- `stats`: every function accepts `None`s. Under 40 rows with a result, or one class only -> `model.skipped`. `MAD == 0` -> z is `None`. Empty group -> skipped, not a division error.
- `coach.ask_ollama`: connection refused, timeout, missing model, HTTP error, or a response missing a section -> `None`; caller falls through to `fallback`. Nothing about Ollama can crash the run.

`collect` ends by reporting, per §5.3: matches discovered, parsed, failed with each reason, and when discovered is 0 a one-line hint that the profile may be private or the layout changed, with the snapshot path.

## 6. Coaching output

Both `ask_ollama` and `fallback` produce exactly these five headings, in the chosen language, in this order (spec §8.3):

1. What the data actually says
2. What is probably noise / uncertain
3. Three coaching priorities
4. Next 10-game experiment
5. What extra data would unlock better coaching

The system prompt carries the §8.4 guardrails verbatim and the §7.7 leakage warning. The model receives the analysis JSON and nothing else. Thinking mode stays on; there is no fast-path flag until latency is measured to be a problem.

The fallback renders each heading from the analysis JSON with fixed templates: interval widths and sample counts drive the wording ("n=4 — too few games to say"), `uncertain: true` signals are listed under noise, and the experiment is always "play 10 more competitive games, same agent pool, rerun".

## 7. Testing

One test file per module, one test per spec-named behaviour, written RED first.

```
tests/
  test_stats.py     Wilson vs literature values. Jeffreys 0/0 does not crash.
                    shrink(3-0) < shrink(55-45). robust_z MAD=0 -> None. ewma(constant) = constant.
                    bootstrap_diff(identical groups) -> uncertain=True.
                    logistic(39 rows) -> skipped. logistic(all wins) -> skipped.
                    every function with None-riddled input -> no exception.
  test_clean.py     "23.4%" -> 23.4. HS%=140 -> None. duplicate match_id -> one row.
                    kills=7, deaths=0 -> computed K/D None, scraped K/D kept.
                    result missing -> stays None.
  test_collect.py   parse_profile(fixture) -> expected URLs. parse_match(fixture) -> expected dict.
                    parse_match(damaged fixture) -> ParseError. No network.
  test_coach.py     fallback contains all five headings in en and fr.
                    ask_ollama against a dead port -> None.
```

Fixtures are real page snapshots captured once by hand, git-ignored. `fetch_all` is covered by the end-to-end run against the real site, not by unit tests.

## 8. Environment facts that constrain the design

- GPU: RTX 4070 SUPER, 12282 MiB. Model budget is 12 GB.
- Project root is an iCloud Drive sync root shared between a Windows PC and a Mac. `.venv` (PC) and `.venv-mac` (Mac) are both git-ignored; each machine uses only its own. `.git` is inside iCloud: commit and push from one machine at a time.
- `PLAYWRIGHT_BROWSERS_PATH` and `OLLAMA_MODELS` are per-machine user env vars. On the PC both point to D:, because C: had 2.3 GB free before reclaim.
- Ollama is 0.5.7 and must be upgraded before `qwen3:14b` will load.

## 9. Addendum 2026-09-21 — statistics and coaching review

Agreed additions after review. None changes the methods in §4; they add context and honesty around them.

- **Multiple comparisons.** `analyze()` counts every interval it reports and exposes `comparisons: {n, expected_false_positives: n/20}`. A win-vs-loss entry is `signal: true` only when its CI is clear of zero **and** `|diff|` exceeds one MAD of that metric across all matches. The fallback and the prompt both use `signal`, not `uncertain`, to name priorities.
- **Model honesty.** `logistic()` returns `auc_std` across folds. Map and agent one-hot columns enter the model only when there are at least 100 rows with a result (`MIN_CATEGORICAL_ROWS`); below that only the five continuous features are used. The result carries `categorical_used: bool`.
- **Round margin.** `clean()` derives `round_diff = score_a - score_b`. `analyze()` reports the median margin in losses and in wins under `margins`. A player who loses 13-11 and one who loses 13-3 need different coaching.
- **Consistency.** `form[field]` carries `mad`, the MAD already computed for the robust z, as a plain consistency number.
- **Team context.** `parse_match` reads the player's whole team block, not one row, and derives `acs_rank_in_team` (1 = top ACS on the team, 5 = bottom). It is a `FIELDS` entry bounded to [1, 5] and joins the win-vs-loss comparisons.
- **Rank context.** `rr_change` (int, unbounded) is a `FIELDS` entry and `lobby_rank` (string label) a `CONTEXT` entry. Both are optional: the parser records them only when the page shows them; the cleaner never invents them.
- **Wider comparisons.** `DIFF_FIELDS` = `acs, adr, kast_pct, dd_delta, hs_pct, opening_balance, mk, kd, acs_rank_in_team`.
