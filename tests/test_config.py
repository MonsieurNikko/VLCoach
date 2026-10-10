import pytest
from vlcoach.config import (
    riot_id, FIELDS, CONTEXT, DERIVED, MODEL_FEATURES, MODEL_CATEGORICAL, FORM_FIELDS, DIFF_FIELDS,
)


def test_riot_id_parses_and_encodes():
    r = riot_id("Ni kko#EUW1")
    assert r["name"] == "Ni kko" and r["tag"] == "EUW1"
    assert r["url_path"] == "/valorant/profile/riot/Ni%20kko%23EUW1"
    assert r["stem"] == "Ni_kko_EUW1"


def test_riot_id_rejects_missing_tag():
    with pytest.raises(ValueError):
        riot_id("NoTagHere")


def test_fields_have_spec_bounds():
    assert FIELDS["hs_pct"] == (float, 0, 100)
    assert FIELDS["kast_pct"] == (float, 0, 100)
    assert FIELDS["kills"][1] == 0
    assert FIELDS["acs_rank_in_team"] == (int, 1, 5)
    assert FIELDS["rr_change"] == (int, None, None)


def test_every_field_stats_reads_is_declared():
    # A name stats reads but nobody declares would come out of clean() misspelled
    # or missing, and every statistic on it would silently be None.
    declared = set(FIELDS) | set(DERIVED) | set(CONTEXT)
    read_by_stats = set(MODEL_FEATURES) | set(MODEL_CATEGORICAL) | set(FORM_FIELDS) | set(DIFF_FIELDS)
    assert read_by_stats | {"win", "round_diff"} <= declared
    assert set(DERIVED) == {"win", "opening_balance", "round_diff"}
