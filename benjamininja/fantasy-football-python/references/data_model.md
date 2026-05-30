# Data Model Reference

Full column specifications for the dynasty league star schema.

## Table of Contents
1. [dim_player](#dim_player)
2. [dim_position](#dim_position)
3. [dim_school](#dim_school)
4. [dim_team](#dim_team)
5. [dim_contract](#dim_contract)
6. [fact_team](#fact_team)
7. [fact_rankings](#fact_rankings)
8. [fact_combine_metrics](#fact_combine_metrics)

---

## dim_player

Player/prospect dimension. One row per unique prospect per draft year.
Seeded from nflverse combine invitees, extended by expert ranking ingestion.

| Column | Type | Description |
|---|---|---|
| `player_key` | str | Deterministic MD5 hash of `name\|position\|school` (12 chars) |
| `player_name` | str | Display name, original casing |
| `player_name_clean` | str | Lowercase, periods stripped, normalized for matching |
| `position_raw` | str | Position exactly as received from source (uppercased) |
| `position_detail` | str | Canonical granular position from dim_position |
| `position_group` | str | Rolled-up group (QB, RB, WR, TE, DL, LB, DB, OL, ST) |
| `side_of_ball` | str | Offense / Defense / Special Teams |
| `fantasy_relevant` | bool | True for dynasty-scorable positions |
| `school_raw` | str | School name as received from source |
| `school_canonical` | str | Canonical school name from dim_school |
| `conference` | str | Athletic conference (SEC, Big Ten, etc.) |
| `height_inches` | float | Height in total inches (nullable) |
| `weight` | float | Weight in pounds (nullable) |
| `pfr_id` | str | Pro-Football-Reference player ID (nullable) |
| `cfb_id` | str | College football reference ID (nullable) |
| `draft_year` | int | NFL draft class year |
| `source` | str | Origin of this record (e.g., `nflverse_combine`, `CBS_preCombine`) |
| `added_date` | str | ISO date when row was created |

**Key**: `player_key` (unique per draft_year)

---

## dim_position

Transformer/lookup table mapping raw position strings to canonical values.

| Column | Type | Description |
|---|---|---|
| `position_raw` | str | Raw position string, uppercased (PK) |
| `position_detail` | str | Granular canonical (QB, RB, WR, TE, EDGE, DE, DT, CB, S, etc.) |
| `position_group` | str | Fantasy group (QB, RB, WR, TE, DL, LB, DB, OL, ST) |
| `side_of_ball` | str | Offense / Defense / Special Teams |
| `fantasy_relevant` | bool | Scores in dynasty leagues |

**Key**: `position_raw`

---

## dim_school

Transformer/lookup table mapping raw school names to canonical + conference.

| Column | Type | Description |
|---|---|---|
| `school_raw` | str | School name as it appears in source (PK) |
| `school_canonical` | str | Canonical/display name |
| `conference` | str | Athletic conference |

**Key**: `school_raw`

---

## dim_team

Fantasy league team dimension. 28 teams across 2 conferences.

| Column | Type | Description |
|---|---|---|
| `team_key` | str | Unique team identifier |
| `team_name` | str | Display name |
| `conference` | str | Fantasy conference (A or B) |
| `owner` | str | Team owner name |
| `total_cap` | int | Team salary cap (from LeagueConfig, default $500M) |

**Key**: `team_key`

---

## dim_contract

Contract scale definitions and historical terms.

| Column | Type | Description |
|---|---|---|
| `contract_id` | str | Unique contract definition ID |
| `contract_type` | str | `initial` or `resign` |
| `total_years` | int | Contract length (default 3) |
| `year_1_pct` | float | Cap hit % in year 1 (0.50) |
| `year_2_pct` | float | Cap hit % in year 2 (0.40) |
| `year_3_pct` | float | Cap hit % in year 3 (0.00) |
| `resign_eligible_year` | int | Year in which re-sign is available (2) |
| `dead_money_applies` | bool | Whether cap hits survive player drop |
| `effective_season` | int | Season this contract scale became active |

**Key**: `contract_id`

---

## fact_team

Active rosters, salaries, and dead cap. One row per team × player.
Players can exist on two rosters (one per conference) with independent contracts.

| Column | Type | Description |
|---|---|---|
| `team_key` | str | FK to dim_team |
| `player_key` | str | FK to dim_player |
| `conference` | str | Which conference roster (A or B) |
| `contract_id` | str | FK to dim_contract |
| `contract_value` | int | Total contract dollar amount |
| `contract_year` | int | Current year of contract (1, 2, or 3) |
| `cap_hit` | int | Calculated cap hit for current season |
| `dead_money` | int | Dead cap if player were dropped now |
| `status` | str | `active`, `ir`, `dropped` |
| `acquired_method` | str | `draft`, `trade`, `free_agent` |
| `season` | int | League season year |

**Key**: `team_key + player_key + conference + season`

---

## fact_rankings

Expert rankings from all sources and phases. Long/narrow format —
one row per player × source × phase.

| Column | Type | Description |
|---|---|---|
| `player_key` | str | FK to dim_player |
| `source` | str | Expert source name (CBS, ESPN, PFF, composite, etc.) |
| `phase` | str | `pre_combine`, `post_combine`, `post_draft` |
| `draft_year` | int | Draft class year |
| `global_rank` | int | Overall ranking (nullable if only positional) |
| `positional_rank` | int | Within-position ranking (nullable) |
| `grade` | float | Expert grade/score if provided (nullable) |
| `capture_date` | str | ISO date when ranking was captured |

**Key**: `player_key + source + phase + draft_year`

---

## fact_combine_metrics

Athletic measurements from NFL Combine and pro days.
One row per player per draft year.

| Column | Type | Description |
|---|---|---|
| `player_key` | str | FK to dim_player |
| `draft_year` | int | Draft class year |
| `metric_source` | str | `combine` or `pro_day` |
| `height_inches` | float | Height in inches |
| `weight` | float | Weight in pounds |
| `forty_yard` | float | 40-yard dash (seconds) |
| `ten_split` | float | 10-yard split (seconds) |
| `bench_press` | int | Bench press reps at 225 lbs |
| `vertical_jump` | float | Vertical jump (inches) |
| `broad_jump` | float | Broad jump (inches) |
| `three_cone` | float | 3-cone drill (seconds) |
| `shuttle` | float | 20-yard shuttle (seconds) |
| `hand_size` | float | Hand size (inches) |
| `arm_length` | float | Arm length (inches) |
| `wingspan` | float | Wingspan (inches) |

**Key**: `player_key + draft_year`
