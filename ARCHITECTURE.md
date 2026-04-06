# ARCHITECTURE.md — LILA BLACK Level Designer Tool

## What I Built and Why

| Layer | Choice | Reason |
|---|---|---|
| Framework | Streamlit (Python) | Zero frontend overhead; data-first; deployed in minutes. The audience is a level designer, not a web user — they need insight, not animations. |
| Data loading | PyArrow + Pandas | PyArrow reads extensionless parquet natively via `pq.read_table()`. Pandas for groupby/filter logic. PyArrow also provided the timestamp fix (see Assumptions). |
| Visualization | Plotly (graph_objects) | Supports layout_image backgrounds (minimap), Heatmap overlays, and Scatter traces in a single figure. Crucially: native `fig.frames` animation runs client-side — no Streamlit rerenders per frame. |
| Animation | Plotly `updatemenus` + `fig.frames` | Pre-computes N frames in Python once, cached. Play/pause/scrub are pure browser JS — smooth, zero server roundtrips. |
| Hosting | Streamlit Cloud | Free, GitHub-connected, no infrastructure configuration. |

---

## Data Flow

```
player_data/February_*/              (1,243 extensionless parquet files)
         │
         ▼  data_loader.py — _build_from_raw()   [FIRST RUN ONLY ~25s]
         │
         ├─ PyArrow reads each file
         ├─ ts column cast to int64 via pa.int64() BEFORE pandas (see Assumptions)
         ├─ event bytes decoded → utf-8
         ├─ is_human derived: UUID user_id = human, numeric = bot
         ├─ match_id cleaned: .nakama-0 stripped
         ├─ ts_relative computed: (ts_raw - match_min) per match group → seconds from start
         ├─ 1,420 exact duplicates dropped (key: user_id + match_id + ts_raw + event)
         └─ pixel_x, plot_y pre-computed for every row (vectorized, per map)
                  │
                  ▼  written to .cache_processed.parquet (Snappy compressed, ~8MB)
                  │
         SUBSEQUENT RUNS: pd.read_parquet(.cache_processed.parquet) [~1s]
                  │
                  ▼  st.cache_data — single load per session
                  │
         app.py — Sidebar filters (Map / Date / Match / Player)
                  │
         ├─ Tab: DATA HEALTH    — automated fix log + anomaly report
         ├─ Tab: INSIGHTS       — 7 pre-computed game design observations (insights.py)
         ├─ Tab: OVERVIEW       — aggregate stats, timing histograms, match table
         ├─ Tab: MATCH REPLAY   — Plotly animation (35 pre-computed frames, cached per match)
         ├─ Tab: PLAYER PROFILE — aggregate heatmap (all matches) or single match path
         └─ Tab: HEATMAPS       — normalized density (% of event type), hotspot bubbles,
                                   auto-generated zone insights (concentration, dead zones,
                                   loot timing, human/bot traffic divergence)
```

---

## Coordinate Mapping — The Tricky Part

The data provides 3D world coordinates `(x, y, z)`. The minimap is a 2D 1024×1024 image. `y` is elevation — irrelevant for map plotting. Only `x` and `z` matter.

**Step 1 — World → UV (0–1 normalized space)**

Each map has a known `origin_x`, `origin_z`, and `scale` (from README):

```
u = (x - origin_x) / scale
v = (z - origin_z) / scale
```

| Map | Scale | Origin X | Origin Z |
|---|---|---|---|
| AmbroseValley | 900 | -370 | -473 |
| GrandRift | 581 | -290 | -290 |
| Lockdown | 1000 | -500 | -500 |

**Step 2 — UV → Image pixel (1024×1024)**

```
pixel_x = u * 1024
pixel_y = (1 - v) * 1024     ← Y flipped: image origin is top-left
```

**Step 3 — Image pixel → Plotly coordinate**

Plotly places y=0 at the *bottom* of the figure, opposite to image convention:

```
plot_y = 1024 - pixel_y       ← second flip to align with Plotly axis
```

The minimap is placed in Plotly at `x=0, y=1024` (its top-left corner in Plotly space). After the double-flip, scatter points land correctly on map features.

**Validation:** Ran coordinate sanity check per match — all UV values within [0, 1.05] bounds. Sample match `039d0edf` showed x ∈ [-2.3, 239.0], z ∈ [-95.3, 247.2] → UV x ∈ [0.41, 0.68], UV z ∈ [0.42, 0.80]. Correctly positioned in central-east zone of AmbroseValley minimap.

