import pytest
from cba.salary_caps import calculate_max_salary
from cba.apron_matrix import check_apron_status
from cba.asset_efficiency import compute_contract_efficiency

def test_salary_caps():
    cap = 100_000_000
    # 0-6 years
    assert calculate_max_salary(cap, 5, False) == 25_000_000
    assert calculate_max_salary(cap, 5, True) == 30_000_000  # Rose rule upgrade
    
    # 7-9 years
    assert calculate_max_salary(cap, 8, False) == 30_000_000
    assert calculate_max_salary(cap, 8, True) == 35_000_000  # Supermax upgrade
    
    # 10+ years
    assert calculate_max_salary(cap, 12, False) == 35_000_000
    assert calculate_max_salary(cap, 12, True) == 35_000_000

def test_apron_matrix():
    first = 150_000_000
    second = 160_000_000
    assert check_apron_status(140_000_000, first, second) == "Below Apron"
    assert check_apron_status(155_000_000, first, second) == "First Apron"
    assert check_apron_status(165_000_000, first, second) == "Second Apron"

def test_asset_efficiency():
    modeled_val = 35_000_000
    cap_hit = 30_000_000
    assert compute_contract_efficiency(modeled_val, cap_hit) == 5_000_000
