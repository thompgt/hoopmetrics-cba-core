def check_apron_status(team_payroll: float, first_apron: float, second_apron: float) -> str:
    """Monitors team payroll totals against Tax Apron thresholds."""
    if team_payroll >= second_apron:
        return "Second Apron"
    elif team_payroll >= first_apron:
        return "First Apron"
    return "Below Apron"
