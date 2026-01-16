from typing import Protocol, List, Tuple
from time_deposit import TimeDeposit  # import domain from existing file

class TimeDepositRepository(Protocol):
    """Port for persistence operations the app needs."""
    def list_all_with_withdrawals(self) -> List[Tuple[TimeDeposit, list]]: ...
    def update_balances(self, items: List[TimeDeposit]) -> int: ...
