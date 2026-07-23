"""FastAPI front end for the HoopMetrics CBA core engine.

Wraps the existing player-evaluation and trade-legality library functions
with a JSON API and a single polished dashboard page. Deliberately reuses
the library's own logic (evaluate_player, evaluate_trade, _apply_risk_adjustment)
rather than re-implementing any CBA math, so the web layer can never drift
out of sync with the engine it's presenting.
"""

import contextlib
import io
import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine_gateway import Player, evaluate_player, evaluate_trade, _apply_risk_adjustment
from analytics.impact_metrics import calculate_simulated_rapm, parse_epm, calculate_net_impact_per_100
from analytics.age_curves import get_age_multiplier
from analytics.injury_risk import get_injury_discount_factor
from analytics.scarcity_curves import get_archetype_multiplier, _ARCHETYPE_MULTIPLIERS
from cba.apron_matrix import ApronStatus
from cba.luxury_tax import compute_luxury_tax_bill
from cba.bird_rights import classify_bird_rights, get_re_signing_salary_cap
from cba.asset_efficiency import compute_contract_efficiency, compute_total_contract_value
from cba.salary_caps import calculate_max_salary
from transactions.matcher import get_max_incoming_salary
from transactions.equity_balancer import EquityBalancer, StepienRuleViolation
from .data.players import PLAYERS, CAP_FIGURES
from .box_score_model import estimate_box_plus_minus, estimate_on_off, estimate_epm, classify_archetype_from_stats

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="HoopMetrics CBA Core")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

ARCHETYPES = sorted(_ARCHETYPE_MULTIPLIERS)
APRON_STATUSES = [s.value for s in ApronStatus]


class PlayerInput(BaseModel):
    name: str = Field(default="Player")
    age: int
    archetype: str
    games_played_last_3: list[int]
    box_plus_minus: float
    on_off: float
    epm: float
    cap_hit: float
    minutes_per_game: float = 32.0


class TradeSidePlayer(BaseModel):
    name: str = "Player"
    cap_hit: float


class TradeInput(BaseModel):
    team_a_apron: str
    team_b_apron: str
    team_a_players: list[TradeSidePlayer]
    team_b_players: list[TradeSidePlayer]
    team_a_cash: float = 0.0
    team_b_cash: float = 0.0


class LuxuryTaxInput(BaseModel):
    team_payroll: float
    tax_line: float
    is_repeater: bool = False


class BirdRightsInput(BaseModel):
    consecutive_seasons_with_team: int
    prior_salary: float


class ContractEfficiencyInput(BaseModel):
    modeled_value_dollars: float
    cap_hit_dollars: float
    years_remaining: int = 1


class StepienRuleInput(BaseModel):
    year: int
    picks_owned_this_year: int
    picks_owned_prior_year: int
    picks_owned_next_year: int


class PlayerLookupInput(BaseModel):
    name: str
    season: str
    cap_space: float


def _apron_from_value(value: str) -> ApronStatus:
    for status in ApronStatus:
        if status.value == value:
            return status
    raise ValueError(f"Unrecognized apron status: {value!r}")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "archetypes": ARCHETYPES, "apron_statuses": APRON_STATUSES},
    )


@app.get("/api/meta")
async def meta():
    return {"archetypes": ARCHETYPES, "apron_statuses": APRON_STATUSES}


@app.post("/api/player/evaluate")
async def player_evaluate(payload: PlayerInput):
    try:
        player = Player(
            payload.name, payload.age, payload.archetype, payload.games_played_last_3,
            payload.box_plus_minus, payload.on_off, payload.epm, payload.cap_hit,
            minutes_per_game=payload.minutes_per_game,
        )
    except ValueError as e:
        return {"error": str(e)}

    rapm = calculate_simulated_rapm(player.box_plus_minus, player.on_off)
    parsed_epm = parse_epm(player.epm)
    net_impact = calculate_net_impact_per_100(rapm, parsed_epm)
    age_mult = get_age_multiplier(player.age)
    injury_discount = get_injury_discount_factor(player.games_played_last_3)
    archetype_mult = get_archetype_multiplier(player.archetype)
    base_value = net_impact * 5_000_000
    composite_mult = age_mult * injury_discount * archetype_mult
    risk_adjusted = _apply_risk_adjustment(base_value, composite_mult)
    workload_mult = player.minutes_per_game / 32.0
    final_value = evaluate_player(player)

    return {
        "name": player.name,
        "rapm": rapm,
        "epm": parsed_epm,
        "net_impact_per_100": net_impact,
        "base_value": base_value,
        "age_multiplier": age_mult,
        "injury_discount": injury_discount,
        "archetype_multiplier": archetype_mult,
        "composite_multiplier": composite_mult,
        "risk_adjusted_value": risk_adjusted,
        "workload_multiplier": workload_mult,
        "final_value": final_value,
        "cap_hit": player.cap_hit,
        "surplus_value": final_value - player.cap_hit,
    }


