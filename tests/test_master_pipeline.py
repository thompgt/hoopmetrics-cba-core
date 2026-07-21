import pytest
from engine_gateway import Player, evaluate_player, evaluate_trade
from cba.apron_matrix import ApronStatus

def test_player_rejects_invalid_age_and_cap_hit():
    with pytest.raises(ValueError):
        Player("Bad Age", 0, "Unknown", [82, 82, 82], 1.0, 1.0, 1.0, 5_000_000)
    with pytest.raises(ValueError):
        Player("Bad Age", -5, "Unknown", [82, 82, 82], 1.0, 1.0, 1.0, 5_000_000)
    with pytest.raises(ValueError):
        Player("Bad Cap Hit", 25, "Unknown", [82, 82, 82], 1.0, 1.0, 1.0, -5_000_000)

def test_negative_value_players_are_penalized_not_rewarded_by_risk_discounts():
    # Same bad underlying performance (negative net impact) for both players.
    # Player A is young, healthy, and archetype-neutral -> composite risk
    # multiplier of ~1.0, so their value should be left roughly unchanged.
    young_healthy_bad = Player(
        "Bad But Safe", 26, "Unknown", [82, 82, 82], -2.0, -1.0, -1.5, 5_000_000
    )
    # Player B has the identical bad performance, but is aging, injury-prone,
    # and off-archetype -> composite risk multiplier well below 1.0. Those
    # are all *negative* signals, so this player should score worse (more
    # negative), not better, than Player A.
    old_injured_bad = Player(
        "Bad And Risky", 34, "Traditional Low-Volume Big", [40, 45, 50], -2.0, -1.0, -1.5, 5_000_000
    )

    val_a = evaluate_player(young_healthy_bad)
    val_b = evaluate_player(old_injured_bad)

    assert val_a < 0
    assert val_b < 0
    # The riskier/older/off-archetype player must be penalized further, not
    # rewarded for being risky on top of being bad.
    assert val_b < val_a
    assert val_a == pytest.approx(-15_500_000)  # composite multiplier ~1.0, base value unchanged

def test_pipeline_integration():
    # Player 1: Highly scarce, young Two-Way Wing on a rookie contract
    young_wing = Player("Young Star", 21, "Two-Way Wing", [82, 82, 82], 3.0, 4.0, 3.5, 8_000_000)
    
    # Player 2: Aging, injury-prone star on a Supermax
    # Played 40, 45, 50 games. 135/246 = 0.548 -> missed 45.2%
    aging_star = Player("Aging Star", 34, "High-Volume Playmaker", [40, 45, 50], 4.0, 2.0, 4.0, 45_000_000)
    
    val_wing = evaluate_player(young_wing)
    val_star = evaluate_player(aging_star)
    
    assert val_wing > 0
    assert val_star > 0
    
    # Test Trade Scenario: Second Apron team trading an aging star + minimum player
    min_player = Player("Min Guy", 25, "Unknown", [82, 82, 82], 0.0, 0.0, 0.0, 2_000_000)

    # This should fail due to aggregation rules for Second Apron teams
    assert evaluate_trade(ApronStatus.SECOND_APRON, ApronStatus.BELOW_APRON, [aging_star, min_player], [young_wing]) == False

    # Trading just the star clears Team A's own bracket (45M -> max incoming
    # 56.5M, and young_wing is only 8M) -- but salary matching is symmetric,
    # and Team B would be taking on a $45M salary while sending out only $8M,
    # which is far outside Team B's own bracket (8M -> max incoming 15.5M).
    # A trade illegal for either side is illegal, so this must fail too.
    assert evaluate_trade(ApronStatus.SECOND_APRON, ApronStatus.BELOW_APRON, [aging_star], [young_wing]) == False

    # First Apron team can't aggregate either
    assert evaluate_trade(ApronStatus.FIRST_APRON, ApronStatus.BELOW_APRON, [aging_star, min_player], [young_wing]) == False

    # Below Apron team CAN aggregate multiple outgoing salaries, but the same
    # lopsided salary mismatch above still makes this swap illegal for Team B.
    assert evaluate_trade(ApronStatus.BELOW_APRON, ApronStatus.BELOW_APRON, [aging_star, min_player], [young_wing]) == False

    # A legally symmetric trade: comparable salaries that fit within both
    # teams' own matching brackets, with no aggregation on either side.
    comparable_vet = Player("Comparable Vet", 30, "High-Volume Playmaker", [78, 80, 79], 3.5, 2.5, 3.0, 40_000_000)
    assert evaluate_trade(ApronStatus.BELOW_APRON, ApronStatus.BELOW_APRON, [aging_star], [comparable_vet]) == True

def test_second_apron_team_cannot_use_standard_stpe_bracket():
    # A single-player, non-aggregated swap that the standard S-TPE bracket
    # would allow (20M -> up to 27.5M incoming), so this only fails once the
    # Second Apron team's own matching bracket is correctly hard-capped at
    # 1:1 instead of falling back to the generous below-apron bracket.
    team_a_player = Player("Team A Player", 27, "Unknown", [82, 82, 82], 1.0, 1.0, 1.0, 20_000_000)
    team_b_player = Player("Team B Player", 27, "Unknown", [82, 82, 82], 1.0, 1.0, 1.0, 25_000_000)
    assert evaluate_trade(ApronStatus.SECOND_APRON, ApronStatus.BELOW_APRON, [team_a_player], [team_b_player]) == False
