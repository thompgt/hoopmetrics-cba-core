def calculate_available_games_ratio(games_played_last_3_seasons: list[int]) -> float:
    """Evaluates a player's historical Available Games Ratio over a rolling window of
    however many trailing seasons are provided (typically 3, but works for players
    with fewer seasons of history, e.g. rookies and second-year players)."""
    if not games_played_last_3_seasons:
        raise ValueError("games_played_last_3_seasons must contain at least one season")
    total_possible_games = 82 * len(games_played_last_3_seasons)
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
