"""Spec section 7. Pure functions, None-tolerant. Each answers one question.

Every function here takes cleaned match data and returns numbers with their
uncertainty attached. None of them decide anything: they measure, and the
caller decides what is worth saying. A missing value is always None, never
guessed, never filled in.
"""
import math

import numpy as np
from scipy import stats as sps

from .config import K, ALPHA, N_BOOT, SEED, MIN_MODEL_ROWS, MIN_CATEGORICAL_ROWS, MODEL_FEATURES, MODEL_CATEGORICAL, FORM_FIELDS, DIFF_FIELDS

LEAKAGE_WARNING = (
    "ACS, KAST, DD-delta and similar end-of-match metrics are partly consequences of how the match "
    "unfolded. They describe matches; they cannot prove that deliberately maximizing a metric will "
    "cause a win. Every coefficient and difference here is an association, not a causal effect."
)


def _vals(xs):
    """Drop the missing values, keep the order of the rest."""
    return [x for x in xs if x is not None]


def wilson(wins, n, z=1.96):
    """Gives the range where your true win rate probably sits, not just one number.

    Example: 3 wins in 4 matches gives [0.30, 0.95]. The 75% you see could really
    be anywhere from 30% to 95%, so the report can say "too few games to tell".
    With 30 wins in 40 matches the range tightens to [0.60, 0.86].

    Used by: analyze(), for the overall win rate in the report. Without it the
    report would show a bare 75% and overclaim on four games.

    Detail: 95% Wilson score interval, spec 7.1. Chosen over the textbook formula
    because it stays inside [0, 1] even at 0 or 100% wins. Returns None when n == 0.
    """
    if n == 0:
        return None

    observed_rate = wins / n

    # Wilson works by asking which true rates could plausibly have produced what
    # we saw. The answer is an interval pulled toward 50% when n is small.
    denominator = 1 + z * z / n
    centre = (observed_rate + z * z / (2 * n)) / denominator
    half_width = z * math.sqrt(observed_rate * (1 - observed_rate) / n + z * z / (4 * n * n)) / denominator

    return [centre - half_width, centre + half_width]


def jeffreys(wins, losses):
    """Gives a best guess of your true win rate, plus its range, the Bayesian way.

    Example: 3 wins and 1 loss gives a best guess of 0.70, range [0.28, 0.97].
    0 wins and 4 losses still works: best guess 0.10, range [0.00, 0.44].

    Used by: analyze(), next to wilson for the overall win rate. Wilson gives
    only a range; this adds one best-guess number the coach can quote, and two
    methods that agree make the report more trustworthy.

    Detail: Beta posterior from Jeffreys' prior Beta(0.5, 0.5), which assumes
    almost nothing before the first match. Returns the posterior mean and a 95%
    credible interval, spec 7.2. Never breaks at 0 wins or 0 losses.
    """
    posterior = sps.beta(wins + 0.5, losses + 0.5)
    return {
        "mean": float(posterior.mean()),
        "ci": [float(posterior.ppf(0.025)), float(posterior.ppf(0.975))],
    }


def shrink(wins_in_group, n_in_group, overall_rate, k=K):
    """Gives a fairer win rate for one map or agent you played only a few times.

    Example: 3 wins in 3 matches on Ascent, overall win rate 50%. Raw says 100%;
    shrink says 0.62. With 30 wins in 40 matches, raw 0.75 only moves to 0.70:
    more games, more trust in the map's own record.

    Used by: analyze(), as the "shrunk" value next to "raw" in by_map and
    by_agent. Without it, a lucky 3-0 map would top the report as your best map.

    Detail: empirical-Bayes shrinkage, spec 7.3. Adds k = 10 imaginary matches
    played at your overall rate: (wins + k * overall) / (n + k).
    """
    return (wins_in_group + k * overall_rate) / (n_in_group + k)


def robust_z(xs):
    """Scores each match by how unusual it was for you, on one stat.

    Example: ACS over six matches [210, 190, 250, 200, 480, 205] scores
    [0.13, -0.94, 2.29, -0.40, 14.70, -0.13]. Near 0 is a normal game for you;
    above 2 stands out. The 480 game is exceptional, and the 250 game is flagged
    too. A plain average would even rate 250 as below average, because the 480
    pulls the average up to 256.

    Used by: analyze(), as outliers[field]["z"] for ACS, ADR, KAST and DD-delta,
    so the report can point at your standout and disaster matches.

    Detail: median/MAD robust z-score, spec 7.4. The 0.67449 factor rescales MAD
    so scores read like ordinary z-scores. Returns one score per input, same
    order, None where the input was None. All None with fewer than 2 values or
    when every value is identical.
    """
    known = _vals(xs)
    if len(known) < 2:
        return [None] * len(xs)

    median = float(np.median(known))
    spread = float(sps.median_abs_deviation(known))

    # Every match identical on this metric: there is no "unusual" here, so say
    # nothing rather than divide by zero.
    if spread == 0:
        return [None] * len(xs)

    return [None if x is None else 0.67449 * (x - median) / spread for x in xs]


