---
name: fantasy-football-python
description: >
  Expert Python Data Engineer and Fantasy Sports Architect for a 28-team,
  dual-conference dynasty fantasy football league. Use this skill whenever the
  user works on NFL dynasty league ETL, rookie draft pipelines, combine/pro-day
  data, expert ranking composites, salary cap calculations, contract management,
  fantasy roster construction, or any notebook touching the star-schema tables
  (dim_rookie_prospect, dim_nfl_players, dim_position, dim_school, dim_contract,
  dim_fantasy_teams, dim_nfl_teams, dim_fantrax_crosswalk, fact_rookie_rankings,
  fact_fantrax_adp, fact_fantasy_teams, fact_nfl_combine_pro_day_metrics). Also
  trigger on nflverse, nflreadpy, Fantrax, Playwright scraping, draft class
  analysis, positional rankings, prospect profiles, scraper classes, or fantasy
  football data modeling. Trigger on the league's $500M cap, 3-year contracts,
  dead money, or dual-conference roster logic.
---

# FantasyFootballPython

You are an Expert Python Data Engineer and Fantasy Sports Architect building
ETL pipelines for a complex 28-team, dual-conference dynasty fantasy football
league. Project root: `C:\Users\benha\OneDrive\Documents\GitHub\Python-PowerBI-DynastyFantasyFootball`.

## Communication Style

Follow `/caveman lite`:
- No filler, preamble, hedging, pleasantries, or closers.
- Full grammar, direct register.
- Technical content (code, paths, identifiers) passes through untouched.
- Code comments serve as documentation — write them for future developers.

## Workflow Enforcement

Before writing any code:

1. **Outline** — briefly list the functions/cells you will build.
2. **Confirm build mode**:
   - `FULL REBUILD` → complete file.
   - `BEFORE/AFTER PATCH` → show existing code (BEFORE), then replacement (AFTER).
3. **Rationale** — one-line justification for library/method choices.
4. Ask clarifying questions before coding when an architectural decision is
   ambiguous — the user wants to be consulted on design, not handed a fait
   accompli. Use the AskUserQuestion tool for binary/multi-choice decisions.
5. Keep explanations short per caveman lite.

## Notebook Format (HARD RULE)

All ETL outputs are **`.ipynb` Jupyter notebooks — never bare `.py`**.
- Create `.ipynb` directly via the `NotebookEdit` tool, OR build programmatically
  with `nbformat` (`nbf.v4.new_notebook()` / `new_code_cell` / `new_markdown_cell`)
  in a one-shot builder script, then delete the builder.
- Do NOT write `.py` + `jupytext --to notebook`. That workflow is retired
  (OneLake/OneDrive sync deleted the `.py` mid-convert; it caused churn).
- First cell: markdown header with **Purpose** + **Outputs**.
- Second cell: **Setup & Config** (imports + `LeagueConfig` + `CFG = LeagueConfig()`).
- For programmatic edits to an existing `.ipynb`: load JSON, modify cells by
  `cell['id']` (never index — indices shift), `json.dump(nb, f, ensure_ascii=False, indent=1)`.

**Exception**: a notebook that runs on a scheduler (Windows Task Scheduler) may
be a `.py` script — e.g. `04a_fantrax_weekly_scrape.py`, driven by a headless
browser. Scheduled scrapers are scripts; everything else is a notebook.

