# Data Model Reference

Column specifications for the dynasty league star schema. Column lists below match
the live `data/*.parquet` files (verified 2026-06-06). Storage: local Parquet,
one file per table; CSV only for `data/review/` staging.

> **Parquet vs Power BI names:** the column/table names below are the **snake_case
> parquet/ETL names**. The Power BI semantic model (`pbi/mouserat2/`) exposes them
> with **PascalCase** table/column names (`Fact_DynastyRankingMetrics`, `MetricNum`,
> `SourceUID`) while each model column's `sourceColumn` keeps the snake_case name —
> so the parquet layer here is the source of truth and is unchanged by the model
> rename. DAX/report reference the PascalCase names. See memory
> `powerbi-semantic-model.md`.

**Player identity is two registries bridged by ids:**
- `dim_rookie_prospect` — current draft class, pre-/post-signing staging, key
  `player_key` (MD5 of name|pos|school).
- `dim_nfl_players` — full nflverse registry (~25k active+historical), key `gsis_id`.
- `dim_fantrax_crosswalk` — maps Fantrax `scorer_id` → both keys.
- `dim_player_alias` — persistent name-decision transformer (stops re-review).

`gsis_id` is the universal join key (the nflverse registry covers ~100% incl.
signed rookies); `player_key` only covers the draft class.

