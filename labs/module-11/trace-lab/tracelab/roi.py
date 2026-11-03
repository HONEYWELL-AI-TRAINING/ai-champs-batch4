"""Cost per accepted output (deck s.11). Every input is an explicit assumption you must fill in."""
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Scenario:
    runs: int                    # every run, including failed and retried ones
    accepted: int                # outputs kept at production quality (not outputs generated)
    tokens_in_per_run: float
    tokens_out_per_run: float
    price_in_per_m: float        # currency per million input tokens (your contract, not a default)
    price_out_per_m: float
    tooling_per_run: float       # hosting, vector store, API calls
    review_min_per_run: float    # a human looks at every output, including the ones thrown away
    edit_min_per_accepted: float
    rework_per_accepted: float   # defects and reverts that arrive later (expected cost)
    hourly_rate: float
    manual_min_per_task: float   # measured baseline for doing the task by hand

    @property
    def token_cost_per_run(self):
        return (self.tokens_in_per_run * self.price_in_per_m + self.tokens_out_per_run * self.price_out_per_m) / 1e6

    @property
    def fixed_per_run(self):     # paid whether or not the output is accepted
        return self.token_cost_per_run + self.tooling_per_run + self.review_min_per_run / 60 * self.hourly_rate

    @property
    def per_accepted(self):      # paid only when the output is kept
        return self.edit_min_per_accepted / 60 * self.hourly_rate + self.rework_per_accepted

    @property
    def total_cost(self):
        return self.runs * self.fixed_per_run + self.accepted * self.per_accepted

    @property
    def cost_per_accepted(self):
        return self.total_cost / self.accepted if self.accepted else None

    @property
    def value_per_accepted(self):
        return self.manual_min_per_task / 60 * self.hourly_rate

    @property
    def net(self):
        return self.accepted * self.value_per_accepted - self.total_cost

    @property
    def acceptance_rate(self):
        return self.accepted / self.runs

    @property
    def breakeven_acceptance(self):
        """Acceptance rate at which net = 0, other per-run inputs held fixed. None = never breaks even."""
        margin = self.value_per_accepted - self.per_accepted
        return self.fixed_per_run / margin if margin > 0 else None


def sweep(s, field, values):
    """What happens to cost per accepted output if one assumption is wrong? Returns [(value, cost)]."""
    return [(v, replace(s, **{field: v}).cost_per_accepted) for v in values]