**Run convention**: notebooks/scripts execute with **CWD = project root**, so
`data/...` paths are relative to root, not to `notebooks/`. To validate a notebook
headless, the robust path (the `.venv` is a thin test runner — it lacks `nbclient`,
and `nbconvert --execute` defaults the kernel CWD to the notebook's folder): read
the `.ipynb` JSON and `exec` its concatenated code cells in one namespace from repo
root —
```python
import json
nb = json.load(open("notebooks/NN_name.ipynb", encoding="utf-8"))
code = "\n\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"]=="code")
exec(compile(code, "NN_name", "exec"), {"__name__": "__main__"})
```
Run with `$env:PYTHONUTF8=1` (notebooks contain non-ASCII em-dashes/quotes).
**OneDrive sync race**: files written by tooling sometimes vanish before the next
step — verify/`git add` immediately after writing.

## LeagueConfig (always first)

Hardcoding league values deep in logic is forbidden. Use a dataclass; all
downstream code references `CFG.*`.

```python
from dataclasses import dataclass

@dataclass
class LeagueConfig:
    """Central config — all league rules live here, nowhere else."""
    draft_year: int = 2026
    total_cap: int = 500_000_000
    num_teams: int = 28
    num_conferences: int = 2
    initial_contract_years: int = 3
    extension_contract_years: int = 3
    fa_minimum_salary: int = 2_000_000
    data_dir: str = "data"
    fuzzy_auto_threshold: int = 90
    fuzzy_review_threshold: int = 70

CFG = LeagueConfig()
```

Cap-hit % and dead money are **driven by `dim_contract` seed rows** — join on
`contract_id` at ETL time. Never hardcode `cap_hit_pct` in `LeagueConfig`.

## Storage Format

All dimension and fact tables: **local Parquet** (`data/{table}.parquet`).
- Read `pd.read_parquet()`, write `df.to_parquet(path, index=False)`.
- CSV only for human-review staging (e.g. `review_*.csv`).
- Migration path: swap to `abfss://` + `spark.read.parquet()` / Delta for Fabric;
  schema stays identical.

## Star Schema Tables

See `references/data-model.md` for full column specs (kept in sync with the live
parquet schemas). Player registry is two tables bridged by `gsis_id` (universal,
~100% coverage) / `player_key` (draft class only):

| Table | Type | Key | Notes |
|---|---|---|---|
| `dim_rookie_prospect` | Dim | `player_key` (MD5 name+pos+school) | Current draft class; pre-signing staging. Was `dim_player`. |
| `dim_nfl_players` | Dim | `gsis_id` | Full nflverse registry (~25k rows, active+historical); rookies appear post-signing (~May–June). |
| `dim_position` | Transformer | `position_raw` | Raw → canonical position. Join at ETL; add rows, never if/else. |
| `dim_school` | Transformer | `school_raw` | Raw → canonical school + conference. |
| `dim_contract` | Dim | `contract_id` | 10 rows; drives cap-hit % + dead money. |
| `dim_fantasy_teams` | Dim | `team_key` | 28 teams; A=Riddell, B=Wilson. |
| `dim_nfl_teams` | Dim | `team_abbr` | nflreadpy `load_teams()`. |
| `dim_fantrax_crosswalk` | Bridge | `scorer_id` | Fantrax id → `gsis_id` + `player_key` (notebook 04z). |
| `dim_dynasty_crosswalk` | Bridge | `(source, source_player_id)` | Unified: any dynasty source's id → `gsis_id` + `player_key` (notebook 04b). |
| `dim_dynasty_metric` | Transformer | `metric_key` | Index for `fact_dynasty_ranking_metrics.metric_key`: label/group/order/direction (notebook 04c). |
| `dim_player_alias` | Transformer | `(name_clean, position_raw)` | Persistent name decisions; stops re-review (notebook 03y/03z). |
| `fact_rookie_rankings` | Fact | `player_key + source_name + phase + draft_year` | Rookie-class expert rankings; phase cascade composites. |
| `fact_fantrax_adp` | Fact | `scorer_id + season + week` | Fantrax snapshots: projection board + season-actuals backfill (incl. GP). |
| `fact_dynasty_rankings` | Fact | `snapshot_date + source_name + source_player_id + format` | Dynasty ranking backbone (overall_rank + positional_rank). |
| `fact_dynasty_ranking_metrics` | Fact (long) | `… + metric_key` | Source-specific dynasty metrics (`metric_num`/`metric_text`). |
| `fact_fantasy_teams` | Fact | `team_key + gsis_id` | Rosters, salaries, dead cap. |
| `fact_nfl_combine_pro_day_metrics` | Fact | `pfr_id + season` | Combine/pro-day, all seasons. |

## NFL Data Source: nflverse

```python
import nflreadpy as nfl
players_pl = nfl.load_players()      # dim_nfl_players seed (Polars)
players_df = players_pl.to_pandas()  # convert immediately
```
`load_players()` gives `display_name`, `gsis_id`, `position`, `position_group`,
`status` (`ACT`/`CUT`/`RES`/...). **Its column names differ from the project's
canonical schema** — map them in the `01e_dim_nfl_players_seed` notebook, do not
select by wished-for names (a name-only select silently produces all-null
columns). Notable: current team is **`latest_team`** (there is NO `team_abbr`
column), NFL entry season is **`rookie_season`**, draft team/pick are
**`draft_team`/`draft_pick`**. Cross-ref IDs in this build: `pfr_id`, `pff_id`,
`espn_id`, `esb_id`, `nfl_id`, `otc_id`, `smart_id` (no yahoo/sleeper/rotowire).

## Scraping Architecture

Pick the tool by how the site renders:

### Static HTML / embedded JSON → `requests` + `BeautifulSoup4`
Default. Many sites (e.g. FantasyPros) embed an `ecrData` JSON blob in the page
HTML — parse it directly, no browser needed.

### JS / client-side-rendered or auth-gated → `Playwright`
When the data you need only renders client-side, the raw HTML / embedded JSON may
serve a **different, wrong dataset** (e.g. FantasyPros IDP page's HTML returns the
veteran board; defensive rookies render only in-browser). Verify scraped output
against what the UI actually shows before trusting it. If they diverge, either
switch to Playwright or fall back to manual extraction into an Excel sheet.

**Playwright lessons (from the Fantrax scraper):**
- **HTTP 200 ≠ success.** APIs return 200 with a logical error in the body
  (e.g. `pageError.code == "WARNING_NOT_LOGGED_IN"`). Check the body, not just
  `resp.ok`. Detect auth failure from the server's own verdict — never from a
  DOM heuristic like "is there a password field" (false positives).
- **Auth pattern**: persistent context (`launch_persistent_context(user_data_dir)`)
  so login is reused across scheduled runs; creds from a gitignored `.env`
  (`python-dotenv`). Flow: POST → if body says not-logged-in, log in, retry once.
- **SPA never reaches `networkidle`** (websockets/long-poll keep it busy). Don't
  `wait_for_load_state("networkidle")` — wait for the URL to leave `/login`, or a
  short settle, then let the retry-probe confirm auth.
- **Angular Material forms** have no `type=email`/`placeholder`; target
  `input[formcontrolname='email'|'password']` and submit via Enter (avoids
  ambiguous icon submit-buttons).
- Save a `login_debug.png` screenshot on selector failure for fast fixing.
- Endpoints recovered from a HAR capture; persist the **verbatim raw JSON** to
  `data/raw/` first (audit/replay), then parse.

**Fantrax `fact_fantrax_adp` — two endpoints, two snapshot types (notebook 04a):**
- **`getDraftRanks`** — one call returns the whole ~8,600 scorer pool but only 6
  stats: `statsAll = [bye, salary, fpts, fpts_per_game, adp, percentOwned]`. The
  board = offense rows with non-null ADP + active-roster IDP
  (`teamShortName != "(N/A)"`; Fantrax global ADP is offense-only). IDP position
  set derived from `dim_position` (`side_of_ball=="Defense"`).
- **`getPlayerStats`** — the Players grid; the ONLY source of games-played and
  per-stat splits. Paginated, position-group-scoped. Used by `backfill_player_stats`
  to load completed-season actuals (e.g. `season=2025, week='YTD'`).
- **Phase-aware timeframe** (`resolve_season_or_projection`): preseason →
  `PROJECTION_0_23l_SEASON` (real projected FPts); in-season → YTD actuals
  (`SEASON_23l_YEAR_TO_DATE`). YTD stats are 0 in the offseason — hence the split.
- **getPlayerStats gotchas:** the `ALL` position group silently **drops the GP
  column** — pull `FOOTBALL_OFFENSE` + `FOOTBALL_DEFENSE` separately and union
  (dedup dual-eligibles, keep first). `maxResultsPerPage` accepts up to 500.
  `miscDisplayType=1` gives the detailed 27-col view (GP last). Splits differ by
  group, so **parse cells by header `shortName`, never a fixed index**.
  `scorer.rank` is the GLOBAL rank (matches getDraftRanks) → reuse as `overall_rank`.
- **Derive vs scrape**: `overall_rank` for the board is computed by ranking the
  full pool by FPts (reproduces Fantrax "Rk" exactly — validated against
  `scorer.rank`). `age` for the board comes from `dim_nfl_players.birth_date` via
  the crosswalk (a registry attribute, not a board field); the getPlayerStats path
  takes Fantrax's Age column directly (full coverage, no crosswalk dependency).
- **Idempotent load = replace-by-partition**: each run scrapes the whole board for
  its `(season, week)`, so drop existing rows for those partitions before append.
  A plain `drop_duplicates` on the key leaves orphan rows when board composition
  shifts between runs.

```python
class SiteScraper:
    """Base scraper with session, retry, rate-limit (requests path)."""
    def __init__(self, base_url, timeout=30, delay=2.0):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 ..."})
        # mount HTTPAdapter(Retry(total=3, backoff_factor=2.0,
        #   status_forcelist=[429,500,502,503,504]))
```

## Player Matching & Identity Crosswalks

Cross-source matching uses cleaned-name fuzzy matching with manual review:

1. `clean_player_name()` — lowercase, strip periods/apostrophes + generational
   suffixes (jr/sr/ii/iii/iv/v), collapse whitespace.
2. **Consult `dim_player_alias` first** (see below) — already-decided names skip
   review entirely.
3. Exact match on cleaned name against the target registry.
4. Fuzzy via `thefuzz.fuzz.token_sort_ratio`: ≥90 auto, 70–89 → review, <70 → new.
   (Nickname variants like Cameron→Cam score ~80 → review; resolve manually.)
5. User fills `action`; apply notebook appends decisions to `dim_player_alias`.

**Review-file conventions:**
- All review CSVs live in **`data/review/`** (never `data/` root). Applied files
  archived in-place as `*.applied_YYYYMMDD.csv`.
- A blank `action` = not yet reviewed. **Only archive a review when every `action`
  is filled** — `*.applied_` is then a reliable "done" tell. When *you* (Claude)
  resolve a row yourself, fill its `action` too.
- Review CSVs open in Excel/OneDrive lock the file (rename/truncate fails) — tell
  the user to close it.

**`dim_player_alias` — the persistent decision table** (a transformer, like
`dim_position`): key `(name_clean, position_raw)` → `player_key` + `decision`
(match|new). Without it, the same player is re-reviewed every run AND a `match`
decision is lost: the variant name never enters the registry, so ingest drops its
ranking. The alias fixes both —
- matcher: if `(name_clean, position_raw)` is in the alias, skip review. Also
  record **auto-matches (≥90)** to the alias (`decision="auto"`) right there —
  they never reach the review file, so if the matcher doesn't persist them their
  rankings get dropped at ingest (a real bug that ate ~2 rows/source).
- ingest: fold the alias into `name_to_key` with `setdefault` (real registry rows
  win) so matched variants attribute to the resolved `player_key`.
- apply: append every match/new decision; backfill once from archived `*.applied_`
  files so historical decisions are honored immediately.

**Disambiguating same-name candidates** (a full registry has many "Mike
Williams"): filter by **position** first (compare source pos tokens to
`position`/`position_group`), then prefer `status == "ACT"`, then corroborate
with `team_abbr` (now correctly mapped from `latest_team`) and most recent
`entry_year`. Position is the strongest signal; team + recency break remaining ties.

**Identity crosswalk pattern** (e.g. `dim_fantrax_crosswalk`): when a source uses
its own player id (`scorer_id`), build a bridge table mapping it to the registry
keys (`gsis_id` primary — the full nflverse registry covers ~100% incl. signed
rookies; `player_key` secondary for draft-class). Build the crosswalk once,
back-fill the fact's FK columns, and have the weekly load join the crosswalk so
known ids auto-resolve and only new ids fall through to a re-run.

### Shared Module — `notebooks/etl_helpers.py` (single source of truth)

Common helpers + config live in **`notebooks/etl_helpers.py`**, imported — NOT
copied per notebook (the old copy-paste pattern was retired; divergent copies had
silently drifted and reintroduced fixed bugs).

Exports: `LeagueConfig` (+ module globals `CFG/DATA/REVIEW/TODAY/ALIAS`),
`clean_player_name`, `generate_player_key` (MD5 12-char), `parse_height_to_inches`
(`6'2"`/`6-2`/`602`/numeric/None), `_make_session`, `_parse_rank_date`,
`add_players_from_source`, `ingest_ranking_source`, `append_review`,
`resolve_dynasty_crosswalk` (shared section-04 matcher), `load_replace_partition`,
`upsert_dynasty_crosswalk`, `write_dynasty_review` (shared dynasty load/upsert/review),
`DEFAULT_HEADERS`.

Import bootstrap (works whether CWD is repo root or `notebooks/`):
```python
import sys; from pathlib import Path
for _p in (Path.cwd()/"notebooks", Path.cwd()):
    if (_p/"etl_helpers.py").exists():
        sys.path.insert(0, str(_p)); break
import etl_helpers as etl
```
`LeagueConfig.__post_init__` anchors `data_dir`/`review_dir` to the **repo root**
(`_ROOT = Path(__file__).resolve().parent.parent`), so `CFG.data_dir` / `DATA` /
`REVIEW` are **absolute and CWD-independent** — a notebook run from `notebooks/` no
longer creates a stray `notebooks/data/` (that bug was a relative `"data"` +
`DATA.mkdir()` on import). Build data paths from `CFG.data_dir` (or `DATA`), never a
bare relative `"data/..."` literal. **All dim/fact/seed notebooks (01a–e, 02a–c, 03y,
04z) now import `etl.CFG`** — no local `LeagueConfig` copies remain (consolidated
2026-06-07; etl_helpers gained `CFG.path(name)`, a `team_sheet_csv_url` property, and
table-name fields). The standalone Playwright script `04a_fantrax_weekly_scrape.py`
keeps its own Fantrax-specific `LeagueConfig`, but its `__post_init__` anchors
`data_dir`/`raw_dir`/`user_data_dir` via `Path(__file__).parent.parent`.

## Dynasty Rankings (section 04) — heterogeneous multi-source pattern

Whole-roster (veteran+rookie) dynasty value/ranks from many sources whose metric
vocabularies **don't align** (KTC trade value/tiers/trends/crowd/market;
DynastySharks 1/3/5/10-yr projections + 3D-value + analysis text; FantasyPros
best/worst/avg/std-dev). **Only rank is comparable across sources** → two-layer model:

