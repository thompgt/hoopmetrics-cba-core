import pytest
from cba.salary_caps import calculate_max_salary
from cba.apron_matrix import check_apron_status, ApronStatus
from cba.asset_efficiency import compute_contract_efficiency, compute_total_contract_value
from cba.luxury_tax import compute_luxury_tax_bill
from cba.bird_rights import classify_bird_rights, get_re_signing_salary_cap, BirdRightsStatus

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

def test_luxury_tax_bill_below_the_line_is_zero():
    assert compute_luxury_tax_bill(190_000_000, 200_000_000) == 0.0
    assert compute_luxury_tax_bill(200_000_000, 200_000_000) == 0.0

def test_luxury_tax_bill_progressive_brackets():
    tax_line = 200_000_000
    # $3M over -> fully in the first ($0-5M) bracket at 1.5x
    assert compute_luxury_tax_bill(203_000_000, tax_line) == pytest.approx(4_500_000)
    # $7M over -> $5M @ 1.5x + $2M @ 1.75x
    assert compute_luxury_tax_bill(207_000_000, tax_line) == pytest.approx(11_000_000)
    # $25M over -> all 4 brackets ($45M) + $5M in the first "extra" bracket @ 3.75x
    assert compute_luxury_tax_bill(225_000_000, tax_line) == pytest.approx(63_750_000)

def test_luxury_tax_bill_repeater_surcharge_is_higher():
    tax_line = 200_000_000
    non_repeater = compute_luxury_tax_bill(210_000_000, tax_line, is_repeater=False)
    repeater = compute_luxury_tax_bill(210_000_000, tax_line, is_repeater=True)
    assert repeater > non_repeater

def test_luxury_tax_bill_rejects_negative_inputs():
    with pytest.raises(ValueError):
        compute_luxury_tax_bill(-1, 200_000_000)
    with pytest.raises(ValueError):
        compute_luxury_tax_bill(200_000_000, -1)

def test_classify_bird_rights():
    assert classify_bird_rights(0) == BirdRightsStatus.NON_BIRD
    assert classify_bird_rights(1) == BirdRightsStatus.NON_BIRD
    assert classify_bird_rights(2) == BirdRightsStatus.EARLY_BIRD
    assert classify_bird_rights(3) == BirdRightsStatus.FULL_BIRD
    assert classify_bird_rights(10) == BirdRightsStatus.FULL_BIRD
    with pytest.raises(ValueError):
        classify_bird_rights(-1)

def test_re_signing_salary_cap():
    prior_salary = 10_000_000
    assert get_re_signing_salary_cap(prior_salary, BirdRightsStatus.NON_BIRD) == 12_000_000
    assert get_re_signing_salary_cap(prior_salary, BirdRightsStatus.EARLY_BIRD) == 17_500_000
    # Full Bird rights aren't bounded by prior salary at all.
    assert get_re_signing_salary_cap(prior_salary, BirdRightsStatus.FULL_BIRD) is None

    with pytest.raises(ValueError):
        get_re_signing_salary_cap(-1, BirdRightsStatus.NON_BIRD)
    with pytest.raises(TypeError):
        get_re_signing_salary_cap(prior_salary, "Non-Bird")
