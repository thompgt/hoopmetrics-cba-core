from enum import Enum


class BirdRightsStatus(Enum):
    """A free agent's "Bird rights" tier, which lets their own team exceed
    the salary cap to re-sign them (an exception unrelated to the S-TPE
    trade-matching brackets in transactions/matcher.py)."""
    NON_BIRD = "Non-Bird"
    EARLY_BIRD = "Early Bird"
    FULL_BIRD = "Full Bird"


def classify_bird_rights(consecutive_seasons_with_team: int) -> BirdRightsStatus:
    """Classifies Bird rights tier from consecutive seasons with the same team
    without the player changing teams as a free agent or being waived.

    Full Bird rights (3+ seasons) let a team exceed the cap to re-sign the
    player up to their ordinary max-salary bracket. Early Bird (2 seasons)
    and Non-Bird (fewer than 2) grant progressively smaller cap exceptions
    -- see get_re_signing_salary_cap.
    """
    if consecutive_seasons_with_team < 0:
        raise ValueError(
            f"consecutive_seasons_with_team cannot be negative, got {consecutive_seasons_with_team}"
        )
    if consecutive_seasons_with_team >= 3:
        return BirdRightsStatus.FULL_BIRD
    elif consecutive_seasons_with_team == 2:
        return BirdRightsStatus.EARLY_BIRD
    else:
        return BirdRightsStatus.NON_BIRD


def get_re_signing_salary_cap(prior_salary: float, bird_rights_status: BirdRightsStatus) -> float:
    """Returns the maximum first-year salary a team can offer its own free
    agent using its Bird exception, exceeding the salary cap to do so.

    Early Bird rights cap the offer at 175% of the player's prior salary;
    Non-Bird rights cap it at 120%. Full Bird rights aren't bounded by
    prior salary at all -- the only ceiling is the player's ordinary
    max-salary bracket (see cba.salary_caps.calculate_max_salary) -- so
    this returns None for Full Bird to signal "no additional cap here"
    rather than a made-up numeric limit.
    """
    if prior_salary < 0:
        raise ValueError(f"prior_salary cannot be negative, got {prior_salary}")
    if not isinstance(bird_rights_status, BirdRightsStatus):
        raise TypeError(
            f"bird_rights_status must be a BirdRightsStatus enum member, got {bird_rights_status!r}"
        )

    if bird_rights_status == BirdRightsStatus.FULL_BIRD:
        return None
    elif bird_rights_status == BirdRightsStatus.EARLY_BIRD:
        return prior_salary * 1.75
    else:
        return prior_salary * 1.20
