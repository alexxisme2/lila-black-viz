"""
LILA BLACK — Level Designer Dashboard v3
Run: streamlit run app.py
"""

import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

from data_loader import load_all_data, MAP_CONFIG, MINIMAP_SIZE

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG + CSS
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="LILA BLACK · LevelOps",
    page_icon="🔫",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family:'Inter',sans-serif; color:#c8d0e0; }
.stApp { background:#07090d; }
#MainMenu,footer,header,[data-testid="stToolbar"]{ display:none!important; }

/* Sidebar */
[data-testid="stSidebar"]{ background:#090c12!important; border-right:1px solid #141c28; }
[data-testid="stSidebar"] *{ color:#8090a8!important; }
[data-testid="stSidebar"] h1,h2,h3{ color:#c8d0e0!important; }
.stSelectbox>div>div, .stMultiSelect>div>div{
    background:#0d1118!important; border:1px solid #1a2235!important;
    color:#c8d0e0!important; border-radius:6px!important;
}
.stCheckbox label{ color:#8090a8!important; font-size:0.82rem!important; }

/* Inputs */
.stTextInput input{
    background:#0d1118!important; border:1px solid #1a2235!important;
    color:#c8d0e0!important; font-family:'IBM Plex Mono',monospace!important;
    font-size:0.78rem!important; border-radius:6px!important;
}
.stSlider [data-baseweb="slider"]{ background:#141c28!important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"]{
    background:#090c12; border-bottom:1px solid #141c28; gap:0; padding:0 4px;
}
.stTabs [data-baseweb="tab"]{
    font-family:'IBM Plex Mono',monospace; font-size:0.68rem; letter-spacing:0.1em;
    color:#3a4a64!important; padding:10px 18px; border-radius:0!important;
    border-bottom:2px solid transparent!important;
}
.stTabs [aria-selected="true"]{
    color:#00e57a!important; border-bottom:2px solid #00e57a!important;
    background:transparent!important;
}

/* Metric card */
.mc{
    background:#0b0e15; border:1px solid #141c28; border-radius:8px;
    padding:16px 18px; position:relative; overflow:hidden;
}
.mc::after{
    content:''; position:absolute; top:0;left:0;right:0;height:2px;
    background:var(--ac,#00e57a);
}
.mc-lbl{ font-family:'IBM Plex Mono',monospace; font-size:0.58rem; letter-spacing:0.14em; color:#2e3d52; text-transform:uppercase; margin-bottom:5px; }
.mc-val{ font-family:'IBM Plex Mono',monospace; font-size:1.6rem; font-weight:600; color:#dde6f5; line-height:1; }
.mc-sub{ font-size:0.68rem; color:#2e3d52; margin-top:5px; }

/* Section label */
.slbl{
    font-family:'IBM Plex Mono',monospace; font-size:0.58rem; letter-spacing:0.18em;
    text-transform:uppercase; color:#2e3d52; border-bottom:1px solid #141c28;
    padding-bottom:5px; margin-bottom:14px; margin-top:4px;
}

/* Legend */
.lgd{ display:flex; flex-wrap:wrap; gap:6px 14px; padding:8px 2px; }
.lgd-item{ display:flex; align-items:center; gap:6px; font-size:0.72rem; color:#6070888; }
.lgd-item span{ font-size:0.72rem; color:#6878a0; }

/* Health chips */
.chip-ok  { background:#081512;color:#00e57a;border:1px solid #0f2a1e;border-radius:4px;padding:3px 9px;font-size:0.72rem;font-family:'IBM Plex Mono',monospace; }
.chip-warn{ background:#151008;color:#ffcc44;border:1px solid #2a2010;border-radius:4px;padding:3px 9px;font-size:0.72rem;font-family:'IBM Plex Mono',monospace; }
.chip-bad { background:#150808;color:#ff4455;border:1px solid #2a1010;border-radius:4px;padding:3px 9px;font-size:0.72rem;font-family:'IBM Plex Mono',monospace; }
.chip-inf { background:#080f18;color:#4488ff;border:1px solid #0d1a2a;border-radius:4px;padding:3px 9px;font-size:0.72rem;font-family:'IBM Plex Mono',monospace; }

/* Fix / anomaly rows */
.fix-row{ border-left:2px solid #00e57a;background:#07100e;padding:7px 12px;border-radius:0 4px 4px 0;margin:3px 0;font-size:0.76rem;color:#608878; }
.anom-row{ border-left:2px solid #ff8844;background:#100d08;padding:7px 12px;border-radius:0 4px 4px 0;margin:3px 0;font-size:0.76rem;color:#886050; }
.anom-row b{ color:#ff8844; }
.fix-row b{ color:#00e57a; }

/* Insight card */
.ins-card{ background:#0b0e15;border:1px solid #141c28;border-radius:8px;padding:16px 20px;margin-bottom:10px; }
.ins-title{ font-family:'IBM Plex Mono',monospace;font-size:0.8rem;color:#dde6f5;margin-bottom:6px; }
.ins-body{ font-size:0.8rem;color:#6878a0;line-height:1.6; }
.ins-tag{ display:inline-block;background:#0d1118;border:1px solid #1a2235;border-radius:3px;padding:2px 7px;font-size:0.65rem;color:#3a4a64;margin:2px;font-family:'IBM Plex Mono',monospace; }

table.data-tbl{ border-collapse:collapse;width:100%;font-size:0.76rem; }
table.data-tbl th{ font-family:'IBM Plex Mono',monospace;font-size:0.6rem;letter-spacing:0.1em;color:#2e3d52;border-bottom:1px solid #141c28;padding:6px 10px;text-align:left; }
table.data-tbl td{ padding:5px 10px;color:#8090a8;border-bottom:1px solid #0f1420; }
table.data-tbl tr:hover td{ background:#0d1118; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
MINIMAP_PATHS = {
    "AmbroseValley": os.path.join("minimaps","AmbroseValley_Minimap.png"),
    "GrandRift":     os.path.join("minimaps","GrandRift_Minimap.png"),
    "Lockdown":      os.path.join("minimaps","Lockdown_Minimap.jpg"),
}

EV_COL = {
    "Position":      "#3366cc",
    "BotPosition":   "#445566",
    "Kill":          "#ff7700",
    "Killed":        "#ff2244",
    "BotKill":       "#ffdd22",
    "BotKilled":     "#ff8855",
    "KilledByStorm": "#cc44ff",
    "Loot":          "#00e57a",
}

COMBAT_EV   = ["Kill","Killed","BotKill","BotKilled","KilledByStorm","Loot"]
HMAP_TYPES  = {
    "Traffic — All Positions":   ["Position","BotPosition"],
    "Human Traffic":             ["Position"],
    "Bot Traffic":               ["BotPosition"],
    "Kill Zones (H→H)":          ["Kill"],
    "Death Zones (all causes)":  ["Killed","KilledByStorm","BotKilled"],
    "Storm Deaths":              ["KilledByStorm"],
    "Loot Pickups":              ["Loot"],
}

# Heatmap colorscale: transparent → cyan → yellow → red
HEAT_SCALE = [
    [0.00, "rgba(0,0,0,0)"],
    [0.15, "rgba(0,220,255,0.35)"],
    [0.45, "rgba(100,255,100,0.6)"],
    [0.75, "rgba(255,200,0,0.8)"],
    [1.00, "rgba(255,50,50,1.0)"],
]

# ══════════════════════════════════════════════════════════════════════════════
# LOAD
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;letter-spacing:0.2em;color:#1e2a3a;margin-bottom:2px">LILA GAMES · LEVEL OPERATIONS · INTERNAL</div>', unsafe_allow_html=True)
st.markdown('<h1 style="font-family:IBM Plex Mono,monospace;font-size:1.4rem;font-weight:600;color:#dde6f5;margin:0 0 20px;letter-spacing:0.04em">LILA BLACK <span style="color:#00e57a">·</span> Designer Dashboard</h1>', unsafe_allow_html=True)

with st.spinner("Parsing match data…"):
    df_all, qr = load_all_data()

if df_all.empty:
    st.error("No data found. Place `player_data/` folder here.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="slbl">Filters</div>', unsafe_allow_html=True)

    sel_map  = st.selectbox("Map", sorted(df_all["map_id"].dropna().unique()))
    df_map   = df_all[df_all["map_id"] == sel_map]

    dates    = sorted(df_map["date"].unique())
    sel_date = st.multiselect("Date", dates, default=dates)
    df_d     = df_map[df_map["date"].isin(sel_date)] if sel_date else df_map

    matches  = sorted(df_d["match_id_clean"].unique())
    sel_m    = st.selectbox(f"Match  ({len(matches)})", ["— All —"] + matches)
    is_sing  = sel_m != "— All —"
    df_view  = df_d[df_d["match_id_clean"] == sel_m].copy() if is_sing else df_d.copy()

    st.markdown('<div class="slbl" style="margin-top:14px">Player Types</div>', unsafe_allow_html=True)
    sh = st.checkbox("Humans", True)
    sb = st.checkbox("Bots",   True)      # ← both on by default

    if sh and not sb:
        df_view = df_view[df_view["is_human"]]
    elif sb and not sh:
        df_view = df_view[~df_view["is_human"]]
    elif not sh and not sb:
        df_view = df_view.iloc[0:0]

    st.markdown("<hr style='border-color:#141c28;margin:12px 0'>", unsafe_allow_html=True)
    nh = int(df_view[df_view["is_human"]]["user_id"].nunique())
    nb = int(df_view[~df_view["is_human"]]["user_id"].nunique())
    nm = int(df_view["match_id_clean"].nunique())
    st.markdown(f"""
    <div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#2e3d52;line-height:2.2">
      EVENTS&nbsp;&nbsp;<span style="color:#c8d0e0">{len(df_view):,}</span><br>
      MATCHES&nbsp;<span style="color:#c8d0e0">{nm}</span><br>
      HUMANS&nbsp;&nbsp;<span style="color:#4477ff">{nh}</span><br>
      BOTS&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#445566">{nb}</span>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def base_fig(map_id: str, h: int = 640) -> go.Figure:
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
        plot_bgcolor="#07090d", paper_bgcolor="#07090d",
        margin=dict(l=0,r=0,t=0,b=0), height=h,
        showlegend=False, uirevision="keep",
        hoverlabel=dict(bgcolor="#0d1118", font=dict(color="#c8d0e0", family="IBM Plex Mono", size=11)),
    )
    return fig


def add_directional_path(fig, x_arr, y_arr, t_arr, uid_label="", n_arrows=10):
    """Gradient-colored path (green=start→red=end) with direction arrow markers."""
    n = len(x_arr)
    if n < 2:
        return

    # ── Gradient line: single trace, color by ts_relative ────────────────
    fig.add_trace(go.Scatter(
        x=x_arr, y=y_arr,
        mode="lines+markers",
        line=dict(width=1.5, color="rgba(100,140,255,0.15)"),
        marker=dict(
            color=t_arr,
            colorscale=[[0,"#00e57a"],[0.4,"#ffdd22"],[0.8,"#ff7700"],[1,"#ff2244"]],
            size=5, showscale=False,
            line=dict(width=0),
        ),
        hovertemplate=f"<b>{uid_label}</b><br>t=%{{marker.color:.0f}}s<extra></extra>",
        showlegend=False,
    ))

    # ── Arrow markers: direction of travel ───────────────────────────────
    step = max(1, n // n_arrows)
    idx  = list(range(0, n - 1, step))
    if not idx:
        return

    ax  = np.array(x_arr)[idx]
    ay  = np.array(y_arr)[idx]
    nxt = [min(i + step, n - 1) for i in idx]
    dx  = np.array(x_arr)[nxt] - ax
    dy  = np.array(y_arr)[nxt] - ay

    # Plotly arrow angle: 0=up, clockwise.
    # arctan2(dx, dy) → angle east-of-north clockwise (our y increases upward)
    angles = np.degrees(np.arctan2(dx, dy))

    fig.add_trace(go.Scatter(
        x=ax, y=ay, mode="markers",
        marker=dict(
            symbol="arrow", size=9, angle=angles,
            color="rgba(255,255,255,0.65)",
            line=dict(width=0),
        ),
        showlegend=False, hoverinfo="skip",
    ))


def legend_html(items):
    """items = list of (css_color_or_gradient, shape, label)"""
    shape_map = {
        "circle":  lambda c: f'<span style="display:inline-block;width:9px;height:9px;border-radius:50%;background:{c};flex-shrink:0"></span>',
        "diamond": lambda c: f'<span style="display:inline-block;width:8px;height:8px;transform:rotate(45deg);background:{c};flex-shrink:0"></span>',
        "star":    lambda c: f'<span style="color:{c};font-size:0.9rem;line-height:1;flex-shrink:0">★</span>',
        "x":       lambda c: f'<span style="color:{c};font-size:0.85rem;font-weight:700;font-family:IBM Plex Mono,monospace;flex-shrink:0">✕</span>',
        "square":  lambda c: f'<span style="display:inline-block;width:9px;height:9px;background:{c};flex-shrink:0;border-radius:1px"></span>',
        "line":    lambda c: f'<span style="display:inline-block;width:22px;height:2.5px;background:{c};flex-shrink:0;border-radius:1px;align-self:center"></span>',
        "gradient":lambda c: f'<span style="display:inline-block;width:26px;height:3px;background:linear-gradient(to right,{c});flex-shrink:0;border-radius:1px;align-self:center"></span>',
        "arrow":   lambda c: f'<span style="color:{c};font-size:0.85rem;flex-shrink:0">▶</span>',
    }
    inner = ""
    for color, shape, label in items:
        icon = shape_map.get(shape, shape_map["circle"])(color)
        inner += f'<span style="display:flex;align-items:center;gap:6px;font-size:0.71rem;color:#6878a0">{icon}<span>{label}</span></span>'
    return f'<div style="display:flex;flex-wrap:wrap;gap:6px 16px;padding:8px 4px;background:#07090d;border-top:1px solid #141c28;margin-top:4px">{inner}</div>'


def mk_card(label, val, sub="", accent="#00e57a"):
    return (f'<div class="mc" style="--ac:{accent}">'
            f'<div class="mc-lbl">{label}</div>'
            f'<div class="mc-val">{val}</div>'
            f'<div class="mc-sub">{sub}</div></div>')


def dark_bar(labels, values, colors=None, h=260, xtitle=""):
    colors = colors or [EV_COL.get(l, "#3a4a64") for l in labels]
    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker_color=colors, marker_line_width=0,
        hovertemplate="%{x}: %{y:,}<extra></extra>",
    ))
    fig.update_layout(
        plot_bgcolor="#0b0e15", paper_bgcolor="#07090d",
        font=dict(color="#6878a0", family="IBM Plex Mono", size=10),
        height=h, margin=dict(l=0,r=0,t=8,b=0),
        xaxis=dict(gridcolor="#141c28", tickangle=-30, title=xtitle),
        yaxis=dict(gridcolor="#141c28"),
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# TAB LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
t_health, t_overview, t_replay, t_player, t_heat = st.tabs([
    "DATA HEALTH", "OVERVIEW", "MATCH REPLAY", "PLAYER PROFILE", "HEATMAPS",
])


# ════════════════════════════════════════════════════════════════════════
# TAB 1 — DATA HEALTH  (first, as requested)
# ════════════════════════════════════════════════════════════════════════
with t_health:
    st.markdown('<div class="slbl">Automated Fixes Applied at Load</div>', unsafe_allow_html=True)
    fixes = [
        f"<b>Timestamps:</b> README states unit=ms — data is actually UNIX SECONDS. "
          f"Fixed via pyarrow int64 cast before pandas. Verified: median match = {qr['median_dur_min']}min.",
        f"<b>Duplicates:</b> {qr['dupes_dropped']:,} rows removed (key: user+match+ts+event). "
          f"Breakdown: Loot 2338 · Position 294 · BotKill 65 · BotKilled 4. Cross-day ingest artifact.",
        "<b>Event column:</b> bytes decoded to utf-8 string.",
        "<b>match_id:</b> .nakama-0 suffix stripped for readability.",
        "<b>is_human:</b> UUID format = human, numeric ID = bot.",
        "<b>Pixel coords:</b> world (x,z) → minimap pixel pre-computed for all rows.",
    ]
    for f in fixes:
        st.markdown(f'<div class="fix-row">✓ {f}</div>', unsafe_allow_html=True)

    st.markdown('<br><div class="slbl">Anomalies — Flagged, Not Auto-Fixed</div>', unsafe_allow_html=True)
    anomalies = [
        (f"{qr['botkill_no_botfiles']} matches have BotKill events but zero bot parquet files loaded.",
         "Human files log BotKill when they kill a bot. Bot's own files simply not present in player_data/. "
         "Bot movement untrackable for 93%+ of matches. Not fixable without the missing files."),
        (f"Bot file coverage: {qr['bot_file_coverage_pct']:.1f}% of matches have BotPosition data.",
         "Only 52 of 796 matches have bot movement. Heatmaps and paths for bots are nearly meaningless at scale."),
        (f"{qr['short_matches']} matches under 60 seconds.",
         "Likely crashed or abandoned test sessions. Included in data but skew duration stats."),
        ("Bot events: BotPosition only. No BotLoot, BotKilledByStorm, or bot-to-bot events.",
         "Bot telemetry is minimal. Bots don't log loot or storm deaths in their own files. "
         "Their kills/deaths appear only in human player files."),
        (f"{qr['oob_coords']} events with out-of-bounds coordinates.",
         "World coords that map outside minimap bounds (UV > 1.05 or < -0.05). "
         "Edge-of-map spawns or teleport artifacts. These markers render off-minimap."),
    ]
    for title, detail in anomalies:
        st.markdown(f'<div class="anom-row"><b>⚑ {title}</b><br><span style="font-size:0.72rem">{detail}</span></div>', unsafe_allow_html=True)

    st.markdown('<br><div class="slbl">Production Readiness</div>', unsafe_allow_html=True)

    signals = [
        ("Avg humans / match",    f"{df_all[df_all['is_human']].groupby('match_id_clean')['user_id'].nunique().mean():.1f}",
         "< 2 → test env", "bad"),
        ("Solo-human matches",    f"{qr['solo_human_pct']:.1f}%",     "> 70% → test env",  "bad"),
        ("Bot file coverage",     f"{qr['bot_file_coverage_pct']:.1f}%", "< 50% → missing","bad"),
        ("H→H kills total",       str(qr['total_pvp_kills']),          "3 kills total",     "bad"),
        ("Storm deaths total",    str(qr['total_storm_deaths']),       "39 deaths",         "warn"),
        ("Median match duration", f"{qr['median_dur_min']} min",       "healthy range",     "ok"),
        ("Coordinate bounds",     "All in range" if qr['oob_coords']==0 else f"{qr['oob_coords']} OOB", "minimap OK","ok"),
        ("Parse errors",          str(qr['parse_errors']),             "failed files",      "ok" if qr['parse_errors']==0 else "warn"),
    ]

    chip_cls = {"ok":"chip-ok","warn":"chip-warn","bad":"chip-bad","inf":"chip-inf"}
    rows = ""
    for label, val, note, status in signals:
        rows += f"<tr><td>{label}</td><td style='font-family:IBM Plex Mono,monospace;color:#c8d0e0'>{val}</td><td style='color:#2e3d52'>{note}</td><td><span class='{chip_cls[status]}'>{status.upper()}</span></td></tr>"

    st.markdown(f"""
    <table class="data-tbl">
    <thead><tr><th>METRIC</th><th>VALUE</th><th>THRESHOLD</th><th>STATUS</th></tr></thead>
    <tbody>{rows}</tbody>
    </table>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#090c12;border:1px solid #141c28;border-left:3px solid #4477ff;
                border-radius:0 8px 8px 0;padding:16px 20px;margin-top:20px;font-size:0.8rem;
                color:#6878a0;line-height:1.7">
    <span style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;color:#4477ff;letter-spacing:0.1em">OVERALL READ</span><br><br>
    This is <b style="color:#c8d0e0">pre-production QA data</b>, not live players.
    97.9% solo-human matches, 3 total H→H kills across 5 days, and partial bot file coverage
    all point to a small dev team running internal playtests (~68 people/day across all maps).<br><br>
    <b style="color:#c8d0e0">Valid to analyze:</b> map traversal routes, loot distribution, individual player behavior,
    storm timing relative to match length, bot spawn density where files exist.<br>
    <b style="color:#c8d0e0">Not valid at this scale:</b> PvP balance, kill zone hotspots,
    H→H encounter frequency — population too thin to be meaningful.
    </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════
# TAB 2 — OVERVIEW  (designer-facing questions)
# ════════════════════════════════════════════════════════════════════════
with t_overview:
    kills     = int((df_view["event"]=="Kill").sum())
    storm_d   = int((df_view["event"]=="KilledByStorm").sum())
    bot_kills = int((df_view["event"]=="BotKill").sum())
    bot_kd    = int((df_view["event"]=="BotKilled").sum())
    loots     = int((df_view["event"]=="Loot").sum())
    deaths    = int((df_view["event"]=="Killed").sum())
    all_d     = deaths + storm_d + bot_kd

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    for col, lbl, val, sub, acc in [
        (c1,"Matches",     nm,        f"{sel_map}",                 "#00e57a"),
        (c2,"H→H Kills",   kills,     f"vs {deaths} H→H deaths",   "#ff7700"),
        (c3,"Bot Kills",   bot_kills, f"{bot_kd} killed by bots",  "#ffdd22"),
        (c4,"Storm Deaths",storm_d,   f"{all_d} total deaths",     "#cc44ff"),
        (c5,"Loot Events", loots,     "items picked up",            "#00e57a"),
        (c6,"Humans",      nh,        f"+ {nb} bots tracked",      "#4477ff"),
    ]:
        col.markdown(mk_card(lbl, val, sub, acc), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1: "Are players meeting each other?" + Duration distribution ──
    r1a, r1b = st.columns([3,2])

    with r1a:
        st.markdown('<div class="slbl">Are players encountering each other? — Engagement breakdown</div>', unsafe_allow_html=True)
        total_d = max(all_d, 1)
        ev_labels = ["H→H Kills","Bot Kills","Died to Bot","Died to Storm","Loot"]
        ev_vals   = [kills, bot_kills, bot_kd, storm_d, loots]
        ev_cols   = [EV_COL["Kill"], EV_COL["BotKill"], EV_COL["BotKilled"], EV_COL["KilledByStorm"], EV_COL["Loot"]]
        st.plotly_chart(dark_bar(ev_labels, ev_vals, ev_cols, h=230), use_container_width=True)
        pvp_pct   = kills / max(kills+bot_kills, 1) * 100
        storm_pct = storm_d / total_d * 100
        st.markdown(f"""
        <div style="display:flex;gap:20px;flex-wrap:wrap;padding:4px 0">
          <span class="chip-{'ok' if pvp_pct>20 else 'bad'}">H→H = {pvp_pct:.1f}% of kills</span>
          <span class="chip-{'ok' if storm_pct>20 else 'warn'}">Storm = {storm_pct:.1f}% of deaths</span>
          <span class="chip-inf">Bot dominant — {bot_kills/(kills+1):.0f}x more bot kills than PvP</span>
        </div>""", unsafe_allow_html=True)

    with r1b:
        st.markdown('<div class="slbl">Match duration distribution</div>', unsafe_allow_html=True)
        durations = df_view.groupby("match_id_clean")["ts_relative"].max().dropna() / 60
        durations = durations[durations > 0]
        if not durations.empty:
            fig_dur = go.Figure(go.Histogram(
                x=durations, nbinsx=20,
                marker_color="#00e57a", marker_line_width=0, opacity=0.85,
                hovertemplate="%.1f min: %{y} matches<extra></extra>",
            ))
            fig_dur.update_layout(
                plot_bgcolor="#0b0e15", paper_bgcolor="#07090d",
                font=dict(color="#6878a0", family="IBM Plex Mono", size=10),
                height=230, margin=dict(l=0,r=0,t=8,b=0),
                xaxis=dict(gridcolor="#141c28", title="minutes"),
                yaxis=dict(gridcolor="#141c28", title="matches"),
            )
            st.plotly_chart(fig_dur, use_container_width=True)
            med = durations.median()
            st.markdown(f'<span class="chip-inf">Median {med:.1f} min &nbsp;·&nbsp; Min {durations.min():.1f} &nbsp;·&nbsp; Max {durations.max():.1f}</span>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 2: Storm timing + Loot timing ─────────────────────────────────
    r2a, r2b = st.columns(2)

    with r2a:
        st.markdown('<div class="slbl">When do storm deaths happen? (% through match)</div>', unsafe_allow_html=True)
        sdf = df_view[df_view["event"]=="KilledByStorm"].copy()
        match_dur = df_view.groupby("match_id_clean")["ts_relative"].max().rename("dur")
        sdf = sdf.merge(match_dur, on="match_id_clean", how="left")
        sdf["pct"] = sdf["ts_relative"] / sdf["dur"].clip(lower=1)
        if not sdf.empty and sdf["pct"].notna().any():
            fig_s = go.Figure(go.Histogram(
                x=sdf["pct"].dropna() * 100, nbinsx=20,
                marker_color="#cc44ff", marker_line_width=0,
                hovertemplate="%{x:.0f}% through match: %{y} deaths<extra></extra>",
            ))
            fig_s.update_layout(
                plot_bgcolor="#0b0e15", paper_bgcolor="#07090d",
                font=dict(color="#6878a0", family="IBM Plex Mono", size=10),
                height=220, margin=dict(l=0,r=0,t=8,b=0),
                xaxis=dict(gridcolor="#141c28", title="% through match", range=[0,100]),
                yaxis=dict(gridcolor="#141c28"),
            )
            st.plotly_chart(fig_s, use_container_width=True)
            med_pct = sdf["pct"].median() * 100
            verdict = "Storm hits at end — players extract before it catches them. Consider faster storm." if med_pct > 80 else "Storm is active mid-match." if med_pct > 40 else "Storm is aggressive — killing players early."
            st.markdown(f'<span class="chip-inf">Median at {med_pct:.0f}% through match — {verdict}</span>', unsafe_allow_html=True)
        else:
            st.info("No storm deaths in current selection.")

    with r2b:
        st.markdown('<div class="slbl">When do players loot? (% through match)</div>', unsafe_allow_html=True)
        ldf = df_view[df_view["event"]=="Loot"].copy()
        ldf = ldf.merge(match_dur, on="match_id_clean", how="left")
        ldf["pct"] = ldf["ts_relative"] / ldf["dur"].clip(lower=1)
        if not ldf.empty and ldf["pct"].notna().any():
            fig_l = go.Figure(go.Histogram(
                x=ldf["pct"].dropna() * 100, nbinsx=20,
                marker_color="#00e57a", marker_line_width=0,
                hovertemplate="%{x:.0f}% through match: %{y} loots<extra></extra>",
            ))
            fig_l.update_layout(
                plot_bgcolor="#0b0e15", paper_bgcolor="#07090d",
                font=dict(color="#6878a0", family="IBM Plex Mono", size=10),
                height=220, margin=dict(l=0,r=0,t=8,b=0),
                xaxis=dict(gridcolor="#141c28", title="% through match", range=[0,100]),
                yaxis=dict(gridcolor="#141c28"),
            )
            st.plotly_chart(fig_l, use_container_width=True)
            med_l = ldf["pct"].median() * 100
            verdict = "Early looting (healthy — gear up before combat)." if med_l < 35 else "Mid-match looting." if med_l < 65 else "Late looting — players may be dying before they can loot."
            st.markdown(f'<span class="chip-inf">Median at {med_l:.0f}% through match — {verdict}</span>', unsafe_allow_html=True)
        else:
            st.info("No loot events in current selection.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 3: Survival outcome + Map split ───────────────────────────────
    r3a, r3b = st.columns([2,3])

    with r3a:
        st.markdown('<div class="slbl">How are human players dying?</div>', unsafe_allow_html=True)
        death_counts = {
            "H→H combat":  deaths,
            "Bot kills":   bot_kd,
            "Storm":       storm_d,
        }
        survived = nh * nm - sum(death_counts.values())   # rough
        survived  = max(0, survived)
        death_counts["Survived/Extracted"] = survived

        fig_do = go.Figure(go.Pie(
            labels=list(death_counts.keys()),
            values=list(death_counts.values()),
            hole=0.55,
            marker=dict(
                colors=["#ff2244","#ff8855","#cc44ff","#00e57a"],
                line=dict(color="#07090d", width=3),
            ),
            textfont=dict(family="IBM Plex Mono", size=9, color="#c8d0e0"),
            hovertemplate="%{label}: %{value}<extra></extra>",
        ))
        fig_do.update_layout(
            paper_bgcolor="#07090d",
            font=dict(color="#6878a0"),
            height=230, margin=dict(l=0,r=0,t=0,b=0),
            legend=dict(font=dict(color="#6878a0", size=9, family="IBM Plex Mono"), bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_do, use_container_width=True)

    with r3b:
        st.markdown('<div class="slbl">Match summary table</div>', unsafe_allow_html=True)
        h_pm   = df_view[df_view["is_human"]].groupby("match_id_clean")["user_id"].nunique().rename("H")
        b_pm   = df_view[~df_view["is_human"]].groupby("match_id_clean")["user_id"].nunique().rename("B")
        ev_piv = df_view.groupby("match_id_clean")["event"].value_counts().unstack(fill_value=0)
        summ   = pd.concat([h_pm,b_pm], axis=1).fillna(0).astype(int)
        for c in ["Kill","Killed","BotKill","BotKilled","KilledByStorm","Loot"]:
            summ[c] = ev_piv[c].astype(int) if c in ev_piv.columns else 0
        summ["Min"] = (df_view.groupby("match_id_clean")["ts_relative"].max()/60).round(1)
        summ = summ.reset_index().rename(columns={"match_id_clean":"Match"})
        summ["Match"] = summ["Match"].str[:20]+"…"
        st.dataframe(summ.sort_values("Min",ascending=False), use_container_width=True, height=230)


# ════════════════════════════════════════════════════════════════════════
# TAB 3 — MATCH REPLAY
# ════════════════════════════════════════════════════════════════════════
with t_replay:
    top_a, top_b = st.columns([3,1])
    with top_b:
        st.markdown('<div class="slbl">Find Match</div>', unsafe_allow_html=True)
        search_mid = st.text_input("Search match ID", placeholder="paste or type…", key="s_mid")
        if search_mid:
            hits = df_all[df_all["match_id_clean"].str.contains(search_mid.strip(), case=False)]["match_id_clean"].unique()
            replay_mid = hits[0] if len(hits) else None
            if replay_mid:
                st.markdown(f'<span class="chip-ok">✓ {replay_mid[:24]}…</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="chip-bad">not found</span>', unsafe_allow_html=True)
        elif is_sing:
            replay_mid = sel_m
        else:
            replay_mid = None

    with top_a:
        if not replay_mid:
            st.info("Select a single match from the sidebar, or search by match ID →")
        else:
            rdf    = df_all[df_all["match_id_clean"] == replay_mid].copy()
            map_id = rdf["map_id"].iloc[0]
            t_max  = float(rdf["ts_relative"].max())

            col_sl, col_info = st.columns([4,1])
            with col_sl:
                t_range = st.slider("Match time (s)", 0.0, max(t_max, 1.0),
                                    (0.0, t_max), step=5.0, key="r_t")
            with col_info:
                st.markdown(f"""
                <div style="font-family:IBM Plex Mono,monospace;font-size:0.65rem;color:#2e3d52;line-height:2;padding-top:8px">
                DUR <span style="color:#c8d0e0">{t_max/60:.1f}min</span><br>
                MAP <span style="color:#00e57a">{map_id}</span>
                </div>""", unsafe_allow_html=True)

            rdf_t = rdf[(rdf["ts_relative"] >= t_range[0]) & (rdf["ts_relative"] <= t_range[1])]

            fig_r = base_fig(map_id, h=600)

            # Human paths
            pos_h = rdf_t[rdf_t["event"]=="Position"].sort_values(["user_id","ts_relative"])
            for uid, grp in pos_h.groupby("user_id", sort=False):
                if len(grp) < 2:
                    continue
                add_directional_path(fig_r,
                    grp["pixel_x"].values, grp["plot_y"].values,
                    grp["ts_relative"].values, uid_label=uid[:16])

            # Bot paths
            pos_b = rdf_t[rdf_t["event"]=="BotPosition"].sort_values(["user_id","ts_relative"])
            for uid, grp in pos_b.groupby("user_id", sort=False):
                if len(grp) < 2:
                    continue
                fig_r.add_trace(go.Scatter(
                    x=grp["pixel_x"], y=grp["plot_y"], mode="lines",
                    line=dict(color="rgba(100,120,150,0.25)", width=1),
                    showlegend=False, hoverinfo="skip",
                ))

            # Events
            for evt, sym, sz in [
                ("Kill","star",14), ("Killed","x",12),
                ("BotKill","circle",9), ("BotKilled","triangle-up",9),
                ("KilledByStorm","diamond",12), ("Loot","square",8),
            ]:
                edf = rdf_t[rdf_t["event"]==evt].dropna(subset=["pixel_x","plot_y"])
                if edf.empty:
                    continue
                fig_r.add_trace(go.Scatter(
                    x=edf["pixel_x"], y=edf["plot_y"], mode="markers",
                    marker=dict(symbol=sym, size=sz, color=EV_COL[evt],
                                line=dict(width=1.2, color="rgba(255,255,255,0.35)")),
                    showlegend=False,
                    hovertemplate=f"<b>{evt}</b><br>%{{text}}<extra></extra>",
                    text=edf["user_id"].str[:16]+"<br>t="+edf["ts_relative"].round(1).astype(str)+"s",
                ))

            st.plotly_chart(fig_r, use_container_width=True)
            st.markdown(legend_html([
                ("#00e57a,#ffdd22,#ff2244","gradient","Human path  (green=early → red=late)"),
                ("rgba(255,255,255,0.6)","arrow","Direction of travel"),
                ("rgba(100,120,150,0.4)","line","Bot path"),
                (EV_COL["Kill"],"star","Kill (H→H)"),
                (EV_COL["Killed"],"x","Died (H→H)"),
                (EV_COL["BotKill"],"circle","Bot killed"),
                (EV_COL["BotKilled"],"circle","Killed by bot"),
                (EV_COL["KilledByStorm"],"diamond","Storm death"),
                (EV_COL["Loot"],"square","Loot"),
            ]), unsafe_allow_html=True)

            # Event timeline
            st.markdown('<div class="slbl" style="margin-top:16px">Event Timeline</div>', unsafe_allow_html=True)
            tl = rdf[rdf["event"].isin(COMBAT_EV)].copy()
            tl["bin"] = (tl["ts_relative"] // 15 * 15).astype(int)
            tl_piv = tl.groupby(["bin","event"]).size().unstack(fill_value=0)
            fig_tl = go.Figure()
            for evt in COMBAT_EV:
                if evt not in tl_piv.columns:
                    continue
                fig_tl.add_trace(go.Bar(
                    x=tl_piv.index, y=tl_piv[evt], name=evt,
                    marker_color=EV_COL[evt], marker_line_width=0,
                ))
            fig_tl.update_layout(
                barmode="stack", plot_bgcolor="#0b0e15", paper_bgcolor="#07090d",
                font=dict(color="#6878a0", family="IBM Plex Mono", size=10),
                height=180, margin=dict(l=0,r=0,t=0,b=0),
                xaxis=dict(gridcolor="#141c28", title="seconds"),
                yaxis=dict(gridcolor="#141c28"),
                showlegend=False,
            )
            st.plotly_chart(fig_tl, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════
# TAB 4 — PLAYER PROFILE  (fully independent filters)
# ════════════════════════════════════════════════════════════════════════
with t_player:
    pa_col, pb_col = st.columns([1,3])

    with pa_col:
        st.markdown('<div class="slbl">Find Player</div>', unsafe_allow_html=True)
        uid_search = st.text_input("User ID", placeholder="paste UUID or bot number…", key="uid_inp")
        all_h_ids  = sorted(df_all[df_all["is_human"]]["user_id"].unique())
        quick_h    = st.selectbox("Or pick player", ["—"]+all_h_ids[:120])
        active_uid = uid_search.strip() if uid_search.strip() else (quick_h if quick_h!="—" else None)

        if active_uid:
            # Independent map/match filter for player tab
            st.markdown('<div class="slbl" style="margin-top:10px">Filter This Player</div>', unsafe_allow_html=True)
            udf_all = df_all[df_all["user_id"]==active_uid]
            if udf_all.empty:
                udf_all = df_all[df_all["user_id"].str.contains(active_uid, case=False, na=False)]
            p_maps   = sorted(udf_all["map_id"].dropna().unique())
            p_map    = st.selectbox("Map", ["All"]+p_maps, key="p_map")
            p_dates  = sorted(udf_all["date"].unique())
            p_date   = st.multiselect("Date", p_dates, default=p_dates, key="p_date")
            p_matches = sorted(udf_all["match_id_clean"].unique())
            p_match  = st.selectbox(f"Match ({len(p_matches)})", ["All"]+p_matches, key="p_match")

    with pb_col:
        if not active_uid:
            st.info("Search for a player ID or pick from the dropdown →")
        else:
            udf_all = df_all[df_all["user_id"]==active_uid]
            if udf_all.empty:
                udf_all = df_all[df_all["user_id"].str.contains(active_uid, case=False, na=False)]

            if udf_all.empty:
                st.error("Player not found.")
            else:
                uid_res = udf_all["user_id"].iloc[0]
                is_h_p  = udf_all["is_human"].iloc[0]

                # Apply independent filters
                udf = udf_all.copy()
                if p_map != "All":
                    udf = udf[udf["map_id"]==p_map]
                if p_date:
                    udf = udf[udf["date"].isin(p_date)]
                if p_match != "All":
                    udf = udf[udf["match_id_clean"]==p_match]

                k   = int((udf["event"]=="Kill").sum())
                d   = int((udf["event"].isin(["Killed","KilledByStorm","BotKilled"])).sum())
                bk  = int((udf["event"]=="BotKill").sum())
                l   = int((udf["event"]=="Loot").sum())
                m   = udf["match_id_clean"].nunique()
                kd  = f"{k/(d or 1):.2f}"
                pt  = "HUMAN" if is_h_p else "BOT"
                pt_col = "#4477ff" if is_h_p else "#445566"

                st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;margin-bottom:12px"><span style="background:{pt_col}22;color:{pt_col};border:1px solid {pt_col}44;border-radius:3px;padding:2px 8px">{pt}</span> &nbsp; <span style="color:#2e3d52">{uid_res}</span></div>', unsafe_allow_html=True)

                cc = st.columns(5)
                for col, lbl, val, acc in [
                    (cc[0],"Matches",m,"#00e57a"),
                    (cc[1],"Kills",k,"#ff7700"),
                    (cc[2],"Deaths",d,"#ff2244"),
                    (cc[3],"K/D",kd,"#ffdd22"),
                    (cc[4],"Loots",l,"#00e57a"),
                ]:
                    col.markdown(f'<div class="mc" style="--ac:{acc}"><div class="mc-lbl">{lbl}</div><div class="mc-val" style="font-size:1.3rem">{val}</div></div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Per-match table
                pm = udf.groupby("match_id_clean").agg(
                    Map=("map_id","first"), Date=("date","first"),
                    K=("event",lambda x:(x=="Kill").sum()),
                    D=("event",lambda x:x.isin(["Killed","KilledByStorm","BotKilled"]).sum()),
                    BK=("event",lambda x:(x=="BotKill").sum()),
                    L=("event",lambda x:(x=="Loot").sum()),
                    Min=("ts_relative",lambda x:round(x.max()/60,1)),
                ).reset_index()
                pm["match_id_clean"] = pm["match_id_clean"].str[:22]+"…"
                pm = pm.rename(columns={"match_id_clean":"Match"})
                st.dataframe(pm, use_container_width=True, height=160)

                # Movement map
                map_for_viz = p_map if p_map != "All" else udf["map_id"].mode()[0]
                match_for_viz = p_match if p_match != "All" else (
                    udf.sort_values("ts_relative").groupby("match_id_clean").last().index[-1]
                )
                viz_df = udf[(udf["map_id"]==map_for_viz)&(udf["match_id_clean"]==match_for_viz)].sort_values("ts_relative")
                map_label = f"{map_for_viz} · {match_for_viz[:20]}…"

                st.markdown(f'<div class="slbl">Movement Map — {map_label}</div>', unsafe_allow_html=True)
                fig_p = base_fig(map_for_viz, h=460)

                pos_p = viz_df[viz_df["event"].isin(["Position","BotPosition"])]
                if len(pos_p) > 1:
                    add_directional_path(fig_p,
                        pos_p["pixel_x"].values, pos_p["plot_y"].values,
                        pos_p["ts_relative"].values, uid_label=uid_res[:16])

                for evt, sym, sz in [
                    ("Kill","star",14), ("Killed","x",12),
                    ("KilledByStorm","diamond",12), ("Loot","square",9),
                    ("BotKill","circle",9),
                ]:
                    edf = viz_df[viz_df["event"]==evt].dropna(subset=["pixel_x","plot_y"])
                    if not edf.empty:
                        fig_p.add_trace(go.Scatter(
                            x=edf["pixel_x"], y=edf["plot_y"], mode="markers",
                            marker=dict(symbol=sym, size=sz, color=EV_COL[evt],
                                        line=dict(width=1.5,color="rgba(255,255,255,0.4)")),
                            showlegend=False,
                            hovertemplate=f"{evt} at t=%{{text}}s<extra></extra>",
                            text=edf["ts_relative"].round(1).astype(str),
                        ))

                st.plotly_chart(fig_p, use_container_width=True)
                st.markdown(legend_html([
                    ("#00e57a,#ffdd22,#ff2244","gradient","Path (green=start→red=end)"),
                    ("rgba(255,255,255,0.6)","arrow","Direction"),
                    (EV_COL["Kill"],"star","Kill"), (EV_COL["Killed"],"x","Died"),
                    (EV_COL["KilledByStorm"],"diamond","Storm"),
                    (EV_COL["Loot"],"square","Loot"), (EV_COL["BotKill"],"circle","Bot kill"),
                ]), unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════
# TAB 5 — HEATMAPS
# ════════════════════════════════════════════════════════════════════════
with t_heat:
    hc1, hc2 = st.columns([4,1])

    with hc2:
        st.markdown('<div class="slbl">Options</div>', unsafe_allow_html=True)
        htype   = st.radio("Layer", list(HMAP_TYPES.keys()), label_visibility="collapsed")
        opacity = st.slider("Overlay opacity", 0.3, 1.0, 0.7, 0.05)
        bins    = st.slider("Resolution", 16, 128, 128)   # default 128
        st.markdown("<hr style='border-color:#141c28'>", unsafe_allow_html=True)
        hevts = HMAP_TYPES[htype]
        hdf   = df_view[df_view["event"].isin(hevts)].dropna(subset=["pixel_x","plot_y"])
        st.markdown(f"""
        <div style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;color:#2e3d52;line-height:2.2">
        EVENTS<br><span style="color:#c8d0e0;font-size:1.1rem">{len(hdf):,}</span>
        </div>""", unsafe_allow_html=True)

    with hc1:
        fig_h = base_fig(sel_map, h=680)

        if hdf.empty:
            st.warning(f"No events for '{htype}' in current selection.")
        else:
            grid, xe, ye = np.histogram2d(
                hdf["pixel_x"].values, hdf["plot_y"].values,
                bins=bins, range=[[0,1024],[0,1024]]
            )
            grid = grid.T.astype(float)
            grid[grid == 0] = np.nan
            xc = 0.5*(xe[:-1]+xe[1:])
            yc = 0.5*(ye[:-1]+ye[1:])

            fig_h.add_trace(go.Heatmap(
                z=grid, x=xc, y=yc,
                colorscale=HEAT_SCALE,   # transparent → cyan → yellow → red
                opacity=opacity, showscale=True, zsmooth="best",
                colorbar=dict(
                    title=dict(text="density", font=dict(color="#6878a0", size=10, family="IBM Plex Mono")),
                    tickfont=dict(color="#6878a0", size=9, family="IBM Plex Mono"),
                    len=0.5, thickness=10,
                ),
                hovertemplate="density: %{z:.0f}<extra></extra>",
            ))
            st.plotly_chart(fig_h, use_container_width=True)

            peak = int(np.nanmax(grid))
            # Dead zone estimate: cells with 0 events / total cells
            total_cells  = bins * bins
            dead_cells   = int(np.sum(np.isnan(grid)))
            dead_pct     = dead_cells / total_cells * 100
            st.markdown(f"""
            <div style="display:flex;gap:14px;flex-wrap:wrap;padding:6px 2px">
              <span class="chip-inf">Peak density: {peak}</span>
              <span class="chip-inf">Total events: {len(hdf):,}</span>
              <span class="chip-{'warn' if dead_pct>70 else 'ok'}">Dead zones: {dead_pct:.0f}% of map unvisited</span>
            </div>""", unsafe_allow_html=True)

            # Legend for heatmap scale
            st.markdown(legend_html([
                ("rgba(0,0,0,0)","circle","No events (transparent)"),
                ("#00dcff","circle","Low density"),
                ("#64ff64","circle","Medium"),
                ("#ffc800","circle","High"),
                ("#ff3232","circle","Peak density"),
            ]), unsafe_allow_html=True)