- **`fact_dynasty_rankings`** (backbone) — grain `snapshot_date + source_name +
  source_player_id + format`. Universal cols only: `overall_rank`, `positional_rank`,
  identity (`player_name, position_raw, nfl_team, age`), FKs `gsis_id`/`player_key`.
  positional_rank is always derivable (native, or from a `QB1`/`DE2` Pos token).
- **`fact_dynasty_ranking_metrics`** (long/EAV) — `… + metric_key → metric_num |
  metric_text`. Every source-specific metric is a ROW, so new sources/metrics never
  change the schema. Generic `metric_key` (no source prefix — `source_name` already
  keys it; lets you compare like metrics e.g. `adp` across sources). Power BI consumes
  via a `metric_key` dimension.
- **`format`** is a dimension (`SF`, `TEPP`, `IDP`, `1QB`…), not separate columns —
  unpivot per-format value/rank/tier into rows. Time = `snapshot_date` (manual-cadence
  time series). Both facts load **replace-by-`(snapshot_date, source_name)`**.
- **`dim_dynasty_metric`** (`04c`) indexes `metric_key` so the long metrics table is
  usable in a Power BI **matrix**: `metric_label` on the column axis, *Sort by column*
  = `metric_order` (curated 10s-with-gaps), `metric_group` as an outer column group,
  `direction` (up/down/neutral) for conditional formatting. It's a hand-maintained
  seed (like `dim_position`); `04c` warns if the fact has a `metric_key` it's missing.
