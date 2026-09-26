# vlcoach — "main weak point" analysis design

Date: 2026-09-26. Status: proposed, awaiting owner review.
Amends: `2026-09-21-vlcoach-design.md` (analysis contract §3, coach §6) and `SPECIFICATION.md` §7, §8.3, §10.

## 1. Goal

The report answers one question for the player: **"What is my main weak point right now, the one that makes me lose and keeps my rank stuck?"**

Today `stats.analyze()` returns many numbers but nothing ranks them. Per-map and per-agent win rates have no uncertainty range, there is no recent-versus-older view, and several personal stats are never analysed. This design adds the missing calculations, ranks candidate weak points, and saves everything in one versioned file the AI coach reads. It is done now, before `clean`, `coach` and `cli` exist (roadmap Tasks 6–9), so no written code has to be reworked.

## 2. Decisions

| Decision | Why |
|---|---|
| The player is compared **with themselves only**: wins against losses, recent against older. No lobby comparison, no rank benchmarks. | A human coach reads one player's own stats. A player whose hidden MMR is above their lobby does not need coaching; players ask for coaching when they are stuck. |
| The AI writes a general profile, then picks and explains the main issue, **only among candidates the code marked as real evidence**. | Keeps the AGENTS.md invariant that the coach phrases computed evidence and never invents a mistake. |
| The code also ranks candidates itself; `weak_points[0]` is its pick. | The no-AI fallback report must still name a main issue. |
| "Right now" = the last `RECENT_N = 20` matches, compared with the ones before. | Owner's choice. |
| Current map pool = maps seen in the last 20 matches. | Automatic; nobody edits a list each act. |
| Agent roles come from a fixed `ROLES` table in `config.py`. An agent missing from the table is `"unknown"`, never guessed. | Agents change rarely. The table is checked against the official Riot roster when written. |
| **TRS (Tracker Score)** is used as a general level and trend, **never** in the win/loss comparison or the ranking. | TRS is tracker.gg's per-match 0–1000 score; its formula is not public and community sources say it includes win %, so "TRS is higher in wins" proves nothing. |
| `rr_change` stays optional and is never required. "Stuck" is decided from win rate only. | tracker.gg shows TRS, not RR, per match (owner's observation; no source found showing RR). |
| Every personal stat gets the full treatment. | Owner: "do not neglect all personal performance". |
| The local AI does not learn between runs. It reads the results file fresh on each run. | So the file must carry every result the AI needs. |

## 3. Report — `data/analysis/<stem>_coach.md`

Replaces the five sections of `SPECIFICATION.md` §8.3.

1. **Your profile.** Win rate overall and in the last 20 games, stuck or not, TRS level and trend, best and worst maps, agents and roles in the current pool. Each number comes with its range.
2. **Your main issue.** The one candidate most tied to your losses, with its numbers. Example: "opening balance +0.8 in wins, −2.1 in losses, worse in the last 20 games: you die first too often."
3. **Why it keeps your rank stuck.** How it shows in your losses and whether it is getting worse.
4. **What is probably noise.** Stats that look bad but could be luck, so you do not chase them.
5. **Plan for the next 10–20 games.** One habit to change and the number to watch to see if it works.

AI rule: the main issue must be a `weak_points` entry. The fallback report uses `weak_points[0]`.

## 4. Calculations

Every calculation reuses a function already in `vlcoach/stats.py` or a `scipy` function (`scipy` is already a dependency). No new dependency.

### 4.1 Recent against older, and "stuck"

- Win rate for the last 20 matches and for the older ones, each with `wilson()`.
- **Stuck rule**: when the recent win-rate range contains 50%, the player wins as much as they lose, so they sit at their current level. Climbing needs more than 50%; the main issue is what stands in the way.
- Every personal stat: recent against older with `bootstrap_diff()`.

### 4.2 Personal stats — all of them

Stats: kills, deaths, assists, plus_minus, kd, acs, adr, dd_delta, hs_pct, kast_pct, fk, fd, opening_balance, mk, acs_rank_in_team, trs, **plus per-round rates** (4.3).

For each stat:
- typical level (`_median`) and usual swing (`_mad`). Reported, not ranked: no invented "unstable" threshold;
- recent against older (4.1);
- wins against losses: `bootstrap_diff()`, Cliff's delta and "how sure" (4.4), existing `signal` rule — **except TRS**;
- conditional win rate (4.4);
- trend over time (4.5).

### 4.3 Per-round rates and opening duels

- Rounds played = `score_a + score_b`. Kills, deaths, assists, first kills, first deaths and multikills are divided by rounds, so a 13–11 game and a 13–3 game compare fairly.
- **Opening duel win rate** = first kills ÷ (first kills + first deaths), pooled over matches, with `wilson()`. Example: "you win 41% of your opening duels, likely 35–47%".

### 4.4 Stronger evidence that a stat is tied to losses

- **Conditional win rate**: win rate in matches where the stat is better than your own median against matches where it is worse, each with `wilson()`; the gap with `bootstrap_diff()` on 0/1 results. Example: "when you die first less than usual you win 58%; when more, 37%."
- **Cliff's delta**: share of win/loss pairs in which the stat is better in the win, rescaled to −1…+1, computed from `scipy.stats.mannwhitneyu` as δ = 2U / (n₁n₂) − 1, together with its p-value. Unit-free, so all stats rank fairly.
- **How sure**: the share of `bootstrap_diff` redraws that fall on the bad side. Example: "94% sure your ADR really drops in losses". `bootstrap_diff` returns it as a new key.
- **Benjamini–Hochberg** false-discovery control over all comparisons: stats, maps, agents, roles, tilt and sessions. It replaces the rough "expect 1 false positive in 20"; `comparisons` keeps the count and adds how many survive.

### 4.5 Progress

- Per stat: **Theil–Sen slope** over match order (`scipy.stats.theilslopes`), a robust trend line. **Mann–Kendall** trend test (`scipy.stats.kendalltau` against the match index): is the trend real? Example: "ADR +4 per 10 games, a real upward trend".
- **Rolling win rate**: `ewma()` on 0/1 results.

### 4.6 Close games against stomps

- Round win % (rounds won ÷ rounds played) with `wilson()`.
- Share of losses by `CLOSE_MARGIN = 2` rounds or fewer. Many close losses point to closing out games; many stomps point to fundamentals.
- Descriptive (profile), not ranked.

### 4.7 Tilt and sessions

- **Tilt**: win rate after a loss against after a win, and after 2 or more losses in a row, with `bootstrap_diff()` on 0/1 results.
- **Sessions**: matches less than `SESSION_GAP_HOURS = 2` apart form one sitting. Win rate and ACS for games 1–2 against game 3 and later.
- Needs match **times**. Task 10 checks whether the page gives times; with dates only, `sessions` is `skipped` with a reason, and tilt still works from match order.
- Meaningful from about 50 matches. Below that the block is marked insufficient, never guessed.

### 4.8 Map pool, agents, roles

Per map (current pool only), per agent, per role: games, wins, raw rate, Wilson range (new), shrunk rate (`shrink()`). A group is weak only when its whole Wilson range lies below the overall win rate.

### 4.9 Ranking — `weak_points`

- Candidates: personal stats including per-round rates (not TRS), weak maps, agents and roles, tilt, session fatigue.
- A candidate counts only if it survives Benjamini–Hochberg, points in the bad direction, and — for stats — its win/loss gap exceeds one MAD (existing `signal` rule).
- Bad direction comes from a new `BETTER` table: higher is better except deaths, first deaths, their per-round rates, and `acs_rank_in_team` (1 = top of the team).
- Strength = |Cliff's delta| (for maps, agents, roles, tilt and sessions: the size of the win-rate gap). Tie-break: a worsening trend (Mann–Kendall significant, bad direction).
- `weak_points[0]` is the code's pick. An empty list is a valid answer: "no weak point stands out from luck yet — play more games".

### 4.10 Folded-in review fixes

- `bootstrap_diff` needs at least `MIN_PER_SIDE = 5` matches on each side. With 2 values, only 3 distinct resampled means exist, which fakes precision.
- `logistic` no longer rescales one-hot map/agent columns.
- `logistic` no longer reports a fake odds ratio of 1.0 for empty or constant features.

### 4.11 Left out

Lobby comparison, rank benchmarks, act or patch splits (no data), per-map combat stats, per-run history copies.

## 5. Saved results — `data/analysis/<stem>.json`

One file per player. Written by `cli.py` (Task 9), read by `coach` and nothing else, overwritten on each run.

| Block | Content |
|---|---|
| `meta` | `version: 1`, generation date, number of matches, `recent_n` |
| `quality` | discovered, parsed, with result, completeness (unchanged) |
| `profile` | win rate overall, recent and older with ranges; `stuck` |
| `personal` | per stat, including per-round rates: median, mad, recent_vs_older, win_vs_loss (diff, ci, cliffs_delta, p, bh_significant, how_sure, signal), conditional win rate, trend (slope, mann_kendall) |
| `opening_duels` | fk, fd, win rate with range |
| `games` | round win % with range, close-loss share, rolling win rate |
| `tilt` | win rate after a loss, after a win, after 2+ losses; gap and evidence |
| `sessions` | games 1–2 against 3+: win rate and ACS, or `skipped` with the reason |
| `pool` | maps (current pool), agents, roles: n, wins, raw, ci, shrunk, weak |
| `outliers` | robust z per match, with `match_id` and `timestamp` |
| `margins`, `model`, `comparisons`, `leakage_warning` | kept |
| `weak_points` | ranked candidates with their evidence; `[0]` is the code's pick |

Today's keys `form`, `win_vs_loss`, `by_map` and `by_agent` move into `personal` and `pool`. A new stat later adds one entry to `personal`; the shape stays. `meta.version` makes any future shape change visible instead of silent.

Pipeline unchanged: collect → clean → `stats.analyze()` → `cli.py` writes the JSON → `coach` reads it → `<stem>_coach.md`.

## 6. Build order

One step = one function or one small feature, then stop for "ok" (AGENTS.md Pace). Each step starts with a failing test.

1. `config.py`: `RECENT_N`, `MIN_PER_SIDE`, `CLOSE_MARGIN`, `SESSION_GAP_HOURS`, `ROLES`, `BETTER`, `PERSONAL_FIELDS`.
2. `bootstrap_diff`: minimum per side, and return "how sure".
3. `logistic`: one-hot scaling and odds-ratio guard.
4. New formula functions, one per step: `per_round`, `opening_duels`, `cliffs_delta`, `conditional_winrate`, `trend`, `bh_adjust`.
5. Helpers: split recent and older; split into sessions.
6. Blocks, one per step: `profile`, `personal`, `games`, `tilt`, `sessions`, `pool`, `outliers`.
7. `weak_points` ranking.
8. `analyze()` returns contract v1.
9. Documents: `SPECIFICATION.md` §7, §8.3, §10; dated amendment in the 2026-09-21 design; plan Tasks 7–9; `ROADMAP.md`.

Then roadmap Tasks 6–12 resume (clean, coach fallback with the new sections, Ollama guardrails, cli, collect, verification).

Every new or changed function gets a plain-first docstring (AGENTS.md, Explaining code). The pending docstring rewrites for `logistic`, `analyze`, its helpers and `config.py` happen in the steps that touch them.

## 7. Verification

- `pytest -q` after every step.
- Each formula checked against a hand-computed or `scipy` reference: Cliff's delta on two tiny lists, Benjamini–Hochberg on a textbook p-value list, Theil–Sen on a straight line returns its slope.
- Planted weakness: synthetic matches where first deaths are high only in losses → `weak_points[0]` is `fd` (or its per-round rate, or opening balance) with real evidence. A dataset without any real gap → no stat candidate.
- Planted tilt: synthetic history where wins after a loss are rare → `tilt` flagged. Dates-only timestamps → `sessions` skipped with a reason.
- TRS never appears as a candidate. A missing `rr_change` never breaks anything.
- Contract: `analyze()` output has every v1 block, `meta.version == 1`, and passes `json.dumps`.
