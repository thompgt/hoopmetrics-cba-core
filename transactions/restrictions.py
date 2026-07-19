from cba.apron_matrix import ApronStatus

class TradeRestrictionError(Exception):
    pass

def validate_salary_aggregation(team_apron_status: ApronStatus, num_outgoing_players: int):
    """Throws validation errors if a First/Second Apron team attempts to aggregate multiple salaries."""
    if not isinstance(team_apron_status, ApronStatus):
        # A raw string (e.g. a typo'd "second apron") would otherwise fail the
        # membership check below silently and skip enforcement entirely.
        raise TypeError(
            f"team_apron_status must be an ApronStatus enum member, got {team_apron_status!r}"
        )
    if team_apron_status in (ApronStatus.FIRST_APRON, ApronStatus.SECOND_APRON) and num_outgoing_players > 1:
        raise TradeRestrictionError(
            f"{team_apron_status.value} teams are prohibited from aggregating multiple outgoing player salaries."
        )
