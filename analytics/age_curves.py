def get_age_multiplier(age: int) -> float:
    """Implements non-linear peak-performance curves."""
    if age <= 23:
        # Exponential growth-projection multiplier. Applied for the entire
        # pre-peak range (not just 19-23): the same formula must cover
        # under-19 prospects too, otherwise the flat under-19 premium falls
        # below the value the formula assigns right at age 19, producing a
        # discontinuous dip in age multiplier for the youngest, highest
        # upside players.
        return 1.0 + (0.05 * (24 - age) ** 1.5)
    elif 24 <= age <= 29:
        # Peak baseline efficiency multiplier
        return 1.0
    else:
        # Quadratic decay penalty factor (age >= 30)
        decay = ((age - 29) ** 2) * 0.015
        return max(0.1, 1.0 - decay)
