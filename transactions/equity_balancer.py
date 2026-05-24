class EquityBalancer:
    def __init__(self):
        self.draft_picks_sent = 0
        self.pick_swaps_sent = 0
        self.cash_sent = 0.0
        self.CASH_LIMIT = 7_960_000.0

    def add_draft_pick(self):
        self.draft_picks_sent += 1

    def add_pick_swap(self):
        self.pick_swaps_sent += 1

    def add_cash(self, amount: float):
        if self.cash_sent + amount > self.CASH_LIMIT:
            raise ValueError(f"Outbound transaction cash limit of ${self.CASH_LIMIT} exceeded.")
        self.cash_sent += amount