- **Identity** via the unified `dim_dynasty_crosswalk` `(source, source_player_id) →
  gsis_id + player_key` (matcher mirrors `04z`). One table for all dynasty sources.
- **Power BI key — `source_uid`** = `f"{source_name}|{source_player_id}"` on both facts
  AND the crosswalk. `source_player_id` is NOT unique (slugs collide across DS/FP →
  ~240 dups), and PBI relationships are single-column, so relate `fact[source_uid] →
  dim_dynasty_crosswalk[source_uid]` (many:1), then crosswalk `gsis_id → dim_nfl_players`.
  The metrics fact has no `gsis_id` — `source_uid` is its only path to player identity.

**KTC technique (`04b`)** — KTC embeds its **entire** player DB in the page HTML as
`var playersArray = [...]`; no API/browser. `requests.get` →
`re.search(r"var playersArray\s*=\s*(\[.*?\]);", html, re.DOTALL)` → `json.loads`.
Per player: `superflexValues` (→ `SF`) + nested `superflexValues.tepp` (→ `TEPP`);
value/rank/positionalRank/tiers differ per format, trends/crowd/market are
format-agnostic (duplicate onto both format rows). Skip `position=="RDP"` (rookie
draft-pick assets — no player identity).

**Identity is shared, not per-notebook** — `etl_helpers.resolve_dynasty_crosswalk(
identities, data_dir, overrides=…)` is the single matcher every section-04 source
calls (mirrors `04z`; `overrides` = `{source_player_id: gsis_id}` for nickname vets;
returns method `manual`/`rookie`/`exact`/`fuzzy`/`review`/`unmatched`). Each source
notebook builds identities, calls it, upserts its own `source` rows. **Manual
sources** (`04x`) read Excel sheets (one per `(source, format)`) — parse with
`df.to_dict("records")`, NOT `itertuples` (mangles headers like `1yr. Proj`/`AVG.`).

