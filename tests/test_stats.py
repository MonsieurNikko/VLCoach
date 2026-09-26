import math
import pytest
from vlcoach import stats as S


def test_wilson_matches_literature():
    # Newcombe 1998, table values for 95% Wilson score interval
    lo, hi = S.wilson(3, 4)
    assert math.isclose(lo, 0.3006, abs_tol=5e-4) and math.isclose(hi, 0.9544, abs_tol=5e-4)
    lo, hi = S.wilson(0, 10)
    assert abs(lo) < 1e-12 and math.isclose(hi, 0.2775, abs_tol=5e-4)
    assert S.wilson(0, 0) is None


def test_jeffreys_extremes_do_not_crash():
    j = S.jeffreys(0, 0)
    assert 0 < j["mean"] < 1 and j["ci"][0] < j["ci"][1]
    j = S.jeffreys(10, 0)
    assert j["mean"] > 0.9


def test_shrink_pulls_small_samples_to_baseline():
    # spec 7.3: a 3-0 map must not be reported as 100%; small samples move far more than large ones
    assert S.shrink(3, 3, 0.5) == pytest.approx(8 / 13)          # (3 + 10*0.5) / (3 + 10), pins k placement
    small_move = 1.0 - S.shrink(3, 3, 0.5)                        # raw 100% -> 61.5%
    large_move = 0.55 - S.shrink(55, 100, 0.5)                    # raw 55%  -> 54.5%
    assert small_move > 10 * large_move


def test_robust_z_handles_none_and_zero_mad():
    z = S.robust_z([10, 12, None, 30, 11])
    assert len(z) == 5 and z[2] is None and z[3] > 2
    assert S.robust_z([5, 5, 5, 5]) == [None] * 4
    assert S.robust_z([None, None]) == [None, None]


def test_ewma_constant_and_gaps():
    assert S.ewma([3.0, 3.0, 3.0]) == [3.0, 3.0, 3.0]
    e = S.ewma([1.0, None, 2.0])
    assert e[1] == e[0] and e[2] > e[1]
    assert S.ewma([]) == []


def test_bootstrap_identical_groups_is_uncertain():
    r = S.bootstrap_diff([1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
    assert r["uncertain"] is True and r["ci"][0] <= 0 <= r["ci"][1]
    r = S.bootstrap_diff([50, 55, 60, 52, 58, 61], [10, 12, 9, 11, 13, 8])
    assert r["uncertain"] is False and r["diff"] > 40
    assert S.bootstrap_diff([1], [1, 2]) is None
    assert S.bootstrap_diff([None, None], [1, 2, 3]) is None


def _rows(n, wins, signal=True):
    """Synthetic clean rows. Wins get higher dd_delta when signal=True."""
    rows = []
    for i in range(n):
        win = 1 if i < wins else 0
        rows.append({
            "win": win, "map": ["Ascent", "Bind", "Haven"][i % 3], "agent": ["Jett", "Omen"][i % 2],
            "dd_delta": (20 if win else -20) + (i % 7) if signal else i % 7,
            "kast_pct": 70.0 + (i % 5), "acs": 200.0 + (i % 11), "opening_balance": (i % 3) - 1,
            "hs_pct": None if i % 9 == 0 else 20.0 + (i % 4),
        })
    return rows


def test_logistic_skips_small_or_single_class():
    assert "need 40" in S.logistic(_rows(39, 20))["skipped"]
    assert S.logistic(_rows(40, 40))["skipped"] == "only one class present"
    assert S.logistic([])["skipped"]


def test_logistic_fits_with_signal_and_missing_values():
    r = S.logistic(_rows(60, 30))
    assert r["skipped"] is None and r["auc"] > 0.8 and r["auc_std"] >= 0
    assert r["odds_ratios"]["dd_delta"] > 1
    assert r["categorical_used"] is False and not any(k.startswith("map_") for k in r["odds_ratios"])


def test_logistic_uses_categoricals_at_100_rows():
    r = S.logistic(_rows(120, 60))
    assert r["categorical_used"] is True and any(k.startswith("map_") for k in r["odds_ratios"])


def test_analyze_shape_and_small_sample():
    quality = {"discovered": 4, "parsed": 4, "with_result": 4, "completeness": {}}
    analysis = S.analyze(_rows(4, 3), quality)

    assert set(analysis) == {
        "quality", "leakage_warning", "winrate", "by_map", "by_agent", "form",
        "outliers", "win_vs_loss", "comparisons", "margins", "model",
    }
    assert analysis["winrate"]["n"] == 4 and analysis["winrate"]["wins"] == 3
    low, high = analysis["winrate"]["wilson"]
    assert high - low > 0.5
    assert analysis["model"]["skipped"]
    assert analysis["leakage_warning"] == S.LEAKAGE_WARNING
    assert analysis["by_map"]["Ascent"]["shrunk"] != analysis["by_map"]["Ascent"]["raw"]
    assert set(analysis["form"]) == set(S.FORM_FIELDS)
    assert {"ewma", "last", "mad"} <= set(analysis["form"]["acs"])
    assert set(analysis["win_vs_loss"]) == set(S.DIFF_FIELDS)
    assert analysis["comparisons"]["n"] >= 1
    assert analysis["comparisons"]["expected_false_positives"] == analysis["comparisons"]["n"] / 20


def test_analyze_signal_requires_clear_ci_and_mad():
    rows = _rows(60, 30)
    for row in rows:
        row["round_diff"] = 6 if row["win"] else -4

    analysis = S.analyze(
        rows,
        {"discovered": 60, "parsed": 60, "with_result": 60, "completeness": {}},
    )
    dd_delta = analysis["win_vs_loss"]["dd_delta"]

    assert dd_delta["uncertain"] is False and dd_delta["signal"] is True
    assert analysis["margins"] == {
        "loss_median_round_diff": -4.0,
        "win_median_round_diff": 6.0,
        "acs_rank_in_team_median": None,
    }
    assert all(
        not result["signal"]
        for result in analysis["win_vs_loss"].values()
        if result and result["uncertain"]
    )


def test_analyze_empty_rows_does_not_crash():
    analysis = S.analyze(
        [],
        {"discovered": 0, "parsed": 0, "with_result": 0, "completeness": {}},
    )

    assert analysis["winrate"]["n"] == 0
    assert analysis["winrate"]["wilson"] is None
    assert analysis["model"]["skipped"]
    assert analysis["margins"] == {
        "loss_median_round_diff": None,
        "win_median_round_diff": None,
        "acs_rank_in_team_median": None,
    }
