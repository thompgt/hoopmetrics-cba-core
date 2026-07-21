from analytics.impact_metrics import calculate_simulated_rapm, parse_epm, calculate_net_impact_per_100
from analytics.age_curves import get_age_multiplier
from analytics.injury_risk import get_injury_discount_factor
from analytics.scarcity_curves import get_archetype_multiplier
from cba.salary_caps import calculate_max_salary
from cba.apron_matrix import check_apron_status, ApronStatus
from cba.asset_efficiency import compute_contract_efficiency
from transactions.matcher import get_max_incoming_salary
from transactions.restrictions import validate_salary_aggregation, TradeRestrictionError
from transactions.equity_balancer import EquityBalancer

class Player:
    def __init__(self, name: str, age: int, archetype: str, games_played_last_3: list[int],
                 box_plus_minus: float, on_off: float, epm: float, cap_hit: float):
        if age <= 0:
            raise ValueError(f"age must be positive, got {age}")
        if cap_hit < 0:
            raise ValueError(f"cap_hit cannot be negative, got {cap_hit}")
        self.name = name
        self.age = age
        self.archetype = archetype
        self.games_played_last_3 = games_played_last_3
        self.box_plus_minus = box_plus_minus
        self.on_off = on_off
        self.epm = epm
        self.cap_hit = cap_hit

def _apply_risk_adjustment(value: float, multiplier: float) -> float:
    """Applies a risk/quality multiplier to a signed dollar value such that a
    discount (multiplier < 1) always makes the value worse and a premium
    (multiplier > 1) always makes it better, regardless of the value's sign.

    Naively multiplying a negative value by a discount factor makes it less
    negative (i.e. *better*), which is backwards: an aging, injury-prone,
    off-archetype player who is already below replacement level should be
    penalized further, not rewarded. Reflecting the multiplier through 1.0
    for negative values fixes this while leaving positive-value behavior
    (the common case) unchanged.
    """
    if value >= 0:
        return value * multiplier
    return value * (2 - multiplier)

def evaluate_player(player: Player) -> float:
    rapm = calculate_simulated_rapm(player.box_plus_minus, player.on_off)
    parsed_epm = parse_epm(player.epm)
    net_impact = calculate_net_impact_per_100(rapm, parsed_epm)

    age_mult = get_age_multiplier(player.age)
    injury_discount = get_injury_discount_factor(player.games_played_last_3)
    archetype_mult = get_archetype_multiplier(player.archetype)

    # Simple modeled value scaling: 1 point of net impact = $5M
    base_value = net_impact * 5_000_000

    composite_mult = age_mult * injury_discount * archetype_mult
    final_value = _apply_risk_adjustment(base_value, composite_mult)
    return final_value

def evaluate_trade(team_a_apron: ApronStatus, team_b_apron: ApronStatus,
                    team_a_sending: list[Player], team_b_sending: list[Player],
                    team_a_equity: EquityBalancer = None, team_b_equity: EquityBalancer = None) -> bool:
    """
    Evaluates if Team A can legally make this trade with Team B under S-TPE and Apron rules.

    Both sides of a trade are subject to the same aggregation and salary-matching
    rules: each team's incoming salary is bounded by a bracket derived from *that
    team's own* outgoing salary and its own apron status, so both directions must
    be checked independently. Second Apron teams are hard-capped at 1:1 salary
    matching and First Apron teams near 110%, regardless of the standard S-TPE
    brackets a team below the First Apron would otherwise receive.

    team_a_equity/team_b_equity are optional EquityBalancer instances tracking
    non-salary assets (cash, picks) each team is sending. If provided, the
    cash-in-trade limit is enforced here rather than trusting that the
    balancer was constructed with the matching apron status: First/Second
    Apron teams cannot send any cash in a trade, full stop.
    """
    try:
        validate_salary_aggregation(team_a_apron, len(team_a_sending))
        validate_salary_aggregation(team_b_apron, len(team_b_sending))
    except TradeRestrictionError as e:
        print(f"Trade blocked: {e}")
        return False

    for label, apron, equity in (("Team A", team_a_apron, team_a_equity), ("Team B", team_b_apron, team_b_equity)):
        if equity is not None and apron in (ApronStatus.FIRST_APRON, ApronStatus.SECOND_APRON) and equity.cash_sent > 0:
            print(f"Trade blocked: {label} is {apron.value} and cannot send cash (${equity.cash_sent}) in a trade")
            return False

    team_a_outgoing_salary = sum(p.cap_hit for p in team_a_sending)
    team_b_outgoing_salary = sum(p.cap_hit for p in team_b_sending)

    max_incoming_for_a = get_max_incoming_salary(team_a_outgoing_salary, team_a_apron)
    max_incoming_for_b = get_max_incoming_salary(team_b_outgoing_salary, team_b_apron)

    if team_b_outgoing_salary > max_incoming_for_a:
        print(f"Trade blocked: Team A's incoming salary {team_b_outgoing_salary} exceeds max {max_incoming_for_a}")
        return False

    if team_a_outgoing_salary > max_incoming_for_b:
        print(f"Trade blocked: Team B's incoming salary {team_a_outgoing_salary} exceeds max {max_incoming_for_b}")
        return False

    return True
