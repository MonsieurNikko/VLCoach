import pytest
from vlcoach.config import riot_id, FIELDS


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
