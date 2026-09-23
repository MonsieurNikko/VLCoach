# Valorant Statistical Coach — Product & Technical Specification

## 1. Purpose

Build a terminal-first program that turns a player's public Valorant Tracker history into evidence-based coaching.

The pipeline must:

1. collect public match data from rendered Tracker.gg pages;
2. preserve raw evidence before transformation;
3. clean and validate the scraped values;
4. calculate statistically defensible summaries and uncertainty;
5. detect patterns associated with wins/losses without claiming causality;
6. send only the calculated evidence to a local AI model;
7. produce a concise coaching report with actionable experiments.

The first release is a personal analytics tool, not a universal player ranking system.

---

## 2. Core principle

The system must not reduce performance to a homemade weighted score such as:

`0.4 * K/D + 0.3 * ACS + 0.3 * win rate`.

Such weights are arbitrary and hide uncertainty. Instead, each statistical method answers a specific question.

| Question | Method |
|---|---|
| How uncertain is my win rate? | Wilson 95% interval + Jeffreys Beta posterior |
| Is a high map/agent win rate based on enough games? | Empirical-Bayes shrinkage toward the player's overall baseline |
| Am I improving recently? | Exponentially Weighted Moving Average (EWMA) |
| Was a recent performance unusually high/low for me? | Median/MAD robust z-score |
| Which match metrics differ between wins and losses? | Match-level bootstrap confidence intervals |
| Which combination of variables is associated with winning? | Regularized logistic regression + cross-validation |
| Can the result be interpreted as causal? | No; the report must explicitly distinguish association from causation |

---

## 3. Scope

### 3.1 Included in v0.2