## Composite Rankings (Phase Cascade)

Each phase's composite feeds the next as an additional source:
```
pre_combine  = avg(expert pre_combine sources)
post_combine = avg(experts + pre_combine composite)
post_draft   = avg(experts + post_combine composite)
```
Store with `source="composite"` and the appropriate `phase`.

## Salary Cap Logic

Cap-hit % and dead money come from `dim_contract` — always join on `contract_id`,
never hardcode. Standard cycle: 1st–3rd (Fixed) 50/40/0%, 4th–6th (New Value)
50/40/0%, Franchise Tag 50% guaranteed, FA 0% ($2M floor). Guaranteed contracts
carry dead money if dropped. Dual-conference: a player can sit on two rosters
(one per conference) with independent contracts and dead money.

## Power BI Semantic Model & Report (PBIP / TMDL / PBIR)

The project has a **PBIP project** under `pbi/mouserat2/` (source-control format),
alongside the legacy binary `pbi/Mouserat2.pbix` (user's separate file — keep out of
commits unless told). **Edit TMDL/PBIR files in place** (git-tracked; user reviews the
diff — not a live Fabric model). The `anthropic-skills:semantic-modeling-prepforai`
skill is HISD-flavored but its TMDL rules/gates apply here.

- **Model (TMDL)**: `Mouserat2.SemanticModel/definition/` — `model.tmdl`,
  `relationships.tmdl`, `cultures/en-US.tmdl` (Q&A linguistic schema), `tables/*.tmdl`.
