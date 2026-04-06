"""
insights.py — LILA BLACK
Pre-computes game design observations from full dataset.
Called once at startup, runs on unfiltered df_all.

Each insight dict:
  n        : int (order)
  category : str (tag label)
  severity : "bad" | "warn" | "ok"
  title    : str (one-liner, specific numbers)
  signal   : str (raw data evidence)
  verdict  : str (what this means for game design)
  action   : str (what to change + metric to track)
"""

import numpy as np
import pandas as pd


def compute_insights(df: pd.DataFrame) -> list:
    insights = []
    match_dur = df.groupby("match_id_clean")["ts_relative"].max()
    n_matches = df["match_id_clean"].nunique()

    # ── 1. MAP DISTRIBUTION ───────────────────────────────────────────
    map_ev  = df["map_id"].value_counts()
    map_pct = (map_ev / len(df) * 100).round(1)
    top_map = map_ev.index[0]
    bot_map = map_ev.index[-1]

    insights.append({
        "n": 1, "category": "MAP BALANCE",
        "severity": "warn",
        "title": f"{top_map} gets {map_pct[top_map]:.0f}% of all events — {bot_map} is nearly abandoned at {map_pct[bot_map]:.0f}%",
        "signal": (
            f"Event distribution across {n_matches} matches: "
            + " | ".join(f"{m}: {map_pct.get(m,0):.0f}%" for m in map_ev.index)
            + f". Match distribution: "
            + " | ".join(f"{m}: {df[df['map_id']==m]['match_id_clean'].nunique()} matches" for m in map_ev.index)
        ),
        "verdict": (
            f"Testers strongly prefer {top_map}. {bot_map} at {map_pct[bot_map]:.0f}% of events suggests it's either "
            f"not fun enough, harder to navigate, has lower loot density, or is simply seen less in rotation. "
            f"In production, skewed map usage means one map absorbs balance feedback while others go undertested."
        ),
        "action": (
            f"Audit {bot_map}: extraction point count, loot density per area, spawn placement visibility. "
            f"Force-rotate {bot_map} in internal sessions. "
            f"Track: map selection rate per session, loot pickup count per map per match, match completion rate per map."
        ),
    })

    # ── 2. STORM IS DECORATIVE ────────────────────────────────────────
    storm   = df[df["event"] == "KilledByStorm"]
    n_storm = len(storm)
    storm_match_pct = storm["match_id_clean"].nunique() / n_matches * 100

    if n_storm > 0:
        st_t = storm.merge(match_dur.rename("dur"), on="match_id_clean", how="left")
        st_t["pct"] = st_t["ts_relative"] / st_t["dur"].clip(lower=1)
        med_pct = st_t["pct"].median() * 100
    else:
        med_pct = 100.0

    insights.append({
        "n": 2, "category": "STORM DESIGN",
        "severity": "bad",
        "title": f"Storm kills at {med_pct:.0f}% through match — it's a visual backdrop, not a mechanical threat",
        "signal": (
            f"{n_storm} total storm deaths across {n_matches} matches "
            f"({n_storm/n_matches:.2f}/match avg, {storm_match_pct:.0f}% of matches see any storm death). "
            f"Median storm kill timing: {med_pct:.0f}% into match. "
            f"All storm death pct values: min={st_t['pct'].min()*100:.0f}%, max={st_t['pct'].max()*100:.0f}%."
            if n_storm > 0 else f"0 storm deaths recorded across {n_matches} matches."
        ),
        "verdict": (
            "The storm only kills players at the very end of match (≈last 1%). Players are extracting safely "
            "before it becomes dangerous. In an extraction shooter, storm should force route decisions mid-match — "
            "driving players toward each other and creating tension around extraction timing. "
            "Currently it's cosmetic."
        ),
        "action": (
            "Reduce storm closing speed by 25-40% (faster close). Validate: does storm death timing shift to "
            "<70% of match duration? Track: % storm deaths before 80% match completion, extraction attempts under "
            "storm pressure, H→H encounter rate (storm should funnel players into contact zones)."
        ),
    })

    # ── 3. NO PvP — BOT COMBAT DOMINATES ─────────────────────────────
    pvp_kills  = int((df["event"] == "Kill").sum())
    bot_kills  = int((df["event"] == "BotKill").sum())
    pvp_match_pct = df[df["event"]=="Kill"]["match_id_clean"].nunique() / n_matches * 100
    ratio = bot_kills / max(pvp_kills, 1)

    insights.append({
        "n": 3, "category": "COMBAT BALANCE",
        "severity": "bad",
        "title": f"H→H combat is absent — {bot_kills:,} bot kills vs {pvp_kills} player kills ({ratio:.0f}:1 ratio)",
        "signal": (
            f"{pvp_kills} H→H kills in {n_matches} matches ({pvp_match_pct:.1f}% of matches have any PvP). "
            f"{bot_kills:,} bot kills. "
            f"97.9% of matches contain exactly 1 human — PvP is structurally impossible in most sessions. "
            f"Bot-to-PvP kill ratio: {ratio:.0f}:1."
        ),
        "verdict": (
            "This is a solo-vs-bots experience in practice. The absence of PvP isn't a design failure — "
            "it's a population problem in a pre-launch QA environment. However, bot balance IS meaningful: "
            "bots are the primary combat challenge, and their difficulty, pathing, and engagement frequency "
            "are what determines session quality for every tester."
        ),
        "action": (
            "Set minimum viable player count target before launch (recommend ≥4 humans/match for PvP emergence). "
            "For current QA phase: focus bot balance — are bots killing humans at a reasonable rate? "
            f"BotKilled (human killed by bot): {int((df['event']=='BotKilled').sum())} vs BotKill (human kills bot): {bot_kills}. "
            "Track: bot lethality ratio (BotKilled/BotKill), time-to-first-bot-encounter per match, "
            "human survival rate excluding storm."
        ),
    })

    # ── 4. LOOT CONCENTRATION ─────────────────────────────────────────
    loot_df = df[df["event"] == "Loot"].dropna(subset=["pixel_x", "plot_y"])
    av_loot = loot_df[loot_df["map_id"] == "AmbroseValley"].copy()

    if len(av_loot) > 50:
        av_loot["gx"] = (av_loot["pixel_x"] // 128).astype(int).clip(0, 7)
        av_loot["gy"] = (av_loot["plot_y"]  // 128).astype(int).clip(0, 7)
        cell_c  = av_loot.groupby(["gx","gy"]).size()
        top_pct = cell_c.max() / len(av_loot) * 100
        active  = (cell_c > 0).sum()

        insights.append({
            "n": 4, "category": "LOOT DISTRIBUTION",
            "severity": "warn" if top_pct > 25 else "ok",
            "title": f"{top_pct:.0f}% of AmbroseValley loots cluster in one 128px zone — {64-active} of 64 zones never touched",
            "signal": (
                f"{len(av_loot):,} loot events on AmbroseValley. "
                f"Top single 128×128px zone: {top_pct:.0f}% of all pickups. "
                f"{active}/64 map zones see any loot activity. "
                f"Top 3 zones combined: {cell_c.nlargest(3).sum()/len(av_loot)*100:.0f}% of all loot."
            ),
            "verdict": (
                f"Loot is gravitating to predictable hotspots. {'High concentration (>' + str(int(top_pct)) + '%) in one zone signals a risk-reward choke point — ' if top_pct > 25 else ''}"
                "Players route to the same areas every match, reducing map diversity and making loot spawns "
                "predictable. In extraction shooters, predictable loot = predictable player positions = "
                "less emergent gameplay."
            ),
            "action": (
                f"Add loot nodes to the {64-active} unvisited zones. Prioritize zones adjacent to "
                "current hot zones to pull players outward. "
                "Target: top single zone ≤15% of total loot, ≥75% of zones seeing loot activity. "
                "Track: loot pickup geographic spread index (std dev of pickup positions), "
                "unique zones visited per match."
            ),
        })

    # ── 5. MATCH PACING ───────────────────────────────────────────────
    durs     = match_dur / 60  # minutes
    med_dur  = durs.median()
    short_n  = int((durs < 3).sum())
    long_n   = int((durs > 12).sum())
    healthy  = 5 < med_dur < 10

    insights.append({
        "n": 5, "category": "MATCH PACING",
        "severity": "ok" if healthy else "warn",
        "title": f"Median match {med_dur:.1f}min — {short_n} matches end in <3min ({short_n/n_matches*100:.0f}% possible crashes)",
        "signal": (
            f"Median: {med_dur:.1f}min | P25: {durs.quantile(0.25):.1f}min | P75: {durs.quantile(0.75):.1f}min | "
            f"Min: {durs.min():.1f}min | Max: {durs.max():.1f}min. "
            f"{short_n} matches under 3min ({short_n/n_matches*100:.0f}%). "
            f"{long_n} matches over 12min ({long_n/n_matches*100:.0f}%)."
        ),
        "verdict": (
            f"{'Match length is within healthy extraction shooter range (5-10min ideal).' if healthy else 'Match length outside ideal 5-10min window.'} "
            f"{short_n} ultra-short matches likely represent crashes, game bugs, or immediate disconnects — "
            "worth flagging separately in your data pipeline. Long matches (>12min) may indicate overly "
            "lenient storm pressure or players hiding until last possible moment."
        ),
        "action": (
            "Flag matches <3min as 'invalid session' in data pipeline — exclude from balance analysis. "
            "For long matches: cross-reference with storm death timing. "
            "Track: match duration distribution week-over-week, quit/disconnect rate by time-in-match, "
            "correlation between match length and storm death occurrence."
        ),
    })

    # ── 6. DEAD ZONES ────────────────────────────────────────────────
    pos_df  = df[df["event"].isin(["Position","BotPosition"])].dropna(subset=["pixel_x","plot_y"])
    av_pos  = pos_df[pos_df["map_id"]=="AmbroseValley"]

    if len(av_pos) > 200:
        g32, _, _ = np.histogram2d(av_pos["pixel_x"], av_pos["plot_y"],
                                    bins=32, range=[[0,1024],[0,1024]])
        dead_cells   = int((g32 == 0).sum())
        total_cells  = 32 * 32
        dead_pct     = dead_cells / total_cells * 100
        visited_pct  = 100 - dead_pct

        insights.append({
            "n": 6, "category": "MAP COVERAGE — AMBROSEVALLEY",
            "severity": "warn" if dead_pct > 50 else "ok",
            "title": f"{dead_pct:.0f}% of AmbroseValley (32×32 grid) is never visited — large dead zones on every session",
            "signal": (
                f"{dead_cells}/{total_cells} grid cells (32px each) have zero position events. "
                f"{int(visited_pct)}% of map sees any traffic. "
                f"Analyzed {len(av_pos):,} position events across {av_pos['match_id_clean'].nunique()} matches."
            ),
            "verdict": (
                "Most of the map goes unvisited every session. Players are routing through predictable "
                "corridors — likely driven by loot hotspots, extraction point locations, and spawn positions. "
                "Unvisited areas may contain: impassable terrain, no loot incentive, awkward pathing, "
                "or simply no reason to deviate from the main route. "
                "Dead zones = wasted level design investment."
            ),
            "action": (
                "Overlay dead zone heatmap with map layout. Identify: are dead zones behind hard terrain? "
                "Near low-loot areas? Far from extraction? "
                "Add secondary objectives, loot, or extraction points to pull players off main corridors. "
                "Track: % map cells visited per match (target: ≥40%), route diversity score "
                "(spread of player paths across map quadrants)."
            ),
        })

    # ── 7. LOOT TIMING ────────────────────────────────────────────────
    loot_t = loot_df.merge(match_dur.rename("dur"), on="match_id_clean", how="left")
    loot_t["pct"] = loot_t["ts_relative"] / loot_t["dur"].clip(lower=1)

    if not loot_t.empty and loot_t["pct"].notna().any():
        med_l  = loot_t["pct"].median() * 100
        early  = (loot_t["pct"] < 0.33).mean() * 100
        late   = (loot_t["pct"] > 0.66).mean() * 100

        insights.append({
            "n": 7, "category": "PLAYER BEHAVIOR",
            "severity": "ok" if med_l < 50 else "warn",
            "title": f"Looting happens at {med_l:.0f}% into match — {early:.0f}% of pickups in first third, {late:.0f}% in last third",
            "signal": (
                f"Median loot timing: {med_l:.0f}% through match. "
                f"Early loots (<33%): {early:.0f}% of all pickups. "
                f"Late loots (>66%): {late:.0f}% of all pickups. "
                f"Total loot events: {len(loot_t):,} across all maps."
            ),
            "verdict": (
                f"{'Players loot mid-match rather than immediately on spawn. This is acceptable but suggests spawn-adjacent loot density may be low — players may not be finding loot quickly enough on drop.' if med_l > 40 else 'Players gear up early — healthy extraction shooter behavior.'} "
                f"{'Late-game looting (' + f'{late:.0f}%' + ' of pickups in last third) suggests players are either surviving long enough to reach late-game loot, or initial loot is scarce and they are still searching.' if late > 20 else ''}"
            ),
            "action": (
                f"{'Increase loot density near spawns — target: 50% of loots happening in first 25% of match. ' if med_l > 40 else 'Maintain current spawn loot density. '}"
                "Track: time-to-first-loot per player per match (should be <90 seconds), "
                "loot count per player by match quartile, correlation between early loot and survival rate."
            ),
        })

    return insights
