# HoopMetrics CBA Core

HoopMetrics CBA Core is a pure-Python modeling library for NBA player valuation and trade
legality under the league's Collective Bargaining Agreement (CBA) rules. It combines a
simulated on-court impact/analytics model with a rules engine for salary caps, tax aprons,
and trade-matching restrictions, then exposes both through a single gateway module so a
proposed trade can be evaluated end-to-end: "is this trade good value, and is it even legal?"

There is no external framework, database, or API server here — it's a collection of
composable calculation modules plus a small integration layer (`engine_gateway.py`) and a
pytest suite that exercises them individually and together.

## Architecture

The codebase is organized into three domains plus a gateway that ties them together:

### `analytics/` — player valuation model

- **`impact_metrics.py`** — Computes a simulated Regularized Adjusted Plus-Minus (RAPM) from
  box plus-minus and on/off ratings, parses Estimated Plus-Minus (EPM), and combines the two
  into a net impact-per-100-possessions figure.
- **`age_curves.py`** — Applies a non-linear age-based performance multiplier: an upside
  premium under 19, an exponential growth-projection curve for ages 19-23, a flat peak
  baseline for 24-29, and a quadratic decay penalty (floored at 0.1x) for 30+.
- **`injury_risk.py`** — Tracks a player's "Available Games Ratio" over however many trailing
  seasons are supplied (typically 3, i.e. games played out of 246 possible, but works for
  players with a shorter history) and applies a multiplicative discount once missed games
  exceed 25%, floored at 0.5x. The discount factor weights more recent seasons more heavily
  than older ones (assumes seasons are ordered oldest-to-most-recent), since a season missed
  three years ago is a weaker signal of current injury risk than one missed last year.
- **`scarcity_curves.py`** — Maps discrete player archetypes (e.g. "Two-Way Wing",
  "Floor-Spacing Rim Protector", "High-Volume Playmaker", "Traditional Low-Volume Big") to a
  scarcity premium/discount multiplier. Unclassified players should use the explicit
  `"Unknown"` archetype (1.0x, neutral); any other unrecognized label raises `ValueError`
  rather than silently defaulting, so typos surface immediately instead of being masked.

### `cba/` — salary cap and tax rules

- **`salary_caps.py`** — Derives a player's maximum allowable salary bracket from cap space,
  years of service, and All-NBA/"Rose Rule" eligibility (25%/30%/35% of the cap tiers).
- **`apron_matrix.py`** — Classifies a team's payroll against the First and Second Apron
  thresholds, returning an `ApronStatus` enum member (`BELOW_APRON`, `FIRST_APRON`, or
  `SECOND_APRON`).
- **`luxury_tax.py`** — Computes a team's progressive luxury tax bill: each $5M of payroll
  above the tax line is taxed at a higher marginal rate, with a repeater surcharge for teams
  that have paid the tax in at least 3 of the previous 4 seasons.
- **`bird_rights.py`** — Classifies a free agent's "Bird rights" tier (Non-Bird, Early Bird,
  Full Bird) from consecutive seasons with the same team, and derives the cap-exceeding
  re-signing salary limit that tier grants (175%/120% of prior salary for Early/Non-Bird;
  Full Bird is only bounded by the player's ordinary max-salary bracket).
- **`asset_efficiency.py`** — Computes a "Contract Efficiency Index" as the per-year dollar
  delta between a player's modeled value and their actual cap hit, plus a total contract
  value that compounds that per-year delta across however many years remain on the deal.

### `transactions/` — trade legality engine

- **`matcher.py`** — Implements Simultaneous Trade Exception (S-TPE) salary-matching
  brackets, returning the maximum incoming salary a team may take back for a given
  outgoing salary. Below-Apron teams get the full tiered brackets; First Apron teams
  are capped near 110% of outgoing salary and Second Apron teams at strict 1:1,
  regardless of the standard brackets.
- **`restrictions.py`** — Enforces First/Second Apron salary-aggregation restrictions,
  raising a `TradeRestrictionError` if an apron team tries to combine more than one outgoing
  player's salary in a single trade.
- **`equity_balancer.py`** — Tracks non-salary trade assets sent by a team (draft picks,
  pick swaps, cash) and enforces the league cash-in-trade limit (currently modeled at
  $7,960,000) for teams below the First Apron; First/Second Apron teams are barred
  from sending any cash in a trade at all. Also enforces the Stepien Rule via
  `add_first_round_pick_for_year`, raising `StepienRuleViolation` if trading a specific
  year's first-round pick would leave the team without a first-rounder in consecutive drafts.

### `engine_gateway.py` — integration layer

Defines the `Player` dataclass-like model and two top-level entry points:

- **`evaluate_player(player)`** — Runs a player through the full analytics pipeline (RAPM +
  EPM -> net impact -> dollar value scaling at $5M per point of net impact -> age, injury,
  and archetype multipliers -> a minutes-played workload scalar against a 32-minute
  full-time-starter baseline) to produce a single modeled dollar value.
- **`evaluate_trade(team_a_apron, team_b_apron, team_a_sending, team_b_sending, team_a_equity=None, team_b_equity=None)`**
  — Validates a proposed trade against apron aggregation rules and apron-aware S-TPE
  salary-matching limits for **both** teams (each team's incoming salary is bounded by a
  bracket derived from its own outgoing salary and its own apron status). If
  `EquityBalancer` instances are passed for either team, also blocks the trade if a
  First/Second Apron team is sending any cash. Returns `True` if the trade is legal for
  both sides and `False` (with a printed reason) if it is blocked.

## Tech stack

- Python 3 (uses `list[int]`-style built-in generics, so Python 3.9+)
- [pytest](https://docs.pytest.org/) for the test suite
- No third-party runtime dependencies, no `requirements.txt`/`pyproject.toml` — the project
  currently has no packaging manifest, so dependencies (just `pytest`) must be installed
  manually

## Setup

```bash
git clone https://github.com/thompgt/hoopmetrics-cba-core.git
cd hoopmetrics-cba-core
pip install pytest
```

## Usage

Import the gateway module and drive it directly, e.g.:

```python
from engine_gateway import Player, evaluate_player, evaluate_trade
from cba.apron_matrix import ApronStatus

young_wing = Player(
    name="Young Star", age=21, archetype="Two-Way Wing",
    games_played_last_3=[82, 82, 82],
    box_plus_minus=3.0, on_off=4.0, epm=3.5, cap_hit=8_000_000,
)
print(evaluate_player(young_wing))  # modeled dollar value

aging_star = Player(
    name="Aging Star", age=34, archetype="High-Volume Playmaker",
    games_played_last_3=[40, 45, 50],
    box_plus_minus=4.0, on_off=2.0, epm=4.0, cap_hit=45_000_000,
)
print(evaluate_trade(ApronStatus.SECOND_APRON, ApronStatus.BELOW_APRON, [aging_star], [young_wing]))  # True/False
```

Individual modules under `analytics/` and `cba/` can also be imported and used standalone.

## Running the tests

```bash
pytest
```

The suite in `tests/` covers each analytics function (`test_analytics.py`), each CBA rule
(`test_cba.py`), the trade-matching and restriction logic (`test_transactions.py`), and a
full end-to-end scenario combining player valuation with trade legality checks
(`test_master_pipeline.py`).
