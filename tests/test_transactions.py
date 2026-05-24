import pytest
from transactions.matcher import get_max_incoming_salary
from transactions.restrictions import validate_salary_aggregation, TradeRestrictionError
from transactions.equity_balancer import EquityBalancer

def test_matcher():
    # <= $7.25M
    assert get_max_incoming_salary(5_000_000) == 10_250_000  # (5M * 2) + 250k
    
    # $7.25M - $29M
    assert get_max_incoming_salary(10_000_000) == 17_500_000  # 10M + 7.5M
    
    # > $29M
    assert get_max_incoming_salary(30_000_000) == 37_750_000  # (30M * 1.25) + 250k

def test_restrictions():
    # Below apron can aggregate
    validate_salary_aggregation("Below Apron", 2)
    validate_salary_aggregation("Below Apron", 1)
    
    # Apron teams cannot aggregate
    with pytest.raises(TradeRestrictionError):
        validate_salary_aggregation("First Apron", 2)
        
    with pytest.raises(TradeRestrictionError):
        validate_salary_aggregation("Second Apron", 3)
        
    # Apron teams can send 1 player
    validate_salary_aggregation("First Apron", 1)
    validate_salary_aggregation("Second Apron", 1)

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
