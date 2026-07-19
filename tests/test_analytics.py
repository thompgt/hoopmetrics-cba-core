import pytest
from analytics.impact_metrics import calculate_simulated_rapm, parse_epm, calculate_net_impact_per_100
from analytics.age_curves import get_age_multiplier
from analytics.injury_risk import calculate_available_games_ratio, get_injury_discount_factor
from analytics.scarcity_curves import get_archetype_multiplier

def test_impact_metrics():
    rapm = calculate_simulated_rapm(2.0, 1.0)
    assert rapm == pytest.approx(1.6)
    epm = parse_epm(3.5)
    assert epm == 3.5
    net_impact = calculate_net_impact_per_100(rapm, epm)
    assert net_impact == pytest.approx(5.1)

def test_age_curves():
    # Age 19-23
    mult_20 = get_age_multiplier(20)
    assert mult_20 > 1.0
    # Age 24-29
    assert get_age_multiplier(26) == 1.0
    # Age 30+
    mult_32 = get_age_multiplier(32)
    assert mult_32 < 1.0
    assert mult_32 == pytest.approx(1.0 - ((32 - 29) ** 2) * 0.015)

def test_injury_risk():
    # 82, 82, 82 -> 1.0
    assert get_injury_discount_factor([82, 82, 82]) == 1.0
    # Missed > 25% (e.g., played 150 out of 246 games. missed = 96. 96/246 = ~39%)
    ratio = calculate_available_games_ratio([50, 50, 50]) # 150/246 = 0.609 -> 39% missed
    assert ratio < 0.75
    discount = get_injury_discount_factor([50, 50, 50])
    assert discount < 1.0

def test_injury_risk_short_history():
    # A rookie with only one season on record should be judged against that
    # one season's 82 games, not a hardcoded 3-season (246 game) denominator.
    ratio_rookie = calculate_available_games_ratio([70])
    assert ratio_rookie == pytest.approx(70 / 82)
    # 70/82 = ~85% available, well under the 25%-missed discount threshold.
    assert get_injury_discount_factor([70]) == 1.0

    # A second-year player with two seasons on record is judged against 164
    # games, not 246.
    ratio_second_year = calculate_available_games_ratio([80, 80])
    assert ratio_second_year == pytest.approx(160 / 164)

def test_injury_risk_rejects_empty_history():
    with pytest.raises(ValueError):
        calculate_available_games_ratio([])
    
def test_scarcity_curves():
    assert get_archetype_multiplier("Two-Way Wing") == 1.25
    assert get_archetype_multiplier("Traditional Low-Volume Big") == 0.85
    assert get_archetype_multiplier("Unknown") == 1.0
