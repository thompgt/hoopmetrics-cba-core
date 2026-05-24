class TradeRestrictionError(Exception):
    pass

def validate_salary_aggregation(team_apron_status: str, num_outgoing_players: int):
    """Throws validation errors if a First/Second Apron team attempts to aggregate multiple salaries."""
    if team_apron_status in ["First Apron", "Second Apron"] and num_outgoing_players > 1:
        raise TradeRestrictionError(
            f"{team_apron_status} teams are prohibited from aggregating multiple outgoing player salaries."
        )
