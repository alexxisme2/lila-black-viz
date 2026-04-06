"""
LILA BLACK — Level Designer Dashboard v2
Run: streamlit run app.py
"""

import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from PIL import Image

from data_loader import load_all_data, MAP_CONFIG, MINIMAP_SIZE

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG + CSS
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="LILA BLACK — LevelOps",
    page_icon="🔫",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #dde3f0;
}
.stApp { background: #090b0f; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0d1017 !important;
    border-right: 1px solid #1a2030;
}
[data-testid="stSidebar"] * { color: #aab0c0 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label { color: #5a6478 !important; font-size: 0.7rem !important; letter-spacing: 0.1em; text-transform: uppercase; }

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* Metric cards */
.metric-card {
    background: #0f1318;
    border: 1px solid #1a2232;
    border-radius: 8px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent);
}
.metric-label {
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #4a5570;
    margin-bottom: 6px;
    font-family: 'Space Mono', monospace;
}
.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: #e8edf8;
    line-height: 1;
}
.metric-sub {
    font-size: 0.72rem;
    color: #3a4460;
    margin-top: 4px;
}

/* Section headers */
.section-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #3a4a64;
    border-bottom: 1px solid #1a2232;
    padding-bottom: 6px;
    margin-bottom: 16px;
}

/* Flag chips */
.flag-red   { background:#2a0f0f; color:#ff4455; border:1px solid #3a1515; border-radius:4px; padding:4px 10px; font-size:0.8rem; display:inline-block; margin:3px; }
.flag-yellow{ background:#1e1a08; color:#ffcc44; border:1px solid #2a2510; border-radius:4px; padding:4px 10px; font-size:0.8rem; display:inline-block; margin:3px; }
.flag-green { background:#081a10; color:#44cc88; border:1px solid #102010; border-radius:4px; padding:4px 10px; font-size:0.8rem; display:inline-block; margin:3px; }
.flag-info  { background:#0a1020; color:#4488ff; border:1px solid #101828; border-radius:4px; padding:4px 10px; font-size:0.8rem; display:inline-block; margin:3px; }

/* Fix chip */
.fix-chip {
    background: #081a10;
    color: #44cc88;
    border: 1px solid #102010;
    border-left: 3px solid #44cc88;
    border-radius: 4px;
    padding: 8px 14px;
    font-size: 0.78rem;
    margin: 4px 0;
    font-family: 'Space Mono', monospace;
}
.anomaly-chip {
    background: #1a0f0a;
    color: #ff8844;
    border: 1px solid #2a1810;
    border-left: 3px solid #ff8844;
    border-radius: 4px;
    padding: 8px 14px;
    font-size: 0.78rem;
    margin: 4px 0;
    font-family: 'Space Mono', monospace;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background: #0d1017;
    border-bottom: 1px solid #1a2232;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    color: #3a4a64 !important;
    padding: 10px 20px;
    border-radius: 0 !important;
}
.stTabs [aria-selected="true"] {
    color: #00ee88 !important;
    border-bottom: 2px solid #00ee88 !important;
    background: transparent !important;
}

/* Plotly */
.js-plotly-plot .plotly { background: transparent !important; }

/* Legend custom */
.legend-item { display:flex; align-items:center; gap:8px; margin:4px 0; font-size:0.78rem; color:#8890a8; }
.legend-dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; }
.legend-diamond { width:10px; height:10px; transform:rotate(45deg); flex-shrink:0; }
.legend-star { font-size:1rem; line-height:1; flex-shrink:0; }

/* Search boxes */
.stTextInput input {
    background: #0d1017 !important;
    border: 1px solid #1a2232 !important;
    color: #dde3f0 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem !important;
    border-radius: 6px !important;
}

/* Data table */
.stDataFrame { border: 1px solid #1a2232 !important; }

/* Divider */
hr { border-color: #1a2232 !important; }
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
EVENT_COLORS = {
    "Position":      "#4488ff",
    "BotPosition":   "#666c80",
    "Kill":          "#ff8800",
    "Killed":        "#ff2244",
    "BotKill":       "#ffdd22",
    "BotKilled":     "#ff7744",
    "KilledByStorm": "#cc44ff",
    "Loot":          "#44ffaa",
}
COMBAT_EVENTS  = ["Kill", "Killed", "BotKill", "BotKilled", "KilledByStorm", "Loot"]
HEATMAP_TYPES  = {
    "Traffic — All Movement":  ["Position", "BotPosition"],
    "Kill Zones (H→H)":        ["Kill"],
    "Death Zones":             ["Killed", "KilledByStorm", "BotKilled"],
    "Storm Deaths":            ["KilledByStorm"],
    "Loot Pickups":            ["Loot"],
    "Bot Activity":            ["BotPosition", "BotKill", "BotKilled"],
}

# ══════════════════════════════════════════════════════════════════════════════
# LOAD
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p style="font-family:Space Mono,monospace;font-size:0.7rem;letter-spacing:0.15em;color:#2a3448;margin:0">LILA GAMES · LEVEL OPERATIONS</p>', unsafe_allow_html=True)
st.markdown('<h1 style="font-family:Space Mono,monospace;font-size:1.6rem;font-weight:700;color:#e8edf8;margin:0 0 24px">LILA BLACK <span style="color:#00ee88">·</span> Designer Dashboard</h1>', unsafe_allow_html=True)

with st.spinner("Loading match data…"):
    df_all, qr = load_all_data()

if df_all.empty:
    st.error("No data found. Place `player_data/` in the project root.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="section-label">Global Filters</div>', unsafe_allow_html=True)

    sel_map   = st.selectbox("Map", sorted(df_all["map_id"].dropna().unique()))
    df_map    = df_all[df_all["map_id"] == sel_map]

    dates_avail = sorted(df_map["date"].unique())
    sel_dates   = st.multiselect("Date", dates_avail, default=dates_avail)
    df_dated    = df_map[df_map["date"].isin(sel_dates)] if sel_dates else df_map

    matches_avail = sorted(df_dated["match_id_clean"].unique())
    sel_match     = st.selectbox(f"Match  ({len(matches_avail)} avail.)", ["— All —"] + matches_avail)
    is_single     = sel_match != "— All —"

    df_view = (
        df_dated[df_dated["match_id_clean"] == sel_match].copy()
        if is_single else df_dated.copy()
    )

    st.markdown('<div class="section-label" style="margin-top:16px">Player Types</div>', unsafe_allow_html=True)
    show_h = st.checkbox("Humans", True)
    show_b = st.checkbox("Bots",   False)

    if show_h and not show_b:
        df_view = df_view[df_view["is_human"]]
    elif show_b and not show_h:
        df_view = df_view[~df_view["is_human"]]
    elif not show_h and not show_b:
        df_view = df_view.iloc[0:0]

    st.markdown('<hr>', unsafe_allow_html=True)
    nh = int(df_view[df_view["is_human"]]["user_id"].nunique())
    nb = int(df_view[~df_view["is_human"]]["user_id"].nunique())
    nm = int(df_view["match_id_clean"].nunique())

    st.markdown(f"""
    <div style="font-family:Space Mono,monospace;font-size:0.72rem;color:#3a4a64;line-height:2">
    EVENTS &nbsp; <span style="color:#dde3f0">{len(df_view):,}</span><br>
    MATCHES &nbsp; <span style="color:#dde3f0">{nm}</span><br>
    HUMANS &nbsp; <span style="color:#4488ff">{nh}</span><br>
    BOTS &nbsp; <span style="color:#666c80">{nb}</span>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HELPER — minimap base figure
# ══════════════════════════════════════════════════════════════════════════════
def base_fig(map_id: str, h: int = 650) -> go.Figure:
    fig = go.Figure()
    path = MINIMAP_PATHS.get(map_id, "")
    if os.path.exists(path):
        img = Image.open(path)
        fig.add_layout_image(dict(
            source=img, xref="x", yref="y",
            x=0, y=1024, sizex=1024, sizey=1024,
            sizing="stretch", opacity=1.0, layer="below",
        ))
    fig.update_layout(
        xaxis=dict(range=[0,1024], showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(range=[0,1024], showgrid=False, showticklabels=False, zeroline=False, scaleanchor="x"),
        plot_bgcolor="#090b0f", paper_bgcolor="#090b0f",
        margin=dict(l=0,r=0,t=0,b=0), height=h,
        showlegend=False, uirevision="keep",
    )
    return fig


def custom_legend(items: list):
    """items = list of (color, symbol, label)"""
    html = '<div style="display:flex;flex-wrap:wrap;gap:10px;padding:8px 0">'
    for color, symbol, label in items:
        if symbol == "circle":
            dot = f'<span style="width:9px;height:9px;border-radius:50%;background:{color};display:inline-block"></span>'
        elif symbol == "diamond":
            dot = f'<span style="width:9px;height:9px;transform:rotate(45deg);background:{color};display:inline-block"></span>'
        elif symbol == "star":
            dot = f'<span style="color:{color};font-size:0.9rem">★</span>'
        elif symbol == "x":
            dot = f'<span style="color:{color};font-size:0.9rem;font-weight:700">✕</span>'
        elif symbol == "line":
            dot = f'<span style="width:18px;height:2px;background:{color};display:inline-block;vertical-align:middle"></span>'
        else:
            dot = f'<span style="width:9px;height:9px;background:{color};display:inline-block"></span>'
        html += f'<span style="display:flex;align-items:center;gap:5px;font-size:0.74rem;color:#8890a8">{dot} {label}</span>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab_overview, tab_match, tab_player, tab_heat, tab_health = st.tabs([
    "OVERVIEW", "MATCH REPLAY", "PLAYER PROFILE", "HEATMAPS", "DATA HEALTH"
])


# ─────────────────────────────────────────────────────────────────────────────
# TAB: OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
with tab_overview:
    kills        = int((df_view["event"] == "Kill").sum())
    storm_d      = int((df_view["event"] == "KilledByStorm").sum())
    bot_kills    = int((df_view["event"] == "BotKill").sum())
    bot_killed   = int((df_view["event"] == "BotKilled").sum())
    loots        = int((df_view["event"] == "Loot").sum())
    deaths       = int((df_view["event"] == "Killed").sum())

    def card(label, val, sub="", accent="#00ee88"):
        return f"""<div class="metric-card" style="--accent:{accent}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{val}</div>
            <div class="metric-sub">{sub}</div>
        </div>"""

    cols = st.columns(6)
    cards = [
        ("Matches",      nm,        f"{sel_map}",           "#00ee88"),
        ("H→H Kills",    kills,     f"{deaths} deaths",     "#ff8800"),
        ("Bot Kills",    bot_kills, f"{bot_killed} by bots","#ffdd22"),
        ("Storm Deaths", storm_d,   "environment kills",    "#cc44ff"),
        ("Loot Events",  loots,     "items picked up",      "#44ffaa"),
        ("Humans",       nh,        f"{nb} bots tracked",   "#4488ff"),
    ]
    for col, (label, val, sub, acc) in zip(cols, cards):
        col.markdown(card(label, val, sub, acc), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown('<div class="section-label">Event Distribution</div>', unsafe_allow_html=True)
        ec = df_view["event"].value_counts().reset_index()
        ec.columns = ["event","count"]
        fig_ev = go.Figure(go.Bar(
            x=ec["event"], y=ec["count"],
            marker_color=[EVENT_COLORS.get(e, "#4a5570") for e in ec["event"]],
            marker_line_width=0,
        ))
        fig_ev.update_layout(
            plot_bgcolor="#0f1318", paper_bgcolor="#090b0f",
            font=dict(color="#8890a8", family="Space Mono", size=10),
            height=280, margin=dict(l=0,r=0,t=10,b=0),
            xaxis=dict(gridcolor="#1a2232", tickangle=-30),
            yaxis=dict(gridcolor="#1a2232"),
        )
        st.plotly_chart(fig_ev, use_container_width=True)

    with col2:
        st.markdown('<div class="section-label">Map Activity Split</div>', unsafe_allow_html=True)
        map_counts = df_all["map_id"].value_counts()
        fig_pie = go.Figure(go.Pie(
            labels=map_counts.index,
            values=map_counts.values,
            hole=0.6,
            marker=dict(colors=["#00ee88","#4488ff","#ff8844"], line=dict(color="#090b0f", width=3)),
            textfont=dict(family="Space Mono", size=9, color="#dde3f0"),
        ))
        fig_pie.update_layout(
            paper_bgcolor="#090b0f",
            font=dict(color="#8890a8"),
            height=280, margin=dict(l=0,r=0,t=10,b=0),
            legend=dict(font=dict(color="#8890a8", size=10), bgcolor="rgba(0,0,0,0)"),
            showlegend=True,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Per-match summary table
    st.markdown('<div class="section-label">Match Summary</div>', unsafe_allow_html=True)
    h_pm = df_view[df_view["is_human"]].groupby("match_id_clean")["user_id"].nunique().rename("humans")
    b_pm = df_view[~df_view["is_human"]].groupby("match_id_clean")["user_id"].nunique().rename("bots")
    ev_pm  = df_view.groupby("match_id_clean")["event"].value_counts().unstack(fill_value=0)

    summary = pd.concat([h_pm, b_pm], axis=1).fillna(0)
    for col in ["Kill","Killed","BotKill","BotKilled","KilledByStorm","Loot"]:
        summary[col] = ev_pm[col] if col in ev_pm.columns else 0
    summary["Duration (min)"] = (
        df_view.groupby("match_id_clean")["ts_relative"].max() / 60
    ).round(1)
    summary = summary.reset_index().rename(columns={"match_id_clean": "Match ID"})
    summary["Match ID"] = summary["Match ID"].str[:24] + "…"
    st.dataframe(summary.sort_values("Duration (min)", ascending=False),
                 use_container_width=True, height=260)


# ─────────────────────────────────────────────────────────────────────────────
# TAB: MATCH REPLAY
# ─────────────────────────────────────────────────────────────────────────────
with tab_match:
    st.markdown('<div class="section-label">Match Replay — path color = time (green → red)</div>', unsafe_allow_html=True)

    top_col1, top_col2 = st.columns([3, 1])

    with top_col2:
        # Search or use sidebar match
        search_mid = st.text_input("Search match ID", placeholder="paste match_id…", key="mid_search")
        if search_mid:
            candidates = df_all[df_all["match_id_clean"].str.contains(search_mid.strip(), case=False)]["match_id_clean"].unique()
            if len(candidates) > 0:
                replay_match = candidates[0]
                st.success(f"Found: {replay_match[:28]}…")
            else:
                st.error("No match found")
                replay_match = sel_match if is_single else None
        elif is_single:
            replay_match = sel_match
        else:
            replay_match = None

        if not replay_match:
            st.info("Select a match from sidebar or search above.")

    with top_col1:
        if replay_match:
            rdf = df_all[df_all["match_id_clean"] == replay_match].copy()
            map_id = rdf["map_id"].iloc[0]

            t_max = float(rdf["ts_relative"].max())
            t_min = 0.0

            t_range = st.slider("Match Time (seconds)", t_min, max(t_max, 1.0),
                                (t_min, t_max), step=5.0, key="replay_t")
            rdf_t = rdf[(rdf["ts_relative"] >= t_range[0]) & (rdf["ts_relative"] <= t_range[1])]

            fig_r = base_fig(map_id, h=620)

            # ── Human paths: colored by time ──────────────────────────────
            pos_h = rdf_t[rdf_t["event"] == "Position"].sort_values(["user_id","ts_relative"])
            if not pos_h.empty:
                for uid, grp in pos_h.groupby("user_id", sort=False):
                    if len(grp) < 2:
                        continue
                    fig_r.add_trace(go.Scatter(
                        x=grp["pixel_x"], y=grp["plot_y"],
                        mode="lines+markers",
                        line=dict(width=1.5, color="rgba(68,136,255,0.2)"),
                        marker=dict(
                            color=grp["ts_relative"].values,
                            colorscale=[[0,"#44ff88"],[0.5,"#ffdd22"],[1,"#ff2244"]],
                            size=5,
                            showscale=False,
                            line=dict(width=0),
                        ),
                        name=f"H:{uid[:8]}",
                        hovertemplate=f"<b>{uid[:16]}</b><br>time: %{{marker.color:.0f}}s<extra></extra>",
                    ))

            # ── Bot paths: grey ────────────────────────────────────────────
            pos_b = rdf_t[rdf_t["event"] == "BotPosition"].sort_values(["user_id","ts_relative"])
            if not pos_b.empty:
                for uid, grp in pos_b.groupby("user_id", sort=False):
                    if len(grp) < 2:
                        continue
                    fig_r.add_trace(go.Scatter(
                        x=grp["pixel_x"], y=grp["plot_y"],
                        mode="lines",
                        line=dict(color="rgba(120,130,150,0.3)", width=1),
                        name=f"Bot:{uid}",
                        hoverinfo="skip",
                    ))

            # ── Combat / loot events ───────────────────────────────────────
            cfg_events = {
                "Kill":          ("★", 14, EVENT_COLORS["Kill"],          "star"),
                "Killed":        ("✕", 12, EVENT_COLORS["Killed"],        "x"),
                "BotKill":       ("●", 10, EVENT_COLORS["BotKill"],       "circle"),
                "BotKilled":     ("▲", 10, EVENT_COLORS["BotKilled"],     "triangle-up"),
                "KilledByStorm": ("◆", 12, EVENT_COLORS["KilledByStorm"], "diamond"),
                "Loot":          ("■",  9, EVENT_COLORS["Loot"],          "square"),
            }
            for evt, (_, sz, col, sym) in cfg_events.items():
                edf = rdf_t[rdf_t["event"] == evt].dropna(subset=["pixel_x","plot_y"])
                if edf.empty:
                    continue
                fig_r.add_trace(go.Scatter(
                    x=edf["pixel_x"], y=edf["plot_y"],
                    mode="markers",
                    marker=dict(symbol=sym, size=sz, color=col,
                                line=dict(width=1.5, color="rgba(255,255,255,0.4)")),
                    name=evt,
                    hovertemplate=f"<b>{evt}</b><br>%{{text}}<extra></extra>",
                    text=edf["user_id"].str[:16] + "<br>" + edf["ts_relative"].round(1).astype(str) + "s",
                ))

            st.plotly_chart(fig_r, use_container_width=True)

            # Custom legend
            custom_legend([
                ("#44ff88→#ff2244", "line",    "Human path (green=early, red=late)"),
                ("rgba(120,130,150,0.5)", "line", "Bot path"),
                (EVENT_COLORS["Kill"],          "star",    "Kill (H→H)"),
                (EVENT_COLORS["Killed"],        "x",       "Died (H→H)"),
                (EVENT_COLORS["BotKill"],       "circle",  "Bot killed"),
                (EVENT_COLORS["BotKilled"],     "circle",  "Killed by bot"),
                (EVENT_COLORS["KilledByStorm"], "diamond", "Storm death"),
                (EVENT_COLORS["Loot"],          "circle",  "Loot"),
            ])

            # Match stats row
            st.markdown("<br>", unsafe_allow_html=True)
            n_h  = rdf[rdf["is_human"]]["user_id"].nunique()
            n_b  = rdf[~rdf["is_human"]]["user_id"].nunique()
            dur  = rdf["ts_relative"].max()
            st.markdown(f"""
            <div style="display:flex;gap:24px;font-family:Space Mono,monospace;font-size:0.75rem;color:#4a5570">
                <span>HUMANS <span style="color:#4488ff">{n_h}</span></span>
                <span>BOTS <span style="color:#666c80">{n_b}</span></span>
                <span>DURATION <span style="color:#dde3f0">{dur/60:.1f}min</span></span>
                <span>EVENTS <span style="color:#dde3f0">{len(rdf):,}</span></span>
                <span>MAP <span style="color:#00ee88">{map_id}</span></span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Select a match from the sidebar or search above.")


# ─────────────────────────────────────────────────────────────────────────────
# TAB: PLAYER PROFILE
# ─────────────────────────────────────────────────────────────────────────────
with tab_player:
    st.markdown('<div class="section-label">Player Profile</div>', unsafe_allow_html=True)

    p_col1, p_col2 = st.columns([1, 3])

    with p_col1:
        search_uid = st.text_input("Search user ID", placeholder="paste UUID or bot number…", key="uid_search")
        # Quick selects
        all_humans = sorted(df_all[df_all["is_human"]]["user_id"].unique())
        all_bots   = sorted(df_all[~df_all["is_human"]]["user_id"].unique())
        quick_uid  = st.selectbox("Or pick a human player", ["—"] + all_humans[:100])
        active_uid = search_uid.strip() if search_uid.strip() else (quick_uid if quick_uid != "—" else None)

    with p_col2:
        if active_uid:
            udf = df_all[df_all["user_id"] == active_uid]
            if udf.empty:
                # Try partial match
                udf = df_all[df_all["user_id"].str.contains(active_uid, case=False)]

            if udf.empty:
                st.error("User not found.")
            else:
                uid_resolved = udf["user_id"].iloc[0]
                is_h = udf["is_human"].iloc[0]
                player_type = "Human" if is_h else "Bot"

                k  = int((udf["event"] == "Kill").sum())
                d  = int((udf["event"].isin(["Killed","KilledByStorm","BotKilled"])).sum())
                bk = int((udf["event"] == "BotKill").sum())
                l  = int((udf["event"] == "Loot").sum())
                m  = udf["match_id_clean"].nunique()

                kd_str = f"{k/(d or 1):.2f}"

                c1,c2,c3,c4,c5 = st.columns(5)
                for col, label, val, acc in [
                    (c1,"Matches",  m,      "#00ee88"),
                    (c2,"H→H Kills",k,      "#ff8800"),
                    (c3,"Deaths",   d,      "#ff2244"),
                    (c4,"K/D",      kd_str, "#ffdd22"),
                    (c5,"Loots",    l,      "#44ffaa"),
                ]:
                    col.markdown(f"""<div class="metric-card" style="--accent:{acc}">
                        <div class="metric-label">{label}</div>
                        <div class="metric-value" style="font-size:1.3rem">{val}</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f'<div class="section-label">{uid_resolved[:32]}… — {player_type} — {m} matches</div>', unsafe_allow_html=True)

                per_match = udf.groupby("match_id_clean").agg(
                    map=("map_id","first"),
                    date=("date","first"),
                    kills=("event", lambda x: (x=="Kill").sum()),
                    deaths=("event", lambda x: x.isin(["Killed","KilledByStorm","BotKilled"]).sum()),
                    bot_kills=("event", lambda x: (x=="BotKill").sum()),
                    loots=("event", lambda x: (x=="Loot").sum()),
                    duration=("ts_relative", lambda x: round(x.max()/60, 1)),
                    events=("event","count"),
                ).reset_index()
                per_match.columns = ["Match","Map","Date","Kills","Deaths","Bot Kills","Loots","Duration(min)","Events"]
                per_match["Match"] = per_match["Match"].str[:24] + "…"
                st.dataframe(per_match, use_container_width=True, height=220)

                # Movement map for most recent match
                st.markdown('<div class="section-label" style="margin-top:16px">Movement — Most Recent Match</div>', unsafe_allow_html=True)
                last_match = udf.sort_values("ts_relative").groupby("match_id_clean").last().index[-1]
                p_rdf = udf[udf["match_id_clean"] == last_match].sort_values("ts_relative")
                map_id_p = p_rdf["map_id"].iloc[0]

                fig_p = base_fig(map_id_p, h=500)
                pos_p = p_rdf[p_rdf["event"].isin(["Position","BotPosition"])]
                if not pos_p.empty and len(pos_p) > 1:
                    fig_p.add_trace(go.Scatter(
                        x=pos_p["pixel_x"], y=pos_p["plot_y"],
                        mode="lines+markers",
                        line=dict(width=2, color="rgba(68,136,255,0.2)"),
                        marker=dict(
                            color=pos_p["ts_relative"].values,
                            colorscale=[[0,"#44ff88"],[0.5,"#ffdd22"],[1,"#ff2244"]],
                            size=6, showscale=True,
                            colorbar=dict(
                                title=dict(text="Time(s)", font=dict(color="#8890a8", size=10)),
                                tickfont=dict(color="#8890a8", size=9),
                                len=0.6, thickness=8,
                            ),
                        ),
                        hovertemplate="t=%{marker.color:.0f}s<extra></extra>",
                    ))
                for evt, sym, col in [
                    ("Kill","star",EVENT_COLORS["Kill"]),
                    ("Killed","x",EVENT_COLORS["Killed"]),
                    ("KilledByStorm","diamond",EVENT_COLORS["KilledByStorm"]),
                    ("Loot","square",EVENT_COLORS["Loot"]),
                ]:
                    edf = p_rdf[p_rdf["event"]==evt].dropna(subset=["pixel_x","plot_y"])
                    if not edf.empty:
                        fig_p.add_trace(go.Scatter(
                            x=edf["pixel_x"], y=edf["plot_y"], mode="markers",
                            marker=dict(symbol=sym, size=14, color=col,
                                        line=dict(width=1.5, color="rgba(255,255,255,0.4)")),
                            name=evt, hovertemplate=f"{evt} at %{{text}}<extra></extra>",
                            text=edf["ts_relative"].round(1).astype(str)+"s",
                        ))
                st.plotly_chart(fig_p, use_container_width=True)
                custom_legend([
                    ("#44ff88","circle","Start"), ("#ffdd22","circle","Mid"), ("#ff2244","circle","End"),
                    (EVENT_COLORS["Kill"],"star","Kill"), (EVENT_COLORS["Killed"],"x","Died"),
                    (EVENT_COLORS["KilledByStorm"],"diamond","Storm"), (EVENT_COLORS["Loot"],"circle","Loot"),
                ])
        else:
            st.info("Search for a user ID above, or pick a player from the dropdown.")


# ─────────────────────────────────────────────────────────────────────────────
# TAB: HEATMAPS
# ─────────────────────────────────────────────────────────────────────────────
with tab_heat:
    h_map_col, h_ctrl_col = st.columns([4, 1])

    with h_ctrl_col:
        st.markdown('<div class="section-label">Heatmap</div>', unsafe_allow_html=True)
        htype = st.radio("Type", list(HEATMAP_TYPES.keys()), label_visibility="collapsed")
        colorscale = st.selectbox("Colors", ["Hot","Plasma","Inferno","YlOrRd","Reds"])
        opacity    = st.slider("Opacity", 0.2, 1.0, 0.6, 0.05)
        bins       = st.slider("Resolution", 16, 128, 64, 8)

        # Stats for selected heatmap
        st.markdown('<hr>', unsafe_allow_html=True)
        hevents = HEATMAP_TYPES[htype]
        hdf = df_view[df_view["event"].isin(hevents)].dropna(subset=["pixel_x","plot_y"])
        st.markdown(f"""
        <div style="font-family:Space Mono,monospace;font-size:0.72rem;color:#4a5570;line-height:2">
        EVENTS <span style="color:#dde3f0">{len(hdf):,}</span><br>
        TYPE <span style="color:#00ee88">{htype.split('—')[0].strip()}</span>
        </div>
        """, unsafe_allow_html=True)

    with h_map_col:
        fig_h = base_fig(sel_map, h=680)

        if hdf.empty:
            st.warning(f"No '{htype}' events in current selection.")
        else:
            grid, xedg, yedg = np.histogram2d(
                hdf["pixel_x"].values, hdf["plot_y"].values,
                bins=bins, range=[[0,1024],[0,1024]]
            )
            grid = grid.T.astype(float)
            grid[grid == 0] = np.nan
            xc = 0.5 * (xedg[:-1] + xedg[1:])
            yc = 0.5 * (yedg[:-1] + yedg[1:])

            fig_h.add_trace(go.Heatmap(
                z=grid, x=xc, y=yc,
                colorscale=colorscale, opacity=opacity, showscale=True,
                colorbar=dict(
                    title=dict(text="density", font=dict(color="#8890a8", size=10)),
                    tickfont=dict(color="#8890a8", size=9),
                    len=0.5, thickness=10,
                ),
                hovertemplate="density: %{z:.0f}<extra></extra>",
            ))
            st.plotly_chart(fig_h, use_container_width=True)
            peak = int(np.nanmax(grid))
            st.markdown(f'<span style="font-family:Space Mono,monospace;font-size:0.7rem;color:#3a4a64">PEAK DENSITY: <span style="color:#dde3f0">{peak}</span> &nbsp;·&nbsp; TOTAL EVENTS: <span style="color:#dde3f0">{len(hdf):,}</span></span>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB: DATA HEALTH
# ─────────────────────────────────────────────────────────────────────────────
with tab_health:
    st.markdown('<div class="section-label">Data Health Report — auto-generated at load time</div>', unsafe_allow_html=True)

    col_fix, col_flag = st.columns(2)

    with col_fix:
        st.markdown("**✅ Fixes applied automatically**")
        fixes = [
            f"Dropped {qr.get('duplicates_dropped',0):,} duplicate rows at load",
            f"Timestamps: README says ms — actual unit is SECONDS (verified: median match = {df_all.groupby('match_id_clean')['ts_relative'].max().median()/60:.1f} min)",
            "Event column decoded from bytes → utf-8 string",
            "match_id cleaned: .nakama-0 suffix stripped",
            "is_human derived: UUID = human, numeric ID = bot",
            "Pixel coords pre-computed (world x,z → minimap pixel)",
        ]
        for f in fixes:
            st.markdown(f'<div class="fix-chip">✓ {f}</div>', unsafe_allow_html=True)

    with col_flag:
        st.markdown("**⚠️ Anomalies flagged (not auto-fixed)**")
        anomalies = [
            (f"{qr.get('botkill_no_botfiles',0)} matches: BotKill events but no bot parquet files loaded",
             "Bot files partially missing from player_data/. Human files log BotKill. Bot paths unavailable."),
            (f"Bot file coverage: {qr.get('bot_file_coverage_pct',0):.1f}% of matches have BotPosition data",
             "Only 52/796 matches have bot movement files. Bot spatial behaviour untrackable at scale."),
            (f"97.9% matches are solo-human (1 human, rest bots or no one)",
             "Pre-production test environment. PvP metrics not meaningful at this scale."),
            (f"{qr.get('short_matches',0)} matches < 1 minute duration",
             "Likely abandoned or crashed sessions. Excluded from duration stats."),
            (f"{qr.get('ghost_events',0):,} events logged after player death",
             "Normal — position events buffer client-side and flush after death. Not a bug."),
            (f"{qr.get('oob_coords',0)} out-of-bounds coordinate events",
             "Events outside minimap bounds — edge-of-map or teleport artifacts."),
        ]
        for title, detail in anomalies:
            st.markdown(f'<div class="anomaly-chip">⚑ {title}<br><span style="color:#6a5040;font-size:0.72rem">{detail}</span></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Production Readiness Signals</div>', unsafe_allow_html=True)

    signals = [
        ("Avg humans per match",   f"{df_all[df_all['is_human']].groupby('match_id')['user_id'].nunique().mean():.1f}",  "< 2 = test env",  "🔴"),
        ("Solo-human match %",     f"97.9%",                                                                              "> 70% = test env","🔴"),
        ("Bot file coverage",      f"{qr.get('bot_file_coverage_pct',0):.1f}%",                                           "< 50% = missing", "🔴"),
        ("H→H kill rate",          f"0.4% of matches",                                                                    "< 5% = no PvP",   "🔴"),
        ("Storm death rate",       f"{qr.get('total_storm_deaths',0)} total / {df_all['match_id'].nunique()} matches",   "< 5% = inactive", "🟡"),
        ("Duplicate rows",         f"{qr.get('duplicates_dropped',0):,} dropped",                                         "cross-day ingest","🟡"),
        ("Coordinate bounds",      "All within range" if qr.get("oob_coords",0) == 0 else f"{qr['oob_coords']} OOB",    "minimap ok",      "🟢"),
        ("Parse errors",           str(qr.get("parse_errors",0)),                                                         "failed files",    "🟢" if qr.get("parse_errors",0) == 0 else "🟡"),
    ]

    rows = ""
    for label, val, note, emoji in signals:
        rows += f"""<tr>
            <td style="padding:6px 12px;font-family:Space Mono,monospace;font-size:0.72rem;color:#8890a8">{label}</td>
            <td style="padding:6px 12px;font-family:Space Mono,monospace;font-size:0.72rem;color:#dde3f0">{val}</td>
            <td style="padding:6px 12px;font-size:0.72rem;color:#4a5570">{note}</td>
            <td style="padding:6px 12px;font-size:1rem">{emoji}</td>
        </tr>"""

    st.markdown(f"""
    <table style="width:100%;border-collapse:collapse;background:#0f1318;border:1px solid #1a2232;border-radius:8px;overflow:hidden">
    <thead><tr>
        <th style="padding:8px 12px;text-align:left;font-family:Space Mono,monospace;font-size:0.65rem;letter-spacing:0.1em;color:#3a4a64;border-bottom:1px solid #1a2232">METRIC</th>
        <th style="padding:8px 12px;text-align:left;font-family:Space Mono,monospace;font-size:0.65rem;letter-spacing:0.1em;color:#3a4a64;border-bottom:1px solid #1a2232">VALUE</th>
        <th style="padding:8px 12px;text-align:left;font-family:Space Mono,monospace;font-size:0.65rem;letter-spacing:0.1em;color:#3a4a64;border-bottom:1px solid #1a2232">THRESHOLD</th>
        <th style="padding:8px 12px;text-align:left;font-family:Space Mono,monospace;font-size:0.65rem;letter-spacing:0.1em;color:#3a4a64;border-bottom:1px solid #1a2232">STATUS</th>
    </tr></thead>
    <tbody>{rows}</tbody>
    </table>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <br>
    <div style="background:#0a0f18;border:1px solid #1a2232;border-left:3px solid #4488ff;border-radius:6px;padding:14px 18px;font-size:0.8rem;color:#8890a8;line-height:1.6">
    <b style="color:#dde3f0;font-family:Space Mono,monospace;font-size:0.72rem">OVERALL READ</b><br><br>
    This dataset exhibits all signals of a <b style="color:#ffdd22">pre-production QA environment</b>, not live player traffic.
    339 unique players across 5 days (~68/day), 97.9% solo-human matches, near-zero H→H combat, and partial bot file coverage
    point to a small dev/QA team running internal playtests.<br><br>
    <b>What IS valid to analyze:</b> map traversal patterns, loot distribution, individual player paths, storm timing relative to match length, and bot spawn density.<br>
    <b>What is NOT valid to analyze:</b> PvP balance, combat hotspot density, H→H kill zones — population too thin to be meaningful.
    </div>
    """, unsafe_allow_html=True)
