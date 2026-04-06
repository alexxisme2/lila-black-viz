"""
LILA BLACK — Level Designer Dashboard v5
Run: streamlit run app.py
"""

import os, time
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

from data_loader import load_all_data, MAP_CONFIG, MINIMAP_SIZE
from insights import compute_insights

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="LILA BLACK · LevelOps", page_icon="🔫",
                   layout="wide", initial_sidebar_state="expanded")

# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;color:#c8d0e0;}
.stApp{background:#07090d;}
#MainMenu,footer,header,[data-testid="stToolbar"]{display:none!important;}

/* Sidebar */
[data-testid="stSidebar"]{background:#090c12!important;border-right:1px solid #141c28;}
[data-testid="stSidebar"] label{color:#4a5a78!important;font-size:0.72rem!important;letter-spacing:0.04em;}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] span{color:#8090a8!important;}
.stSelectbox>div>div,.stMultiSelect>div>div{background:#0d1118!important;border:1px solid #1a2235!important;color:#c8d0e0!important;border-radius:6px!important;}
/* Date / multiselect tags — fix the salmon */
.stMultiSelect [data-baseweb="tag"]{background:#0d1827!important;border:1px solid #1a3050!important;border-radius:3px!important;}
.stMultiSelect [data-baseweb="tag"] span{color:#4a9eff!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.72rem!important;}
.stMultiSelect [data-baseweb="tag"] button{color:#1a4060!important;}
/* Text inputs */
.stTextInput input{background:#0d1118!important;border:1px solid #1a2235!important;color:#c8d0e0!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.78rem!important;border-radius:6px!important;}
/* Expander */
.streamlit-expanderHeader{background:#0d1118!important;border:1px solid #141c28!important;border-radius:6px!important;color:#4a9eff!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.68rem!important;letter-spacing:0.1em!important;}
/* Tabs */
.stTabs [data-baseweb="tab-list"]{background:#090c12;border-bottom:1px solid #141c28;gap:0;padding:0 6px;}
.stTabs [data-baseweb="tab"]{font-family:'IBM Plex Mono',monospace;font-size:0.67rem;letter-spacing:0.1em;color:#2e3d52!important;padding:10px 16px;border-radius:0!important;border-bottom:2px solid transparent!important;}
.stTabs [aria-selected="true"]{color:#00e57a!important;border-bottom:2px solid #00e57a!important;background:transparent!important;}
/* Metric card */
.mc{background:#0b0e15;border:1px solid #141c28;border-radius:8px;padding:14px 16px;position:relative;overflow:hidden;}
.mc::after{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--ac,#00e57a);}
.mc-lbl{font-family:'IBM Plex Mono',monospace;font-size:0.56rem;letter-spacing:0.14em;color:#2e3d52;text-transform:uppercase;margin-bottom:4px;}
.mc-val{font-family:'IBM Plex Mono',monospace;font-size:1.5rem;font-weight:600;color:#dde6f5;line-height:1;}
.mc-sub{font-size:0.66rem;color:#2e3d52;margin-top:4px;}
/* Section label */
.slbl{font-family:'IBM Plex Mono',monospace;font-size:0.58rem;letter-spacing:0.18em;text-transform:uppercase;color:#2e3d52;border-bottom:1px solid #141c28;padding-bottom:5px;margin-bottom:12px;margin-top:4px;}
/* Chips */
.chip-ok{display:inline-block;background:#081512;color:#00e57a;border:1px solid #0f2a1e;border-radius:3px;padding:2px 8px;font-size:0.68rem;font-family:'IBM Plex Mono',monospace;margin:2px;}
.chip-warn{display:inline-block;background:#151008;color:#ffcc44;border:1px solid #2a2010;border-radius:3px;padding:2px 8px;font-size:0.68rem;font-family:'IBM Plex Mono',monospace;margin:2px;}
.chip-bad{display:inline-block;background:#150808;color:#ff4455;border:1px solid #2a1010;border-radius:3px;padding:2px 8px;font-size:0.68rem;font-family:'IBM Plex Mono',monospace;margin:2px;}
.chip-inf{display:inline-block;background:#080f18;color:#4a9eff;border:1px solid #0d1a2a;border-radius:3px;padding:2px 8px;font-size:0.68rem;font-family:'IBM Plex Mono',monospace;margin:2px;}
/* Health rows */
.fix-row{border-left:2px solid #00e57a;background:#07100e;padding:7px 12px;border-radius:0 4px 4px 0;margin:3px 0;font-size:0.76rem;color:#608878;}
.anom-row{border-left:2px solid #ff8844;background:#100d08;padding:7px 12px;border-radius:0 4px 4px 0;margin:3px 0;font-size:0.76rem;color:#886050;}
.fix-row b{color:#00e57a;}.anom-row b{color:#ff8844;}
/* Insight card */
.ins-card{background:#0b0e15;border:1px solid #141c28;border-radius:8px;padding:18px 20px;margin-bottom:12px;position:relative;overflow:hidden;}
.ins-card::before{content:'';position:absolute;top:0;left:0;bottom:0;width:3px;background:var(--sev);}
.ins-n{font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#2e3d52;letter-spacing:0.12em;margin-bottom:4px;}
.ins-cat{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:0.6rem;letter-spacing:0.1em;background:#0d1118;border:1px solid #1a2235;border-radius:3px;padding:1px 7px;color:#4a5a78;margin-bottom:8px;}
.ins-title{font-size:0.92rem;font-weight:600;color:#dde6f5;margin-bottom:12px;line-height:1.4;}
.ins-section-lbl{font-family:'IBM Plex Mono',monospace;font-size:0.58rem;letter-spacing:0.12em;color:#2e3d52;text-transform:uppercase;margin-bottom:3px;margin-top:8px;}
.ins-body{font-size:0.78rem;color:#6878a0;line-height:1.65;}
table.data-tbl{border-collapse:collapse;width:100%;font-size:0.76rem;}
table.data-tbl th{font-family:'IBM Plex Mono',monospace;font-size:0.58rem;letter-spacing:0.1em;color:#2e3d52;border-bottom:1px solid #141c28;padding:6px 10px;text-align:left;}
table.data-tbl td{padding:5px 10px;color:#8090a8;border-bottom:1px solid #0f1420;}
table.data-tbl tr:hover td{background:#0d1118;}
.stCheckbox label span{color:#8090a8!important;font-size:0.8rem!important;}
.stRadio label{color:#8090a8!important;font-size:0.8rem!important;}
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
EV_SYM = {
    "Kill":"star","Killed":"x","BotKill":"circle",
    "BotKilled":"triangle-up","KilledByStorm":"diamond","Loot":"square",
}
COMBAT_EV  = list(EV_COL.keys())
HMAP_TYPES = {
    "Traffic — All":      ["Position","BotPosition"],
    "Human Traffic":      ["Position"],
    "Bot Traffic":        ["BotPosition"],
    "Kill Zones (H→H)":   ["Kill"],
    "All Deaths":         ["Killed","KilledByStorm","BotKilled"],
    "Storm Deaths":       ["KilledByStorm"],
    "Loot Pickups":       ["Loot"],
}
HEAT_SCALE = [
    [0.00, "rgba(0,0,0,0)"],
    [0.01, "rgba(255,220,0,0.25)"],
    [0.30, "rgba(255,180,0,0.55)"],
    [0.60, "rgba(255,100,0,0.80)"],
    [1.00, "rgba(255,20,20,1.0)"],
]
SEV_COL = {"bad":"#ff4455","warn":"#ffcc44","ok":"#00e57a"}

# ══════════════════════════════════════════════════════════════════════════════
# LOAD
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;letter-spacing:0.2em;color:#1e2a3a;margin-bottom:2px">LILA GAMES · LEVEL OPERATIONS · INTERNAL</div>', unsafe_allow_html=True)
st.markdown('<h1 style="font-family:IBM Plex Mono,monospace;font-size:1.35rem;font-weight:600;color:#dde6f5;margin:0 0 18px;letter-spacing:0.04em">LILA BLACK <span style="color:#00e57a">·</span> Designer Dashboard</h1>', unsafe_allow_html=True)

with st.spinner("Loading match data…"):
    df_all, qr = load_all_data()

if df_all.empty:
    st.error("No data found. Place player_data/ here."); st.stop()

with st.spinner("Computing insights…"):
    all_insights = compute_insights(df_all)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — TWO SECTIONS
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # ── SECTION 1: MATCH VIEW ─────────────────────────────────────────
    with st.expander("MATCH VIEW", expanded=True):
        st.caption("Affects: Overview · Replay · Heatmaps")
        sel_map  = st.selectbox("Map", sorted(df_all["map_id"].dropna().unique()), key="m_map")
        df_map   = df_all[df_all["map_id"] == sel_map]
        dates    = sorted(df_map["date"].unique())
        sel_date = st.multiselect("Date", dates, default=dates, key="m_date")
        df_d     = df_map[df_map["date"].isin(sel_date)] if sel_date else df_map
        matches  = sorted(df_d["match_id_clean"].unique())
        sel_m    = st.selectbox(f"Match ({len(matches)})", ["— All —"] + matches, key="m_match")
        is_sing  = sel_m != "— All —"
        df_view  = df_d[df_d["match_id_clean"] == sel_m].copy() if is_sing else df_d.copy()
        sh = st.checkbox("Humans", True, key="m_h")
        sb = st.checkbox("Bots",   True, key="m_b")
        if sh and not sb:   df_view = df_view[df_view["is_human"]]
        elif sb and not sh: df_view = df_view[~df_view["is_human"]]
        elif not sh and not sb: df_view = df_view.iloc[0:0]

        nh = int(df_view[df_view["is_human"]]["user_id"].nunique())
        nb = int(df_view[~df_view["is_human"]]["user_id"].nunique())
        nm = int(df_view["match_id_clean"].nunique())
        st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;color:#2e3d52;line-height:2.2;margin-top:8px">EVENTS&nbsp;<span style="color:#c8d0e0">{len(df_view):,}</span> &nbsp; MATCHES&nbsp;<span style="color:#c8d0e0">{nm}</span> &nbsp; H&nbsp;<span style="color:#4a9eff">{nh}</span> &nbsp; B&nbsp;<span style="color:#445566">{nb}</span></div>', unsafe_allow_html=True)

    # ── SECTION 2: PLAYER VIEW ────────────────────────────────────────
    with st.expander("PLAYER VIEW", expanded=True):
        st.caption("Affects: Player Profile tab only")
        p_search = st.text_input("User ID", placeholder="UUID or bot number…", key="p_uid_in")
        all_h    = sorted(df_all[df_all["is_human"]]["user_id"].unique())
        p_pick   = st.selectbox("Or pick player", ["—"] + all_h[:150], key="p_pick")
        p_uid    = p_search.strip() if p_search.strip() else (p_pick if p_pick != "—" else None)

        if p_uid:
            p_udf_all = df_all[df_all["user_id"] == p_uid]
            if p_udf_all.empty:
                p_udf_all = df_all[df_all["user_id"].str.contains(p_uid, case=False, na=False)]
            if not p_udf_all.empty:
                p_maps  = ["All"] + sorted(p_udf_all["map_id"].dropna().unique())
                p_map   = st.selectbox("Map", p_maps, key="p_map")
                p_mode  = st.radio("Mode", ["Aggregate — all matches", "Single match path"],
                                   label_visibility="collapsed", key="p_mode")
                if p_mode == "Single match path":
                    p_mlist = sorted(p_udf_all["match_id_clean"].unique())
                    p_match = st.selectbox(f"Match ({len(p_mlist)})", p_mlist, key="p_match")
                else:
                    p_match = None

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def base_fig(map_id: str, h: int = 640, show_legend: bool = True) -> go.Figure:
    fig = go.Figure()
    path = MINIMAP_PATHS.get(map_id, "")
    if os.path.exists(path):
        img = Image.open(path)
        fig.add_layout_image(dict(source=img, xref="x", yref="y",
                                  x=0, y=1024, sizex=1024, sizey=1024,
                                  sizing="stretch", opacity=1.0, layer="below"))
    fig.update_layout(
        xaxis=dict(range=[0,1024], showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(range=[0,1024], showgrid=False, showticklabels=False, zeroline=False, scaleanchor="x"),
        plot_bgcolor="#07090d", paper_bgcolor="#07090d",
        margin=dict(l=0,r=0,t=0,b=0), height=h,
        showlegend=show_legend,
        legend=dict(x=0.01, y=0.99, xanchor="left", yanchor="top",
                    bgcolor="rgba(7,9,13,0.88)", bordercolor="#1a2235", borderwidth=1,
                    font=dict(family="IBM Plex Mono", size=10, color="#c8d0e0")),
        uirevision="keep",
        hoverlabel=dict(bgcolor="#0d1118", font=dict(color="#c8d0e0", family="IBM Plex Mono", size=11)),
    )
    return fig


# Clustering ──────────────────────────────────────────────────────────────────
CLUSTER_GRID = 40
MIN_SZ, MAX_SZ = 8, 22

def cluster_events(evt_df: pd.DataFrame):
    if evt_df.empty:
        return pd.DataFrame(columns=["cx","cy","count","size","label"])
    cell = 1024 / CLUSTER_GRID
    d = evt_df.copy()
    d["gx"] = (d["pixel_x"] // cell).clip(0, CLUSTER_GRID-1).astype(int)
    d["gy"] = (d["plot_y"]  // cell).clip(0, CLUSTER_GRID-1).astype(int)
    g = d.groupby(["gx","gy"]).agg(cx=("pixel_x","mean"), cy=("plot_y","mean"),
                                    count=("pixel_x","count")).reset_index()
    mx = g["count"].max()
    g["size"]  = (np.sqrt(g["count"] / mx) * (MAX_SZ - MIN_SZ) + MIN_SZ).round(0)
    g["label"] = g["count"].apply(lambda x: str(x) if x > 1 else "")
    return g


def add_clustered_events(fig: go.Figure, edf: pd.DataFrame, t_cursor: float = None):
    """Renders all event types as clustered circle markers with count labels.
    Z-order: latest event type on top (added last = renders above).
    Legend order: latest event type at top (legendrank=1 = highest in legend).
    These are decoupled via Plotly's legendrank property."""
    if "ts_relative" in edf.columns and not edf.empty:
        first_ts = (
            edf[edf["event"].isin(COMBAT_EV)]
            .groupby("event")["ts_relative"]
            .min()
            .reindex(COMBAT_EV)
            .fillna(float("inf"))
        )
        # Ascending = earliest added first (bottom z), latest added last (top z)
        ordered_evts = first_ts.sort_values(ascending=True).index.tolist()
        # legendrank: latest event gets rank 1 (top of legend), earliest gets highest rank (bottom)
        n = len(ordered_evts)
        legend_ranks = {evt: (n - i) for i, evt in enumerate(ordered_evts)}
    else:
        ordered_evts = COMBAT_EV
        legend_ranks = {evt: i for i, evt in enumerate(COMBAT_EV)}

    for evt in ordered_evts:
        rows = edf[edf["event"] == evt].dropna(subset=["pixel_x","plot_y"])
        if rows.empty:
            continue
        cl = cluster_events(rows)
        if cl.empty:
            continue

        sizes = cl["size"].tolist()

        # Near-cursor emphasis during playback
        if t_cursor is not None:
            emphasis_rows = rows[rows["ts_relative"] >= (t_cursor - 20)]
            if not emphasis_rows.empty:
                emph_cl = cluster_events(emphasis_rows)
                # boost sizes for cells that overlap with recent events
                boost_cells = set(zip(emph_cl.index, emph_cl.index))
                sizes = [min(s * 1.6, MAX_SZ * 1.5) if i in boost_cells else s
                         for i, s in enumerate(sizes)]

        fig.add_trace(go.Scatter(
            x=cl["cx"], y=cl["cy"],
            mode="markers+text",
            marker=dict(symbol=EV_SYM[evt], size=sizes, color=EV_COL[evt],
                        line=dict(width=1.2, color="rgba(255,255,255,0.35)")),
            text=cl["label"],
            textfont=dict(color="white", size=8, family="IBM Plex Mono"),
            textposition="middle center",
            name=evt,
            legendgroup=evt,
            legendrank=legend_ranks.get(evt, 999),
            showlegend=True,
            hovertemplate=f"<b>{evt}</b><br>count: %{{customdata}}<extra></extra>",
            customdata=cl["count"].tolist(),
        ))


def add_player_path(fig: go.Figure, pos: pd.DataFrame, color: str, label: str, n_arrows: int = 8):
    if len(pos) < 2:
        return
    x = pos["pixel_x"].values; y = pos["plot_y"].values; t = pos["ts_relative"].values
    # Path
    fig.add_trace(go.Scatter(x=x.tolist(), y=y.tolist(), mode="lines",
                              line=dict(color=color, width=2.5), name=label,
                              legendgroup=label, showlegend=True,
                              hovertemplate=f"<b>{label}</b> t=%{{text}}s<extra></extra>",
                              text=[f"{ti:.0f}" for ti in t]))
    # Arrows along path
    n = len(x); step = max(1, n // n_arrows); idxs = list(range(0, n-1, step))
    if idxs:
        ax, ay = x[idxs], y[idxs]
        nxt = [min(i+step, n-1) for i in idxs]
        dx = x[nxt]-ax; dy = y[nxt]-ay
        angles = np.degrees(np.arctan2(dx, dy))
        fig.add_trace(go.Scatter(x=ax.tolist(), y=ay.tolist(), mode="markers",
                                  marker=dict(symbol="arrow", size=9, angle=angles.tolist(),
                                              color=color, opacity=0.85, line=dict(width=0)),
                                  showlegend=False, hoverinfo="skip",
                                  legendgroup=label))
    # Start dot
    fig.add_trace(go.Scatter(x=[float(x[0])], y=[float(y[0])], mode="markers",
                              marker=dict(symbol="circle", size=13, color=color,
                                          line=dict(color="white", width=2.5)),
                              showlegend=False, legendgroup=label,
                              hovertemplate=f"<b>{label}</b> START<extra></extra>"))
    # End dot
    fig.add_trace(go.Scatter(x=[float(x[-1])], y=[float(y[-1])], mode="markers",
                              marker=dict(symbol="x", size=12, color=color,
                                          line=dict(color=color, width=2.5)),
                              showlegend=False, legendgroup=label,
                              hovertemplate=f"<b>{label}</b> END t={t[-1]:.0f}s<extra></extra>"))


def mk_card(label, val, sub="", accent="#00e57a"):
    return (f'<div class="mc" style="--ac:{accent}">'
            f'<div class="mc-lbl">{label}</div>'
            f'<div class="mc-val">{val}</div>'
            f'<div class="mc-sub">{sub}</div></div>')


def dark_bar(labels, values, colors=None, h=250):
    colors = colors or [EV_COL.get(l, "#3a4a64") for l in labels]
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color=colors, marker_line_width=0,
                           hovertemplate="%{x}: %{y:,}<extra></extra>"))
    fig.update_layout(plot_bgcolor="#0b0e15", paper_bgcolor="#07090d",
                      font=dict(color="#6878a0", family="IBM Plex Mono", size=10),
                      height=h, margin=dict(l=0,r=0,t=8,b=0),
                      xaxis=dict(gridcolor="#141c28", tickangle=-30),
                      yaxis=dict(gridcolor="#141c28"), showlegend=False)
    return fig


# Plotly native animation ─────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def build_animated_figure(match_id_clean: str, _df: pd.DataFrame, n_frames: int = 35) -> go.Figure:
    """
    Pre-computes Plotly animation frames for a match.
    Play/pause/scrub are pure client-side JS — zero Streamlit reruns.
    Cached by match_id_clean so switching back is instant.
    """
    rdf     = _df[_df["match_id_clean"] == match_id_clean].copy()
    map_id  = rdf["map_id"].iloc[0]
    t_max   = float(rdf["ts_relative"].max())
    if t_max <= 0:
        return base_fig(map_id)

    human_ids     = sorted(rdf[rdf["is_human"]]["user_id"].unique())
    player_colors = {uid: PLAYER_PALETTE[i % len(PLAYER_PALETTE)] for i, uid in enumerate(human_ids)}
    time_points   = np.linspace(0, t_max, n_frames)

    fig = base_fig(map_id, h=600)

    # ── Define initial empty traces (order = frame data order) ────────
    trace_order = []

    for uid in human_ids:
        color = player_colors[uid]; label = uid[:8]
        fig.add_trace(go.Scatter(x=[], y=[], mode="lines",
                                  line=dict(color=color, width=2.5),
                                  name=label, showlegend=True))
        trace_order.append(("path", uid))
        fig.add_trace(go.Scatter(x=[], y=[], mode="markers",
                                  marker=dict(symbol="arrow", size=9, color=color, line=dict(width=0)),
                                  showlegend=False, hoverinfo="skip"))
        trace_order.append(("arrows", uid))
        fig.add_trace(go.Scatter(x=[], y=[], mode="markers",
                                  marker=dict(symbol="circle", size=13, color=color,
                                              line=dict(color="white", width=2.5)),
                                  showlegend=False,
                                  hovertemplate=f"<b>{label}</b> start<extra></extra>"))
        trace_order.append(("start", uid))

    # Bot paths
    fig.add_trace(go.Scatter(x=[], y=[], mode="lines",
                              line=dict(color="rgba(100,120,150,0.2)", width=1),
                              showlegend=False, hoverinfo="skip"))
    trace_order.append(("bots", None))

    # Event traces (clustered)
    for evt in COMBAT_EV:
        fig.add_trace(go.Scatter(x=[], y=[], mode="markers+text",
                                  marker=dict(symbol=EV_SYM[evt], size=[],
                                              color=EV_COL[evt],
                                              line=dict(width=1.2, color="rgba(255,255,255,0.35)")),
                                  text=[], textfont=dict(color="white", size=8, family="IBM Plex Mono"),
                                  textposition="middle center",
                                  name=evt, showlegend=True,
                                  hovertemplate=f"<b>{evt}</b><br>count: %{{customdata}}<extra></extra>",
                                  customdata=[]))
        trace_order.append(("event", evt))

    # ── Build frames ──────────────────────────────────────────────────
    frames = []
    for t in time_points:
        rdf_t = rdf[rdf["ts_relative"] <= t]
        fd    = []  # frame data — same order as trace_order

        for uid in human_ids:
            pos = (rdf_t[(rdf_t["user_id"]==uid) & (rdf_t["event"]=="Position")]
                   .sort_values("ts_relative"))
            step = max(1, len(pos)//250)
            pos  = pos.iloc[::step]

            if len(pos) >= 2:
                px, py, pt = pos["pixel_x"].values, pos["plot_y"].values, pos["ts_relative"].values
                fd.append(go.Scatter(x=px.tolist(), y=py.tolist()))

                n = len(px); n_arr = min(8, n-1); step_a = max(1, n//max(n_arr,1))
                idxs = list(range(0, n-1, step_a))
                if idxs:
                    ax, ay = px[idxs], py[idxs]
                    nxt = [min(i+step_a, n-1) for i in idxs]
                    dx, dy = px[nxt]-ax, py[nxt]-ay
                    angles = np.degrees(np.arctan2(dx, dy))
                    fd.append(go.Scatter(x=ax.tolist(), y=ay.tolist(),
                                          marker=dict(angle=angles.tolist())))
                else:
                    fd.append(go.Scatter(x=[], y=[]))

                fd.append(go.Scatter(x=[float(px[0])], y=[float(py[0])]))
            else:
                fd.extend([go.Scatter(x=[],y=[]), go.Scatter(x=[],y=[]), go.Scatter(x=[],y=[])])

        # Bot paths
        bp = rdf_t[rdf_t["event"]=="BotPosition"].sort_values(["user_id","ts_relative"])
        bx, by = [], []
        for _, bg in bp.groupby("user_id", sort=False):
            bx.extend(bg["pixel_x"].tolist()+[None])
            by.extend(bg["plot_y"].tolist()+[None])
        fd.append(go.Scatter(x=bx, y=by))

        # Events (clustered)
        for evt in COMBAT_EV:
            ev = rdf_t[rdf_t["event"]==evt].dropna(subset=["pixel_x","plot_y"])
            cl = cluster_events(ev)
            if not cl.empty:
                fd.append(go.Scatter(x=cl["cx"].tolist(), y=cl["cy"].tolist(),
                                      marker=dict(size=cl["size"].tolist()),
                                      text=cl["label"].tolist(),
                                      customdata=cl["count"].tolist()))
            else:
                fd.append(go.Scatter(x=[], y=[], marker=dict(size=[]),
                                      text=[], customdata=[]))

        frames.append(go.Frame(data=fd, name=f"{t:.0f}"))

    fig.frames = frames

    # ── Animation controls (all client-side) ──────────────────────────
    fig.update_layout(
        updatemenus=[dict(
            type="buttons", showactive=False,
            bgcolor="#0d1118", bordercolor="#1a2235",
            font=dict(color="#c8d0e0", family="IBM Plex Mono", size=12),
            x=0.01, y=0.01, xanchor="left", yanchor="bottom",
            pad=dict(t=0, r=5),
            buttons=[
                dict(label="▶  PLAY", method="animate",
                     args=[None, {"frame":{"duration":180,"redraw":True},
                                  "fromcurrent":True,"transition":{"duration":0}}]),
                dict(label="⏸  PAUSE", method="animate",
                     args=[[None], {"frame":{"duration":0,"redraw":False},
                                    "mode":"immediate","transition":{"duration":0}}]),
            ]
        )],
        sliders=[dict(
            active=0,
            bgcolor="#0d1118", bordercolor="#1a2235",
            font=dict(color="#6878a0", family="IBM Plex Mono", size=9),
            currentvalue=dict(prefix="Match time: ", suffix="s  ", visible=True,
                              xanchor="right",
                              font=dict(color="#c8d0e0", family="IBM Plex Mono", size=11)),
            pad=dict(t=50, b=10, l=100),
            steps=[dict(method="animate", label=f"{int(t)}s",
                        args=[[f"{t:.0f}"], {"frame":{"duration":0,"redraw":True},
                                             "mode":"immediate","transition":{"duration":0}}])
                   for t in time_points]
        )]
    )

    return fig


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
t_health, t_insights, t_overview, t_replay, t_player, t_heat = st.tabs([
    "DATA HEALTH", "INSIGHTS", "OVERVIEW", "MATCH REPLAY", "PLAYER PROFILE", "HEATMAPS",
])


# ════════════════════════════════════════════════════════════════════════
# TAB 1 — DATA HEALTH
# ════════════════════════════════════════════════════════════════════════
with t_health:
    st.markdown('<div class="slbl">Fixes Applied at Load</div>', unsafe_allow_html=True)
    for f in [
        f"<b>Timestamps:</b> README says ms — data is UNIX SECONDS. Fixed via pyarrow int64 cast before pandas. Verified: median match = {qr['median_dur_min']}min ✓",
        f"<b>Duplicates:</b> {qr['dupes_dropped']:,} rows dropped (key: user+match+ts+event). Loot 2338 · Position 294 · BotKill 65 · BotKilled 4. Cross-day ingest artifact.",
        "<b>Event column:</b> bytes decoded to utf-8.", "<b>match_id:</b> .nakama-0 suffix stripped.",
        "<b>is_human:</b> UUID = human, numeric = bot.", "<b>Pixel coords:</b> world (x,z) → minimap pixel pre-computed.",
    ]:
        st.markdown(f'<div class="fix-row">✓ {f}</div>', unsafe_allow_html=True)

    st.markdown('<br><div class="slbl">Anomalies Flagged</div>', unsafe_allow_html=True)
    for t, d in [
        (f"{qr['botkill_no_botfiles']} matches: BotKill events but zero bot files loaded.",
         "Human files log BotKill when they kill a bot. Bot's own parquet files simply absent."),
        (f"Bot file coverage: {qr['bot_file_coverage_pct']:.1f}% of matches have BotPosition data.",
         "52/796 matches only. Bot spatial behavior nearly untrackable."),
        (f"{qr['short_matches']} matches under 60 seconds.", "Likely crashes. Included but skew durations."),
        ("Bot events: BotPosition only — no BotLoot, BotStorm, bot-vs-bot.",
         "Bot telemetry minimal. Kills/deaths appear only in human logs."),
    ]:
        st.markdown(f'<div class="anom-row"><b>⚑ {t}</b><br><span style="font-size:0.72rem">{d}</span></div>', unsafe_allow_html=True)

    st.markdown('<br><div class="slbl">Production Readiness</div>', unsafe_allow_html=True)
    signals = [
        ("Avg humans/match", f"{df_all[df_all['is_human']].groupby('match_id_clean')['user_id'].nunique().mean():.1f}", "bad"),
        ("Solo-human matches", f"{qr['solo_human_pct']:.1f}%", "bad"),
        ("Bot file coverage", f"{qr['bot_file_coverage_pct']:.1f}%", "bad"),
        ("H→H kills total", str(qr['total_pvp_kills']), "bad"),
        ("Storm deaths", str(qr['total_storm_deaths']), "warn"),
        ("Median match duration", f"{qr['median_dur_min']} min", "ok"),
        ("OOB coordinates", str(qr['oob_coords']), "ok"),
        ("Parse errors", str(qr['parse_errors']), "ok" if qr['parse_errors']==0 else "warn"),
    ]
    rows = "".join(f"<tr><td>{l}</td><td style='font-family:IBM Plex Mono,monospace;color:#c8d0e0'>{v}</td><td><span class='chip-{s}'>{s.upper()}</span></td></tr>" for l,v,s in signals)
    st.markdown(f'<table class="data-tbl"><thead><tr><th>METRIC</th><th>VALUE</th><th>STATUS</th></tr></thead><tbody>{rows}</tbody></table>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#090c12;border:1px solid #141c28;border-left:3px solid #4a9eff;border-radius:0 8px 8px 0;padding:14px 18px;margin-top:18px;font-size:0.8rem;color:#6878a0;line-height:1.7">
    <span style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#4a9eff;letter-spacing:0.1em">OVERALL READ</span><br><br>
    <b style="color:#c8d0e0">Pre-production QA data</b>, not live players. 97.9% solo-human matches, 3 H→H kills in 5 days.
    Valid for: map traversal, loot distribution, individual paths, storm timing, bot spawn density.
    Not valid for: PvP balance or H→H kill zone analysis at scale.
    </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════
# TAB 2 — INSIGHTS
# ════════════════════════════════════════════════════════════════════════
with t_insights:
    st.markdown('<div class="slbl">Game Design Observations — computed on full 5-day dataset</div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.8rem;color:#4a5a78;margin-bottom:18px">Pre-launch QA analysis. Each insight backed by specific event data. Read top-to-bottom: critical issues first.</p>', unsafe_allow_html=True)

    for ins in all_insights:
        sev_color = SEV_COL[ins["severity"]]
        sev_label = {"bad":"🔴 CRITICAL","warn":"🟡 NEEDS ATTENTION","ok":"🟢 HEALTHY"}[ins["severity"]]
        st.markdown(f"""
        <div class="ins-card" style="--sev:{sev_color}">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
            <span class="ins-cat">{ins['category']}</span>
            <span style="font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:{sev_color}">{sev_label}</span>
            <span style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;color:#2e3d52;margin-left:auto">#{ins['n']}</span>
          </div>
          <div class="ins-title">{ins['title']}</div>
          <div class="ins-section-lbl">Signal</div>
          <div class="ins-body">{ins['signal']}</div>
          <div class="ins-section-lbl">Verdict</div>
          <div class="ins-body">{ins['verdict']}</div>
          <div class="ins-section-lbl">Action</div>
          <div class="ins-body" style="color:#8090a8">{ins['action']}</div>
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════
# TAB 3 — OVERVIEW
# ════════════════════════════════════════════════════════════════════════
with t_overview:
    kills   = int((df_view["event"]=="Kill").sum())
    storm_d = int((df_view["event"]=="KilledByStorm").sum())
    bk      = int((df_view["event"]=="BotKill").sum())
    bkd     = int((df_view["event"]=="BotKilled").sum())
    loots   = int((df_view["event"]=="Loot").sum())
    deaths  = int((df_view["event"]=="Killed").sum())

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    for col,lbl,val,sub,acc in [
        (c1,"Matches",nm,f"{sel_map}","#00e57a"),
        (c2,"H→H Kills",kills,f"{deaths} H→H deaths","#ff8c00"),
        (c3,"Bot Kills",bk,f"{bkd} by bots","#ffdd22"),
        (c4,"Storm Deaths",storm_d,"env kills","#cc44ff"),
        (c5,"Loot",loots,"pickups","#00e57a"),
        (c6,"Humans",nh,f"+ {nb} bots","#4a9eff"),
    ]:
        col.markdown(mk_card(lbl, val, sub, acc), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    r1a, r1b = st.columns([3,2])
    with r1a:
        st.markdown('<div class="slbl">Engagement breakdown</div>', unsafe_allow_html=True)
        st.plotly_chart(dark_bar(
            ["H→H Kills","Bot Kills","Died→Bot","Storm Deaths","Loot"],
            [kills,bk,bkd,storm_d,loots],
            [EV_COL["Kill"],EV_COL["BotKill"],EV_COL["BotKilled"],EV_COL["KilledByStorm"],EV_COL["Loot"]],h=220
        ), use_container_width=True)
        pvp_pct = kills/max(kills+bk,1)*100
        st.markdown(f'<span class="chip-{"ok" if pvp_pct>20 else "bad"}">PvP = {pvp_pct:.1f}% of kills</span><span class="chip-inf">Bots dominate {bk/(kills+1):.0f}×</span>', unsafe_allow_html=True)

    with r1b:
        st.markdown('<div class="slbl">Match duration</div>', unsafe_allow_html=True)
        durs = df_view.groupby("match_id_clean")["ts_relative"].max().dropna() / 60
        durs = durs[durs > 0]
        if not durs.empty:
            fig_d = go.Figure(go.Histogram(x=durs, nbinsx=20, marker_color="#00e57a", marker_line_width=0))
            fig_d.update_layout(plot_bgcolor="#0b0e15", paper_bgcolor="#07090d",
                                font=dict(color="#6878a0",family="IBM Plex Mono",size=10),
                                height=220, margin=dict(l=0,r=0,t=8,b=0),
                                xaxis=dict(gridcolor="#141c28",title="minutes"),
                                yaxis=dict(gridcolor="#141c28"))
            st.plotly_chart(fig_d, use_container_width=True)
            st.markdown(f'<span class="chip-inf">Median {durs.median():.1f}min · Max {durs.max():.1f}min</span>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    r2a, r2b = st.columns(2)
    match_dur = df_view.groupby("match_id_clean")["ts_relative"].max().rename("dur")

    def timing_chart(ev_list, color, title):
        edf = df_view[df_view["event"].isin(ev_list)].merge(match_dur, on="match_id_clean", how="left")
        edf["pct"] = edf["ts_relative"] / edf["dur"].clip(lower=1)
        if edf.empty or edf["pct"].isna().all():
            return None, None
        fig = go.Figure(go.Histogram(x=edf["pct"].dropna()*100, nbinsx=20,
                                      marker_color=color, marker_line_width=0))
        fig.update_layout(plot_bgcolor="#0b0e15", paper_bgcolor="#07090d",
                          font=dict(color="#6878a0",family="IBM Plex Mono",size=10),
                          height=200, margin=dict(l=0,r=0,t=8,b=0),
                          xaxis=dict(gridcolor="#141c28",title="% through match",range=[0,100]),
                          yaxis=dict(gridcolor="#141c28"))
        return fig, edf["pct"].median()*100

    with r2a:
        st.markdown('<div class="slbl">Storm death timing</div>', unsafe_allow_html=True)
        fig_s, med_s = timing_chart(["KilledByStorm"], "#cc44ff", "storm")
        if fig_s:
            st.plotly_chart(fig_s, use_container_width=True)
            v = "Hits at end → storm inactive mid-match. Speed up?" if med_s>80 else "Active mid-match." if med_s>40 else "Aggressive — early kills."
            st.markdown(f'<span class="chip-inf">Median at {med_s:.0f}% — {v}</span>', unsafe_allow_html=True)
        else:
            st.info("No storm deaths in selection.")

    with r2b:
        st.markdown('<div class="slbl">Loot timing</div>', unsafe_allow_html=True)
        fig_l, med_l = timing_chart(["Loot"], "#00e57a", "loot")
        if fig_l:
            st.plotly_chart(fig_l, use_container_width=True)
            v = "Early gear-up (healthy)." if med_l<35 else "Late — dying before looting?" if med_l>65 else "Mid-match looting."
            st.markdown(f'<span class="chip-inf">Median at {med_l:.0f}% — {v}</span>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    r3a, r3b = st.columns([2,3])
    with r3a:
        st.markdown('<div class="slbl">Cause of death breakdown</div>', unsafe_allow_html=True)
        dc = {"H→H":deaths,"By bot":bkd,"Storm":storm_d,"Extracted":max(0,nh*nm-deaths-bkd-storm_d)}
        fig_pie = go.Figure(go.Pie(labels=list(dc.keys()), values=list(dc.values()), hole=0.55,
                                    marker=dict(colors=["#ff2244","#ff8844","#cc44ff","#00e57a"],
                                                line=dict(color="#07090d",width=3)),
                                    textfont=dict(family="IBM Plex Mono",size=9,color="#c8d0e0")))
        fig_pie.update_layout(paper_bgcolor="#07090d",font=dict(color="#6878a0"),
                              height=220,margin=dict(l=0,r=0,t=0,b=0),
                              legend=dict(font=dict(color="#6878a0",size=9,family="IBM Plex Mono"),bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig_pie, use_container_width=True)
    with r3b:
        st.markdown('<div class="slbl">Match summary</div>', unsafe_allow_html=True)
        h_pm = df_view[df_view["is_human"]].groupby("match_id_clean")["user_id"].nunique().rename("H")
        b_pm = df_view[~df_view["is_human"]].groupby("match_id_clean")["user_id"].nunique().rename("B")
        ep   = df_view.groupby("match_id_clean")["event"].value_counts().unstack(fill_value=0)
        summ = pd.concat([h_pm,b_pm],axis=1).fillna(0).astype(int)
        for c in ["Kill","Killed","BotKill","KilledByStorm","Loot"]:
            summ[c] = ep[c].astype(int) if c in ep.columns else 0
        summ["Min"] = (df_view.groupby("match_id_clean")["ts_relative"].max()/60).round(1)
        summ = summ.reset_index().rename(columns={"match_id_clean":"Match"})
        summ["Match"] = summ["Match"].str[:20]+"…"
        st.dataframe(summ.sort_values("Min",ascending=False), use_container_width=True, height=220)


# ════════════════════════════════════════════════════════════════════════
# TAB 4 — MATCH REPLAY (Plotly native animation)
# ════════════════════════════════════════════════════════════════════════
with t_replay:
    s_col, i_col = st.columns([4,1])
    with i_col:
        st.markdown('<div class="slbl">Find Match</div>', unsafe_allow_html=True)
        s_mid = st.text_input("Match ID", placeholder="paste or type…", key="s_mid")
        if s_mid:
            hits = df_all[df_all["match_id_clean"].str.contains(s_mid.strip(),case=False)]["match_id_clean"].unique()
            replay_mid = hits[0] if len(hits) else None
            st.markdown(f'<span class="chip-{"ok" if replay_mid else "bad"}">{"✓ found" if replay_mid else "not found"}</span>', unsafe_allow_html=True)
        elif is_sing:
            replay_mid = sel_m
        else:
            replay_mid = None

    with s_col:
        if not replay_mid:
            st.info("Select a match from sidebar (MATCH VIEW) or search →")
        else:
            rdf_info = df_all[df_all["match_id_clean"]==replay_mid]
            nh_r = rdf_info[rdf_info["is_human"]]["user_id"].nunique()
            nb_r = rdf_info[~rdf_info["is_human"]]["user_id"].nunique()
            t_max_r = rdf_info["ts_relative"].max()
            map_r   = rdf_info["map_id"].iloc[0]

            st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;color:#2e3d52;margin-bottom:8px">MAP <span style="color:#00e57a">{map_r}</span> · DUR <span style="color:#c8d0e0">{t_max_r/60:.1f}min</span> · HUMANS <span style="color:#4a9eff">{nh_r}</span> · BOTS <span style="color:#445566">{nb_r}</span></div>', unsafe_allow_html=True)

            st.markdown("""
            <div style="font-family:IBM Plex Mono,monospace;font-size:0.66rem;color:#2e3d52;padding:6px 10px;background:#0d1118;border:1px solid #141c28;border-radius:4px;margin-bottom:8px">
            ▶ PLAY / ⏸ PAUSE buttons are inside the map below (bottom-left). Scrub with the timeline slider inside the chart.
            Time step per frame = ~{:.0f}s of match time.
            </div>""".format(t_max_r / 35), unsafe_allow_html=True)

            with st.spinner(f"Pre-computing {35} animation frames… (~3s, cached after)"):
                fig_anim = build_animated_figure(replay_mid, df_all, n_frames=35)

            st.plotly_chart(fig_anim, use_container_width=True)

            # Player roster — SVG line+circle+arrow per human, dashed for bots
            human_ids_r = sorted(rdf_info[rdf_info["is_human"]]["user_id"].unique())
            player_colors_r = {uid: PLAYER_PALETTE[i%len(PLAYER_PALETTE)] for i,uid in enumerate(human_ids_r)}
            roster = (
                '<div style="display:flex;flex-wrap:wrap;gap:6px 18px;padding:10px 6px;'
                'background:#07090d;border-top:1px solid #141c28;align-items:center">'
                '<span style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;'
                'color:#2e3d52;text-transform:uppercase;letter-spacing:0.1em">Humans:</span>'
            )
            for uid in human_ids_r:
                c = player_colors_r[uid]
                roster += (
                    f'<span style="display:flex;align-items:center;gap:6px">'
                    # SVG: line + start circle + arrow
                    f'<svg width="28" height="14" xmlns="http://www.w3.org/2000/svg">'
                    f'<line x1="0" y1="7" x2="28" y2="7" stroke="{c}" stroke-width="2.5"/>'
                    f'<circle cx="5" cy="7" r="4.5" fill="{c}" stroke="white" stroke-width="1.5"/>'
                    f'<polygon points="28,7 22,4 22,10" fill="{c}"/>'
                    f'</svg>'
                    f'<span style="font-size:0.68rem;color:{c};'
                    f'font-family:IBM Plex Mono,monospace;letter-spacing:0.02em">'
                    f'{uid[:14]}…</span></span>'
                )
            if nb_r > 0:
                roster += (
                    '<span style="display:flex;align-items:center;gap:6px;margin-left:6px">'
                    '<svg width="28" height="14" xmlns="http://www.w3.org/2000/svg">'
                    '<line x1="0" y1="7" x2="28" y2="7" stroke="#556070" '
                    'stroke-width="1.5" stroke-dasharray="5,4"/>'
                    '</svg>'
                    '<span style="font-size:0.68rem;color:#556070;'
                    'font-family:IBM Plex Mono,monospace">Bots</span></span>'
                )
            roster += '</div>'
            st.markdown(roster, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════
# TAB 5 — PLAYER PROFILE (reads from sidebar PLAYER VIEW)
# ════════════════════════════════════════════════════════════════════════
with t_player:
    if not p_uid:
        st.info("Search or pick a player in the PLAYER VIEW section of the sidebar →")
    else:
        p_udf_all = df_all[df_all["user_id"]==p_uid]
        if p_udf_all.empty:
            p_udf_all = df_all[df_all["user_id"].str.contains(p_uid,case=False,na=False)]

        if p_udf_all.empty:
            st.error(f"Player '{p_uid}' not found.")
        else:
            uid_res = p_udf_all["user_id"].iloc[0]
            is_h_p  = p_udf_all["is_human"].iloc[0]
            ptc     = "#4a9eff" if is_h_p else "#445566"

            # Apply player filters
            p_udf = p_udf_all.copy()
            if p_map != "All": p_udf = p_udf[p_udf["map_id"]==p_map]

            k_  = int((p_udf["event"]=="Kill").sum())
            d_  = int((p_udf["event"].isin(["Killed","KilledByStorm","BotKilled"])).sum())
            bk_ = int((p_udf["event"]=="BotKill").sum())
            l_  = int((p_udf["event"]=="Loot").sum())
            m_  = p_udf["match_id_clean"].nunique()

            st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;margin-bottom:12px"><span style="background:{ptc}22;color:{ptc};border:1px solid {ptc}44;border-radius:3px;padding:2px 8px">{"HUMAN" if is_h_p else "BOT"}</span> &nbsp;<span style="color:#4a5a78">{uid_res}</span></div>', unsafe_allow_html=True)

            cc = st.columns(5)
            for col,lbl,val,acc in [(cc[0],"Matches",m_,"#00e57a"),(cc[1],"Kills",k_,"#ff8c00"),
                                     (cc[2],"Deaths",d_,"#ff2244"),(cc[3],"K/D",f"{k_/(d_ or 1):.2f}","#ffdd22"),
                                     (cc[4],"Loots",l_,"#00e57a")]:
                col.markdown(f'<div class="mc" style="--ac:{acc}"><div class="mc-lbl">{lbl}</div><div class="mc-val" style="font-size:1.2rem">{val}</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            map_for_viz = p_map if p_map != "All" else p_udf["map_id"].mode()[0] if not p_udf.empty else "AmbroseValley"

            if p_mode == "Aggregate — all matches":
                st.markdown(f'<div class="slbl">Favorite Zones — {map_for_viz} · {m_} matches · all position events</div>', unsafe_allow_html=True)

                agg = p_udf[p_udf["map_id"]==map_for_viz]
                pos_agg = agg[agg["event"].isin(["Position","BotPosition"])].dropna(subset=["pixel_x","plot_y"])

                fig_agg = base_fig(map_for_viz, h=520, show_legend=True)
                if not pos_agg.empty:
                    g, xe, ye = np.histogram2d(pos_agg["pixel_x"], pos_agg["plot_y"],
                                               bins=96, range=[[0,1024],[0,1024]])
                    g = g.T.astype(float); g[g==0] = np.nan
                    xc = 0.5*(xe[:-1]+xe[1:]); yc = 0.5*(ye[:-1]+ye[1:])
                    fig_agg.add_trace(go.Heatmap(z=g, x=xc, y=yc, colorscale=HEAT_SCALE,
                                                  opacity=0.72, showscale=False, zsmooth="best",
                                                  hovertemplate="visits: %{z:.0f}<extra></extra>"))
                combat_agg = agg[agg["event"].isin(COMBAT_EV)]
                add_clustered_events(fig_agg, combat_agg)
                st.plotly_chart(fig_agg, use_container_width=True)

                st.markdown('<div class="slbl" style="margin-top:8px">Per-match breakdown</div>', unsafe_allow_html=True)
                pm = p_udf.groupby("match_id_clean").agg(
                    Map=("map_id","first"), Date=("date","first"),
                    K=("event",lambda x:(x=="Kill").sum()), D=("event",lambda x:x.isin(["Killed","KilledByStorm","BotKilled"]).sum()),
                    BK=("event",lambda x:(x=="BotKill").sum()), L=("event",lambda x:(x=="Loot").sum()),
                    Min=("ts_relative",lambda x:round(x.max()/60,1)),
                ).reset_index()
                pm["match_id_clean"] = pm["match_id_clean"].str[:22]+"…"
                pm = pm.rename(columns={"match_id_clean":"Match"})
                st.dataframe(pm, use_container_width=True, height=180)

            else:  # Single match path
                viz = p_udf[(p_udf["map_id"]==map_for_viz) & (p_udf["match_id_clean"]==p_match)].sort_values("ts_relative")
                st.markdown(f'<div class="slbl">Path — {map_for_viz} · {p_match[:22]}…</div>', unsafe_allow_html=True)

                fig_p = base_fig(map_for_viz, h=520, show_legend=True)
                pos_p = viz[viz["event"].isin(["Position","BotPosition"])]
                if len(pos_p) > 1:
                    add_player_path(fig_p, pos_p, PLAYER_PALETTE[0], uid_res[:12])
                add_clustered_events(fig_p, viz[viz["event"].isin(COMBAT_EV)])
                st.plotly_chart(fig_p, use_container_width=True)

                dur_s = viz["ts_relative"].max()
                st.markdown(f'<span class="chip-inf">Duration: {dur_s/60:.1f}min</span><span class="chip-ok">Kills: {(viz["event"]=="Kill").sum()}</span><span class="chip-bad">Deaths: {viz["event"].isin(["Killed","KilledByStorm","BotKilled"]).sum()}</span><span class="chip-ok">Loots: {(viz["event"]=="Loot").sum()}</span>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════
# TAB 6 — HEATMAPS
# ════════════════════════════════════════════════════════════════════════
with t_heat:
    hc1, hc2 = st.columns([4,1])

    with hc2:
        st.markdown('<div class="slbl">Options</div>', unsafe_allow_html=True)
        htype       = st.radio("Layer", list(HMAP_TYPES.keys()), label_visibility="collapsed")
        opacity_h   = st.slider("Overlay opacity", 0.3, 1.0, 0.72, 0.05)
        bins_h      = st.slider("Resolution", 16, 128, 128)
        show_bubbles = st.checkbox("Show hotspot bubbles", True)
        st.markdown("<hr style='border-color:#141c28'>", unsafe_allow_html=True)
        hevts = HMAP_TYPES[htype]
        hdf   = df_view[df_view["event"].isin(hevts)].dropna(subset=["pixel_x","plot_y"])
        st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;color:#2e3d52;line-height:2.2">EVENTS<br><span style="color:#c8d0e0;font-size:1.1rem">{len(hdf):,}</span></div>', unsafe_allow_html=True)

    with hc1:
        fig_h = base_fig(sel_map, h=660, show_legend=False)

        if hdf.empty:
            st.warning(f"No events for '{htype}' in current selection.")
        else:
            total_ev = len(hdf)
            g, xe, ye = np.histogram2d(hdf["pixel_x"].values, hdf["plot_y"].values,
                                        bins=bins_h, range=[[0,1024],[0,1024]])
            g_raw = g.T.astype(float)
            # Normalize: % of total events in this type
            g_norm = g_raw / total_ev * 100
            g_norm[g_norm == 0] = np.nan

            xc = 0.5*(xe[:-1]+xe[1:]); yc = 0.5*(ye[:-1]+ye[1:])

            fig_h.add_trace(go.Heatmap(
                z=g_norm, x=xc, y=yc,
                colorscale=HEAT_SCALE, opacity=opacity_h,
                showscale=True, zsmooth="best",
                colorbar=dict(
                    title=dict(text="% of events", font=dict(color="#6878a0",size=10,family="IBM Plex Mono")),
                    tickfont=dict(color="#6878a0",size=9,family="IBM Plex Mono"),
                    ticksuffix="%", len=0.45, thickness=10,
                ),
                hovertemplate="%{z:.2f}% of events here<extra></extra>",
            ))

            # Coarse 8×8 grid — computed always (bubbles + insights both use it)
            BUBBLE_GRID = 8
            g_coarse, bxe, bye = np.histogram2d(
                hdf["pixel_x"].values, hdf["plot_y"].values,
                bins=BUBBLE_GRID, range=[[0,1024],[0,1024]]
            )
            g_coarse   = g_coarse.T
            coarse_pct = g_coarse / total_ev * 100
            bxc = 0.5*(bxe[:-1]+bxe[1:])
            byc = 0.5*(bye[:-1]+bye[1:])

            # Hotspot bubbles
            if show_bubbles:
                peak_pct = coarse_pct.max()

                for iy in range(BUBBLE_GRID):
                    for ix in range(BUBBLE_GRID):
                        pct = coarse_pct[iy, ix]
                        if pct < 0.1:   # skip near-empty cells
                            continue

                        # Size: sqrt scaling so small cells still visible
                        norm = pct / peak_pct  # 0→1
                        sz = 18 + norm * 52    # 18px min → 70px max

                        # Color: yellow→orange→red by norm
                        r = 255
                        g_ch = int(220 * (1 - norm))
                        b_ch = 0
                        alpha = 0.25 + norm * 0.55  # more opaque at peak
                        fill_color = f"rgba({r},{g_ch},{b_ch},{alpha:.2f})"
                        border_color = f"rgba({r},{g_ch},{b_ch},0.9)"

                        fig_h.add_trace(go.Scatter(
                            x=[float(bxc[ix])], y=[float(byc[iy])],
                            mode="markers+text",
                            marker=dict(
                                size=sz,
                                color=fill_color,
                                line=dict(color=border_color, width=1.5),
                                symbol="circle",
                            ),
                            text=[f"{pct:.1f}%"],
                            textfont=dict(color="white", size=8,
                                         family="IBM Plex Mono"),
                            textposition="middle center",
                            hovertemplate=(
                                f"<b>{pct:.2f}%</b> of {htype} events<br>"
                                f"({int(g_coarse[iy,ix]):,} events)<extra></extra>"
                            ),
                            showlegend=False,
                        ))

            st.plotly_chart(fig_h, use_container_width=True)
            peak    = float(np.nanmax(g_norm))
            dead_pct = int(np.sum(np.isnan(g_norm)) / (bins_h*bins_h) * 100)
            st.markdown(
                f'<span class="chip-inf">Peak cell: {peak:.2f}% of events</span>'
                f'<span class="chip-inf">Total events: {total_ev:,}</span>'
                f'<span class="chip-{"warn" if dead_pct>70 else "ok"}">Dead zones: {dead_pct}% of map</span>',
                unsafe_allow_html=True
            )
            st.markdown("""
            <div style="display:flex;gap:12px;align-items:center;padding:8px 2px;font-size:0.71rem;color:#6878a0;border-top:1px solid #141c28;margin-top:6px">
              <span>Heatmap:</span>
              <span style="width:12px;height:12px;border-radius:2px;background:rgba(255,220,0,0.45);display:inline-block"></span><span>Low</span>
              <span style="width:12px;height:12px;border-radius:2px;background:rgba(255,140,0,0.75);display:inline-block"></span><span>Medium</span>
              <span style="width:12px;height:12px;border-radius:2px;background:rgba(255,40,40,1);display:inline-block"></span><span>Peak</span>
              <span style="width:12px;height:12px;border-radius:2px;background:transparent;border:1px solid #2e3d52;display:inline-block"></span><span>No events</span>
              &nbsp;|&nbsp;
              <span>Bubbles (8×8 grid):</span>
              <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:rgba(255,220,0,0.4);border:1px solid rgba(255,220,0,0.8)"></span><span>Low %</span>
              <span style="display:inline-block;width:16px;height:16px;border-radius:50%;background:rgba(255,80,0,0.7);border:1px solid rgba(255,80,0,0.9)"></span><span>High %</span>
              <span style="font-size:0.65rem;color:#2e3d52">(all bubbles sum to 100%)</span>
            </div>""", unsafe_allow_html=True)

            # ── Auto-generated heatmap insights ──────────────────────────
            st.markdown('<div class="slbl" style="margin-top:16px">What the data says — '
                        f'{sel_map} · {htype}</div>', unsafe_allow_html=True)

            if total_ev > 0:
                # Reuse coarse grid already computed above
                flat_pct  = coarse_pct.flatten()
                flat_cnt  = g_coarse.flatten()
                active    = flat_pct[flat_pct >= 0.1]
                n_active  = len(active)
                n_dead    = 64 - n_active
                top1_pct  = float(flat_pct.max())
                top3_pct  = float(np.sort(flat_pct)[::-1][:3].sum())
                top3_share = top3_pct / flat_pct.sum() * 100 if flat_pct.sum() > 0 else 0

                # Concentration signal
                if top1_pct > 20:
                    conc_chip = "chip-bad"
                    conc_msg  = (f"🔴 Extreme concentration — single zone holds "
                                 f"<b>{top1_pct:.1f}%</b> of all {htype} events. "
                                 f"Players are funnelling to one spot every match.")
                elif top1_pct > 10:
                    conc_chip = "chip-warn"
                    conc_msg  = (f"🟡 High concentration — top zone holds "
                                 f"<b>{top1_pct:.1f}%</b> of events. "
                                 f"Predictable routing risk.")
                else:
                    conc_chip = "chip-ok"
                    conc_msg  = (f"🟢 Healthy spread — top zone only "
                                 f"<b>{top1_pct:.1f}%</b>. Events distributed across map.")

                # Dead zone signal
                if n_dead > 40:
                    dead_chip = "chip-bad"
                    dead_msg  = (f"🔴 <b>{n_dead}/64 zones</b> have near-zero activity. "
                                 f"Large portions of {sel_map} are never visited. "
                                 f"Check loot density and pathing in dark areas.")
                elif n_dead > 25:
                    dead_chip = "chip-warn"
                    dead_msg  = (f"🟡 <b>{n_dead}/64 zones</b> barely touched. "
                                 f"Some map areas are underutilised.")
                else:
                    dead_chip = "chip-ok"
                    dead_msg  = (f"🟢 <b>{64-n_dead}/64 zones</b> see activity. "
                                 f"Good map coverage.")

                # Top-3 share signal
                top3_msg = (f"Top 3 zones account for "
                            f"<b>{top3_pct:.1f}%</b> of all {htype} events "
                            f"({top3_share:.0f}% of active zone traffic).")

                # Loot-specific: if showing loot, flag mid-match timing
                extra_msg = ""
                if "Loot" in hevts:
                    ldf2 = hdf.merge(
                        df_view.groupby("match_id_clean")["ts_relative"].max().rename("dur"),
                        on="match_id_clean", how="left"
                    )
                    ldf2["pct"] = ldf2["ts_relative"] / ldf2["dur"].clip(lower=1)
                    med_l = ldf2["pct"].median() * 100
                    if med_l > 40:
                        extra_msg = (
                            f"⚠️  Loot median timing: <b>{med_l:.0f}%</b> through match — "
                            f"players aren't finding loot near spawn. "
                            f"Consider adding loot nodes in the {n_dead} cold zones."
                        )

                # Traffic-specific: flag if bot + human traffic diverge
                if "BotPosition" in hevts and "Position" in hevts:
                    h_traffic = df_view[df_view["event"]=="Position"].dropna(subset=["pixel_x","plot_y"])
                    b_traffic = df_view[df_view["event"]=="BotPosition"].dropna(subset=["pixel_x","plot_y"])
                    if len(h_traffic) > 10 and len(b_traffic) > 10:
                        h_cx = h_traffic["pixel_x"].mean()
                        b_cx = b_traffic["pixel_x"].mean()
                        diverge = abs(h_cx - b_cx)
                        if diverge > 150:
                            extra_msg = (
                                f"⚠️  Human and bot traffic centroids are "
                                f"<b>{diverge:.0f}px apart</b> on the minimap — "
                                f"humans and bots are operating in different map areas. "
                                f"Switch to 'Human Traffic' vs 'Bot Traffic' layers to compare."
                            )

                for msg in [conc_msg, dead_msg, top3_msg]:
                    st.markdown(
                        f'<div style="font-size:0.78rem;color:#6878a0;line-height:1.6;'
                        f'padding:6px 12px;margin:3px 0;background:#0b0e15;'
                        f'border:1px solid #141c28;border-radius:4px">{msg}</div>',
                        unsafe_allow_html=True
                    )
                if extra_msg:
                    st.markdown(
                        f'<div style="font-size:0.78rem;color:#ffcc44;line-height:1.6;'
                        f'padding:6px 12px;margin:3px 0;background:#151008;'
                        f'border:1px solid #2a2010;border-radius:4px">{extra_msg}</div>',
                        unsafe_allow_html=True
                    )
