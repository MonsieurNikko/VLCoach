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
