import pytest
from time_deposit import TimeDeposit, TimeDepositCalculator

@pytest.mark.parametrize("plan,days,balance,expected", [
    ("basic",   30, 1000.00, 1000.00),   # no interest first 30 days
    ("basic",   31, 1000.00, 1000.83),   # 1%/12
    ("student", 365, 1000.00, 1002.50),  # 3%/12 applies (still < 366)
    ("student", 366, 1000.00, 1000.00),  # no interest after 1 year
    ("premium", 45, 1000.00, 1000.00),   # starts after 45 days
    ("premium", 46, 1000.00, 1004.17),   # 5%/12
])
def test_update_balance(plan, days, balance, expected):
    td = TimeDeposit(1, plan, balance, days)
    TimeDepositCalculator().update_balance([td])
    assert td.balance == expected