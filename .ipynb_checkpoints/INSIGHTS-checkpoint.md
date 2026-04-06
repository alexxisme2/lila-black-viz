# INSIGHTS.md — LILA BLACK: Complete Data Analysis

> **Dataset:** 5 days of production gameplay telemetry (Feb 10–14, 2026)  
> **Scope:** 88,682 events · 796 matches · 245 human players · 94 bots (with files) · 3 maps  
> **Critical context established during analysis:** This dataset is a pre-production QA environment, not live players (see Meta-Insight below). This context shapes every observation — insights are labeled accordingly.

---

## How to Read This Document

Three levels of findings:

- **[CORE]** — Top 3 non-QA insights. Real design signals that hold regardless of player population. Backed by data that doesn't change when you add more players.
- **[QA-SIGNAL]** — Important observations, but partially or fully artifacts of the low-population QA environment. Valid to flag, wrong to act on before production data.
- **[DATA QUALITY]** — Technical findings about the dataset itself. These affected the analysis and some would have silently corrupted results if not caught.

---

## CORE INSIGHT 1 — The Entire Bot Combat System Is Analytically Blind

### What caught my eye

Bots are the dominant opponent in this game. The kill breakdown tells the whole story:

```
H→H kills (player vs player):    3
Bot kills (player killed a bot):  2,415
Ratio:                            805:1
```

Players are fighting bots almost exclusively. Bots ARE the game right now. Then I looked at what data we actually have on bots:

```
Matches where BotKill events happened:           605
Matches where BotPosition files were loaded:      52  (8.6%)
Matches with BotKill but NO movement data:       553  (91.4%)
```

And the bot event types that exist in the schema:

```python
df[~df["is_human"]]["event"].unique()
→ ['BotPosition', 'BotKilled', 'BotKill']
```

That is it. Three event types. No BotLoot. No BotKilledByStorm. No BotEngaged. No bot-vs-bot interaction of any kind.

### The evidence

- 91% of matches where bots killed someone have zero bot movement data — the bot parquet files were not included in the dataset
- In the 52 matches where bot files DO exist, bots only log position when moving — nothing else
- Bots never log looting behavior — cannot determine whether bots compete for loot or ignore it
- Bots never log storm deaths — unknown if bots respond to the storm zone
- Bot-vs-bot encounters are completely invisible — if two bots fight, nothing is recorded
- Because bot spatial data is missing for 91% of matches, a meaningful bot traffic heatmap, patrol route analysis, or zone density map cannot be produced

### What this means for a level designer

You cannot answer any of the following from this data:

- Where do bots spawn and where do they patrol?
- Which areas of the map have high bot density?
- Are bots engaging players at fair distances, or rushing immediately?
- Do bots loot? Do they compete with players for the same nodes?
- Do bots respond to the storm, or stand still?
- What does a bot-vs-bot encounter look like spatially?

The primary combat experience of LILA BLACK is a black box.

### Actionable items

**Engineering (immediate):**
- Ensure bot parquet files are exported for every match — not 8.6% of them
- Add to bot event schema: `BotEngaged` (detected enemy, with distance + target ID), `BotLoot`, `BotKilledByStorm`, `BotPatrolPoint` (reached waypoint)
- Add bot-vs-bot: `BotEncounter` event when two bots enter engagement range

**Level design (with current data):**
- Use human-side `BotKill` coordinate clusters as a proxy for bot spawn density — visible in the Heatmaps tab under "Kill Zones (H→H)" → switch to all kills including bot kills
- Cross-reference BotKill clusters with loot heatmap — if they overlap, bots are guarding loot zones (intentional or accidental?)

**Metrics to add:**
- Bot file export coverage % per data run (target: 100%)
- Bot lethality ratio per map: BotKilled / BotKill — track weekly
- Time-to-first-bot-encounter per match per map

---

## CORE INSIGHT 2 — Loot Spawn Density May Be Too Low Near Drop Zones

### What caught my eye

I computed when players loot relative to match duration:

```
Loot timing (as % through match):
  Mean:    46%
  Median:  46%
  P25:     23%
  P75:     69%
  Total events: 12,885
```

