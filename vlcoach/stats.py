"""Spec section 7. Pure functions, None-tolerant. Each answers one question."""
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
    return [x for x in xs if x is not None]


def wilson(w, n, z=1.96):
    """95% Wilson score interval. Spec 7.1."""
    if n == 0:
        return None
    p = w / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [c - h, c + h]


def jeffreys(w, l):
    """Beta(w+0.5, l+0.5) posterior mean and 95% credible interval. Spec 7.2."""
    b = sps.beta(w + 0.5, l + 0.5)
    return {"mean": float(b.mean()), "ci": [float(b.ppf(0.025)), float(b.ppf(0.975))]}


def shrink(wins_g, n_g, p_global, k=K):
    """Pseudo-count shrinkage toward the player's overall rate. Spec 7.3."""
    return (wins_g + k * p_global) / (n_g + k)


def robust_z(xs):
    """Median/MAD z-score per value, 0.67449 scaling. Spec 7.4. MAD == 0 -> all None."""
    v = _vals(xs)
    if len(v) < 2:
        return [None] * len(xs)
    med, mad = float(np.median(v)), float(sps.median_abs_deviation(v))
    if mad == 0:
        return [None] * len(xs)
    return [None if x is None else 0.67449 * (x - med) / mad for x in xs]


def ewma(xs, alpha=ALPHA):
    """Exponentially weighted moving average; a None carries the previous value. Spec 7.5."""
    out, s = [], None
    for x in xs:
        if x is not None:
            s = x if s is None else s + alpha * (x - s)  # exact on a constant series
        out.append(s)
    return out


def bootstrap_diff(win_vals, loss_vals, n_boot=N_BOOT, seed=SEED):
    """mean(win) - mean(loss) with a 95% match-level bootstrap CI. Spec 7.6."""
    w, l = np.array(_vals(win_vals), float), np.array(_vals(loss_vals), float)
    if len(w) < 2 or len(l) < 2:
        return None
    rng = np.random.default_rng(seed)
    diffs = [rng.choice(w, len(w)).mean() - rng.choice(l, len(l)).mean() for _ in range(n_boot)]
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return {"diff": float(w.mean() - l.mean()), "ci": [float(lo), float(hi)], "uncertain": bool(lo <= 0 <= hi)}
