"""
LILA BLACK — Level Designer Dashboard v4
Run: streamlit run app.py
"""

import os, time
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

from data_loader import load_all_data, MAP_CONFIG, MINIMAP_SIZE

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="LILA BLACK · LevelOps",
    page_icon="🔫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');

html,body,[class*="css"]{ font-family:'Inter',sans-serif; color:#c8d0e0; }
.stApp{ background:#07090d; }
#MainMenu,footer,header,[data-testid="stToolbar"]{ display:none!important; }

/* ── Sidebar ── */
[data-testid="stSidebar"]{ background:#090c12!important; border-right:1px solid #141c28; }
[data-testid="stSidebar"] label{ color:#4a5a78!important; font-size:0.72rem!important; letter-spacing:0.06em; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span{ color:#8090a8!important; }

/* Selectbox / multiselect dropdowns */
.stSelectbox>div>div, .stMultiSelect>div>div{
    background:#0d1118!important; border:1px solid #1a2235!important;
    color:#c8d0e0!important; border-radius:6px!important;
}
/* ── DATE TAGS — the salmon ones ── */
.stMultiSelect [data-baseweb="tag"]{
    background:#0d1827!important;
    border:1px solid #1a3050!important;
    border-radius:3px!important;
}
.stMultiSelect [data-baseweb="tag"] span[role="img"],
.stMultiSelect [data-baseweb="tag"] span{
    color:#4a9eff!important;
    font-family:'IBM Plex Mono',monospace!important;
    font-size:0.72rem!important;
}
/* tag close button */
.stMultiSelect [data-baseweb="tag"] button{ color:#1a4060!important; }

/* Inputs */
.stTextInput input{
    background:#0d1118!important; border:1px solid #1a2235!important;
    color:#c8d0e0!important; font-family:'IBM Plex Mono',monospace!important;
    font-size:0.78rem!important; border-radius:6px!important;
}
/* Slider */
[data-baseweb="slider"] [data-testid="stThumbValue"]{ color:#c8d0e0!important; font-size:0.7rem!important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"]{
    background:#090c12; border-bottom:1px solid #141c28; gap:0; padding:0 6px;
}
.stTabs [data-baseweb="tab"]{
    font-family:'IBM Plex Mono',monospace; font-size:0.67rem; letter-spacing:0.1em;
    color:#2e3d52!important; padding:10px 18px; border-radius:0!important;
    border-bottom:2px solid transparent!important;
}
.stTabs [aria-selected="true"]{ color:#00e57a!important; border-bottom:2px solid #00e57a!important; background:transparent!important; }

/* ── Metric card ── */
.mc{ background:#0b0e15; border:1px solid #141c28; border-radius:8px; padding:14px 16px; position:relative; overflow:hidden; }
.mc::after{ content:''; position:absolute; top:0;left:0;right:0;height:2px; background:var(--ac,#00e57a); }
.mc-lbl{ font-family:'IBM Plex Mono',monospace; font-size:0.56rem; letter-spacing:0.14em; color:#2e3d52; text-transform:uppercase; margin-bottom:4px; }
.mc-val{ font-family:'IBM Plex Mono',monospace; font-size:1.5rem; font-weight:600; color:#dde6f5; line-height:1; }
.mc-sub{ font-size:0.66rem; color:#2e3d52; margin-top:4px; }

/* ── Section label ── */
.slbl{ font-family:'IBM Plex Mono',monospace; font-size:0.58rem; letter-spacing:0.18em; text-transform:uppercase; color:#2e3d52; border-bottom:1px solid #141c28; padding-bottom:5px; margin-bottom:12px; margin-top:4px; }

/* ── Chips ── */
.chip-ok  { display:inline-block; background:#081512;color:#00e57a;border:1px solid #0f2a1e;border-radius:3px;padding:2px 8px;font-size:0.68rem;font-family:'IBM Plex Mono',monospace;margin:2px; }
.chip-warn{ display:inline-block; background:#151008;color:#ffcc44;border:1px solid #2a2010;border-radius:3px;padding:2px 8px;font-size:0.68rem;font-family:'IBM Plex Mono',monospace;margin:2px; }
.chip-bad { display:inline-block; background:#150808;color:#ff4455;border:1px solid #2a1010;border-radius:3px;padding:2px 8px;font-size:0.68rem;font-family:'IBM Plex Mono',monospace;margin:2px; }
.chip-inf { display:inline-block; background:#080f18;color:#4a9eff;border:1px solid #0d1a2a;border-radius:3px;padding:2px 8px;font-size:0.68rem;font-family:'IBM Plex Mono',monospace;margin:2px; }

/* ── Fix / anomaly rows ── */
.fix-row  { border-left:2px solid #00e57a;background:#07100e;padding:7px 12px;border-radius:0 4px 4px 0;margin:3px 0;font-size:0.76rem;color:#608878; }
.anom-row { border-left:2px solid #ff8844;background:#100d08;padding:7px 12px;border-radius:0 4px 4px 0;margin:3px 0;font-size:0.76rem;color:#886050; }
.fix-row b{ color:#00e57a; } .anom-row b{ color:#ff8844; }

/* ── Play button ── */
div[data-testid="stButton"] button[kind="primary"]{
    background:#00e57a!important; color:#07090d!important; border:none!important;
    font-family:'IBM Plex Mono',monospace!important; font-weight:600!important;
    border-radius:4px!important; padding:6px 18px!important;
}
div[data-testid="stButton"] button:not([kind="primary"]){
    background:#0d1118!important; color:#6878a0!important; border:1px solid #1a2235!important;
    font-family:'IBM Plex Mono',monospace!important; font-size:0.72rem!important;
    border-radius:4px!important; padding:6px 14px!important;
}

/* Checkbox */
.stCheckbox label span{ color:#8090a8!important; font-size:0.8rem!important; }

table.data-tbl{ border-collapse:collapse;width:100%;font-size:0.76rem; }
table.data-tbl th{ font-family:'IBM Plex Mono',monospace;font-size:0.58rem;letter-spacing:0.1em;color:#2e3d52;border-bottom:1px solid #141c28;padding:6px 10px;text-align:left; }
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

# 12 perceptually distinct bright colors — all visible on dark map
PLAYER_PALETTE = [
    "#00e57a","#4a9eff","#ff4455","#ffdd22","#ff8c00","#cc44ff",
    "#00d4ff","#ff44aa","#aaff44","#ff6633","#44ffdd","#ff99cc",
]

EV_COL = {
    "Kill":          "#ff8c00",
    "Killed":        "#ff2244",
    "BotKill":       "#ffdd22",
    "BotKilled":     "#ff8844",
    "KilledByStorm": "#cc44ff",
    "Loot":          "#00e57a",
}

HMAP_TYPES = {
    "Traffic — All":       ["Position","BotPosition"],
    "Human Traffic":       ["Position"],
    "Bot Traffic":         ["BotPosition"],
    "Kill Zones (H→H)":    ["Kill"],
    "All Deaths":          ["Killed","KilledByStorm","BotKilled"],
    "Storm Deaths":        ["KilledByStorm"],
    "Loot Pickups":        ["Loot"],
}

HEAT_SCALE = [
    [0.00, "rgba(0,0,0,0)"],
    [0.20, "rgba(0,200,255,0.4)"],
    [0.50, "rgba(80,255,120,0.65)"],
    [0.78, "rgba(255,200,0,0.85)"],
    [1.00, "rgba(255,40,40,1.0)"],
]

COMBAT_EV = ["Kill","Killed","BotKill","BotKilled","KilledByStorm","Loot"]


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
for k, v in [("playing", False), ("t_cursor", 0.0), ("play_speed", 10.0)]:
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;letter-spacing:0.2em;color:#1e2a3a;margin-bottom:2px">LILA GAMES · LEVEL OPERATIONS · INTERNAL</div>', unsafe_allow_html=True)
st.markdown('<h1 style="font-family:IBM Plex Mono,monospace;font-size:1.35rem;font-weight:600;color:#dde6f5;margin:0 0 18px;letter-spacing:0.04em">LILA BLACK <span style="color:#00e57a">·</span> Designer Dashboard</h1>', unsafe_allow_html=True)

with st.spinner("Parsing match data…"):
    df_all, qr = load_all_data()

if df_all.empty:
    st.error("No data. Place player_data/ here."); st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR FILTERS
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

    st.markdown('<div class="slbl" style="margin-top:12px">Player Types</div>', unsafe_allow_html=True)
    sh = st.checkbox("Humans", True)
    sb = st.checkbox("Bots",   True)
    if sh and not sb:   df_view = df_view[df_view["is_human"]]
    elif sb and not sh: df_view = df_view[~df_view["is_human"]]
    elif not sh and not sb: df_view = df_view.iloc[0:0]

    st.markdown("<hr style='border-color:#141c28;margin:10px 0'>", unsafe_allow_html=True)
    nh = int(df_view[df_view["is_human"]]["user_id"].nunique())
    nb = int(df_view[~df_view["is_human"]]["user_id"].nunique())
    nm = int(df_view["match_id_clean"].nunique())
    st.markdown(f"""
    <div style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;color:#2e3d52;line-height:2.2">
      EVENTS&nbsp;&nbsp;<span style="color:#c8d0e0">{len(df_view):,}</span><br>
      MATCHES&nbsp;<span style="color:#c8d0e0">{nm}</span><br>
      HUMANS&nbsp;&nbsp;<span style="color:#4a9eff">{nh}</span><br>
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
        margin=dict(l=0, r=0, t=0, b=0), height=h,
        showlegend=True,
        legend=dict(
            x=0.01, y=0.99, xanchor="left", yanchor="top",
            bgcolor="rgba(7,9,13,0.88)",
            bordercolor="#1a2235", borderwidth=1,
            font=dict(family="IBM Plex Mono", size=10, color="#c8d0e0"),
        ),
        uirevision="keep",
        hoverlabel=dict(bgcolor="#0d1118", font=dict(color="#c8d0e0", family="IBM Plex Mono", size=11)),
    )
    return fig


def add_player_path(fig, grp: pd.DataFrame, color: str, label: str, n_arrows: int = 8):
    """
    Draws one player's path:
    - Solid colored line (player color)
    - Start dot (bright) + End dot (dim X)
    - Direction arrows AS markers along the line (same color, small)
    """
    if len(grp) < 2:
        return

    x = grp["pixel_x"].values
    y = grp["plot_y"].values
    t = grp["ts_relative"].values

    # ── 1. Main path line ────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="lines",
        line=dict(color=color, width=2),
        name=label, legendgroup=label,
        hovertemplate=f"<b>{label}</b><br>t=%{{text}}s<extra></extra>",
        text=[f"{ti:.0f}" for ti in t],
        showlegend=True,
    ))

    # ── 2. Direction arrows along path ───────────────────────────────
    n = len(x)
    step = max(1, n // n_arrows)
    idxs = list(range(0, n - 1, step))
    if idxs:
        ax, ay = x[idxs], y[idxs]
        nxt    = [min(i + step, n - 1) for i in idxs]
        dx     = x[nxt] - ax
        dy     = y[nxt] - ay
        angles = np.degrees(np.arctan2(dx, dy))

        fig.add_trace(go.Scatter(
            x=ax, y=ay, mode="markers",
            marker=dict(
                symbol="arrow", size=8, angle=angles,
                color=color, opacity=0.9,
                line=dict(width=0),
            ),
            name=label, legendgroup=label,
            showlegend=False, hoverinfo="skip",
        ))

    # ── 3. Start dot (bright) ────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=[x[0]], y=[y[0]], mode="markers",
        marker=dict(symbol="circle", size=12, color=color,
                    line=dict(color="white", width=2)),
        name=label, legendgroup=label, showlegend=False,
        hovertemplate=f"<b>{label}</b> START<extra></extra>",
    ))

    # ── 4. End dot ───────────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=[x[-1]], y=[y[-1]], mode="markers",
        marker=dict(symbol="x", size=12, color=color,
                    line=dict(color=color, width=2.5)),
        name=label, legendgroup=label, showlegend=False,
        hovertemplate=f"<b>{label}</b> END (t={t[-1]:.0f}s)<extra></extra>",
    ))


def add_event_markers(fig, edf: pd.DataFrame, t_window=None):
    """
    Renders kill/death/loot markers.
    t_window: optional (t_min, t_max) for playback — kills at cursor are LARGE.
    """
    cfg = {
        "Kill":          ("star",    16, EV_COL["Kill"],          "★ KILL"),
        "Killed":        ("x",       13, EV_COL["Killed"],        "✕ DIED"),
        "BotKill":       ("circle",  10, EV_COL["BotKill"],       "● Bot kill"),
        "BotKilled":     ("triangle-up", 10, EV_COL["BotKilled"], "▲ Killed by bot"),
        "KilledByStorm": ("diamond", 14, EV_COL["KilledByStorm"], "◆ Storm"),
        "Loot":          ("square",   8, EV_COL["Loot"],          "■ Loot"),
    }

    for evt, (sym, sz, col, lbl) in cfg.items():
        rows = edf[edf["event"] == evt].dropna(subset=["pixel_x","plot_y"])
        if rows.empty:
            continue

        # During playback: kills/deaths near cursor are emphasized (2x size)
        sizes = [sz] * len(rows)
        if t_window and evt in ("Kill","Killed","KilledByStorm"):
            t_lo, t_hi = t_window
            window = (t_hi - t_lo) * 0.15  # last 15% of window = "just happened"
            sizes = [
                sz * 2.2 if r["ts_relative"] >= (t_hi - window) else sz
                for _, r in rows.iterrows()
            ]

        fig.add_trace(go.Scatter(
            x=rows["pixel_x"], y=rows["plot_y"], mode="markers",
            marker=dict(
                symbol=sym, size=sizes, color=col,
                line=dict(width=1.5, color="rgba(255,255,255,0.4)"),
            ),
            name=lbl, legendgroup=lbl,
            hovertemplate=(
                f"<b>{lbl}</b><br>"
                "Player: %{text}<br>"
                "t=%{customdata:.0f}s<extra></extra>"
            ),
            text=rows["user_id"].str[:18],
            customdata=rows["ts_relative"].values,
            showlegend=True,
        ))


def mk_card(label, val, sub="", accent="#00e57a"):
    return (f'<div class="mc" style="--ac:{accent}">'
            f'<div class="mc-lbl">{label}</div>'
            f'<div class="mc-val">{val}</div>'
            f'<div class="mc-sub">{sub}</div></div>')


def dark_bar(labels, values, colors=None, h=250):
    colors = colors or [EV_COL.get(l, "#3a4a64") for l in labels]
    fig = go.Figure(go.Bar(
        x=labels, y=values, marker_color=colors, marker_line_width=0,
        hovertemplate="%{x}: %{y:,}<extra></extra>",
    ))
    fig.update_layout(
        plot_bgcolor="#0b0e15", paper_bgcolor="#07090d",
        font=dict(color="#6878a0", family="IBM Plex Mono", size=10),
        height=h, margin=dict(l=0,r=0,t=8,b=0),
        xaxis=dict(gridcolor="#141c28", tickangle=-30),
        yaxis=dict(gridcolor="#141c28"),
        showlegend=False,
    )
    return fig


def timing_hist(x_vals, color, title_x, h=210):
    fig = go.Figure(go.Histogram(
        x=x_vals * 100, nbinsx=20,
        marker_color=color, marker_line_width=0,
        hovertemplate="%{x:.0f}%: %{y}<extra></extra>",
    ))
    fig.update_layout(
        plot_bgcolor="#0b0e15", paper_bgcolor="#07090d",
        font=dict(color="#6878a0", family="IBM Plex Mono", size=10),
        height=h, margin=dict(l=0,r=0,t=8,b=0),
        xaxis=dict(gridcolor="#141c28", title=title_x, range=[0,100]),
        yaxis=dict(gridcolor="#141c28"),
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
t_health, t_overview, t_replay, t_player, t_heat = st.tabs([
    "DATA HEALTH", "OVERVIEW", "MATCH REPLAY", "PLAYER PROFILE", "HEATMAPS",
])


# ════════════════════════════════════════════════════════════════════════
# TAB 1 — DATA HEALTH
# ════════════════════════════════════════════════════════════════════════
with t_health:
    st.markdown('<div class="slbl">Fixes Applied at Load</div>', unsafe_allow_html=True)
    for f in [
        f"<b>Timestamps:</b> README says ms — data is UNIX SECONDS. Fixed via pyarrow int64 cast. Median match = {qr['median_dur_min']}min ✓",
        f"<b>Duplicates:</b> {qr['dupes_dropped']:,} rows dropped (key: user+match+ts+event). Breakdown: Loot 2338 · Position 294 · BotKill 65 · BotKilled 4.",
        "<b>Event column:</b> bytes decoded to utf-8.",
        "<b>match_id:</b> .nakama-0 suffix stripped.",
        "<b>is_human:</b> UUID = human, numeric = bot.",
        "<b>Pixel coords:</b> world (x,z) → minimap pixel pre-computed per map.",
    ]:
        st.markdown(f'<div class="fix-row">✓ {f}</div>', unsafe_allow_html=True)

    st.markdown('<br><div class="slbl">Anomalies Flagged</div>', unsafe_allow_html=True)
    for title, detail in [
        (f"{qr['botkill_no_botfiles']} matches: BotKill events but zero bot files loaded.",
         "Human files log BotKill. Bot parquet files simply missing from player_data/. Not fixable."),
        (f"Bot file coverage: {qr['bot_file_coverage_pct']:.1f}% of matches have BotPosition data.",
         "52/796 matches only. Bot spatial data nearly unusable at scale."),
        (f"{qr['short_matches']} matches under 60s.",
         "Crashed or abandoned sessions. Included but skew durations."),
        ("Bot events: BotPosition only — no BotLoot, BotStorm, bot-vs-bot.",
         "Bots don't log loot/storm in their own files. Their kills appear only in human logs."),
        (f"{qr['oob_coords']} out-of-bounds coordinate events.",
         "World coords outside minimap UV range. Edge-of-map or teleport artifacts."),
    ]:
        st.markdown(f'<div class="anom-row"><b>⚑ {title}</b><br><span style="font-size:0.72rem">{detail}</span></div>', unsafe_allow_html=True)

    st.markdown('<br><div class="slbl">Production Readiness</div>', unsafe_allow_html=True)
    signals = [
        ("Avg humans/match",   f"{df_all[df_all['is_human']].groupby('match_id_clean')['user_id'].nunique().mean():.1f}", "bad"),
        ("Solo-human matches", f"{qr['solo_human_pct']:.1f}%",                      "bad"),
        ("Bot file coverage",  f"{qr['bot_file_coverage_pct']:.1f}%",               "bad"),
        ("H→H kills total",    str(qr['total_pvp_kills']),                           "bad"),
        ("Storm deaths",       str(qr['total_storm_deaths']),                        "warn"),
        ("Median match dur.",  f"{qr['median_dur_min']} min",                       "ok"),
        ("OOB coordinates",    str(qr['oob_coords']),                               "ok"),
        ("Parse errors",       str(qr['parse_errors']),                             "ok" if qr['parse_errors']==0 else "warn"),
    ]
    rows = "".join(
        f"<tr><td>{l}</td><td style='font-family:IBM Plex Mono,monospace;color:#c8d0e0'>{v}</td>"
        f"<td><span class='chip-{s}'>{s.upper()}</span></td></tr>"
        for l,v,s in signals
    )
    st.markdown(f'<table class="data-tbl"><thead><tr><th>METRIC</th><th>VALUE</th><th>STATUS</th></tr></thead><tbody>{rows}</tbody></table>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#090c12;border:1px solid #141c28;border-left:3px solid #4a9eff;
                border-radius:0 8px 8px 0;padding:14px 18px;margin-top:18px;font-size:0.8rem;color:#6878a0;line-height:1.7">
    <span style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#4a9eff;letter-spacing:0.1em">OVERALL READ</span><br><br>
    <b style="color:#c8d0e0">Pre-production QA data</b>, not live players. 97.9% solo-human matches, 3 H→H kills in 5 days.
    Valid for: map traversal, loot distribution, individual paths, storm timing, bot spawn density.
    Not valid for: PvP balance, kill zone analysis at scale.
    </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════
# TAB 2 — OVERVIEW
# ════════════════════════════════════════════════════════════════════════
with t_overview:
    kills   = int((df_view["event"]=="Kill").sum())
    storm_d = int((df_view["event"]=="KilledByStorm").sum())
    bk      = int((df_view["event"]=="BotKill").sum())
    bkd     = int((df_view["event"]=="BotKilled").sum())
    loots   = int((df_view["event"]=="Loot").sum())
    deaths  = int((df_view["event"]=="Killed").sum())

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    for col, lbl, val, sub, acc in [
        (c1,"Matches",nm,     f"{sel_map}",              "#00e57a"),
        (c2,"H→H Kills",kills,f"{deaths} H→H deaths",   "#ff8c00"),
        (c3,"Bot Kills",bk,   f"{bkd} killed by bots",  "#ffdd22"),
        (c4,"Storm Deaths",storm_d,"env kills",          "#cc44ff"),
        (c5,"Loot Events",loots,"items picked up",       "#00e57a"),
        (c6,"Humans",nh,      f"+ {nb} bots tracked",   "#4a9eff"),
    ]:
        col.markdown(mk_card(lbl, val, sub, acc), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    r1a, r1b = st.columns([3,2])

    with r1a:
        st.markdown('<div class="slbl">Engagement Breakdown — are players meeting each other?</div>', unsafe_allow_html=True)
        ev_l = ["H→H Kills","Bot Kills","Died→Bot","Storm Deaths","Loot"]
        ev_v = [kills, bk, bkd, storm_d, loots]
        ev_c = [EV_COL["Kill"],EV_COL["BotKill"],EV_COL["BotKilled"],EV_COL["KilledByStorm"],EV_COL["Loot"]]
        st.plotly_chart(dark_bar(ev_l, ev_v, ev_c, h=220), use_container_width=True)
        pvp_pct = kills / max(kills+bk,1)*100
        st.markdown(
            f'<span class="chip-{"ok" if pvp_pct>20 else "bad"}">PvP = {pvp_pct:.1f}% of kills</span>'
            f'<span class="chip-inf">Bots dominate {bk/(kills+1):.0f}x over PvP</span>',
            unsafe_allow_html=True
        )

    with r1b:
        st.markdown('<div class="slbl">Match duration distribution</div>', unsafe_allow_html=True)
        durs = df_view.groupby("match_id_clean")["ts_relative"].max().dropna() / 60
        durs = durs[durs > 0]
        if not durs.empty:
            fig_d = go.Figure(go.Histogram(
                x=durs, nbinsx=20, marker_color="#00e57a", marker_line_width=0,
                hovertemplate="%.1f min: %{y}<extra></extra>",
            ))
            fig_d.update_layout(
                plot_bgcolor="#0b0e15", paper_bgcolor="#07090d",
                font=dict(color="#6878a0", family="IBM Plex Mono", size=10),
                height=220, margin=dict(l=0,r=0,t=8,b=0),
                xaxis=dict(gridcolor="#141c28", title="minutes"),
                yaxis=dict(gridcolor="#141c28"),
            )
            st.plotly_chart(fig_d, use_container_width=True)
            st.markdown(f'<span class="chip-inf">Median {durs.median():.1f}min · Max {durs.max():.1f}min</span>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    r2a, r2b = st.columns(2)

    match_dur = df_view.groupby("match_id_clean")["ts_relative"].max().rename("dur")

    with r2a:
        st.markdown('<div class="slbl">When do storm deaths happen? (% into match)</div>', unsafe_allow_html=True)
        sdf = df_view[df_view["event"]=="KilledByStorm"].merge(match_dur, on="match_id_clean", how="left")
        sdf["pct"] = sdf["ts_relative"] / sdf["dur"].clip(lower=1)
        if not sdf.empty and sdf["pct"].notna().any():
            st.plotly_chart(timing_hist(sdf["pct"].dropna(), "#cc44ff", "% through match"), use_container_width=True)
            med = sdf["pct"].median()*100
            v = "Storm hits at end — players extract first. Faster storm?" if med>80 else "Storm is aggressive mid-match." if med<40 else "Storm active at mid-match."
            st.markdown(f'<span class="chip-inf">Median at {med:.0f}% — {v}</span>', unsafe_allow_html=True)
        else:
            st.info("No storm deaths in selection.")

    with r2b:
        st.markdown('<div class="slbl">When do players loot? (% into match)</div>', unsafe_allow_html=True)
        ldf = df_view[df_view["event"]=="Loot"].merge(match_dur, on="match_id_clean", how="left")
        ldf["pct"] = ldf["ts_relative"] / ldf["dur"].clip(lower=1)
        if not ldf.empty and ldf["pct"].notna().any():
            st.plotly_chart(timing_hist(ldf["pct"].dropna(), "#00e57a", "% through match"), use_container_width=True)
            med = ldf["pct"].median()*100
            v = "Early gear-up (healthy)." if med<35 else "Late looting — dying before they can loot?" if med>65 else "Mid-match looting."
            st.markdown(f'<span class="chip-inf">Median at {med:.0f}% — {v}</span>', unsafe_allow_html=True)
        else:
            st.info("No loot events in selection.")

    st.markdown("<br>", unsafe_allow_html=True)
    r3a, r3b = st.columns([2,3])

    with r3a:
        st.markdown('<div class="slbl">How are humans dying?</div>', unsafe_allow_html=True)
        dc = {"H→H combat": deaths, "By bot": bkd, "Storm": storm_d}
        surv = max(0, nh * nm - sum(dc.values()))
        dc["Extracted"] = surv
        fig_pie = go.Figure(go.Pie(
            labels=list(dc.keys()), values=list(dc.values()), hole=0.55,
            marker=dict(colors=["#ff2244","#ff8844","#cc44ff","#00e57a"],
                        line=dict(color="#07090d",width=3)),
            textfont=dict(family="IBM Plex Mono",size=9,color="#c8d0e0"),
        ))
        fig_pie.update_layout(
            paper_bgcolor="#07090d", font=dict(color="#6878a0"),
            height=220, margin=dict(l=0,r=0,t=0,b=0),
            legend=dict(font=dict(color="#6878a0",size=9,family="IBM Plex Mono"),bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with r3b:
        st.markdown('<div class="slbl">Match summary</div>', unsafe_allow_html=True)
        h_pm  = df_view[df_view["is_human"]].groupby("match_id_clean")["user_id"].nunique().rename("H")
        b_pm  = df_view[~df_view["is_human"]].groupby("match_id_clean")["user_id"].nunique().rename("B")
        ep    = df_view.groupby("match_id_clean")["event"].value_counts().unstack(fill_value=0)
        summ  = pd.concat([h_pm,b_pm],axis=1).fillna(0).astype(int)
        for c in ["Kill","Killed","BotKill","KilledByStorm","Loot"]:
            summ[c] = ep[c].astype(int) if c in ep.columns else 0
        summ["Min"] = (df_view.groupby("match_id_clean")["ts_relative"].max()/60).round(1)
        summ = summ.reset_index().rename(columns={"match_id_clean":"Match"})
        summ["Match"] = summ["Match"].str[:20]+"…"
        st.dataframe(summ.sort_values("Min",ascending=False), use_container_width=True, height=220)


# ════════════════════════════════════════════════════════════════════════
# TAB 3 — MATCH REPLAY
# ════════════════════════════════════════════════════════════════════════
with t_replay:
    search_col, info_col = st.columns([3,1])

    with info_col:
        st.markdown('<div class="slbl">Find Match</div>', unsafe_allow_html=True)
        search_mid = st.text_input("Match ID", placeholder="paste or type…", key="s_mid")
        if search_mid:
            hits = df_all[df_all["match_id_clean"].str.contains(search_mid.strip(), case=False)]["match_id_clean"].unique()
            replay_mid = hits[0] if len(hits) else None
            if replay_mid:
                st.markdown(f'<span class="chip-ok">✓ found</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="chip-bad">not found</span>', unsafe_allow_html=True)
                replay_mid = sel_m if is_sing else None
        elif is_sing:
            replay_mid = sel_m
        else:
            replay_mid = None

    with search_col:
        if not replay_mid:
            st.info("Select a match from the sidebar or search →")
        else:
            rdf    = df_all[df_all["match_id_clean"] == replay_mid].copy()
            map_id = rdf["map_id"].iloc[0]
            t_max  = float(rdf["ts_relative"].max())
            t_max  = max(t_max, 1.0)

            # ── Playback controls ─────────────────────────────────────
            ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([1,1,1,5])

            if ctrl1.button("▶ Play", type="primary"):
                st.session_state.playing = True
                if st.session_state.t_cursor >= t_max:
                    st.session_state.t_cursor = 0.0

            if ctrl2.button("⏸ Pause"):
                st.session_state.playing = False

            if ctrl3.button("↺ Reset"):
                st.session_state.playing = False
                st.session_state.t_cursor = 0.0

            speed = ctrl4.select_slider(
                "Speed", options=[5, 10, 20, 30, 60], value=10,
                label_visibility="collapsed"
            )

            # Slider shows current cursor position; also lets user scrub
            if not st.session_state.playing:
                t_cur = st.slider(
                    "Match time (s)", 0.0, t_max,
                    st.session_state.t_cursor, step=5.0, key="r_slider"
                )
                st.session_state.t_cursor = t_cur
            else:
                t_cur = st.session_state.t_cursor
                pct   = t_cur / t_max * 100
                st.markdown(
                    f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#4a9eff">'
                    f'▶ {t_cur:.0f}s / {t_max:.0f}s &nbsp;·&nbsp; {pct:.0f}%</div>',
                    unsafe_allow_html=True
                )

            # Filter by current cursor time
            t_win_end = st.session_state.t_cursor
            rdf_t = rdf[rdf["ts_relative"] <= t_win_end]

            # ── Build figure ──────────────────────────────────────────
            fig_r = base_fig(map_id, h=580)

            # Assign unique color per human player
            human_ids = sorted(rdf[rdf["is_human"]]["user_id"].unique())
            player_colors = {uid: PLAYER_PALETTE[i % len(PLAYER_PALETTE)]
                             for i, uid in enumerate(human_ids)}

            # Human paths — each player distinct color
            pos_h = rdf_t[rdf_t["event"]=="Position"].sort_values(["user_id","ts_relative"])
            for uid, grp in pos_h.groupby("user_id", sort=False):
                if len(grp) < 2: continue
                color = player_colors.get(uid, "#ffffff")
                label = uid[:8]
                add_player_path(fig_r, grp, color, label)

            # Bot paths — grey, no individual distinction needed
            pos_b = rdf_t[rdf_t["event"]=="BotPosition"].sort_values(["user_id","ts_relative"])
            for uid, grp in pos_b.groupby("user_id", sort=False):
                if len(grp) < 2: continue
                fig_r.add_trace(go.Scatter(
                    x=grp["pixel_x"], y=grp["plot_y"], mode="lines",
                    line=dict(color="rgba(100,120,150,0.22)", width=1),
                    showlegend=False, hoverinfo="skip",
                ))

            # Events — size emphasized near cursor
            add_event_markers(fig_r, rdf_t, t_window=(max(0, t_win_end-30), t_win_end))

            # Legend entries for event types (manual, compact)
            for evt_label, col in [
                ("★ Kill", EV_COL["Kill"]), ("✕ Died", EV_COL["Killed"]),
                ("◆ Storm", EV_COL["KilledByStorm"]), ("■ Loot", EV_COL["Loot"]),
            ]:
                fig_r.add_trace(go.Scatter(
                    x=[None], y=[None], mode="markers",
                    marker=dict(color=col, size=8),
                    name=evt_label, showlegend=True,
                ))

            st.plotly_chart(fig_r, use_container_width=True)

            # ── Player roster (who = which color) ────────────────────
            roster_html = '<div style="display:flex;flex-wrap:wrap;gap:6px 14px;padding:8px 2px;background:#07090d;border-top:1px solid #141c28">'
            roster_html += '<span style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:#2e3d52;text-transform:uppercase;letter-spacing:0.1em;align-self:center">Players: </span>'
            for uid in human_ids:
                c = player_colors[uid]
                roster_html += (
                    f'<span style="display:flex;align-items:center;gap:5px;font-size:0.72rem;color:{c}">'
                    f'<span style="width:10px;height:10px;border-radius:50%;background:{c};display:inline-block"></span>'
                    f'{uid[:12]}…</span>'
                )
            if rdf[~rdf["is_human"]]["user_id"].nunique() > 0:
                roster_html += '<span style="display:flex;align-items:center;gap:5px;font-size:0.72rem;color:#445566"><span style="width:10px;height:2px;background:#445566;display:inline-block"></span>Bots (grey)</span>'
            roster_html += '</div>'
            st.markdown(roster_html, unsafe_allow_html=True)

            # ── Event timeline ────────────────────────────────────────
            tl = rdf[rdf["event"].isin(COMBAT_EV)].copy()
            tl["bin"] = (tl["ts_relative"] // 15 * 15).astype(int)
            tl_piv = tl.groupby(["bin","event"]).size().unstack(fill_value=0)
            fig_tl = go.Figure()
            for evt in COMBAT_EV:
                if evt not in tl_piv.columns: continue
                fig_tl.add_trace(go.Bar(
                    x=tl_piv.index, y=tl_piv[evt], name=evt,
                    marker_color=EV_COL.get(evt,"#3a4a64"), marker_line_width=0,
                ))
            # Cursor line
            if st.session_state.playing or True:
                fig_tl.add_vline(
                    x=st.session_state.t_cursor,
                    line=dict(color="#00e57a", width=1.5, dash="dot"),
                )
            fig_tl.update_layout(
                barmode="stack", plot_bgcolor="#0b0e15", paper_bgcolor="#07090d",
                font=dict(color="#6878a0",family="IBM Plex Mono",size=10),
                height=140, margin=dict(l=0,r=0,t=8,b=0),
                xaxis=dict(gridcolor="#141c28",title="seconds"),
                yaxis=dict(gridcolor="#141c28"),
                showlegend=False,
            )
            st.plotly_chart(fig_tl, use_container_width=True)

            # ── Match info row ────────────────────────────────────────
            nh_r = rdf[rdf["is_human"]]["user_id"].nunique()
            nb_r = rdf[~rdf["is_human"]]["user_id"].nunique()
            st.markdown(
                f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;color:#2e3d52;display:flex;gap:20px">'
                f'<span>HUMANS <span style="color:#4a9eff">{nh_r}</span></span>'
                f'<span>BOTS <span style="color:#445566">{nb_r}</span></span>'
                f'<span>DUR <span style="color:#c8d0e0">{t_max/60:.1f}min</span></span>'
                f'<span>MAP <span style="color:#00e57a">{map_id}</span></span>'
                f'</div>', unsafe_allow_html=True
            )

            # ── Advance playback cursor ───────────────────────────────
            if st.session_state.playing:
                st.session_state.t_cursor = min(
                    st.session_state.t_cursor + float(speed), t_max
                )
                if st.session_state.t_cursor >= t_max:
                    st.session_state.playing = False
                else:
                    time.sleep(0.35)
                    st.rerun()


# ════════════════════════════════════════════════════════════════════════
# TAB 4 — PLAYER PROFILE
# ════════════════════════════════════════════════════════════════════════
with t_player:
    pa_col, pb_col = st.columns([1,3])

    with pa_col:
        st.markdown('<div class="slbl">Find Player</div>', unsafe_allow_html=True)
        uid_in  = st.text_input("User ID", placeholder="UUID or bot number…", key="uid_inp")
        all_h   = sorted(df_all[df_all["is_human"]]["user_id"].unique())
        quick_h = st.selectbox("Or pick player", ["—"]+all_h[:150])
        auid    = uid_in.strip() if uid_in.strip() else (quick_h if quick_h!="—" else None)

        if auid:
            udf_all = df_all[df_all["user_id"]==auid]
            if udf_all.empty:
                udf_all = df_all[df_all["user_id"].str.contains(auid, case=False, na=False)]

            if not udf_all.empty:
                st.markdown('<div class="slbl" style="margin-top:10px">Profile Filters</div>', unsafe_allow_html=True)
                p_maps  = sorted(udf_all["map_id"].dropna().unique())
                p_map   = st.selectbox("Map", ["All"]+p_maps, key="p_map")
                p_dates = sorted(udf_all["date"].unique())
                p_date  = st.multiselect("Date", p_dates, default=p_dates, key="p_date")
                p_mlist = sorted(udf_all["match_id_clean"].unique())
                p_match = st.selectbox(f"Match ({len(p_mlist)})", ["All"]+p_mlist, key="p_match")

                st.markdown('<div class="slbl" style="margin-top:10px">View Mode</div>', unsafe_allow_html=True)
                view_mode = st.radio("Mode", ["Aggregate (all matches)", "Single match path"],
                                     label_visibility="collapsed", key="p_mode")

    with pb_col:
        if not auid:
            st.info("Search or pick a player →")
        else:
            udf_all = df_all[df_all["user_id"]==auid]
            if udf_all.empty:
                udf_all = df_all[df_all["user_id"].str.contains(auid, case=False, na=False)]

            if udf_all.empty:
                st.error("Player not found.")
            else:
                uid_res = udf_all["user_id"].iloc[0]
                is_h_p  = udf_all["is_human"].iloc[0]

                # Apply filters
                udf = udf_all.copy()
                if p_map != "All":  udf = udf[udf["map_id"]==p_map]
                if p_date:          udf = udf[udf["date"].isin(p_date)]
                if p_match != "All": udf = udf[udf["match_id_clean"]==p_match]

                k   = int((udf["event"]=="Kill").sum())
                d   = int((udf["event"].isin(["Killed","KilledByStorm","BotKilled"])).sum())
                bk_ = int((udf["event"]=="BotKill").sum())
                l_  = int((udf["event"]=="Loot").sum())
                m_  = udf["match_id_clean"].nunique()
                pt  = "HUMAN" if is_h_p else "BOT"
                ptc = "#4a9eff" if is_h_p else "#445566"

                st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;margin-bottom:10px"><span style="background:{ptc}22;color:{ptc};border:1px solid {ptc}44;border-radius:3px;padding:2px 8px">{pt}</span> &nbsp;<span style="color:#2e3d52">{uid_res}</span></div>', unsafe_allow_html=True)

                cc = st.columns(5)
                for col,lbl,val,acc in [
                    (cc[0],"Matches",m_,"#00e57a"),
                    (cc[1],"Kills",k,"#ff8c00"),
                    (cc[2],"Deaths",d,"#ff2244"),
                    (cc[3],"K/D",f"{k/(d or 1):.2f}","#ffdd22"),
                    (cc[4],"Loots",l_,"#00e57a"),
                ]:
                    col.markdown(f'<div class="mc" style="--ac:{acc}"><div class="mc-lbl">{lbl}</div><div class="mc-val" style="font-size:1.2rem">{val}</div></div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                map_for_viz = p_map if p_map != "All" else udf["map_id"].mode()[0]

                # ── MODE A: AGGREGATE HEATMAP ─────────────────────────
                if view_mode == "Aggregate (all matches)":
                    st.markdown(f'<div class="slbl">Favorite Zones — {uid_res[:24]} on {map_for_viz} (all {m_} matches)</div>', unsafe_allow_html=True)

                    agg_df = udf[udf["map_id"]==map_for_viz]
                    pos_agg = agg_df[agg_df["event"].isin(["Position","BotPosition"])].dropna(subset=["pixel_x","plot_y"])

                    fig_agg = base_fig(map_for_viz, h=520)
                    fig_agg.update_layout(showlegend=False)

                    if not pos_agg.empty:
                        grid, xe, ye = np.histogram2d(
                            pos_agg["pixel_x"].values, pos_agg["plot_y"].values,
                            bins=96, range=[[0,1024],[0,1024]]
                        )
                        grid = grid.T.astype(float)
                        grid[grid==0] = np.nan
                        xc = 0.5*(xe[:-1]+xe[1:])
                        yc = 0.5*(ye[:-1]+ye[1:])
                        fig_agg.add_trace(go.Heatmap(
                            z=grid, x=xc, y=yc,
                            colorscale=HEAT_SCALE, opacity=0.72,
                            showscale=False, zsmooth="best",
                            hovertemplate="visits: %{z:.0f}<extra></extra>",
                        ))

                    # Also show their combat/loot events across all matches
                    all_combat = agg_df[agg_df["event"].isin(COMBAT_EV)].dropna(subset=["pixel_x","plot_y"])
                    add_event_markers(fig_agg, all_combat)

                    st.plotly_chart(fig_agg, use_container_width=True)

                    # Stat breakdown across matches
                    st.markdown('<div class="slbl">Per-match breakdown</div>', unsafe_allow_html=True)
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
                    st.dataframe(pm, use_container_width=True, height=180)

                # ── MODE B: SINGLE MATCH PATH ─────────────────────────
                else:
                    match_for_viz = (
                        p_match if p_match != "All"
                        else udf.sort_values("ts_relative").groupby("match_id_clean").last().index[-1]
                    )
                    viz = udf[(udf["map_id"]==map_for_viz)&(udf["match_id_clean"]==match_for_viz)].sort_values("ts_relative")

                    st.markdown(f'<div class="slbl">Path — {map_for_viz} · {match_for_viz[:22]}…</div>', unsafe_allow_html=True)

                    fig_p = base_fig(map_for_viz, h=520)
                    fig_p.update_layout(showlegend=False)

                    pos_p = viz[viz["event"].isin(["Position","BotPosition"])]
                    if len(pos_p) > 1:
                        color = PLAYER_PALETTE[0]
                        add_player_path(fig_p, pos_p, color, uid_res[:12])

                    add_event_markers(fig_p, viz[viz["event"].isin(COMBAT_EV)])
                    st.plotly_chart(fig_p, use_container_width=True)

                    # Quick stats for this match
                    dur_s = viz["ts_relative"].max()
                    st.markdown(
                        f'<span class="chip-inf">Duration: {dur_s/60:.1f}min</span>'
                        f'<span class="chip-ok">Kills: {(viz["event"]=="Kill").sum()}</span>'
                        f'<span class="chip-bad">Deaths: {viz["event"].isin(["Killed","KilledByStorm","BotKilled"]).sum()}</span>'
                        f'<span class="chip-ok">Loots: {(viz["event"]=="Loot").sum()}</span>',
                        unsafe_allow_html=True
                    )


# ════════════════════════════════════════════════════════════════════════
# TAB 5 — HEATMAPS
# ════════════════════════════════════════════════════════════════════════
with t_heat:
    hc1, hc2 = st.columns([4,1])

    with hc2:
        st.markdown('<div class="slbl">Options</div>', unsafe_allow_html=True)
        htype   = st.radio("Layer", list(HMAP_TYPES.keys()), label_visibility="collapsed")
        opacity = st.slider("Opacity", 0.3, 1.0, 0.72, 0.05)
        bins    = st.slider("Resolution", 16, 128, 128)
        st.markdown("<hr style='border-color:#141c28'>", unsafe_allow_html=True)
        hevts = HMAP_TYPES[htype]
        hdf   = df_view[df_view["event"].isin(hevts)].dropna(subset=["pixel_x","plot_y"])
        st.markdown(
            f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;color:#2e3d52;line-height:2.2">EVENTS<br>'
            f'<span style="color:#c8d0e0;font-size:1.1rem">{len(hdf):,}</span></div>',
            unsafe_allow_html=True
        )

    with hc1:
        fig_h = base_fig(sel_map, h=660)
        fig_h.update_layout(showlegend=False)

        if hdf.empty:
            st.warning(f"No events for '{htype}'.")
        else:
            grid, xe, ye = np.histogram2d(
                hdf["pixel_x"].values, hdf["plot_y"].values,
                bins=bins, range=[[0,1024],[0,1024]]
            )
            grid = grid.T.astype(float)
            grid[grid==0] = np.nan
            xc = 0.5*(xe[:-1]+xe[1:])
            yc = 0.5*(ye[:-1]+ye[1:])
            fig_h.add_trace(go.Heatmap(
                z=grid, x=xc, y=yc,
                colorscale=HEAT_SCALE, opacity=opacity,
                showscale=True, zsmooth="best",
                colorbar=dict(
                    title=dict(text="density", font=dict(color="#6878a0",size=10,family="IBM Plex Mono")),
                    tickfont=dict(color="#6878a0",size=9,family="IBM Plex Mono"),
                    len=0.45, thickness=10,
                    tickvals=[], ticktext=[],
                    # Custom labels
                ),
                hovertemplate="density: %{z:.0f}<extra></extra>",
            ))

            # Colorbar manual labels since we have custom scale
            fig_h.add_annotation(
                x=1.045, y=0.98, xref="paper", yref="paper",
                text="HIGH", font=dict(color="#ff4040",size=9,family="IBM Plex Mono"),
                showarrow=False, xanchor="left",
            )
            fig_h.add_annotation(
                x=1.045, y=0.73, xref="paper", yref="paper",
                text="MED", font=dict(color="#ffc800",size=9,family="IBM Plex Mono"),
                showarrow=False, xanchor="left",
            )
            fig_h.add_annotation(
                x=1.045, y=0.53, xref="paper", yref="paper",
                text="LOW", font=dict(color="#00c8ff",size=9,family="IBM Plex Mono"),
                showarrow=False, xanchor="left",
            )

            st.plotly_chart(fig_h, use_container_width=True)

            peak    = int(np.nanmax(grid))
            dead_pct = int(np.sum(np.isnan(grid)) / (bins*bins) * 100)
            st.markdown(
                f'<span class="chip-inf">Peak density: {peak}</span>'
                f'<span class="chip-inf">Total events: {len(hdf):,}</span>'
                f'<span class="chip-{"warn" if dead_pct>70 else "ok"}">Dead zones: {dead_pct}% of map unvisited</span>',
                unsafe_allow_html=True
            )

            # Scale explanation
            st.markdown("""
            <div style="display:flex;gap:12px;align-items:center;padding:8px 2px;font-size:0.71rem;color:#6878a0;border-top:1px solid #141c28;margin-top:6px">
              <span>Heatmap scale:</span>
              <span style="width:14px;height:14px;border-radius:2px;background:rgba(0,200,255,0.5);display:inline-block"></span><span>Low traffic</span>
              <span style="width:14px;height:14px;border-radius:2px;background:rgba(80,255,120,0.7);display:inline-block"></span><span>Medium</span>
              <span style="width:14px;height:14px;border-radius:2px;background:rgba(255,200,0,0.9);display:inline-block"></span><span>High</span>
              <span style="width:14px;height:14px;border-radius:2px;background:rgba(255,40,40,1);display:inline-block"></span><span>Peak</span>
              <span style="width:14px;height:14px;border-radius:2px;background:rgba(0,0,0,0);border:1px solid #2e3d52;display:inline-block"></span><span>No events (transparent)</span>
            </div>""", unsafe_allow_html=True)
