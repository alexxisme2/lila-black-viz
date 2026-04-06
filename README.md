# LILA BLACK — Level Designer Dashboard

> Internal tool for analyzing player behavior on LILA BLACK maps.  
> Built for the LILA Games Level Design team.

## Live Demo
**[https://lila-black-viz.streamlit.app](https://lila-black-viz.streamlit.app)**

---

## What It Does

A web-based visualization tool that turns raw match telemetry into actionable level design insights.

| Tab | What you get |
|---|---|
| **Data Health** | Automated data quality report — fixes applied, anomalies flagged |
| **Insights** | 7 pre-computed game design observations with evidence and actions |
| **Overview** | Match-level stats, engagement breakdown, storm/loot timing |
| **Match Replay** | Animated playback of any match — per-player color-coded paths, clustered events |
| **Player Profile** | Aggregate heatmap of a player's favorite zones + single-match path view |
| **Heatmaps** | Normalized event density (% of total), hotspot bubbles, auto-generated zone insights |

---

## Local Setup

```bash
git clone https://github.com/alexxisme2/lila-black-viz
cd lila-black-viz

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Place your data files:
```
lila-black-viz/
├── player_data/
│   ├── February_10/
│   ├── February_11/
│   ├── February_12/
│   ├── February_13/
│   └── February_14/
└── minimaps/
    ├── AmbroseValley_Minimap.png
    ├── GrandRift_Minimap.png
    └── Lockdown_Minimap.jpg
```

```bash
streamlit run app.py
```

First load: ~25s (processes 1,243 parquet files, writes local cache).  
Subsequent loads: ~1s (reads `.cache_processed.parquet`).

---

## Tech Stack

- **Streamlit** — UI framework
- **PyArrow + Pandas** — parquet loading and data processing
- **Plotly** — interactive maps, charts, and native animation
- **Pillow** — minimap image rendering

---

## Key Technical Notes

- `ts` column in parquet is **unix seconds**, not milliseconds (README was incorrect — verified via median match duration = 6.4 min)
- 1,420 duplicate rows dropped at load time (cross-day ingestion artifact)
- Bot parquet files missing for 91% of matches — BotKill events inferred from human-side logs only
- Coordinate mapping: world `(x,z)` → UV `(0-1)` → pixel `(1024×1024)` → Plotly coords (y-axis flipped twice)

See `ARCHITECTURE.md` for full technical documentation.  
See `INSIGHTS.md` for game design analysis.
