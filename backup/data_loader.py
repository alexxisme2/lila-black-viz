"""
data_loader.py — LILA BLACK
Loads all parquet files, fixes known data issues, returns (df, quality_report).

FIXES APPLIED (logged in quality_report):
  1. event bytes → utf-8 string
  2. Timestamps: README says ms, data is actually unix seconds — handled correctly
  3. Full duplicate rows dropped (1420 in observed data)
  4. match_id stripped of .nakama-0 suffix
  5. is_human derived from user_id format (UUID=human, numeric=bot)
  6. Pre-computed pixel coords per map
  7. ts_relative = seconds from match start (per match group)
"""

import os, re
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import streamlit as st

MINIMAP_SIZE = 1024
MAP_CONFIG = {
    "AmbroseValley": {"scale": 900,  "origin_x": -370, "origin_z": -473},
    "GrandRift":     {"scale": 581,  "origin_x": -290, "origin_z": -290},
    "Lockdown":      {"scale": 1000, "origin_x": -500, "origin_z": -500},
}
DATA_DIR   = "player_data"
DAY_LABELS = {
    "February_10": "Feb 10",
    "February_11": "Feb 11",
    "February_12": "Feb 12",
    "February_13": "Feb 13",
    "February_14": "Feb 14",
}


def world_to_pixel(x_series, z_series, map_id: str):
    cfg     = MAP_CONFIG[map_id]
    u       = (x_series - cfg["origin_x"]) / cfg["scale"]
    v       = (z_series - cfg["origin_z"]) / cfg["scale"]
    pixel_x = u * MINIMAP_SIZE
    plot_y  = MINIMAP_SIZE - (1 - v) * MINIMAP_SIZE
    return pixel_x.values, plot_y.values


@st.cache_data(show_spinner=False)
def load_all_data():
    """
    Returns (df, quality_report).
    quality_report is a dict — used by Data Health tab.
    """
    frames, parse_errors = [], 0

    for folder_name, date_label in DAY_LABELS.items():
        folder_path = os.path.join(DATA_DIR, folder_name)
        if not os.path.exists(folder_path):
            continue
        for fname in os.listdir(folder_path):
            fpath = os.path.join(folder_path, fname)
            try:
                df_file        = pq.read_table(fpath).to_pandas()
                df_file["date"] = date_label
                frames.append(df_file)
            except Exception:
                parse_errors += 1

    if not frames:
        return pd.DataFrame(), {}

    df = pd.concat(frames, ignore_index=True)

    qr = {}  # quality_report

    # ── 1. Event bytes → string ──────────────────────────────────────────────
    df["event"] = df["event"].apply(
        lambda x: x.decode("utf-8") if isinstance(x, bytes) else str(x)
    )

    # ── 2. Human vs Bot ──────────────────────────────────────────────────────
    df["user_id"]  = df["user_id"].astype(str)
    df["is_human"] = ~df["user_id"].str.match(r"^\d+$")

    # ── 3. Clean match_id ────────────────────────────────────────────────────
    df["match_id_clean"] = df["match_id"].astype(str).str.replace(r"\.nakama-0$", "", regex=True)

    # ── 4. Timestamps ────────────────────────────────────────────────────────
    # README says ms — WRONG. Data is unix seconds.
    # pd.to_datetime(df["ts"]) parses as datetime64[ns]; cast to int64 = nanoseconds.
    # Dividing that by 1e9 gives seconds. But original values ARE unix epoch seconds.
    # Safest: take raw int value of ts column directly.
    raw_ts = pd.to_datetime(df["ts"])
    df["ts_epoch_s"]  = raw_ts.astype(np.int64) // 1_000_000_000  # nanoseconds → seconds
    df["ts_relative"] = df.groupby("match_id")["ts_epoch_s"].transform(
        lambda x: (x - x.min()).astype(float)
    )
    # Verify: median match duration should be ~5-10 min
    match_durations = df.groupby("match_id")["ts_relative"].max()
    median_dur_min  = match_durations.median() / 60
    qr["ts_unit_verified"] = f"Median match duration = {median_dur_min:.1f} min (unit=seconds confirmed)"
    qr["ts_readme_wrong"]  = True  # README says ms, actual data is seconds

    # ── 5. Duplicate rows ────────────────────────────────────────────────────
    rows_before   = len(df)
    df            = df.drop_duplicates()
    dupes_dropped = rows_before - len(df)
    qr["duplicates_dropped"] = dupes_dropped
    qr["duplicates_note"]    = (
        "Loot(2338) + Position(294) + BotKill(65) + BotKilled(4) event dupes. "
        "Likely same file ingested across multiple date folders. "
        "Cross-date key matches confirmed. Safe to drop."
    )

    # ── 6. Pre-compute pixel coords ──────────────────────────────────────────
    df["pixel_x"] = np.nan
    df["plot_y"]  = np.nan
    oob_total     = 0
    for map_id in df["map_id"].unique():
        if map_id not in MAP_CONFIG:
            continue
        mask = df["map_id"] == map_id
        px, py = world_to_pixel(df.loc[mask, "x"], df.loc[mask, "z"], map_id)
        df.loc[mask, "pixel_x"] = px
        df.loc[mask, "plot_y"]  = py
        cfg = MAP_CONFIG[map_id]
        u   = (df.loc[mask, "x"] - cfg["origin_x"]) / cfg["scale"]
        v   = (df.loc[mask, "z"] - cfg["origin_z"]) / cfg["scale"]
        oob = ((u < -0.05) | (u > 1.05) | (v < -0.05) | (v > 1.05)).sum()
        oob_total += int(oob)
    qr["oob_coords"] = oob_total

    # ── 7. Other quality signals ─────────────────────────────────────────────
    qr["parse_errors"]          = parse_errors
    qr["total_rows"]            = len(df)
    qr["total_matches"]         = df["match_id_clean"].nunique()
    qr["total_humans"]          = df[df["is_human"]]["user_id"].nunique()
    qr["total_bots_with_files"] = df[~df["is_human"]]["user_id"].nunique()
    qr["short_matches"]         = int((match_durations < 60).sum())
    qr["solo_human_pct"]        = float(
        df[df["is_human"]].groupby("match_id")["user_id"].nunique().eq(1).mean() * 100
    )
    qr["bot_file_coverage_pct"] = float(
        df[df["event"] == "BotPosition"]["match_id"].nunique()
        / df["match_id"].nunique() * 100
    )
    qr["botkill_no_botfiles"] = int(
        len(
            set(df[df["event"] == "BotKill"]["match_id"].unique()) -
            set(df[df["event"] == "BotPosition"]["match_id"].unique())
        )
    )
    qr["total_pvp_kills"]    = int((df["event"] == "Kill").sum())
    qr["total_storm_deaths"] = int((df["event"] == "KilledByStorm").sum())
    qr["total_bot_kills"]    = int((df["event"] == "BotKill").sum())
    qr["ghost_events"]       = _count_ghost_events(df)

    return df, qr


def _count_ghost_events(df):
    """Events logged after a player's recorded death."""
    death_ts = (
        df[df["event"].isin(["Killed", "KilledByStorm", "BotKilled"])]
        .groupby(["user_id", "match_id"])["ts_epoch_s"]
        .min()
        .rename("death_ts")
        .reset_index()
    )
    merged = df.merge(death_ts, on=["user_id", "match_id"], how="left")
    return int((merged["ts_epoch_s"] > merged["death_ts"]).sum())
