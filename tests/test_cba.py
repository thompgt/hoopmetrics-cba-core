import pytest
from cba.salary_caps import calculate_max_salary
from cba.apron_matrix import check_apron_status, ApronStatus
from cba.asset_efficiency import compute_contract_efficiency, compute_total_contract_value

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

def test_salary_caps_rejects_negative_inputs():
    with pytest.raises(ValueError):
        calculate_max_salary(-100_000_000, 5, False)
    with pytest.raises(ValueError):
        calculate_max_salary(100_000_000, -1, False)

def test_apron_matrix():
    first = 150_000_000
    second = 160_000_000
    assert check_apron_status(140_000_000, first, second) == ApronStatus.BELOW_APRON
    assert check_apron_status(155_000_000, first, second) == ApronStatus.FIRST_APRON
    assert check_apron_status(165_000_000, first, second) == ApronStatus.SECOND_APRON

def test_apron_matrix_rejects_swapped_thresholds():
    # first_apron/second_apron passed in the wrong order (150M/160M swapped)
    with pytest.raises(ValueError):
        check_apron_status(140_000_000, 160_000_000, 150_000_000)

def test_asset_efficiency():
    modeled_val = 35_000_000
    cap_hit = 30_000_000
    assert compute_contract_efficiency(modeled_val, cap_hit) == 5_000_000

def test_total_contract_value_compounds_across_years_remaining():
    modeled_val = 35_000_000
    cap_hit = 30_000_000
    # A 1-year bargain is worth far less as a trade asset than the identical
    # per-year bargain locked in for 4 more years.
    assert compute_total_contract_value(modeled_val, cap_hit, 1) == 5_000_000
    assert compute_total_contract_value(modeled_val, cap_hit, 4) == 20_000_000

    # The same logic applies in reverse: a bad contract's deficit compounds
    # too, making a multi-year albatross a bigger liability than a 1-year one.
    bad_modeled_val = 10_000_000
    bad_cap_hit = 40_000_000
    assert compute_total_contract_value(bad_modeled_val, bad_cap_hit, 3) == -90_000_000

    with pytest.raises(ValueError):
        compute_total_contract_value(modeled_val, cap_hit, 0)
