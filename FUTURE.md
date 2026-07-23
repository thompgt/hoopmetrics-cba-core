# Scaling the Player Dataset to Hundreds of Players

`webapp/data/players.py` currently holds 41 players / 51 player-season
records, hand-written and hard-coded into a Python dict. That approach
does not scale past a few dozen entries — this document lays out how to
get to hundreds (eventually the full league, every season) without that
becoming an unmaintainable wall of `dict(...)` literals.

## Why the current approach breaks down

- **Manual authoring doesn't scale.** Every player-season is a hand-typed
  dict; hundreds of entries means hundreds of literals to write, review,
  and keep accurate — not viable by hand past a few dozen.
- **No accuracy guarantee.** The current stats are approximate, from
  memory, for demonstration purposes. That's an explicit, disclosed
  limitation today; it becomes a real liability at "hundreds of players"
  scale where users will expect correctness.
- **No update path.** A hard-coded dict never gets new seasons, trades,
  or corrections without a code change and redeploy.
- **Single file, single format.** Everything lives in one Python module;
  there's no separation between data and the code that serves it.

## Target architecture

Replace the hard-coded dict with three separable layers:

1. **A real data source** — an external stats provider (a licensed NBA
   stats API, or a reputable public dataset/CSV export) instead of
   memory-derived figures. This is the actual accuracy fix; everything
   else below is plumbing around it.
2. **A local data store** — pull data from the source on a schedule (e.g.
   nightly) into a lightweight local database (SQLite is enough at
   hundreds-to-low-thousands of rows; Postgres if this ever needs to be
   multi-instance or shared) rather than re-fetching live on every
   request.
3. **A thin repository layer in the app** — `webapp/main.py` queries the
   store through a small `PlayerRepository` interface instead of
   importing `PLAYERS` directly, so the API/frontend code doesn't change
   when the storage backend changes.

## Data source options, roughly ordered by effort

| Option | Effort | Accuracy | Notes |
|---|---|---|---|
| Manual dict (current) | none | approximate | fine for a demo, not for "hundreds" |
| Public stats CSV/export, imported once | low | good, frozen in time | needs a re-import step to refresh |
| Free/public stats API, fetched on a schedule | medium | good, refreshable | rate limits, ToS review needed |
| Licensed commercial stats API | higher (cost) | best | the real production answer |

Any of the API options should go through `WebFetch`/a scheduled job
rather than being fetched inline on each user request — see "Refresh
strategy" below.

## Schema sketch (storage-agnostic)

```
players
  id, name, birthdate, position(s)

player_seasons
  player_id, season, team, age, years_of_service, all_nba_honors,
  games_played, minutes_per_game, pts, reb, ast, stl, blk
  (extendable: fg_pct, three_pt_pct, usage_rate, etc. as the box-score
  estimator in webapp/box_score_model.py evolves to use them)
```

This mirrors the current `PLAYERS[name][season] = {...}` shape closely
enough that the migration is additive, not a rewrite of the derivation
logic in `box_score_model.py`.

## Refresh strategy

- A scheduled background job (a cron-style task, run nightly or weekly
  depending on how often the source updates) re-pulls from the data
  source and upserts into the local store.
- The web app never calls the external source directly on a user
  request — it only ever reads from the local store, so a slow/rate-limited/
  down upstream API never affects page load times.
- Each row keeps a `last_updated` timestamp so staleness is visible/
  auditable rather than silent.

## API surface changes

The existing endpoints stay the same shape, just backed differently:

- `GET /api/players` — today returns the *entire* player→seasons map in
  one response. At hundreds of players this should become paginated or,
  better, replaced by a proper search endpoint (`GET /api/players/search?q=`)
  that queries the store with a `LIKE`/prefix match and returns only
  matching names, so the autofill `<datalist>` doesn't have to hold every
  player in the league in memory on page load.
- `GET /api/players/{name}/seasons` — a lightweight follow-up call the
  frontend already effectively needs once search narrows to one player.
- `POST /api/player/evaluate-by-name` — unchanged in shape; the data it
  reads just comes from the store's query instead of a dict lookup.

## Frontend implication

The current `<datalist>` approach loads the full name→seasons map once on
page load, which works at 41 players but not at hundreds+. Once search is
server-side, the name field becomes a debounced autocomplete: type a few
characters, fetch matching names from `/api/players/search`, populate
suggestions from the response instead of a pre-loaded list.

## Migration path (incremental, no big-bang rewrite)

1. Stand up the local store (SQLite to start) with the schema above.
2. Write a one-time import script that loads the *existing* 41
   hand-written players into it, so nothing regresses.
3. Swap `webapp/main.py`'s direct `PLAYERS` dict access for calls through
   a `PlayerRepository` that today just wraps the same dict — this
   decouples the API layer from storage *before* the storage actually
   changes, so that swap is low-risk.
4. Point `PlayerRepository` at the SQLite store instead of the dict.
5. Add the scheduled refresh job pulling from a real data source.
6. Convert `GET /api/players` into the paginated/search form; update the
   frontend to debounced server-side search.
7. Only after 1-6 are stable, actually scale the row count from 41 up to
   "every active NBA player, every season" by running the refresh job
   against the full roster instead of a curated subset.

Each step is independently shippable and testable — the app keeps
working (with 41 players) through every step until step 7, where the
row count grows without any further code changes being required.