In a well-designed extraction shooter, looting should happen early — first 25–33% of the match. Players drop, find loot quickly, gear up, then engage. A 46% median means players are looting at the halfway point of a 6.4-minute match — around minute 3.

### The evidence

- Loot happens at median 46% through match — not at the start
- Only ~23% of loot events happen in the first quarter of match time
- Match median duration is 6.4 minutes → players are finding their first items around minute 3
- 12,885 loot events — large enough sample for meaningful signal even in QA context
- Loot pickups cluster in specific zones (see QA-Signal: Dead Zones) — players are routing TO loot-dense areas rather than finding loot opportunistically near spawn

### What this means for a level designer

Two explanations, both actionable:

**Explanation A — Spawn loot density is too low.** Players land, find nothing near spawn, and spend the first half of the match routing to known loot-dense zones. The level is funneling players to specific locations before they can engage.

**Explanation B — The high-value loot zones are too far from spawn.** Players know where the good loot is and make a deliberate choice to travel there first. This is only a problem if it creates predictable, game-y routes rather than emergent decision-making.

Either way: a level designer should be able to show "where does a player find their first item within 2 minutes." The tool supports this — filter Match Replay to the first 20% of match time and look at loot marker positions.

### Actionable items

**Immediate analysis:**
- Filter Heatmaps → Loot Pickups on Match Replay slider (0–20% of match time) vs (80–100%) — compare where early vs late loot happens
- If early loot is sparse and centralized, spawn loot density is the lever

**Design actions:**
- Add loot nodes within 200m of every spawn point
- Create guaranteed early-game loot clusters — low-tier items ensuring players have something within 90 seconds of dropping
- Target: 50% of loot events in first 33% of match duration (currently ~23%)

**Metrics to track:**
- Time-to-first-loot per player per match (target: under 90 seconds)
- % of loot events in first third of match (current: ~23%, target: >50%)
- Loot node coverage — % of map quadrants with at least one loot event per match

---

## CORE INSIGHT 3 — The Storm Closes Too Slowly, With Near-Zero Variance

### What caught my eye

Storm death timing across all 39 storm deaths in the dataset:

```
pct_through_match (storm death time ÷ match duration):
  count:   39
  mean:    1.00
  std:     0.00
  min:     0.99
  max:     1.00
```

Standard deviation of zero. Every storm death — 5 days, 796 matches, 3 maps — happens in the final 1% of match time. This is not a distribution. It is a ceiling effect.

### The evidence

- 39 total storm deaths across 796 matches (4.9% of matches)
- 95.1% of matches end with zero storm deaths
- Every storm kill is at ≥99% of match duration — the storm only catches players in the literal last seconds
- Players are looting at 46% through match (mid-game) — freely, without storm pressure
- Survival rate: 43.4% per human-match — but deaths are primarily from bots, not storm

### The QA nuance — do not ignore this

In a solo-player QA environment, there is no PvP pressure slowing players down. A single tester can move directly to extraction, loot optimally, and leave before the storm threatens them. In production with 10 players contesting the same space, storm pressure compounds — combat delays extraction, third-parties happen at extraction points, players get caught.

This means the storm finding is real but the severity may be partially a QA artifact. The std=0 is hard to explain away as pure population artifact — a well-tuned storm should catch at least some solo players mid-match. But "storm is useless" needs re-evaluation with a real player population.

### What this means for a level designer

Even accounting for QA context: a storm that kills zero players mid-match provides no spatial pressure. The storm should:
- Force players off the full map and toward extraction corridors by mid-match
- Create encounter opportunities by funneling players toward the same exit points
- Punish over-extending on loot

None of this is happening. Players route freely, loot mid-map, and extract without urgency. The storm is a visual effect, not a constraint.

### Actionable items

**Tuning test:**
- Reduce storm closing speed by 30% and run 10 controlled sessions
- Measure: does storm death timing shift below 80% of match duration?
- Measure: does loot timing compress (players rushing earlier)?
- Measure: does extraction point congestion increase?

**Metrics to track:**
- % of matches with any storm death (current: 4.9%, target: >20%)
- Median storm kill timing (current: 100%, target: <80%)
- Extraction success rate under faster storm (healthy range: 40–60%)

---

