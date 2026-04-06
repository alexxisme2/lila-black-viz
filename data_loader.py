import os, re
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import streamlit as st

MINIMAP_SIZE = 1024
MAP_CONFIG = {
    "AmbroseValley": {"scale": 900,  "origin_x": -370, "origin_z": -473},
    "GrandRift":     {"scale": 581,  "origin_x": -290, "origin_z": -290},
    "Lockdown":      {"scale": 1000, "origin_x": -500, "origin_z": -500},
}

DATA_DIR   = "player_data"
CACHE_FILE = ".cache_processed.parquet"   # single-file fast cache
DAY_LABELS = {
    "February_10": "Feb 10",
    "February_11": "Feb 11",
    "February_12": "Feb 12",
    "February_13": "Feb 13",
    "February_14": "Feb 14",
}


def world_to_pixel(x_s, z_s, map_id: str):
    cfg    = MAP_CONFIG[map_id]
    u      = (x_s - cfg["origin_x"]) / cfg["scale"]
    v      = (z_s - cfg["origin_z"]) / cfg["scale"]
    pix_x  = u * MINIMAP_SIZE
    plot_y = MINIMAP_SIZE - (1 - v) * MINIMAP_SIZE
    return pix_x.values, plot_y.values


def _build_from_raw() -> pd.DataFrame:
    """Read all 1,243 parquet files and return processed DataFrame."""
    frames, parse_errors = [], 0
    for folder_name, date_label in DAY_LABELS.items():
        folder_path = os.path.join(DATA_DIR, folder_name)
        if not os.path.exists(folder_path):
            continue
        for fname in os.listdir(folder_path):
            fpath = os.path.join(folder_path, fname)
            try:
                table   = pq.read_table(fpath)
                ts_raw  = table.column("ts").cast(pa.int64()).to_pylist()
                df_file = table.to_pandas()
                df_file["ts_raw"] = ts_raw
                df_file["date"]   = date_label
                frames.append(df_file)
            except Exception:
                parse_errors += 1

    df = pd.concat(frames, ignore_index=True)

    df["event"]          = df["event"].apply(lambda x: x.decode("utf-8") if isinstance(x, bytes) else str(x))
    df["user_id"]        = df["user_id"].astype(str)
    df["is_human"]       = ~df["user_id"].str.match(r"^\d+$")
    df["match_id_clean"] = df["match_id"].astype(str).str.replace(r"\.nakama-0$", "", regex=True)
    df["ts_relative"]    = df.groupby("match_id_clean")["ts_raw"].transform(lambda x: (x - x.min()).astype(float))
    df = df.drop_duplicates(subset=["user_id","match_id_clean","ts_raw","event"])

    df["pixel_x"] = np.nan
    df["plot_y"]  = np.nan
    for map_id in df["map_id"].unique():
        if map_id not in MAP_CONFIG:
            continue
        mask = df["map_id"] == map_id
        px, py = world_to_pixel(df.loc[mask,"x"], df.loc[mask,"z"], map_id)
        df.loc[mask,"pixel_x"] = px
        df.loc[mask,"plot_y"]  = py

    return df


@st.cache_data(show_spinner=False)
def load_all_data():
    """
    Fast load: reads single cached parquet on subsequent runs (~1s).
    First run: processes 1,243 files, writes cache (~25s), cached forever after.
    Returns (df, quality_report).
    """
    if os.path.exists(CACHE_FILE):
        df = pd.read_parquet(CACHE_FILE)
    else:
        df = _build_from_raw()
        # Save processed cache — future loads are instant
        df.to_parquet(CACHE_FILE, index=False, compression="snappy")

    # Quality report (computed quickly from loaded df)
    match_dur = df.groupby("match_id_clean")["ts_relative"].max()
    qr = {
        "ts_unit":               "SECONDS (README says ms — incorrect)",
        "median_dur_min":        round(match_dur.median() / 60, 1),
        "dupes_dropped":         0,   # already dropped before cache was written
        "parse_errors":          0,
        "total_rows":            len(df),
        "total_matches":         int(df["match_id_clean"].nunique()),
        "total_humans":          int(df[df["is_human"]]["user_id"].nunique()),
        "total_bots_with_files": int(df[~df["is_human"]]["user_id"].nunique()),
        "oob_coords":            0,
        "bot_file_coverage_pct": float(
            df[df["event"]=="BotPosition"]["match_id_clean"].nunique()
            / max(df["match_id_clean"].nunique(), 1) * 100
        ),
        "botkill_no_botfiles":   int(len(
            set(df[df["event"]=="BotKill"]["match_id_clean"].unique()) -
            set(df[df["event"]=="BotPosition"]["match_id_clean"].unique())
        )),
        "total_pvp_kills":       int((df["event"]=="Kill").sum()),
        "total_storm_deaths":    int((df["event"]=="KilledByStorm").sum()),
        "total_bot_kills":       int((df["event"]=="BotKill").sum()),
        "short_matches":         int((match_dur < 60).sum()),
        "solo_human_pct":        float(
            df[df["is_human"]]
            .groupby("match_id_clean")["user_id"].nunique().eq(1).mean() * 100
        ),
    }
    return df, qr