- Public Tracker.gg profile input via `RiotName#TAG`.
- Competitive match discovery from the rendered public profile page.
- Public match page collection using Scrapling (`D4Vinci/Scrapling` — https://github.com/D4Vinci/Scrapling).
- The coding agent must evaluate the available Scrapling approaches and select the most appropriate collection/parsing strategy for the actual Tracker.gg pages encountered during implementation.
- No private API key required.
- Raw JSON archive for reproducibility/debugging.
- Clean per-match CSV.
- Analysis JSON containing statistical results and uncertainty.
- Local AI coaching through Ollama.
- Deterministic non-AI fallback report if Ollama is unavailable.
- CLI commands for collection, analysis, coaching, and the full pipeline.

### 3.2 Explicitly excluded from v0.2

- Tracker Network undocumented/internal API calls.
- CAPTCHA solving, proxy rotation, fingerprint spoofing, rate-limit evasion, or other attempts to bypass access controls.
- Capturing/replaying Tracker Network internal XHR/API endpoints.
- Private Tracker profiles.
- Real per-action Win Probability Added (WPA), because this requires reliable round-event/state data.
- Claims that a correlation causes wins.
- Automated in-game actions.

### 3.3 Phase 2 target

If reliable round-level data can be collected lawfully from public/authorized sources, add:

- attack vs defense split;
- economy state;
- first-kill/first-death timing;
- trade windows;
- 5v4 / 4v5 conversion;
- plant/retake state;
- clutch state;
- survival after advantage;
- round-level mixed-effects/logistic model;
- estimated Win Probability Added.

---

## 4. Data model

One cleaned row represents one competitive match for the target player.

### 4.1 Identity and context

- `match_id`
- `url`
- `timestamp`
- `map`
- `agent`
- `result` (`win`, `loss`, `draw`, or missing)
- `score_a`, `score_b` when safely parsed

### 4.2 Combat metrics

- TRS
- ACS
- kills
- deaths
- assists
- +/-
- K/D
- damage delta per round (DDΔ)
- ADR
- HS%
- KAST%
- first kills (FK)
- first deaths (FD)
- multikills (MK)

### 4.3 Derived metrics

- computed K/D from kills and deaths (validation field)
- opening balance = `FK - FD`
- binary win target

Missing values remain missing. The cleaner must never fabricate unavailable values.

---

## 5. Collection design

### 5.1 Input

`RiotName#TAG`

### 5.2 Scrapling collection strategy

The required scraping framework is the official GitHub project **`D4Vinci/Scrapling`**: https://github.com/D4Vinci/Scrapling

`D4Vinci/Scrapling` must be installed and used as the primary scraping framework. The specification intentionally does **not** prescribe a specific Scrapling fetcher, session type, selector strategy, browser mode, or parsing technique.

The coding agent is responsible for inspecting the current Tracker.gg public pages, evaluating the available Scrapling capabilities, and selecting the most appropriate approach for the data that actually needs to be collected. The choice must be justified by reliability, maintainability, testability, and the observed behavior of the target pages rather than by a hard-coded architectural preference in this specification.

The implementation must still:

1. collect only the public data required by this specification;
2. preserve raw evidence/snapshots needed for debugging and parser updates;
3. avoid undocumented/internal Tracker Network API calls;
4. stop cleanly if automated access is blocked rather than attempting to bypass access controls;
5. keep collection logic isolated behind a clear interface so the scraping strategy can be changed without rewriting the cleaning, statistical, or coaching layers.

The exact Scrapling components and scraping technique are therefore an implementation decision for the coding agent.

### 5.3 Failure behavior

The scraper must return partial results rather than discard the entire run when one match fails.

Tracker Network has publicly stated that scraping its websites is not allowed. The implementation must therefore fail closed on an automated-access block and must not add stealth/proxy/challenge-bypass logic.

It must report:

- private/empty profile possibility;
- changed DOM possibility;
- per-match failure details;
- parsing completeness downstream.

---

## 6. Cleaning and validation

### 6.1 Rules

- deduplicate by `match_id`;
- convert numeric strings and percentages to numeric values;
- turn implausible values into missing values rather than silently trusting them;
- keep both scraped K/D and computed K/D when possible;
- never infer a result if the page does not provide enough evidence;
- preserve source URL for auditability.

### 6.2 Sanity examples

- HS% must be between 0 and 100;
- KAST% must be between 0 and 100;
- ADR/ACS must be non-negative and within generous upper safety bounds;
- kills/deaths/assists must be non-negative;
- duplicate match IDs are removed.

### 6.3 Data-quality report

Every analysis must expose:

- number of matches discovered;
- number with successfully parsed win/loss;
- completeness percentage for each main stat.

Coaching confidence must be conditioned on this information.

---

## 7. Statistical methods

## 7.1 Win-rate uncertainty — Wilson interval

For `w` wins out of `n` games, the raw estimate is:

`p = w / n`

A 95% Wilson score interval is used instead of the normal approximation because it behaves better for small samples and proportions near 0 or 1.

Purpose: prevent statements such as “75% win rate is excellent” when it comes from only four games.

## 7.2 Bayesian win-rate estimate — Jeffreys prior

Use:

`p ~ Beta(w + 0.5, losses + 0.5)`

Report:

- posterior mean;
- 95% credible interval.

The Jeffreys prior is deliberately weak and behaves sensibly at extreme observed values.

## 7.3 Map/agent small-sample correction — empirical Bayes shrinkage

For subgroup `g`:

`p_shrunk = (wins_g + k * p_global) / (n_g + k)`

where:

- `p_global` is the player's overall observed win rate;
- `k = 10` is the initial prior strength and is configurable in future versions.

Purpose: a 3-0 map should not be treated as stronger evidence than a 55-45 map merely because 100% > 55%.

The program reports both raw and shrunk values; it does not hide the original data.

## 7.4 Robust personal baseline — median/MAD z-score

Use:

`z_robust = 0.67449 * (x - median(x)) / MAD(x)`

where:

`MAD = median(|x - median(x)|)`

Purpose: quantify whether a match/recent period is unusual relative to the player's own history while resisting outlier games.

This is not a rank-percentile score.

## 7.5 Recent form — EWMA

Use:

`S_t = alpha * x_t + (1 - alpha) * S_(t-1)`

Default `alpha = 0.20`.

Purpose: follow gradual skill/form changes without treating a single recent game as the new true level.

## 7.6 Win/loss metric differences — cluster bootstrap

For each interpretable metric, compute:

`mean(metric | win) - mean(metric | loss)`

Then resample whole matches with replacement and recalculate the difference 2,000 times.

Report the 2.5th and 97.5th percentiles.

A signal whose interval crosses zero is presented as uncertain.

In v0.2, one row is one match, so the cluster is naturally the match. In the round-level version, all rounds from the same match must be resampled together to avoid pretending correlated rounds are independent.

## 7.7 Multivariable win association — regularized logistic regression

Target:

`Y = 1` for win, `0` for loss.

Candidate variables:

- DDΔ
- KAST%
- ACS
- opening balance (`FK-FD`)
- HS%
- map
- agent

Continuous variables are standardized. Map and agent are one-hot encoded. Missing values are imputed inside the modeling pipeline. Use L2 regularization to reduce instability caused by correlated features.

Minimum first-pass sample: 40 parsed win/loss matches with both classes.

Evaluate with stratified cross-validated ROC AUC when class counts permit.

Report coefficients/odds ratios as **associations**, not causal effects.

### Important leakage warning

ACS, KAST, DDΔ and similar end-of-match metrics are partly consequences of how the match unfolded. They are useful descriptors but cannot prove that deliberately maximizing the metric will cause a win.

The AI prompt receives this warning explicitly.

---

## 8. AI coach

### 8.1 Default runtime and local-model selection

Local Ollama endpoint:

`http://localhost:11434`

The target machine uses an **NVIDIA GeForce RTX 4070 SUPER**. The coding agent must **select, install, and use the best practical local model for this GPU at implementation time** instead of hard-coding an arbitrary model name in the specification.

Model selection is an implementation responsibility. The agent must evaluate current Ollama-compatible candidates and choose the strongest model that provides the best overall balance of:

- coaching/reasoning quality;
- ability to interpret structured statistical JSON correctly;
- instruction following and low hallucination rate;
- French and English output quality;
- usable latency on the RTX 4070 SUPER;
- VRAM fit and quantization quality;
- minimal CPU offload or swapping when avoidable.

The selected model should make effective use of the available GPU memory rather than choosing a smaller model only because it is easier to run. Conversely, the agent must not choose a model so large that heavy CPU offload makes the coaching experience impractically slow.

Because the local-model ecosystem changes rapidly, the agent must verify current model availability and benchmark or test realistic candidates on the actual machine before finalizing the choice. The chosen model, quantization, approximate VRAM usage, measured response speed, and reason for selection must be documented in the project README.

If no explicit model is provided by the user, the CLI should use an `auto` selection mode that resolves to the model chosen for the RTX 4070 SUPER during setup.

No cloud key is required.

### 8.2 AI input

The model receives the final analysis JSON, not the raw scraped HTML/text.

This minimizes hallucinations and forces the model to reason from already-computed evidence.

### 8.3 AI output contract

The response must contain:

1. **What the data actually says**
2. **What is probably noise / uncertain**
3. **Three coaching priorities**
4. **Next 10-game experiment**
5. **What extra data would unlock better coaching**

### 8.4 Guardrails

The coach must:

- never invent a gameplay mistake not represented in the data;
- distinguish association from causation;
- explicitly respect confidence intervals/sample size;
- avoid treating headshot percentage as a universal aim score;
- avoid treating K/D as the objective;
- recommend controlled experiments and data collection when evidence is weak.

---

## 9. CLI interface

### Full pipeline

```bash
vlcoach run "Player#TAG" --matches 50 --model auto
```

### Individual stages

```bash
vlcoach collect "Player#TAG" --matches 50
vlcoach analyze "Player#TAG"
vlcoach coach "Player#TAG" --model auto
```

If headless rendering fails:

```bash
vlcoach collect "Player#TAG" --matches 50 --headed
```

---

## 10. Outputs

For `Player#TAG`:

```text
data/
  raw/Player_TAG.json
  clean/Player_TAG.csv
  analysis/Player_TAG.json
  analysis/Player_TAG_coach.md
```

The separation allows every stage to be inspected independently.

---


## 11. Development methodology — mandatory use of Superpowers

The project **must be developed using the Superpowers methodology from**:

`https://github.com/obra/superpowers`

This is a development-process requirement for the coding agent, not a Python runtime dependency of Valorant Stat Coach. **Before starting implementation, the coding agent must install and configure everything required to build, run, test, scrape, analyze, and operate the project.** It must not assume that dependencies or external tools are already present on the machine.

At minimum, the agent must detect the host environment and install/configure the required project tooling when missing, including the appropriate Python version and virtual environment, project Python dependencies, `D4Vinci/Scrapling` (https://github.com/D4Vinci/Scrapling) and its browser/runtime requirements, the test tooling, Ollama when local AI coaching is enabled, the best practical local model selected for the NVIDIA GeForce RTX 4070 SUPER, and any other dependency introduced by the implementation. Installation commands must be documented and reproducible. The agent must verify each critical dependency after installation instead of merely assuming that installation succeeded.

**Superpowers itself must also be installed and enabled in the coding-agent harness used to implement the project**, using the official instructions from:

`https://github.com/obra/superpowers`

The agent must use the installation method appropriate for the active environment (for example Codex, OpenCode, Claude Code, Cursor, or another supported harness) and verify that the Superpowers skills are actually available before development continues. Merely cloning the repository, mentioning Superpowers in documentation, or installing it without invoking its workflow does **not** satisfy this requirement.

The coding agent must then **actively use** the relevant Superpowers skills/workflow throughout implementation, including at minimum:

1. **brainstorming** before major design or behavioral changes;
2. **writing-plans** before implementing multi-step features;
3. **test-driven-development** using RED → GREEN → REFACTOR for new behavior and bug fixes;
4. **systematic-debugging** when investigating failures instead of making ad-hoc fixes;
5. **requesting-code-review / receiving-code-review** for meaningful implementation milestones when available in the chosen harness;
6. **verification-before-completion** before claiming that a feature works, tests pass, or a task is complete.

Implementation plans produced through Superpowers should be stored under:

`docs/superpowers/plans/`

Design/specification artifacts produced by the workflow should remain version-controlled with the project.

### Required project bootstrap and engineering behavior

- Inspect the current machine/tooling state before development and identify missing requirements.
- Install all dependencies and tools required by the project rather than asking the user to perform routine setup manually when the agent has terminal access.
- Create and use an isolated Python virtual environment for the project.
- Install the project in that environment, install `D4Vinci/Scrapling` from https://github.com/D4Vinci/Scrapling, and install any additional Scrapling/runtime/browser dependencies that the chosen implementation requires.
- When AI coaching is enabled, install/configure Ollama and select the best practical current local model for the NVIDIA GeForce RTX 4070 SUPER, install it if missing, benchmark/verify it on the actual machine, and confirm that it can be invoked locally before continuing.
- Install/enable `obra/superpowers` in the current coding harness and verify that its skills can actually be invoked.
- Use Superpowers during the work; do not treat it as optional documentation or a passive dependency.
- Record reproducible setup commands in the project README so a fresh machine can reproduce the environment.
- Do not jump directly from an idea to production code for non-trivial features.
- Write or update tests before implementation whenever the Superpowers TDD workflow applies.
- Run the relevant failing test first, then implement the smallest change that makes it pass.
- Run the full applicable test suite before declaring a task complete.
- Prefer simple, testable components and clear interfaces over speculative abstractions.
- Preserve evidence of verification in terminal output or development logs when practical.
- If the implementation deviates from the approved specification, update the design/plan explicitly rather than silently changing behavior.

The purpose of this requirement is to keep the scraper, cleaning pipeline, statistical engine, and AI coaching layer auditable and reproducible as the project grows.

---

## 12. Acceptance criteria for v0.2

The release is acceptable when:

- the CLI installs successfully;
- the statistical unit tests pass;
- raw, clean, analysis and coaching files are generated from a public profile when Tracker's DOM is compatible;
- missing values do not crash the statistical pipeline;
- small samples display uncertainty rather than confident conclusions;
- the AI can be removed and the statistical report still remains useful;
- if Ollama is unavailable, a deterministic fallback coaching report is generated;
- no undocumented Tracker API or anti-bot bypass mechanism is used.
- all required project dependencies/tooling have been installed or provisioned and verified on the development environment;
- `obra/superpowers` has been installed/enabled in the active coding harness, its availability has been verified, and implementation work is actually performed using the workflow defined in Section 11;
- the README contains reproducible bootstrap/install commands for a fresh machine.

---

## 13. Main limitation and next engineering priority

The current bottleneck is not the mathematics; it is the granularity and reliability of the available public data.

Match-level analysis can identify patterns, but the strongest coaching questions are round-level: opening duel context, trades, advantage conversion, economy, post-plant decisions and deaths after gaining an advantage.

Therefore the next major version should prioritize an authorized/reliable round-event source before adding more sophisticated machine learning. More complex models applied to weak data would create false precision rather than better coaching.
