def compute_contract_efficiency(modeled_value_dollars: float, cap_hit_dollars: float) -> float:
    """Computes the per-year Contract Efficiency Index by tracking the absolute dollar Delta."""
    return modeled_value_dollars - cap_hit_dollars

def compute_total_contract_value(modeled_value_dollars: float, cap_hit_dollars: float, years_remaining: int) -> float:
    """Computes total tradable surplus/deficit value across the life of a contract.

    A per-year efficiency figure alone treats a one-year bargain and the
    same bargain locked in for four years identically, but the latter is a
    far more valuable trade asset (and the former a far smaller liability
    if it's a deficit) since the surplus or deficit compounds over every
    remaining year of the deal.
    """
    if years_remaining < 1:
        raise ValueError(f"years_remaining must be at least 1, got {years_remaining}")
    per_year_efficiency = compute_contract_efficiency(modeled_value_dollars, cap_hit_dollars)
    return per_year_efficiency * years_remaining