@app.post("/api/trade/evaluate")
async def trade_evaluate(payload: TradeInput):
    try:
        team_a_apron = _apron_from_value(payload.team_a_apron)
        team_b_apron = _apron_from_value(payload.team_b_apron)
    except ValueError as e:
        return {"error": str(e)}

    def make_player(p: TradeSidePlayer) -> Player:
        return Player(p.name, 27, "Unknown", [82, 82, 82], 0.0, 0.0, 0.0, p.cap_hit)

    try:
        team_a_players = [make_player(p) for p in payload.team_a_players]
        team_b_players = [make_player(p) for p in payload.team_b_players]
    except ValueError as e:
        return {"error": str(e)}

    team_a_equity = None
    team_b_equity = None
    if payload.team_a_cash:
        team_a_equity = EquityBalancer(team_a_apron)
        try:
            team_a_equity.add_cash(payload.team_a_cash)
        except ValueError as e:
            return {"error": f"Team A cash: {e}"}
    if payload.team_b_cash:
        team_b_equity = EquityBalancer(team_b_apron)
        try:
            team_b_equity.add_cash(payload.team_b_cash)
        except ValueError as e:
            return {"error": f"Team B cash: {e}"}

    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        legal = evaluate_trade(
            team_a_apron, team_b_apron, team_a_players, team_b_players,
            team_a_equity=team_a_equity, team_b_equity=team_b_equity,
        )
    reasons = [line for line in captured.getvalue().splitlines() if line.strip()]

    team_a_outgoing = sum(p.cap_hit for p in team_a_players)
    team_b_outgoing = sum(p.cap_hit for p in team_b_players)

    return {
        "legal": legal,
        "reasons": reasons,
        "team_a_outgoing_salary": team_a_outgoing,
        "team_b_outgoing_salary": team_b_outgoing,
        "team_a_max_incoming": get_max_incoming_salary(team_a_outgoing, team_a_apron),
        "team_b_max_incoming": get_max_incoming_salary(team_b_outgoing, team_b_apron),
    }


@app.post("/api/luxury-tax/evaluate")
async def luxury_tax_evaluate(payload: LuxuryTaxInput):
    try:
        bill = compute_luxury_tax_bill(payload.team_payroll, payload.tax_line, payload.is_repeater)
    except ValueError as e:
        return {"error": str(e)}
    return {
        "team_payroll": payload.team_payroll,
        "tax_line": payload.tax_line,
        "amount_over_line": max(0.0, payload.team_payroll - payload.tax_line),
        "is_repeater": payload.is_repeater,
        "tax_bill": bill,
    }


@app.post("/api/bird-rights/evaluate")
async def bird_rights_evaluate(payload: BirdRightsInput):
    try:
        status = classify_bird_rights(payload.consecutive_seasons_with_team)
        cap = get_re_signing_salary_cap(payload.prior_salary, status)
    except ValueError as e:
        return {"error": str(e)}
    return {
        "status": status.value,
        "prior_salary": payload.prior_salary,
        "re_signing_cap": cap,
        "uncapped": cap is None,
    }


@app.post("/api/contract-efficiency/evaluate")
async def contract_efficiency_evaluate(payload: ContractEfficiencyInput):
    try:
        per_year = compute_contract_efficiency(payload.modeled_value_dollars, payload.cap_hit_dollars)
        total = compute_total_contract_value(
            payload.modeled_value_dollars, payload.cap_hit_dollars, payload.years_remaining
        )
    except ValueError as e:
        return {"error": str(e)}
    return {
        "per_year_efficiency": per_year,
        "years_remaining": payload.years_remaining,
        "total_contract_value": total,
        "is_bargain": total >= 0,
    }


