"""Constants, field table, Riot ID parsing. Imports nothing from the package."""
import os
import re
from urllib.parse import quote

K = 10                     # pseudo-count prior strength for shrinkage, spec 7.3 (fixed, not estimated)
ALPHA = 0.20               # EWMA smoothing, spec 7.5
N_BOOT = 2000              # bootstrap resamples, spec 7.6
SEED = 42
MIN_MODEL_ROWS = 40        # spec 7.7
MIN_CATEGORICAL_ROWS = 100 # map/agent one-hot only above this; design addendum
OLLAMA_URL = "http://localhost:11434"
AUTO_MODEL = "qwen3:14b"
DATA_DIR = os.environ.get("VLCOACH_DATA", "data")

# name -> (type, min, max). None bound = unbounded. Spec 4.2 and 6.2, plus design addendum.
FIELDS = {
    "trs": (float, 0, None),
    "acs": (float, 0, 1000),
    "kills": (int, 0, None),
    "deaths": (int, 0, None),
    "assists": (int, 0, None),
    "plus_minus": (int, None, None),
    "kd": (float, 0, None),
    "dd_delta": (float, None, None),
    "adr": (float, 0, 1000),
    "hs_pct": (float, 0, 100),
    "kast_pct": (float, 0, 100),
    "fk": (int, 0, None),
    "fd": (int, 0, None),
    "mk": (int, 0, None),
    "acs_rank_in_team": (int, 1, 5),   # 1 = top ACS on own team
    "rr_change": (int, None, None),    # optional, only when the page shows it
}
CONTEXT = ("match_id", "url", "timestamp", "map", "agent", "result", "score_a", "score_b", "lobby_rank")
MODEL_FEATURES = ("dd_delta", "kast_pct", "acs", "opening_balance", "hs_pct")  # continuous, spec 7.7
MODEL_CATEGORICAL = ("map", "agent")
FORM_FIELDS = ("acs", "adr", "kast_pct", "dd_delta")
DIFF_FIELDS = FORM_FIELDS + ("hs_pct", "opening_balance", "mk", "kd", "acs_rank_in_team")


def riot_id(s):
    """'Name#TAG' -> dict(name, tag, url_path, stem). Raises ValueError."""
    name, sep, tag = s.partition("#")
    if not sep or not name or not tag:
        raise ValueError(f"expected Name#TAG, got {s!r}")
    return {
        "name": name,
        "tag": tag,
        "url_path": f"/valorant/profile/riot/{quote(name)}%23{quote(tag)}",
        "stem": re.sub(r"[^\w-]", "_", f"{name}_{tag}"),
    }
