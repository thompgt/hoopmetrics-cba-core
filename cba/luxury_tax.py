# Progressive luxury tax brackets, modeled on the current CBA's publicly
# documented structure: each $5M increment of payroll above the tax line is
# taxed at a higher marginal rate, doubled up further for "repeater"
# offenders (a team taxpaying in at least 3 of the previous 4 seasons).
# This is a simplified approximation for planning/valuation purposes, not
# an official tax computation.
_BRACKET_SIZE = 5_000_000
_BASE_RATES = [1.5, 1.75, 2.5, 3.25]
_REPEATER_RATES = [2.5, 2.75, 3.25, 3.75]
_EXTRA_BRACKET_STEP = 0.5


def compute_luxury_tax_bill(team_payroll: float, tax_line: float, is_repeater: bool = False) -> float:
    """Computes a team's progressive luxury tax bill for a given payroll.

    Returns 0.0 for a team at or below the tax line. Every $5M of payroll
    above the line is taxed at a progressively higher marginal rate; once a
    team's excess exceeds the last defined bracket ($20M over), the rate
    keeps climbing by an additional 0.5x per further $5M increment.
    """
    if team_payroll < 0:
        raise ValueError(f"team_payroll cannot be negative, got {team_payroll}")
    if tax_line < 0:
        raise ValueError(f"tax_line cannot be negative, got {tax_line}")

    remaining = team_payroll - tax_line
    if remaining <= 0:
        return 0.0

    rates = _REPEATER_RATES if is_repeater else _BASE_RATES
    tax = 0.0

    for rate in rates:
        if remaining <= 0:
            break
        portion = min(remaining, _BRACKET_SIZE)
        tax += portion * rate
        remaining -= portion

    extra_rate = rates[-1] + _EXTRA_BRACKET_STEP
    while remaining > 0:
        portion = min(remaining, _BRACKET_SIZE)
        tax += portion * extra_rate
        remaining -= portion
        extra_rate += _EXTRA_BRACKET_STEP

    return tax
