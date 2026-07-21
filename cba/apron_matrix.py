from enum import Enum

class ApronStatus(Enum):
    """A team's Tax Apron classification.

    Using an enum instead of raw strings means a typo or case mismatch
    (e.g. "second apron" vs "Second Apron") is caught immediately as an
    AttributeError/ImportError at the call site, instead of silently
    disabling apron restrictions downstream in restrictions.py.
    """
    BELOW_APRON = "Below Apron"
    FIRST_APRON = "First Apron"
    SECOND_APRON = "Second Apron"

def check_apron_status(team_payroll: float, first_apron: float, second_apron: float) -> ApronStatus:
    """Monitors team payroll totals against Tax Apron thresholds."""
    if first_apron > second_apron:
        raise ValueError(
            f"first_apron ({first_apron}) cannot be greater than second_apron ({second_apron})"
        )
    if team_payroll >= second_apron:
        return ApronStatus.SECOND_APRON
    elif team_payroll >= first_apron:
        return ApronStatus.FIRST_APRON
    return ApronStatus.BELOW_APRON
