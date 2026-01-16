from __future__ import annotations
from typing import List, Optional, Protocol

from time_deposit import TimeDeposit, TimeDepositCalculator  # domain from existing file
from app.application.ports import TimeDepositRepository


class BalanceCalculator(Protocol):
    """Seam for future extensibility without changing the method signature."""
    def update_balance(self, xs: List[TimeDeposit]) -> None: ...


class UpdateBalancesService:
    """Application service: fetch -> calculate -> persist."""
    def __init__(self, repo: TimeDepositRepository, calc: Optional[BalanceCalculator] = None):
        self.repo = repo
        # Use the original calculator by default; this preserves behaviour.
        self.calc = calc or TimeDepositCalculator()

    def run(self) -> int:
        # Get domain objects from the repository 
        rows = self.repo.list_all_with_withdrawals()
        deposits: List[TimeDeposit] = [d for (d, _ws) in rows]

        self.calc.update_balance(deposits)

        # Persist updated balances
        return self.repo.update_balances(deposits)