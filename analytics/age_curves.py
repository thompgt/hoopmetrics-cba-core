def get_age_multiplier(age: int) -> float:
    """Implements non-linear peak-performance curves."""
    if 19 <= age <= 23:
        # Exponential projection multiplier
        return 1.0 + (0.05 * (24 - age) ** 1.5)
    elif 24 <= age <= 29:
        # Peak baseline efficiency multiplier
        return 1.0
    elif age >= 30:
        # Quadratic decay penalty factor
        decay = ((age - 29) ** 2) * 0.015
        return max(0.1, 1.0 - decay)
    else:
        # For age < 19, high upside
        return 1.5
