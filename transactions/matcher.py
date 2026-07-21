from cba.apron_matrix import ApronStatus

def get_max_incoming_salary(outgoing_salary: float, apron_status: ApronStatus = ApronStatus.BELOW_APRON) -> float:
    """Enforces salary-matching limits on incoming salary for a trade.

    The generous tiered Simultaneous Trade Exception (S-TPE) brackets only
    apply to teams below the First Apron. Apron teams are hard-capped
    regardless of the standard brackets: Second Apron teams cannot take
    back any salary beyond what they send out (strict 1:1), and First
    Apron teams are limited to roughly 110% of outgoing salary. Previously
    every team received the same full S-TPE brackets regardless of apron
    status, so apron restrictions were only enforced on aggregation, not
    on matching -- letting hard-capped teams take back far more salary
    than the CBA allows.
    """
    if apron_status == ApronStatus.SECOND_APRON:
        return outgoing_salary
    if apron_status == ApronStatus.FIRST_APRON:
        return (outgoing_salary * 1.10) + 100_000

    if outgoing_salary <= 7_250_000:
        return (outgoing_salary * 2.0) + 250_000
    elif 7_250_000 < outgoing_salary <= 29_000_000:
        return outgoing_salary + 7_500_000
    else:
        return (outgoing_salary * 1.25) + 250_000