---

## Assumptions Made

| Ambiguity | What I encountered | How I handled it |
|---|---|---|
| **Timestamp unit** | README states `ts` is stored as milliseconds. Using `pd.to_datetime(ts, unit='ms')` produced dates in 1970, and a match "duration" of 0.6 seconds. Using `unit='s'` gave Feb 2026 dates and ~6-minute match durations. Confirmed: median match = 6.4 min. | Cast via `pa.int64()` in PyArrow before pandas touches it, bypassing the parquet schema's ms annotation. Treated as unix seconds throughout. |
| **Bot files missing** | 556 matches have `BotKill` events (human killed a bot) but zero `BotPosition` files for that match. | Bot parquet files simply weren't included in the dataset. Human files log `BotKill` when they kill a bot — the bot's own file records its movement. No fix possible without the files; flagged in Data Health tab. |
| **Duplicate rows** | 1,420 exact duplicate rows (2,701 rows involved). Not random — Loot (2,338), Position (294), BotKill (65), BotKilled (4). Duplicates decrease day-over-day (Feb 10: 1,231 → Feb 14: 116). Cross-date key check found 85 rows present in multiple date folders. | Dropped on key `(user_id, match_id_clean, ts_raw, event)`. Logged in Data Health with breakdown. |
| **Bot telemetry scope** | Bots only generate `BotPosition` events. No `BotLoot`, no storm deaths, no bot-vs-bot events. | By design or a telemetry gap — documented. Bot spatial analysis is limited to the 52/796 matches where bot files exist. |
| **Ghost events** | 177 events logged after a player's recorded death event across the dataset. | Normal in extraction shooters: position events buffer client-side and flush post-death, or spectator mode continues logging. Not treated as data corruption. |
| **Match composition** | 744 matches have only human players, 16 have only bots, 36 are mixed. Bot-only matches are likely automated test sessions. | Included as-is. Filters allow isolating human-only matches. |

---

## Major Tradeoffs

| Decision | What I considered | What I decided | Why |
|---|---|---|---|
| **Paths vs. heatmaps for multi-match views** | Rendering individual paths across 796 matches | Paths only on single-match selection; heatmaps for aggregate | 796 paths = unreadable noise. Heatmaps communicate aggregate behavior clearly. |
| **Animation approach** | `st.rerun()` per frame (5s reload) vs. Plotly native frames | Plotly `fig.frames` + `updatemenus` | Pre-computed frames run in browser JS — smooth, zero server cost. First compute ~3s, then cached. |
| **Event rendering** | Individual markers vs. clustered | Cluster grid (40×40 cells), markers scale by sqrt(count) | Individual markers overlap and become unreadable at scale. Clusters show density at a glance with count labels. |
| **Heatmap normalization** | Raw counts vs. % of total events | % of total events per type | Allows comparison across event types. All cells sum to 100%. Dead zones are transparent. |
| **Persistent data cache** | Re-parse 1,243 files every cold start (~25s) vs. write processed parquet once | Write `.cache_processed.parquet` on first run, read it (~1s) on all subsequent runs | 25× faster cold start. Tradeoff: cache must be deleted manually if source data changes. Documented in README. |
| **Heatmap bubble grid** | Top-N hotspot circles (overlapping, non-exhaustive) vs. fixed 8×8 grid | Fixed 8×8 grid — one circle per cell, all cells rendered | Top-N approach caused overlapping circles with no spatial consistency. 8×8 grid guarantees no overlap, cells sum to 100%, and spatial layout matches map quadrants. |
| **Streamlit vs. React** | Full frontend control vs. rapid iteration | Streamlit | Target users are designers, not web users. Faster to ship, easier to iterate. |
| **All data in memory** | Chunked loading vs. full load + cache | Full load + `st.cache_data` | 89k rows after dedup = ~50MB. Fine for this scale. Would need chunked loading at 10M+ rows. |

---

## What I'd Do Differently With More Time

- **Real-time playback controls** outside the Plotly figure (Streamlit's button styling can't override Plotly's built-in play button)
- **Storm zone overlay** — animate the shrinking play area as a circle on the map using match timing ( If I get the events for it )
- **Extraction point markers** — overlay known extraction locations to contextualize player routing ( Need an event )
- **Bot file re-ingestion** — request complete bot parquet files to enable bot-vs-bot encounter analysis
- **Per-session URL state** — shareable links that encode a specific map/match/filter state 