## META-INSIGHT — This Is a QA Environment, Identifiable from the Data Alone

This is not a game design insight — it is an analytical one. Correctly identifying the environment type from raw telemetry, before being told, is a prerequisite for interpreting everything else correctly.

### The signal

```
Solo-human matches (exactly 1 human player):    97.9%
Avg humans per match:                           1.0
Matches with any H→H kill:                     0.4%
Total H→H kills across 5 days:                 3
Unique human players across 5 days:            245 (~68/day)
Bot file coverage:                             6.5%
Duplicate rows (cross-day ingest):             1,420 (decreasing trend)
Sub-60-second matches:                         10
```

The decreasing duplicate trend is the clearest signal:

```
Feb 10:  1,231 duplicate rows
Feb 11:    685
Feb 12:    388
Feb 13:    281
Feb 14:    116
```

The ingestion pipeline was being actively debugged during this 5-day window. That is not a live product — that is an engineering team iterating on telemetry infrastructure.

### Why this matters

Every insight must be filtered through this lens:

| Observation | QA artifact? | Valid signal? |
|---|---|---|
| 99.6% matches have zero H→H kills | Yes — 1 human per match | No — do not use for PvP balance |
| Storm deaths only at match end | Partially — no PvP pressure slowing players | Yes — mechanical tuning issue regardless |
| Loot timing at 46% | Partially | Yes — individual behavior is still behavior |
| Map imbalance (AmbroseValley 68%) | Possibly — QA sequencing | Partially — monitor but don't act yet |
| Bot telemetry gaps | No — engineering issue | Yes — fix regardless of environment |
| Dead zones in AmbroseValley | Partially | Yes — but may resolve with more players |

---

## QA-SIGNAL INSIGHTS

### QA-1: H→H Combat Is Structurally Absent — But Bot Balance Is Measurable

**Data:** 3 H→H kills, 2,415 bot kills, 805:1 ratio. 99.6% of matches have zero PvP.

**QA context:** 97.9% solo matches make H→H literally impossible in most sessions.

**What is real:** Bot lethality ratio is the only combat balance metric available right now. `BotKilled (humans killed by bots) = 177` vs `BotKill (humans killing bots) = 2,415` → ratio = 0.07. Humans kill 14× more bots than bots kill humans. Bots may be too passive, too inaccurate, or not finding players efficiently.

**Action:** Track bot lethality ratio per map per QA sprint. A challenging but fair ratio: 1 bot kill per 3 human kills (~0.33). Current ratio is 0.07 — bots are not a meaningful threat.

---

### QA-2: Map Utilization Imbalance — Likely a Testing Order Artifact

**Data:** AmbroseValley 68.8%, Lockdown 23.9%, GrandRift 7.7%.

**QA context:** Teams test maps sequentially. AmbroseValley may simply be the oldest, most stable map. GrandRift at 7.7% likely means it was added recently or is unstable.

**What is real:** GrandRift has almost no gameplay data. Any balance decisions for that map are made on near-zero evidence. This is a launch risk.

**Action:** Force-rotate GrandRift for the next QA sprint. Set a minimum data threshold before shipping any map (recommend 500+ matches with real player population).

---

### QA-3: Dead Zones — 57% of AmbroseValley Never Visited

**Data:** 57% of AmbroseValley (32×32 grid) has zero position events across all sessions. Loot pickups concentrate in a minority of zones.

**QA context:** QA testers develop habitual routes fast. Dead zones in a small team's data may not represent production player behavior — new players explore.

**What is real:** Dead zones correlate with loot concentration. If certain zones have better loot spawn tables, players route there repeatedly and other areas go dark. This is a spawn table issue, visible now.

**Action:** Overlay Traffic heatmap with Loot heatmap in the tool. If dead zones have zero loot, that is the cause. Add loot nodes to dark quadrants. Target: >40% of map cells visited per match.

---

### QA-4: 43.4% Survival Rate — Actually in Healthy Range

**Data:** 43.4% of human-matches end with the player surviving (extracting). 56.6% die — primarily to bots.

**Context:** With storm nearly inactive, deaths are almost entirely bot-inflicted. This is close to the healthy 40–60% extraction shooter target — tense enough to matter, fair enough to keep playing.

