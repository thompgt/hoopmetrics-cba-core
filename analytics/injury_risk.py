def calculate_available_games_ratio(games_played_last_3_seasons: list[int]) -> float:
    """Evaluates a player's historical Available Games Ratio over a rolling 3-season window."""
    total_possible_games = 82 * 3
    total_played = sum(games_played_last_3_seasons)
    return total_played / total_possible_games

def get_injury_discount_factor(games_played_last_3_seasons: list[int]) -> float:
    """Computes an active baseline penalty scaling factor based on missed games."""
    ratio = calculate_available_games_ratio(games_played_last_3_seasons)
    missed_ratio = 1.0 - ratio
    if missed_ratio > 0.25:
        # Apply a multiplicative haircut if a player misses greater than 25% of games
        extra_missed = missed_ratio - 0.25
        haircut = extra_missed * 1.5
        return max(0.5, 1.0 - haircut)
    return 1.0