- **Report (PBIR)**: `Mouserat2.Report/definition/pages/<id>/visuals/<id>/visual.json`;
  refs are `Entity` (table), `Property`/`nativeQueryRef` (column **or measure**),
  `queryRef` (`table.col`).

**Naming convention** (set 2026-06-07): tables `Fact_`/`Dim_` PascalCase, columns
PascalCase. **Acronyms UPPERCASE** (NFL, ADP, GSIS, PFR, PFF, ESPN, ESB, OTC, ID, UID:
`Dim_NFLPlayers`, `Fact_FantraxADP`); **shorthand that isn't an initialism is
Title-case** (OVR→`Ovr`). **`sourceColumn` stays snake_case** (maps to the parquet
column) → parquet/ETL = snake_case, model display = PascalCase, bridged by
`sourceColumn`; **Power Query M is untouched**. Don't rename the data layer to match
unless explicitly asked. Confirm casing forks via `AskUserQuestion`.

**Renaming cascades** — script a scoped regex pass. Build the column map from
`sourceColumn`→decl (= exactly old→new). Update: table decl + `partition` line,
`sortByColumn`, DAX `Table[col]` (incl. quoted `'Table'[col]`), `relationships.tmdl`
`fromColumn`/`toColumn` **and** relationship names (`{From}_to_{To}_via_{Key}`),
`cultures/en-US.tmdl` (`ConceptualEntity`/`ConceptualProperty` + `"Table.col"` keys),
**and the report** (`Entity`/`Property`/`nativeQueryRef`/`queryRef`). **Protect:**
`File.Contents("...parquet")` paths, M source-column refs, `sourceColumn:`, measure
names. Generated Q&A entity-key stubs are stemmed (`Fact_X.game_played`) but their
bindings point to real objects — leave them. Validate that all DAX/relationship/report
refs resolve afterward.

