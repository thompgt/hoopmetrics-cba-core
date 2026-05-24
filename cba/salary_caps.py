def calculate_max_salary(cap_space: float, years_of_service: int, all_nba_honors: bool = False) -> float:
    """Derives exact Maximum Salary brackets based on service time and Rose Rule."""
    if years_of_service >= 10:
        return cap_space * 0.35
    elif 7 <= years_of_service <= 9:
        if all_nba_honors:
            return cap_space * 0.35
        return cap_space * 0.30
    else:
        if all_nba_honors:
            return cap_space * 0.30
        return cap_space * 0.25
