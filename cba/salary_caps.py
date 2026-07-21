def calculate_max_salary(cap_space: float, years_of_service: int, all_nba_honors: bool = False) -> float:
    """Derives exact Maximum Salary brackets based on service time and Rose Rule."""
    if cap_space < 0:
        raise ValueError(f"cap_space cannot be negative, got {cap_space}")
    if years_of_service < 0:
        raise ValueError(f"years_of_service cannot be negative, got {years_of_service}")
    if years_of_service >= 10:
        return cap_space * 0.35
    elif 7 <= years_of_service <= 9:
        if all_nba_honors:
            return cap_space * 0.35
        return cap_space * 0.30
    else:
        if all_nba_honors:
            return cap_space * 0.30
        return cap_space * 0.25


def apply_trade_kicker(base_salary: float, kicker_percentage: float, max_salary_for_player: float) -> float:
    """Applies a trade bonus ("kicker") clause, triggered when a player with
    one in their contract is traded.

    The bonus is up to 15% of base salary, but the boosted salary can never
    push the player's total cap hit above their maximum-salary bracket (see
    calculate_max_salary) -- any excess above that ceiling is forfeited
    entirely, not carried forward, so this simply caps the result rather
    than raising.
    """
    if base_salary < 0:
        raise ValueError(f"base_salary cannot be negative, got {base_salary}")
    if max_salary_for_player < 0:
        raise ValueError(f"max_salary_for_player cannot be negative, got {max_salary_for_player}")
    if not 0 <= kicker_percentage <= 0.15:
        raise ValueError(f"kicker_percentage must be between 0 and 0.15, got {kicker_percentage}")

    boosted_salary = base_salary * (1 + kicker_percentage)
    return min(boosted_salary, max_salary_for_player)