def ewma(xs, alpha=ALPHA):
    """Gives your recent form on one stat: a running average that favours the latest matches.

    Example: ACS [200, 200, 300, 300] gives [200, 200, 220, 236]. Two good games
    lift your form from 200 to 236, not straight to 300: each game moves it by a
    fifth of the gap. A missing match keeps the previous value:
    [None, 200, None, 300] gives [None, 200, 200, 220].

    Used by: analyze(), as form[field]["ewma"] and form[field]["last"] for ACS,
    ADR, KAST and DD-delta, so the report can say whether you are trending up or down.

    Detail: exponentially weighted moving average, spec 7.5, alpha = 0.20
    (config.ALPHA). Returns one value per input, same order. Leading Nones stay
    None until the first real value arrives.
    """
    smoothed = []
    current = None
    for x in xs:
        if x is not None:
            if current is None:
                current = x          # the first real value starts the series
            else:
                # Written as a step toward x rather than alpha*x + (1-alpha)*current:
                # algebraically identical, but exact when x equals current, so a flat
                # series stays flat instead of drifting by floating-point dust.
                current = current + alpha * (x - current)
        smoothed.append(current)
    return smoothed


def bootstrap_diff(win_vals, loss_vals, n_boot=N_BOOT, seed=SEED):
    """How much better is this metric in wins than in losses, and could it be luck?

    Returns the observed gap, a 95% interval around it, and `uncertain`, which is
    True when that interval contains zero — meaning the gap may be noise and must
    not be coached on. Returns None when either side has fewer than two matches.
    Spec 7.6.
    """
    wins = np.array(_vals(win_vals), float)
    losses = np.array(_vals(loss_vals), float)
    if len(wins) < 2 or len(losses) < 2:
        return None                       # one match per side proves nothing

    observed_gap = float(wins.mean() - losses.mean())

    # Bootstrap: redraw both groups at random, with replacement, n_boot times.
    # Each redraw is a plausible alternative history. How far those fake gaps
    # spread tells us how much the real gap could move by chance alone.
    rng = np.random.default_rng(seed)     # fixed seed, so the same data gives the same report
    fake_gaps = []
    for _ in range(n_boot):
        redrawn_wins = rng.choice(wins, len(wins))
        redrawn_losses = rng.choice(losses, len(losses))
        fake_gaps.append(redrawn_wins.mean() - redrawn_losses.mean())

    low, high = np.percentile(fake_gaps, [2.5, 97.5])   # middle 95% of the fake gaps

    return {
        "diff": observed_gap,
        "ci": [float(low), float(high)],
        "uncertain": bool(low <= 0 <= high),   # straddles zero -> cannot claim a real gap
    }


def logistic(rows):
    """Which metrics move together with winning, once considered together?

    Fits an L2-regularized logistic regression of win on the continuous features,
    plus map and agent once there is enough data. Returns:

        skipped           why no model was fitted, or None if one was
        auc               cross-validated AUC: 0.5 is a coin flip, 1.0 is perfect
        auc_std           how much that AUC moved between folds; a large value
                          means the model is unstable and the AUC is not trustworthy
        odds_ratios       per feature, above 1 = associated with winning
        categorical_used  whether map and agent made it into the model

    These are associations, never causes — see LEAKAGE_WARNING. Spec 7.7.
    """
    nothing_fitted = {
        "skipped": None, "auc": None, "auc_std": None,
        "odds_ratios": {}, "categorical_used": False,
    }

    # A match with no parsed result cannot train anything.
    scored_rows = [r for r in rows if r.get("win") is not None]
    won = [r["win"] for r in scored_rows]

    if len(won) < MIN_MODEL_ROWS:
        return {**nothing_fitted, "skipped": f"need {MIN_MODEL_ROWS} rows with a result, have {len(won)}"}
    if len(set(won)) < 2:
        return {**nothing_fitted, "skipped": "only one class present"}

    # Imported here rather than at module level: sklearn is slow to import, and
    # every other function in this file works without it.
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold, cross_val_score
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    # One row per match, one column per feature. A missing value becomes NaN here
    # and is filled by the imputer below — never guessed by us.
    features = []
    for row in scored_rows:
        features.append([np.nan if row.get(name) is None else row[name] for name in MODEL_FEATURES])
    features = np.array(features, float)
    feature_names = list(MODEL_FEATURES)

    # Below this many matches, one-hot map and agent columns carry about three
    # observations each: the model would fit noise and report it as insight.
    use_categoricals = len(won) >= MIN_CATEGORICAL_ROWS
    if use_categoricals:
        encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        # ponytail: one-hot fit outside CV; harmless for categoricals, move into the pipeline if it ever matters
        labels = [[row.get(name) or "unknown" for name in MODEL_CATEGORICAL] for row in scored_rows]
        encoded = encoder.fit_transform(labels)
        features = np.hstack([features, encoded])
        feature_names += list(encoder.get_feature_names_out(MODEL_CATEGORICAL))

    # Fill the gaps, put every feature on the same scale so the coefficients are
    # comparable, then fit with L2 so no single feature can dominate.
    model = make_pipeline(
        SimpleImputer(keep_empty_features=True),
        StandardScaler(),
        LogisticRegression(l1_ratio=0, max_iter=1000),   # l1_ratio=0 means pure L2
    )

    # Score the model on data it did not train on. Never more folds than the
    # rarer outcome has matches, otherwise a fold could end up with one class.
    folds = min(5, won.count(0), won.count(1))
    auc = auc_std = None
    if folds >= 2:
        scores = cross_val_score(
            model, features, won,
            cv=StratifiedKFold(folds, shuffle=True, random_state=SEED),
            scoring="roc_auc",
        )
        auc, auc_std = float(scores.mean()), float(scores.std())

    # Refit on everything to report the coefficients themselves.
    model.fit(features, won)
    coefficients = model[-1].coef_[0]

    # exp() turns a log-odds coefficient into an odds ratio: 1.3 reads as
    # "one standard deviation more of this goes with 1.3x the odds of winning".
    odds_ratios = {name: float(math.exp(c)) for name, c in zip(feature_names, coefficients)}

    return {
        **nothing_fitted,
        "auc": auc,
        "auc_std": auc_std,
        "categorical_used": use_categoricals,
        "odds_ratios": odds_ratios,
    }


