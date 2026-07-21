def _validate_games_played(games_played_seasons: list[int]) -> None:
    if not games_played_seasons:
        raise ValueError("games_played_last_3_seasons must contain at least one season")
    for games in games_played_seasons:
        if not 0 <= games <= 82:
            raise ValueError(
                f"games played in a season must be between 0 and 82, got {games}"
            )

def calculate_available_games_ratio(games_played_last_3_seasons: list[int]) -> float:
    """Evaluates a player's historical Available Games Ratio over a rolling window of
    however many trailing seasons are provided (typically 3, but works for players
    with fewer seasons of history, e.g. rookies and second-year players)."""
    _validate_games_played(games_played_last_3_seasons)
    total_possible_games = 82 * len(games_played_last_3_seasons)
    total_played = sum(games_played_last_3_seasons)
    return total_played / total_possible_games

def _calculate_recency_weighted_games_ratio(games_played_seasons: list[int]) -> float:
    """Same as calculate_available_games_ratio, but weights the most recent season
    (last element) more heavily than older ones. A season missed 3 years ago is a
    weaker signal of *current* injury risk than a season missed last year, so
    weighting every season equally understates risk for a player trending toward
    more missed games and overstates it for one who has recently recovered.

    Assumes games_played_seasons is ordered oldest-to-most-recent.
    """
    _validate_games_played(games_played_seasons)
    n = len(games_played_seasons)
    weights = range(1, n + 1)  # oldest season weight 1, most recent weight n
    weighted_played = sum(games * weight for games, weight in zip(games_played_seasons, weights))
    weighted_possible = 82 * sum(weights)
    return weighted_played / weighted_possible

def get_injury_discount_factor(games_played_last_3_seasons: list[int]) -> float:
    """Computes an active baseline penalty scaling factor based on missed games,
    weighting more recent seasons more heavily (see
    _calculate_recency_weighted_games_ratio)."""
    ratio = _calculate_recency_weighted_games_ratio(games_played_last_3_seasons)
    missed_ratio = 1.0 - ratio
    if missed_ratio > 0.25:
        # Apply a multiplicative haircut if a player misses greater than 25% of games
        extra_missed = missed_ratio - 0.25
        haircut = extra_missed * 1.5
        return max(0.5, 1.0 - haircut)
    return 1.0
