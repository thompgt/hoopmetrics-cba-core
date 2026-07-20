import pytest
from transactions.matcher import get_max_incoming_salary
from transactions.restrictions import validate_salary_aggregation, TradeRestrictionError
from transactions.equity_balancer import EquityBalancer
from cba.apron_matrix import ApronStatus

def test_matcher():
    # <= $7.25M
    assert get_max_incoming_salary(5_000_000) == 10_250_000  # (5M * 2) + 250k
    
    # $7.25M - $29M
    assert get_max_incoming_salary(10_000_000) == 17_500_000  # 10M + 7.5M
    
    # > $29M
    assert get_max_incoming_salary(30_000_000) == 37_750_000  # (30M * 1.25) + 250k

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
