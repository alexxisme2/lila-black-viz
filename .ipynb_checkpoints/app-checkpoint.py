"""
LILA BLACK — Level Designer Dashboard
Run:  streamlit run app.py
"""

import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from PIL import Image

from coordinate_utils import MAP_CONFIG
from data_loader import load_all_data

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="LILA BLACK — Level Designer Tool",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  [data-testid="stMetricValue"] { font-size: 1.4rem; }
  .stTabs [data-baseweb="tab"] { font-size: 1rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
MINIMAP_PATHS = {
    "AmbroseValley": os.path.join("minimaps", "AmbroseValley_Minimap.png"),
    "GrandRift":     os.path.join("minimaps", "GrandRift_Minimap.png"),
    "Lockdown":      os.path.join("minimaps", "Lockdown_Minimap.jpg"),
}

# Solid colors used everywhere
EVENT_COLORS = {
    "Position":      "#4488ff",
    "BotPosition":   "#888888",
    "Kill":          "#ff8800",
    "Killed":        "#ff2244",
    "BotKill":       "#ffee22",
    "BotKilled":     "#ff7744",
    "KilledByStorm": "#bb44ff",
    "Loot":          "#44ff99",
}

EVENT_SYMBOLS = {
    "Kill":          "star",
    "Killed":        "x",
    "BotKill":       "circle-open",
    "BotKilled":     "triangle-up",
    "KilledByStorm": "diamond",
    "Loot":          "square",
}

COMBAT_EVENTS = ["Kill", "Killed", "BotKill", "BotKilled", "KilledByStorm", "Loot"]

HEATMAP_EVENT_MAP = {
    "Traffic (All Movement)": ["Position", "BotPosition"],
    "Kill Zones":             ["Kill"],
    "Death Zones":            ["Killed", "KilledByStorm", "BotKilled"],
    "Storm Deaths":           ["KilledByStorm"],
    "Loot Pickups":           ["Loot"],
}


# ══════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════
st.title("🎮 LILA BLACK — Level Designer Dashboard")

with st.spinner("⏳ Loading match data… (first load ~30s, then cached)"):
    df_all = load_all_data()

if df_all.empty:
    st.error("❌ No data found. Place the `player_data/` folder in the project root and refresh.")
    st.info("Expected path: `player_data/February_10/`, `player_data/February_11/`, etc.")
    st.stop()

st.success(f"✅ Loaded **{len(df_all):,}** events across **{df_all['match_id_clean'].nunique()}** matches")


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — FILTERS
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.header("🗺️ Filters")

    # Map
    maps_available = sorted(df_all["map_id"].dropna().unique())
    selected_map = st.selectbox("Map", maps_available)
    df_map = df_all[df_all["map_id"] == selected_map]

    # Date
    dates_available = sorted(df_map["date"].unique())
    selected_dates = st.multiselect("Date(s)", dates_available, default=dates_available[:1])
    df_dated = df_map[df_map["date"].isin(selected_dates)] if selected_dates else df_map

    # Match
    matches_available = sorted(df_dated["match_id_clean"].unique())
    match_options = ["— All Matches —"] + matches_available
    selected_match = st.selectbox(f"Match ({len(matches_available)} available)", match_options)

    is_single = selected_match != "— All Matches —"
    df_view = (
        df_dated[df_dated["match_id_clean"] == selected_match].copy()
        if is_single
        else df_dated.copy()
    )

    st.divider()

    # Player type
    st.subheader("👤 Player Types")
    show_humans = st.checkbox("Humans", value=True)
    show_bots   = st.checkbox("Bots", value=False)

    if show_humans and not show_bots:
        df_view = df_view[df_view["is_human"]]
    elif show_bots and not show_humans:
        df_view = df_view[~df_view["is_human"]]
    elif not show_humans and not show_bots:
        df_view = df_view.iloc[0:0]

    st.divider()

    # Summary
    n_human  = int(df_view[df_view["is_human"]]["user_id"].nunique())
    n_bot    = int(df_view[~df_view["is_human"]]["user_id"].nunique())
    n_match  = int(df_view["match_id_clean"].nunique())
    st.markdown(f"""
    | | |
    |--|--|
    | Events | **{len(df_view):,}** |
    | Matches | **{n_match}** |
    | Humans | **{n_human}** |
    | Bots | **{n_bot}** |
    """)


# ══════════════════════════════════════════════════════════════════════════════
# HELPER — Build base Plotly figure with minimap background
# ══════════════════════════════════════════════════════════════════════════════
def build_base_fig(map_id: str, height: int = 680) -> go.Figure:
    """Creates a Plotly figure with the minimap as a background image."""
    fig = go.Figure()

    path = MINIMAP_PATHS.get(map_id, "")
    if os.path.exists(path):
        img = Image.open(path)
        fig.add_layout_image(dict(
            source=img,
            xref="x", yref="y",
            x=0, y=1024,         # top-left of image in plotly coords
            sizex=1024, sizey=1024,
            sizing="stretch",
            opacity=1.0,
            layer="below",
        ))
    else:
        st.warning(f"Minimap not found: {path}  —  place images in `minimaps/` folder.")

    fig.update_layout(
        xaxis=dict(range=[0, 1024], showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(range=[0, 1024], showgrid=False, showticklabels=False,
                   zeroline=False, scaleanchor="x"),
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        margin=dict(l=0, r=0, t=30, b=0),
        height=height,
        legend=dict(
            bgcolor="rgba(14,17,23,0.85)",
            font=dict(color="white", size=11),
            bordercolor="#444",
            borderwidth=1,
        ),
        uirevision="constant",  # preserve zoom when sliders update
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["🗺️ Player Journeys", "🔥 Heatmaps", "📊 Match Stats"])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — PLAYER JOURNEYS
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    map_col, ctrl_col = st.columns([4, 1])

    with ctrl_col:
        st.markdown("**Display**")
        show_paths  = st.checkbox("Movement paths", value=True,  key="j_paths")
        show_events = st.checkbox("Combat / loot events", value=True, key="j_events")

        st.markdown("---")

        # Timeline slider — only meaningful for a single match
        if is_single and not df_view.empty:
            ts_min = float(df_view["ts_relative"].min())
            ts_max = float(df_view["ts_relative"].max())
            st.markdown("**⏱️ Timeline**")
            if ts_max > ts_min:
                t_range = st.slider(
                    "Match time (s)",
                    min_value=ts_min,
                    max_value=ts_max,
                    value=(ts_min, ts_max),
                    step=5.0,
                    key="timeline",
                )
                df_time = df_view[
                    (df_view["ts_relative"] >= t_range[0]) &
                    (df_view["ts_relative"] <= t_range[1])
                ]
            else:
                df_time = df_view
                st.info("Only 1 timestamp in this match.")
        else:
            df_time = df_view
            if not is_single:
                st.info("Select a single match to enable the timeline slider and player paths.")

        # Legend
        st.markdown("---")
        st.markdown("**Legend**")
        for evt, color in EVENT_COLORS.items():
            if evt not in ("Position", "BotPosition"):
                st.markdown(
                    f'<span style="color:{color}; font-size:1.1rem">■</span> {evt}',
                    unsafe_allow_html=True,
                )
        st.markdown('<span style="color:#4488ff">─</span> Human path', unsafe_allow_html=True)
        st.markdown('<span style="color:#888">─</span> Bot path', unsafe_allow_html=True)

    with map_col:
        fig1 = build_base_fig(selected_map)

        # ── Movement Paths ────────────────────────────────────────────────────
        # Only draw paths for a single match — too noisy across all matches
        if show_paths and is_single:
            # Human paths — all in one trace using None separators (fast)
            pos_h = (
                df_time[df_time["event"] == "Position"]
                .sort_values(["user_id", "ts_relative"])
            )
            if not pos_h.empty:
                x_path, y_path = [], []
                for _, grp in pos_h.groupby("user_id", sort=False):
                    x_path.extend(grp["pixel_x"].tolist() + [None])
                    y_path.extend(grp["plot_y"].tolist()  + [None])

                fig1.add_trace(go.Scatter(
                    x=x_path, y=y_path,
                    mode="lines",
                    line=dict(color="rgba(68,136,255,0.5)", width=1.5),
                    name="Human Path",
                    hoverinfo="skip",
                ))

            # Bot paths
            pos_b = (
                df_time[df_time["event"] == "BotPosition"]
                .sort_values(["user_id", "ts_relative"])
            )
            if not pos_b.empty:
                x_path_b, y_path_b = [], []
                for _, grp in pos_b.groupby("user_id", sort=False):
                    x_path_b.extend(grp["pixel_x"].tolist() + [None])
                    y_path_b.extend(grp["plot_y"].tolist()  + [None])

                fig1.add_trace(go.Scatter(
                    x=x_path_b, y=y_path_b,
                    mode="lines",
                    line=dict(color="rgba(160,160,160,0.35)", width=1),
                    name="Bot Path",
                    hoverinfo="skip",
                ))

        # ── Combat & Loot Events ──────────────────────────────────────────────
        if show_events:
            df_combat = df_time[df_time["event"].isin(COMBAT_EVENTS)].dropna(
                subset=["pixel_x", "plot_y"]
            )
            for evt in COMBAT_EVENTS:
                evt_df = df_combat[df_combat["event"] == evt]
                if evt_df.empty:
                    continue

                hover = (
                    "<b>" + evt + "</b><br>"
                    + "Player: " + evt_df["user_id"].str[:16]
                    + "<br>Time: " + evt_df["ts_relative"].round(1).astype(str) + "s"
                )

                fig1.add_trace(go.Scatter(
                    x=evt_df["pixel_x"],
                    y=evt_df["plot_y"],
                    mode="markers",
                    marker=dict(
                        symbol=EVENT_SYMBOLS[evt],
                        size=10,
                        color=EVENT_COLORS[evt],
                        line=dict(width=1, color="rgba(255,255,255,0.5)"),
                    ),
                    name=evt,
                    text=hover,
                    hovertemplate="%{text}<extra></extra>",
                ))

        st.plotly_chart(fig1, use_container_width=True)

        if not is_single:
            st.caption("💡 *Movement paths shown for single matches only — too noisy at scale.*")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — HEATMAPS
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    map_col2, ctrl_col2 = st.columns([4, 1])

    with ctrl_col2:
        st.markdown("**Heatmap Type**")
        heatmap_option = st.radio(
            "Show density of:",
            list(HEATMAP_EVENT_MAP.keys()),
            label_visibility="collapsed",
        )
        st.markdown("---")
        colorscale = st.selectbox("Color Scale", ["Hot", "Plasma", "Viridis", "Reds", "YlOrRd"])
        opacity    = st.slider("Overlay Opacity", 0.2, 1.0, 0.55, step=0.05)
        bins       = st.slider("Resolution (bins)", 16, 128, 64, step=8)

    with map_col2:
        heat_events = HEATMAP_EVENT_MAP[heatmap_option]
        df_heat = df_view[df_view["event"].isin(heat_events)].dropna(
            subset=["pixel_x", "plot_y"]
        )

        fig2 = build_base_fig(selected_map)

        if df_heat.empty:
            st.warning(f"No '{heatmap_option}' events in the current selection.")
        else:
            px_arr = df_heat["pixel_x"].values
            py_arr = df_heat["plot_y"].values

            # 2D histogram in pixel space
            heat_grid, xedges, yedges = np.histogram2d(
                px_arr, py_arr,
                bins=bins,
                range=[[0, 1024], [0, 1024]],
            )
            heat_grid = heat_grid.T.astype(float)
            heat_grid[heat_grid == 0] = np.nan  # transparent empty cells

            x_centers = 0.5 * (xedges[:-1] + xedges[1:])
            y_centers = 0.5 * (yedges[:-1] + yedges[1:])

            fig2.add_trace(go.Heatmap(
                z=heat_grid,
                x=x_centers,
                y=y_centers,
                colorscale=colorscale,
                opacity=opacity,
                showscale=True,
                colorbar=dict(
                    title=dict(text="Density", font=dict(color="white")),
                    tickfont=dict(color="white"),
                ),
                hovertemplate="density: %{z:.0f}<extra></extra>",
            ))

            n_events = len(df_heat)
            fig2.update_layout(title=dict(
                text=f"<b>{heatmap_option}</b> — {selected_map} ({n_events:,} events)",
                font=dict(color="white", size=14),
                x=0.01,
            ))

            st.plotly_chart(fig2, use_container_width=True)

            # Top hotspot stats
            max_density = int(np.nanmax(heat_grid))
            st.caption(
                f"Peak density: **{max_density}** events/cell · "
                f"Total events plotted: **{n_events:,}**"
            )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — MATCH STATS
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    # ── Top Metrics ──────────────────────────────────────────────────────────
    kills        = int((df_view["event"] == "Kill").sum())
    deaths       = int((df_view["event"] == "Killed").sum())
    storm_deaths = int((df_view["event"] == "KilledByStorm").sum())
    bot_kills    = int((df_view["event"] == "BotKill").sum())
    loots        = int((df_view["event"] == "Loot").sum())

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Matches",      n_match)
    c2.metric("Human Players", n_human)
    c3.metric("Bots",         n_bot)
    c4.metric("H→H Kills",    kills)
    c5.metric("Storm Deaths", storm_deaths)
    c6.metric("Loot Events",  loots)

    st.divider()

    col_a, col_b = st.columns(2)

    # ── Event breakdown ───────────────────────────────────────────────────────
    with col_a:
        st.subheader("Event Breakdown")
        event_counts = df_view["event"].value_counts().reset_index()
        event_counts.columns = ["Event", "Count"]

        fig_bar = px.bar(
            event_counts, x="Event", y="Count",
            color="Event",
            color_discrete_map=EVENT_COLORS,
            template="plotly_dark",
        )
        fig_bar.update_layout(
            paper_bgcolor="#0e1117",
            plot_bgcolor="#161b22",
            showlegend=False,
            height=320,
            margin=dict(t=10, b=40),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Human vs Bot activity ─────────────────────────────────────────────────
    with col_b:
        st.subheader("Human vs Bot Activity")

        human_ec = df_view[df_view["is_human"]]["event"].value_counts()
        bot_ec   = df_view[~df_view["is_human"]]["event"].value_counts()

        all_evts = sorted(set(human_ec.index) | set(bot_ec.index))

        fig_cmp = go.Figure()
        fig_cmp.add_trace(go.Bar(
            x=all_evts,
            y=[human_ec.get(e, 0) for e in all_evts],
            name="Humans", marker_color="#4488ff",
        ))
        fig_cmp.add_trace(go.Bar(
            x=all_evts,
            y=[bot_ec.get(e, 0) for e in all_evts],
            name="Bots", marker_color="#888888",
        ))
        fig_cmp.update_layout(
            barmode="group",
            template="plotly_dark",
            paper_bgcolor="#0e1117",
            plot_bgcolor="#161b22",
            height=320,
            margin=dict(t=10, b=40),
            legend=dict(font=dict(color="white")),
        )
        st.plotly_chart(fig_cmp, use_container_width=True)

    st.divider()

    # ── Per-match summary table ───────────────────────────────────────────────
    st.subheader("Match Summary Table")

    match_summary = (
        df_view.groupby("match_id_clean")
        .agg(
            date=("date", "first"),
            map_id=("map_id", "first"),
            humans=("is_human", lambda x: x.sum() > 0),   # placeholder
            events=("event", "count"),
            kills=("event", lambda x: (x == "Kill").sum()),
            storm_deaths=("event", lambda x: (x == "KilledByStorm").sum()),
            loot=("event", lambda x: (x == "Loot").sum()),
            duration_s=("ts_relative", "max"),
        )
        .reset_index()
    )
    # Better human/bot counts
    human_per_match = (
        df_view[df_view["is_human"]]
        .groupby("match_id_clean")["user_id"].nunique()
        .rename("n_humans")
    )
    bot_per_match = (
        df_view[~df_view["is_human"]]
        .groupby("match_id_clean")["user_id"].nunique()
        .rename("n_bots")
    )
    match_summary = (
        match_summary
        .drop(columns="humans")
        .merge(human_per_match, on="match_id_clean", how="left")
        .merge(bot_per_match,   on="match_id_clean", how="left")
        .fillna(0)
    )
    match_summary["duration_s"] = match_summary["duration_s"].round(0).astype(int)
    match_summary = match_summary.rename(columns={
        "match_id_clean": "Match ID",
        "date":           "Date",
        "map_id":         "Map",
        "n_humans":       "Humans",
        "n_bots":         "Bots",
        "events":         "Total Events",
        "kills":          "H→H Kills",
        "storm_deaths":   "Storm Deaths",
        "loot":           "Loots",
        "duration_s":     "Duration (s)",
    })

    st.dataframe(
        match_summary.sort_values("Duration (s)", ascending=False),
        use_container_width=True,
        height=300,
    )

    # ── Single-match event timeline ───────────────────────────────────────────
    if is_single:
        st.divider()
        st.subheader("⏱️ Match Event Timeline")

        tl_df = df_view[df_view["event"].isin(COMBAT_EVENTS)].copy()
        if not tl_df.empty:
            tl_df["time_bin"] = (tl_df["ts_relative"] // 15 * 15).astype(int)
            tl_pivot = (
                tl_df.groupby(["time_bin", "event"])
                .size()
                .reset_index(name="count")
            )
            fig_tl = px.bar(
                tl_pivot, x="time_bin", y="count", color="event",
                color_discrete_map=EVENT_COLORS,
                labels={"time_bin": "Match Time (seconds)", "count": "Events"},
                template="plotly_dark",
                barmode="stack",
            )
            fig_tl.update_layout(
                paper_bgcolor="#0e1117",
                plot_bgcolor="#161b22",
                height=280,
                margin=dict(t=10, b=40),
                legend=dict(font=dict(color="white")),
            )
            st.plotly_chart(fig_tl, use_container_width=True)
    else:
        st.info("💡 Select a single match above to see its event timeline.")
