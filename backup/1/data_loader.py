"""
Loads all parquet files from player_data/, preprocesses, and caches.

Pre-computation done here (once, on first load):
  - event bytes → string
  - is_human flag (UUID user_id = human, numeric = bot)
  - match_id cleaned (strip .nakama-0)
  - ts_relative: seconds from match start (for timeline slider)
  - pixel_x, plot_y: pre-computed minimap pixel positions
"""

import os
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import streamlit as st

from coordinate_utils import world_to_pixel_vectorized, MAP_CONFIG

DATA_DIR = "player_data"

# Folder name → readable date label
DAY_LABELS = {
    "February_10": "Feb 10",
    "February_11": "Feb 11",
    "February_12": "Feb 12",
    "February_13": "Feb 13",
    "February_14": "Feb 14",
}


@st.cache_data(show_spinner=False)
def load_all_data() -> pd.DataFrame:
    """
    Reads every parquet file in player_data/February_*/
    Returns a single fully-preprocessed DataFrame.
    Cached by Streamlit — only runs once per session.
    """
    frames = []
    errors = 0

    for folder_name, date_label in DAY_LABELS.items():
        folder_path = os.path.join(DATA_DIR, folder_name)
        if not os.path.exists(folder_path):
            continue

        files = os.listdir(folder_path)
        for fname in files:
            fpath = os.path.join(folder_path, fname)
            try:
                table = pq.read_table(fpath)
                df_file = table.to_pandas()
                df_file["date"] = date_label
                frames.append(df_file)
            except Exception:
                errors += 1
                continue

    if not frames:
        return pd.DataFrame()

    df = pd.concat(frames, ignore_index=True)

    # ── 1. Decode event bytes ────────────────────────────────────────────────
    df["event"] = df["event"].apply(
        lambda x: x.decode("utf-8") if isinstance(x, bytes) else str(x)
    )

    # ── 2. Human vs Bot ──────────────────────────────────────────────────────
    # Bots have purely numeric user_ids (e.g. "1440"), humans have UUIDs
    df["user_id"] = df["user_id"].astype(str)
    df["is_human"] = ~df["user_id"].str.match(r"^\d+$")

    # ── 3. Clean match_id ────────────────────────────────────────────────────
    df["match_id_clean"] = df["match_id"].astype(str).str.replace(
        r"\.nakama-0$", "", regex=True
    )

    # ── 4. Relative timestamp (seconds from match start) ────────────────────
    # ts is stored as milliseconds; pandas parses it as datetime64[ns]
    # We convert to int64 (nanoseconds), then compute per-match offset
    df["ts_ns"] = pd.to_datetime(df["ts"]).astype(np.int64)
    df["ts_relative"] = df.groupby("match_id")["ts_ns"].transform(
        lambda x: (x - x.min()) / 1e9  # nanoseconds → seconds
    )

    # ── 5. Pre-compute pixel coords ──────────────────────────────────────────
    df["pixel_x"] = np.nan
    df["plot_y"]  = np.nan

    for map_id in df["map_id"].unique():
        if map_id not in MAP_CONFIG:
            continue
        mask = df["map_id"] == map_id
        px, py = world_to_pixel_vectorized(df.loc[mask, "x"], df.loc[mask, "z"], map_id)
        df.loc[mask, "pixel_x"] = px
        df.loc[mask, "plot_y"]  = py

    return df
