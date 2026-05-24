def compute_contract_efficiency(modeled_value_dollars: float, cap_hit_dollars: float) -> float:
    """Computes the Contract Efficiency Index by tracking the absolute dollar Delta."""
    return modeled_value_dollars - cap_hit_dollars