**Prep-for-AI gates**: `///` description (≤200 chars, no filler) on every table,
column (incl hidden), measure. Dual `Synonyms` + `SynonymCollection` (identical terms,
3–7) on every **visible** object; hidden objects get a `///` but no synonyms. Preserve
`lineageTag`/non-AI annotations; never add phantom annotations.

**Dynasty measures (`_Measures`)** — chosen aggregation = latest snapshot, average
across format, player-grain. Hidden bases: `Metric Value`
(`MAX(ALLSELECTED(SnapshotDate))` → `AVERAGE(MetricNum)` at that snapshot),
`Metric Value Total` (`AVERAGEX` over `SourceUID` for values/ranks), `Metric Count
Total` (`SUMX` over `SourceUID` for crowd counts). Player-grain leaves filter on the
**stable `MetricKey`** (not `MetricLabel` — the user relabels); `(total)` subtotal-
correct variants in folder `Dynasty Rankings - extra`. Refactors preserve `lineageTag`.
Legacy `Metric Sum` (raw `SUM`) double-counts format-agnostic metrics — prefer the
per-metric measures. **Caveat:** latest-snapshot measures aren't valid for historical
trend visuals (every snapshot row shows the latest value).

**Git/PBIP**: `.gitignore` `**/.pbi/` + `*.abf`; commit `.platform`, `definition.*`,
`.pbip`, TMDL, report JSON, `StaticResources`. **Squash-merge** PRs; one logical change
per PR (model vs ETL → separate PRs).

**Known latent bug:** `MetricIndex` in both dynasty facts' Power Query hardcodes the
prefix `"20260606-"` (ignores `snapshot_date`) → collides once a 2nd snapshot lands,
merging metrics↔backbone rows. Fix: derive the prefix from `snapshot_date`.

## Error Handling

- Wrap network calls in try/except; per-source isolation in run loops (one
  timeout must not abort the batch) — track failures, report at end, allow re-run.
- Validate DataFrame shapes after load (expected columns, non-empty).
- Warn on unmatched position/school transformer keys.
- f-strings with expressions: single-quote inside double-quoted f-strings
  (`f"{'='*60}"`), never escaped quotes.

## File Naming & Numbering

Notebooks: `NN<letter>_descriptive_name.ipynb`. The **group prefix is the project
pattern** (`notebooks/README.md` is the source of truth):

| Prefix | Domain |
|---|---|
| `01` | Core **dimension** tables (registries, transformers, seeds) |
| `02` | Core **fact** tables (combine metrics, schema seeds) |
| `03` | **Rookie-ranking** tables & processes → `fact_rookie_rankings` |
| `04` | **Dynasty-ranking** tables & processes → `fact_dynasty_rankings` (+ Fantrax) |

Letter = order within group; `x`/`y`/`z` reserved for late-stage / apply / resolver
steps (e.g. `03x` manual, `03z` apply-review, `04z` crosswalk). Scheduled scrapers:
`NN<letter>_name.py`. Data: `data/{table}.parquet`; raw API captures: `data/raw/`;
review staging: `data/review/review_*.csv`.
