import pytest
from engine_gateway import Player, evaluate_player, evaluate_trade

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
    assert evaluate_trade("Second Apron", [aging_star, min_player], [young_wing]) == False
    
    # If they trade just the star, they can take back up to 125% + 250k.
    # Outgoing: 45M -> Max incoming: 56.5M. Young wing is 8M, so it's valid.
    assert evaluate_trade("Second Apron", [aging_star], [young_wing]) == True
    
    # First Apron team can't aggregate either
    assert evaluate_trade("First Apron", [aging_star, min_player], [young_wing]) == False
    
    # Below Apron team CAN aggregate
    # Outgoing: 47M -> Max incoming: 47M * 1.25 + 250k = 59M.
    assert evaluate_trade("Below Apron", [aging_star, min_player], [young_wing]) == True