## Table of Contents
1. [dim_rookie_prospect](#dim_rookie_prospect)
2. [dim_nfl_players](#dim_nfl_players)
3. [dim_position](#dim_position)
4. [dim_school](#dim_school)
5. [dim_contract](#dim_contract)
6. [dim_fantasy_teams](#dim_fantasy_teams)
7. [dim_nfl_teams](#dim_nfl_teams)
8. [dim_fantrax_crosswalk](#dim_fantrax_crosswalk)
9. [dim_dynasty_crosswalk](#dim_dynasty_crosswalk)
10. [dim_dynasty_metric](#dim_dynasty_metric)
11. [dim_player_alias](#dim_player_alias)
12. [fact_rookie_rankings](#fact_rookie_rankings)
13. [fact_fantrax_adp](#fact_fantrax_adp)
14. [fact_dynasty_rankings](#fact_dynasty_rankings)
15. [fact_dynasty_ranking_metrics](#fact_dynasty_ranking_metrics)
16. [fact_fantasy_teams](#fact_fantasy_teams)
17. [fact_nfl_combine_pro_day_metrics](#fact_nfl_combine_pro_day_metrics)

---

## dim_rookie_prospect

Current draft-class prospects (pre-signing staging). Seeded from nflverse combine
invitees (~319), extended by expert-ranking ingestion (~468 rows). Was `dim_player`.

| Column | Type | Description |
|---|---|---|
| `player_key` | str | Deterministic MD5 of `name\|position\|school` (12 chars) — PK |
| `player_name` | str | Display name, original casing |
| `player_name_clean` | str | Normalized for matching (see `clean_player_name`) |
| `position_raw` | str | Position as received (uppercased) |
| `position_detail` | str | Canonical granular position (from `dim_position`) |
| `position_group` | str | Rolled-up group |
| `side_of_ball` | str | Offense / Defense / Special Teams |
| `fantasy_relevant` | bool | Dynasty-scorable position |
| `school_raw` | str | School as received |
| `school_canonical` | str | Canonical school (from `dim_school`) |
| `conference` | str | Athletic conference |
| `height_inches` | float | Height in inches (nullable) |
| `weight` | float | Weight in lbs (nullable) |
| `pfr_id` | str | Pro-Football-Reference id (nullable) |
| `cfb_id` | str | College-football-reference id (nullable) |
| `gsis_id` | str | nflverse id once signed/matched (nullable) |
| `draft_year` | int | NFL draft class |
| `source` | str | Origin record (e.g. `nflverse_combine`) |
| `added_date` | str | ISO date row created |

**Key**: `player_key`

---

## dim_nfl_players

Full nflverse player registry (active + historical), seeded by `nflreadpy.load_players()`
in `01e_dim_nfl_players_seed`. Rookies appear post-signing (~May–June).

| Column | Type | Description |
|---|---|---|
| `gsis_id` | str | nflverse GSIS id — PK, universal join key |
| `display_name`, `first_name`, `last_name` | str | Names |
| `birth_date` | str | ISO date (used to derive age; ~0.5% null) |
| `status` | str | `ACT` / `CUT` / `RES` / … |
| `team_abbr` | str | Current NFL team — **mapped from nflverse `latest_team`** |
| `position`, `position_group` | str | nflverse position |
| `jersey_number`, `years_of_experience` | num | |
| `college_name`, `college_conference` | str | |
| `entry_year` | int | NFL entry season — **from `rookie_season`** |
| `last_season` | int | Most recent season |
| `draft_year`, `draft_round`, `draft_number` | int | Draft — **`draft_number` from `draft_pick`** |
| `draft_club` | str | Drafting team — **from `draft_team`** |
| `height`, `weight` | num | |
| `pfr_id`, `pff_id`, `espn_id`, `esb_id`, `nfl_id`, `otc_id`, `smart_id` | str | Cross-ref ids |

**Key**: `gsis_id`. **Gotcha**: nflverse column names differ from these canonical
names — map explicitly in the seed notebook (a name-only select yields all-null
columns; this caused a 100%-null `team_abbr` bug).

---

## dim_position

Transformer mapping raw position strings → canonical. Add rows, never if/else.

| Column | Type | Description |
|---|---|---|
| `position_raw` | str | Raw position, uppercased — PK |
| `position_detail` | str | Granular canonical |
| `position_group` | str | Fantasy group |
| `position_sort_order` | int | Display order |
| `side_of_ball` | str | Offense / Defense / Special Teams |
| `side_of_ball_sort_order` | int | |
| `fantasy_relevant` | bool | Scores in dynasty |

**Key**: `position_raw`. Notebook 04a derives its IDP set from
`side_of_ball == "Defense"` here (single source of truth).

---

## dim_school

Transformer mapping raw school names → canonical + conference.

| Column | Type | Description |
|---|---|---|
| `school_raw` | str | School as in source — PK |
| `school_canonical` | str | Canonical/display name |
| `conference` | str | Athletic conference |

**Key**: `school_raw`

---

## dim_contract

Contract-scale definitions; **drives cap-hit % and dead money** — join on
`contract_id` at ETL, never hardcode. 10 rows, all unique.

| Column | Type | Description |
|---|---|---|
| `contract_id` | str | PK (e.g. `1st`..`6th`, `Franchise Tag`, `X`, `Minor`, `FA`) |
| `contract_type` | str | Fixed Salary / New Value / etc. |
| `contract_label` | str | Display label |
| `salary_type` | str | Salary category |
| `contract_year` | int | Position within term (1/2/3) for ETL advancement |
| `total_years` | int | Term length |
| `cap_hit_pct` | float | 50% / 40% / 0% by year |
| `guaranteed` | bool | Guaranteed → carries dead money |
| `cap_exempt` | bool | Exempt (Minor / FA) |
| `min_salary` | int | League-minimum floor where applicable |
| `notes` | str | |

**Key**: `contract_id`

---

## dim_fantasy_teams

28 league teams across 2 conferences (A=Riddell, B=Wilson). Sourced from a Google
Sheet. Was `dim_team`.

| Column | Type | Description |
|---|---|---|
| `team_key` | str | PK (A01..A14, B01..B14) |
| `team_name`, `team_abbr` | str | |
| `conference` | str | A / B |
| `division` | str | |
| `manager_email`, `manager_email_2` | str | |
| `original_cap`, `reinvestment_cap` | int | Cap structure |
| `cap_hits_current_yr`, `cap_hits_next_yr` | int | |
| `active_roster_salary` | int | |
| `remaining_cap_current_yr`, `remaining_cap_next_yr` | int | |

**Key**: `team_key`

---

## dim_nfl_teams

NFL team dimension from `nflreadpy.load_teams()` (36 rows incl. historical).

| Column | Type | Description |
|---|---|---|
| `team_abbr` | str | PK |
| `team_name` | str | |
| `team_id_pfr` | str | PFR id |
| `team_conf`, `team_division` | str | AFC/NFC + division |
| `team_color`, `team_color2` | str | Brand colors |
| `team_logo_wikipedia`, `team_logo_espn`, `team_wordmark` | str | Asset URLs |
| `team_stadium` | str | |

**Key**: `team_abbr`

---

## dim_fantrax_crosswalk

Bridge: Fantrax `scorer_id` → registry keys. Built by notebook 04z from distinct
`scorer_id`s in `fact_fantrax_adp`; back-fills the fact's FK columns.

| Column | Type | Description |
|---|---|---|
| `scorer_id` | str | Fantrax-native player id — PK |
| `player_name`, `position_raw`, `nfl_team`, `is_rookie` | — | Carried for review |
| `gsis_id` | str | FK → dim_nfl_players (primary, ~98% resolved) |
| `player_key` | str | FK → dim_rookie_prospect (draft class only) |
| `match_method` | str | `exact` / `exact+disambig` / `fuzzy` / `review` / `unmatched` |
| `match_score` | int | Fuzzy score where applicable |
| `resolved_date` | str | ISO date |

**Key**: `scorer_id`. Matcher: exact cleaned-name → disambiguate by **position**
(strongest) / `status==ACT` / team / recency → fuzzy ≥90. `scorer.rank` in the
Fantrax response is global, reused as `overall_rank`.

---

## dim_dynasty_crosswalk

Unified bridge: any dynasty source's native id → registry keys. One table for all
sources (vs per-source `dim_fantrax_crosswalk`). Built/refreshed by `04b` (and a
future shared `04y` resolver).

| Column | Type | Description |
|---|---|---|
| `source_uid` | str | **PK** = `f"{source}\|{source_player_id}"` — single-column key for PBI relationships |
| `source` | str | Source key (e.g. `KTC`) |
| `source_player_id` | str | Source-native id (KTC `playerID`; manual = name slug) |
| `source_player_name`, `source_position`, `source_team` | str | Carried for review |
| `gsis_id` | str | FK → dim_nfl_players (primary) |
| `player_key` | str | FK → dim_rookie_prospect (rookie fallback) |
| `match_method` | str | `exact` / `exact+disambig` / `fuzzy` / `manual` / `rookie` / `review` / `unmatched` |
| `match_score` | int | Fuzzy score where applicable |
| `resolved_date` | str | ISO date |

**Key**: `source_uid` (unique; the natural composite `(source, source_player_id)` is
not single-column, and `source_player_id` alone collides across sources — slugs shared
DS/FP). Matcher mirrors `dim_fantrax_crosswalk` (shared `etl_helpers.resolve_dynasty_crosswalk`).

---

## dim_dynasty_metric

Curated index for `fact_dynasty_ranking_metrics.metric_key` (notebook 04c). Lets
Power BI use metrics as a **matrix column axis**. Hand-maintained seed (like
`dim_position`); 04c validates it covers every metric_key in the fact.

| Column | Type | Description |
|---|---|---|
| `metric_key` | str | PK; joins to the long metrics fact |
| `metric_label` | str | Display name for the column header |
| `metric_group` | str | Value / Tier / Projection / Consensus / Market / Trend / Crowd / Notes |
| `metric_order` | int | Column flow (10s with gaps) — set `metric_label` *Sort by column* = this |
| `value_type` | str | `num` / `text` |
| `direction` | str | `up` (higher=better) / `down` / `neutral` — conditional formatting |

**Key**: `metric_key`.

---

## dim_player_alias

Persistent name-decision transformer (like `dim_position`). Stops the fuzzy review
from re-asking the same player and prevents matched variants from being dropped at
ingest. Backfilled from archived `*.applied_*.csv` by notebook 03y.

| Column | Type | Description |
|---|---|---|
| `name_clean` | str | Cleaned name — PK part |
| `position_raw` | str | Position — PK part |
| `player_key` | str | Resolved registry key |
| `decision` | str | `match` / `auto` / `new` |
| `source_example` | str | A source that produced this variant |
| `decided_date` | str | ISO date |

**Key**: `(name_clean, position_raw)`

---

## fact_rookie_rankings

Expert rankings, long/narrow — one row per player × source × phase. Phase-cascade
composites stored with `source_name="composite"`.

| Column | Type | Description |
|---|---|---|
| `player_key` | str | FK → dim_rookie_prospect |
| `gsis_id` | str | FK → dim_nfl_players (nullable) |
| `source_name` | str | Expert source (or `composite`) |
| `source_site` | str | Site/provider |
| `phase` | str | `pre_combine` / `post_combine` / `post_draft` |
| `draft_year` | int | |
| `global_rank` | int | Overall (nullable) |
| `positional_rank` | int | Within-position (nullable) |
| `grade` | float | Expert grade (nullable) |
| `capture_date`, `rank_date` | str | ISO dates |

**Key**: `player_key + source_name + phase + draft_year`

---

## fact_fantrax_adp

Fantrax snapshots. **Two snapshot types share this table** (notebook 04a):
- **Projection board** (`getDraftRanks`, `board_to_frame`): weekly, ~1,655 rows,
  `week`=`PRE`/`01`..`18`, `games_played` null. Phase-aware: preseason → season
  projection, in-season → YTD actuals.
- **Season-actuals backfill** (`getPlayerStats`, `backfill_player_stats`):
  completed seasons, e.g. `season=2025, week='YTD'` (~2,282 active-roster O+D
  players incl. real `games_played`).

| Column | Type | Description |
|---|---|---|
| `scorer_id` | str | Fantrax id — PK part |
| `season` | int | e.g. 2026 (projection) or 2025 (actuals) — PK part |
| `week` | str | `PRE` / `01`..`18` / `YTD` — PK part |
| `capture_date` | str | Scrape date |
| `player_name`, `position_raw`, `nfl_team` | str | |
| `is_rookie` | bool | |
| `overall_rank` | int | Fantrax "Rk" = rank by FPts across all players |
| `adp` | float | Average draft position (offense only; null for IDP) |
| `salary` | float | Cap salary |
| `percent_drafted` | float | |
| `fpts` | float | Total fantasy points (was `score`; phase-aware) |
| `fpts_per_game` | float | FP/G (phase-aware) |
| `games_played` | int | GP — null on board rows, populated by backfill |
| `age` | int | Board: derived from `dim_nfl_players.birth_date`; backfill: Fantrax Age column |
| `gsis_id` | str | FK → dim_nfl_players (via crosswalk) |
| `player_key` | str | FK → dim_rookie_prospect (via crosswalk) |

**Key**: `scorer_id + season + week`. **Load** = replace-by-`(season, week)`
(each run scrapes the whole board → drop the partition, re-append; truly idempotent).

---

## fact_dynasty_rankings

Dynasty value/ranks **backbone** — the cross-source-comparable layer (notebook 04b;
two-layer model, see SKILL.md "Dynasty Rankings"). One row per player × format × snapshot.

| Column | Type | Description |
|---|---|---|
| `snapshot_date` | str | ISO run date — PK part (manual-cadence time series) |
| `source_name` | str | `KTC`, … — PK part |
| `source_player_id` | str | Source-native id — PK part |
| `format` | str | `SF` / `TEPP` / `IDP` / `1QB` — PK part |
| `source_uid` | str | `f"{source_name}\|{source_player_id}"` → rel to `dim_dynasty_crosswalk` |
| `source_site` | str | e.g. `KeepTradeCut` |
| `player_name`, `position_raw`, `nfl_team` | str | Identity |
| `age` | float | From the source |
| `overall_rank` | int | Universal comparable rank |
| `positional_rank` | int | Always populated (native or from Pos token) |
| `gsis_id`, `player_key` | str | FKs via `dim_dynasty_crosswalk` |

**Key**: `snapshot_date + source_name + source_player_id + format`. Load =
replace-by-`(snapshot_date, source_name)`.

---

## fact_dynasty_ranking_metrics

**Long/EAV** companion holding every source-specific metric as a row (so new sources
add rows, not columns). Examples: KTC `value`/`overall_tier`/`trend_7d`/`kept`/`adp`;
DynastySharks `proj_3yr`/`ds_value`/`analysis`(text); FantasyPros `avg`/`stddev`.

| Column | Type | Description |
|---|---|---|
| `snapshot_date`, `source_name`, `source_player_id`, `format` | — | PK parts (FK to backbone) |
| `metric_key` | str | Metric name, generic (no source prefix) — PK part; → `dim_dynasty_metric` |
| `source_uid` | str | `f"{source_name}\|{source_player_id}"` → rel to `dim_dynasty_crosswalk` |
| `metric_num` | float | Numeric metrics (nullable) |
| `metric_text` | str | Text metrics e.g. analysis (nullable) |

**Key**: `… + metric_key`. PBI: relate `metric_key` → `dim_dynasty_metric` and
`source_uid` → `dim_dynasty_crosswalk` (the only single-column path to player identity —
this fact has no `gsis_id`).

---

## fact_fantasy_teams

Active rosters, salaries, dead cap (schema seed; populated by the draft notebook).
Players can sit on two conference rosters with independent contracts. Was `fact_team`.

| Column | Type | Description |
|---|---|---|
| `team_key` | str | FK → dim_fantasy_teams |
| `gsis_id` | str | FK → dim_nfl_players |
| `player_key` | str | FK → dim_rookie_prospect (nullable) |
| `conference` | str | A / B |
| `contract_id` | str | FK → dim_contract |
| `contract_value` | int | Total contract $ |
| `contract_year` | int | Current year (1/2/3) |
| `cap_hit` | int | Current-season cap hit |
| `dead_money` | int | Dead cap if dropped now |
| `status` | str | `active` / `ir` / `dropped` |
| `acquired_method` | str | `draft` / `trade` / `free_agent` |
| `season` | int | League season |

**Key**: `team_key + gsis_id` (+ conference + season in practice)

---

## fact_nfl_combine_pro_day_metrics

Athletic measurements, all seasons. Both registry FKs present. `is_current_season`
flags the active draft class.

| Column | Type | Description |
|---|---|---|
| `pfr_id` | str | PFR id — PK part |
| `season` | int | Draft/combine season — PK part |
| `gsis_id`, `player_key` | str | Registry FKs |
| `is_current_season` | bool | Current draft class flag |
| `cfb_id`, `player_name`, `pos`, `school` | — | Identity |
| `draft_team`, `draft_round`, `draft_ovr` | — | Draft outcome |
| `metric_source` | str | `combine` / `pro_day` |
| `height_inches`, `weight` | float | |
| `forty_yard`, `ten_split` | float | 40 + 10-split (s) |
| `bench_press` | int | 225-lb reps |
| `vertical_jump`, `broad_jump` | float | Jumps (in) |
| `three_cone`, `shuttle` | float | Agility (s) |
| `hand_size`, `arm_length`, `wingspan` | float | Measurements (in) |

**Key**: `pfr_id + season`