def analyze(rows, quality):
    """Assemble the complete analysis contract consumed by the coach."""
    scored_rows = [row for row in rows if row.get("win") is not None]
    match_count = len(scored_rows)
    wins = sum(row["win"] for row in scored_rows)
    overall_rate = wins / match_count if match_count else None

    analysis = {
        "quality": quality,
        "leakage_warning": LEAKAGE_WARNING,
        "winrate": {
            "n": match_count,
            "wins": wins,
            "p": overall_rate,
            "wilson": wilson(wins, match_count),
            "jeffreys": jeffreys(wins, match_count - wins) if match_count else None,
        },
        "by_map": {},
        "by_agent": {},
        "form": {},
        "outliers": {},
        "win_vs_loss": {},
        "comparisons": {"n": 0, "expected_false_positives": 0.0},
        "margins": {
            "loss_median_round_diff": None,
            "win_median_round_diff": None,
            "acs_rank_in_team_median": None,
        },
    }

    for group_name in ("map", "agent"):
        groups = {}
        for row in scored_rows:
            group = row.get(group_name) or "unknown"
            wins_in_group, rows_in_group = groups.setdefault(group, [0, 0])
            groups[group] = [wins_in_group + row["win"], rows_in_group + 1]
        analysis[f"by_{group_name}"] = {
            group: {
                "n": rows_in_group,
                "wins": wins_in_group,
                "raw": wins_in_group / rows_in_group,
                "shrunk": shrink(wins_in_group, rows_in_group, overall_rate),
            }
            for group, (wins_in_group, rows_in_group) in groups.items()
        }

    for field in FORM_FIELDS:
        series = [row.get(field) for row in rows]
        smoothed = ewma(series)
        analysis["form"][field] = {
            "ewma": smoothed,
            "last": next((value for value in reversed(smoothed) if value is not None), None),
            "mad": _mad(series),
        }
        analysis["outliers"][field] = {"z": robust_z(series)}

    for field in DIFF_FIELDS:
        result = bootstrap_diff(
            [row.get(field) for row in scored_rows if row["win"]],
            [row.get(field) for row in scored_rows if not row["win"]],
        )
        if result is not None:
            metric_mad = _mad([row.get(field) for row in scored_rows])
            result["signal"] = (
                not result["uncertain"]
                and metric_mad is not None
                and abs(result["diff"]) > metric_mad
            )
            analysis["comparisons"]["n"] += 1
        analysis["win_vs_loss"][field] = result

    analysis["comparisons"]["n"] += len(analysis["by_map"]) + len(analysis["by_agent"])
    analysis["comparisons"]["expected_false_positives"] = analysis["comparisons"]["n"] / 20
    analysis["margins"] = {
        "loss_median_round_diff": _median(
            [row.get("round_diff") for row in scored_rows if not row["win"]]
        ),
        "win_median_round_diff": _median(
            [row.get("round_diff") for row in scored_rows if row["win"]]
        ),
        "acs_rank_in_team_median": _median(
            [row.get("acs_rank_in_team") for row in rows]
        ),
    }
    analysis["model"] = logistic(rows)
    return analysis


def _mad(xs):
    """Return the median absolute deviation, or None without two values."""
    values = _vals(xs)
    return float(sps.median_abs_deviation(values)) if len(values) >= 2 else None


def _median(xs):
    """Return a median for present values, or None when there are none."""
    values = _vals(xs)
    return float(np.median(values)) if values else None
