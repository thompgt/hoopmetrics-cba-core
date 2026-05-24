def get_max_incoming_salary(outgoing_salary: float) -> float:
    """Enforces the Simultaneous Trade Exception (S-TPE) matching brackets."""
    if outgoing_salary <= 7_250_000:
        return (outgoing_salary * 2.0) + 250_000
    elif 7_250_000 < outgoing_salary <= 29_000_000:
        return outgoing_salary + 7_500_000
    else:
        return (outgoing_salary * 1.25) + 250_000