@app.post("/api/stepien-rule/evaluate")
async def stepien_rule_evaluate(payload: StepienRuleInput):
    picks_owned = {
        payload.year: payload.picks_owned_this_year,
        payload.year - 1: payload.picks_owned_prior_year,
        payload.year + 1: payload.picks_owned_next_year,
    }
    balancer = EquityBalancer()
    try:
        balancer.add_first_round_pick_for_year(payload.year, picks_owned)
    except StepienRuleViolation as e:
        return {"legal": False, "reason": str(e)}
    except ValueError as e:
        return {"legal": False, "reason": str(e), "unowned": True}
    return {"legal": True, "reason": f"Trading the {payload.year} first-round pick is permitted under the Stepien Rule."}


@app.get("/api/players")
async def list_players():
    """Name -> list of seasons on file, used to drive the autofill/season dropdown."""
    return {name: sorted(seasons.keys()) for name, seasons in PLAYERS.items()}


@app.get("/api/cap-figures")
async def cap_figures():
    return CAP_FIGURES


@app.post("/api/player/evaluate-by-name")
async def player_evaluate_by_name(payload: PlayerLookupInput):
    seasons = PLAYERS.get(payload.name)
    if not seasons:
        return {"error": f"No data on file for {payload.name!r}."}
    record = seasons.get(payload.season)
    if not record:
        return {"error": f"No {payload.season} data on file for {payload.name!r}."}

    bpm = estimate_box_plus_minus(record["pts"], record["reb"], record["ast"], record["stl"], record["blk"])
    on_off = estimate_on_off(bpm)
    epm = estimate_epm(bpm, record["ast"])
    archetype = classify_archetype_from_stats(record["pts"], record["reb"], record["ast"], record["stl"], record["blk"])

    try:
        cap_hit = calculate_max_salary(payload.cap_space, record["years_of_service"], record["all_nba_honors"])
    except ValueError as e:
        return {"error": str(e)}

    try:
        player = Player(
            payload.name, record["age"], archetype,
            [record["games_played"]] * 3,
            bpm, on_off, epm, cap_hit,
            minutes_per_game=record["minutes_per_game"],
        )
    except ValueError as e:
        return {"error": str(e)}

    net_impact = calculate_net_impact_per_100(calculate_simulated_rapm(bpm, on_off), parse_epm(epm))
    age_mult = get_age_multiplier(player.age)
    injury_discount = get_injury_discount_factor(player.games_played_last_3)
    archetype_mult = get_archetype_multiplier(archetype)
    base_value = net_impact * 5_000_000
    composite_mult = age_mult * injury_discount * archetype_mult
    risk_adjusted = _apply_risk_adjustment(base_value, composite_mult)
    workload_mult = player.minutes_per_game / 32.0
    final_value = evaluate_player(player)

    return {
        "name": payload.name,
        "season": payload.season,
        "team": record["team"],
        "archetype": archetype,
        "stat_line": {
            "PTS": record["pts"], "REB": record["reb"], "AST": record["ast"],
            "STL": record["stl"], "BLK": record["blk"],
            "GP": record["games_played"], "MIN": record["minutes_per_game"],
        },
        "derived_inputs": {"box_plus_minus": bpm, "on_off": on_off, "epm": epm},
        "years_of_service": record["years_of_service"],
        "all_nba_honors": record["all_nba_honors"],
        "cap_hit": cap_hit,
        "rapm": calculate_simulated_rapm(bpm, on_off),
        "epm": epm,
        "net_impact_per_100": net_impact,
        "base_value": base_value,
        "age_multiplier": age_mult,
        "injury_discount": injury_discount,
        "archetype_multiplier": archetype_mult,
        "composite_multiplier": composite_mult,
        "risk_adjusted_value": risk_adjusted,
        "workload_multiplier": workload_mult,
        "final_value": final_value,
        "surplus_value": final_value - cap_hit,
    }