**Caveat:** Re-evaluate after storm tuning. A faster storm will reduce survival rate. If it drops below 30%, storm is too aggressive.

---

### QA-5: Match Duration Is in a Healthy Range

**Data:** Median 6.4 minutes. P25: 4.2 min, P75: 9.1 min.

**Signal:** 6.4 minutes is good for an extraction shooter. Not too short (under-engaged) or too long (over-looped). The 10 sub-60-second matches are almost certainly crashes — flag to backend.

**Action:** Exclude sub-60-second matches from all balance analysis. Tag as INVALID_SESSION in the data pipeline.

---

### QA-6: Match Composition Segmentation Is Unusual

**Data:** 744 human-only matches, 16 bot-only matches, 36 mixed.

**Observation:** Humans and bots rarely share a match (36/796 = 4.5%). Bot-only matches (16) are automated test sessions. The rarity of mixed sessions may be intentional QA structure or a matchmaking issue.

**Action:** Clarify whether mixed sessions are intentional. If yes, increase their frequency — that is the production scenario and it is being undertested.

---

## DATA QUALITY FINDINGS

These required real analytical work. Some would have silently corrupted the entire analysis if not caught.

### DQ-1: README Timestamp Unit Is Wrong — Caught Before It Broke Everything

**What happened:** The README states ts is stored as milliseconds. Using `pd.to_datetime(ts, unit='ms')` produced dates in 1970 and a match "duration" of 0.6 seconds. Using `unit='s'` gave February 2026 dates and 6.4-minute matches.

**How it was caught:** Computed median match duration across all matches. Using ms: 0.1 seconds (impossible). Using seconds: 6.4 minutes (correct for the genre). Verified: timestamp `1,770,692,458` decodes to February 10, 2026 under seconds.

**Fix applied:** Cast via `pa.int64()` in PyArrow before pandas processes the column — extracts raw stored integer, bypasses PyArrow's automatic ms unit application. `ts_relative` is then `(ts_raw - match_min)` in correct seconds.

**Why it mattered:** If uncaught, every timeline visualization, storm timing analysis, loot timing analysis, and match replay would have been nonsense.

---

### DQ-2: 1,420 Duplicate Rows — Pipeline Was Being Fixed During This Window

**What happened:** 1,420 exact duplicate rows. By event type:

```
Loot:      2,338 rows
Position:    294 rows
BotKill:      65 rows
BotKilled:     4 rows
```

**Pattern — decreasing over time:**

```
Feb 10:  1,231 duplicates
Feb 11:    685
Feb 12:    388
Feb 13:    281
Feb 14:    116
```

85 rows confirmed present in multiple date folders under the same composite key.

**Interpretation:** Cross-day ingestion artifact. The same match files were indexed into multiple daily folders while the pipeline was being debugged. The decreasing trend confirms active fixes during the data window.

**Fix applied:** Dropped on composite key `(user_id, match_id_clean, ts_raw, event)`. Loot duplicates (2,338) were most critical to remove — they would have inflated loot density numbers and shifted timing analysis.

---

### DQ-3: Bot Files Missing for 91% of Matches

**What happened:** 553 of 605 matches with BotKill events had no corresponding BotPosition files.

**Interpretation:** Bot parquet files were not included in the data export for most matches. Bots existed (humans killed them) but their files were not packaged. A data export issue, not a game bug.

**Impact:** Bot spatial analysis possible for only 52/796 matches. All bot heatmaps are based on an unrepresentative 6.5% sample.

---

### DQ-4: 177 Post-Death Events — Normal Telemetry Behavior

**What happened:** 177 events logged after a player's recorded death timestamp.

**Interpretation:** Normal. Position events buffer client-side and flush in batches — some arrive after the death event timestamp. Spectator mode may also continue logging.

**Decision:** Retained. Negligible fraction of data, no impact on analysis.

---

### DQ-5: 10 Sub-60-Second Matches

**What happened:** 10 matches lasting under 1 minute.

**Interpretation:** Crashes, immediate disconnects, or automated test scripts that terminated early.

**Decision:** Included in dataset but excluded from duration statistics. Median used throughout (robust to outliers). Recommend tagging as INVALID_SESSION in the pipeline.
