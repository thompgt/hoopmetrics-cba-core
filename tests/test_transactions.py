import pytest
from transactions.matcher import get_max_incoming_salary
from transactions.restrictions import validate_salary_aggregation, TradeRestrictionError
from transactions.equity_balancer import EquityBalancer, StepienRuleViolation
from cba.apron_matrix import ApronStatus

def test_matcher():
    # <= $7.25M
    assert get_max_incoming_salary(5_000_000) == 10_250_000  # (5M * 2) + 250k
    
    # $7.25M - $29M
    assert get_max_incoming_salary(10_000_000) == 17_500_000  # 10M + 7.5M
    
    # > $29M
    assert get_max_incoming_salary(30_000_000) == 37_750_000  # (30M * 1.25) + 250k

def test_matcher_is_apron_aware():
    # Below Apron teams still get the full tiered S-TPE brackets.
    assert get_max_incoming_salary(10_000_000, ApronStatus.BELOW_APRON) == 17_500_000

    # Second Apron teams cannot take back any salary beyond what they send.
    assert get_max_incoming_salary(30_000_000, ApronStatus.SECOND_APRON) == 30_000_000

    # First Apron teams are capped near 110% of outgoing salary, far below
    # the standard S-TPE bracket for the same outgoing salary.
    assert get_max_incoming_salary(10_000_000, ApronStatus.FIRST_APRON) == pytest.approx(11_100_000)
    assert get_max_incoming_salary(10_000_000, ApronStatus.FIRST_APRON) < get_max_incoming_salary(10_000_000, ApronStatus.BELOW_APRON)

def test_restrictions():
    # Below apron can aggregate
    validate_salary_aggregation(ApronStatus.BELOW_APRON, 2)
    validate_salary_aggregation(ApronStatus.BELOW_APRON, 1)

    # Apron teams cannot aggregate
    with pytest.raises(TradeRestrictionError):
        validate_salary_aggregation(ApronStatus.FIRST_APRON, 2)

    with pytest.raises(TradeRestrictionError):
        validate_salary_aggregation(ApronStatus.SECOND_APRON, 3)

    # Apron teams can send 1 player
    validate_salary_aggregation(ApronStatus.FIRST_APRON, 1)
    validate_salary_aggregation(ApronStatus.SECOND_APRON, 1)

def test_restrictions_rejects_raw_strings():
    # A typo'd or mis-cased raw string (e.g. "second apron") used to fail the
    # membership check silently and skip enforcement entirely. It must now
    # raise loudly instead of pretending the team is unrestricted.
    with pytest.raises(TypeError):
        validate_salary_aggregation("Second Apron", 2)
    with pytest.raises(TypeError):
        validate_salary_aggregation("second apron", 2)

def test_equity_balancer():
    balancer = EquityBalancer()
    balancer.add_draft_pick()
    balancer.add_pick_swap()
    assert balancer.draft_picks_sent == 1
    assert balancer.pick_swaps_sent == 1
    
    balancer.add_cash(7_000_000)
    assert balancer.cash_sent == 7_000_000

    with pytest.raises(ValueError, match="cash limit"):
        balancer.add_cash(1_000_000)

def test_equity_balancer_rejects_negative_cash():
    balancer = EquityBalancer()
    with pytest.raises(ValueError, match="negative"):
        balancer.add_cash(-1_000_000)
    # The rejected call must not have mutated state.
    assert balancer.cash_sent == 0.0

def test_equity_balancer_bars_cash_for_apron_teams():
    # First/Second Apron teams cannot send any cash in a trade.
    for apron in (ApronStatus.FIRST_APRON, ApronStatus.SECOND_APRON):
        balancer = EquityBalancer(apron)
        assert balancer.CASH_LIMIT == 0.0
        with pytest.raises(ValueError, match="cash limit"):
            balancer.add_cash(1)

    # A Below Apron team still gets the standard limit.
    below_apron_balancer = EquityBalancer(ApronStatus.BELOW_APRON)
    assert below_apron_balancer.CASH_LIMIT == 7_960_000.0

def test_stepien_rule_blocks_two_consecutive_empty_drafts():
    balancer = EquityBalancer()
    # Team already traded away its 2028 first-rounder; 2027 is its last pick
    # (a swap-protected pick they got back doesn't count toward 2027 here).
    picks_owned = {2027: 1, 2028: 0}
    with pytest.raises(StepienRuleViolation):
        balancer.add_first_round_pick_for_year(2027, picks_owned)
    # The rejected call must not have mutated state.
    assert balancer.draft_picks_sent == 0

def test_stepien_rule_allows_trading_a_second_first_rounder():
    balancer = EquityBalancer()
    # Team owns two 2027 first-rounders (its own + an acquired one); trading
    # one still leaves them a first-rounder that year.
    picks_owned = {2027: 2}
    balancer.add_first_round_pick_for_year(2027, picks_owned)
    assert balancer.draft_picks_sent == 1

def test_stepien_rule_rejects_trading_an_unowned_pick():
    balancer = EquityBalancer()
    with pytest.raises(ValueError):
        balancer.add_first_round_pick_for_year(2027, {2027: 0})
