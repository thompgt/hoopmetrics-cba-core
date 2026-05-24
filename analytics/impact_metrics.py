def calculate_simulated_rapm(box_plus_minus: float, on_off_rating: float) -> float:
    """Computes simulated Regularized Adjusted Plus-Minus (RAPM)."""
    return (box_plus_minus * 0.6) + (on_off_rating * 0.4)

def parse_epm(raw_epm: float) -> float:
    """Parses predictive Estimated Plus-Minus (EPM) values."""
    return float(raw_epm)

def calculate_net_impact_per_100(rapm: float, epm: float) -> float:
    """Isolates an on-off net point differential per 100 possessions."""
    return rapm + epm
