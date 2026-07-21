def calculate_simulated_rapm(box_plus_minus: float, on_off_rating: float) -> float:
    """Computes simulated Regularized Adjusted Plus-Minus (RAPM)."""
    return (box_plus_minus * 0.6) + (on_off_rating * 0.4)

def parse_epm(raw_epm: float) -> float:
    """Parses predictive Estimated Plus-Minus (EPM) values.

    Real-world EPM has never been observed outside roughly [-15, 15] per-100
    possessions -- a value outside that range is far more likely to be a
    data/unit error (e.g. a percentage passed as a whole number) than a real
    player rating, so it's rejected rather than silently fed into the rest
    of the valuation pipeline.
    """
    parsed = float(raw_epm)
    if not -15.0 <= parsed <= 15.0:
        raise ValueError(f"EPM value {parsed} is outside the plausible [-15, 15] range")
    return parsed

def calculate_net_impact_per_100(rapm: float, epm: float) -> float:
    """Isolates an on-off net point differential per 100 possessions."""
    return rapm + epm
