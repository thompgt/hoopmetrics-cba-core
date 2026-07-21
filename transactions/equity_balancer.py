from cba.apron_matrix import ApronStatus


class StepienRuleViolation(Exception):
    pass


class EquityBalancer:
    def __init__(self, apron_status: ApronStatus = ApronStatus.BELOW_APRON):
        self.draft_picks_sent = 0
        self.pick_swaps_sent = 0
        self.cash_sent = 0.0
        # First/Second Apron teams are barred from sending cash in trades
        # entirely under the current CBA; only teams below the First Apron
        # get the standard league cash-in-trade limit.
        if apron_status in (ApronStatus.FIRST_APRON, ApronStatus.SECOND_APRON):
            self.CASH_LIMIT = 0.0
        else:
            self.CASH_LIMIT = 7_960_000.0

    def add_draft_pick(self):
        self.draft_picks_sent += 1

    def add_first_round_pick_for_year(self, year: int, picks_owned_by_year: dict) -> None:
        """Records trading away a first-round pick for a specific draft year,
        enforcing the Stepien Rule: a team may never end up without a
        first-round pick in any two consecutive drafts.

        picks_owned_by_year maps draft year -> number of first-round picks
        the team currently owns for that year; a year absent from the dict
        is assumed to have one (the team's own, unmodified pick).
        """
        owned_this_year = picks_owned_by_year.get(year, 1)
        if owned_this_year <= 0:
            raise ValueError(f"team does not own a first-round pick to trade in {year}")

        remaining_after_trade = owned_this_year - 1
        if remaining_after_trade == 0:
            prev_year_owned = picks_owned_by_year.get(year - 1, 1)
            next_year_owned = picks_owned_by_year.get(year + 1, 1)
            if prev_year_owned <= 0 or next_year_owned <= 0:
                raise StepienRuleViolation(
                    f"Trading the team's last {year} first-round pick would leave them "
                    "without a first-round pick in consecutive drafts."
                )

        self.draft_picks_sent += 1

    def add_pick_swap(self):
        self.pick_swaps_sent += 1

    def add_cash(self, amount: float):
        if amount < 0:
            raise ValueError("Cash amount sent in a trade cannot be negative.")
        if self.cash_sent + amount > self.CASH_LIMIT:
            raise ValueError(f"Outbound transaction cash limit of ${self.CASH_LIMIT} exceeded.")
        self.cash_sent += amount
