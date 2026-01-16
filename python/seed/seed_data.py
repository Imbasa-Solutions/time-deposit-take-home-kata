"""Dev-only seed script to populate the DB for manual testing.
Run from the `python/` folder with your venv active:

    export DATABASE_URL="sqlite:///./app.db"
    python -m seed.seed_data

"""
from datetime import date
from app.adapters.persistence import (
    init_db,
    SessionLocal,
    TimeDepositRow,
    WithdrawalRow,
)

def reset_and_seed() -> None:
    init_db()
    with SessionLocal() as s:
        # wipe existing rows (dev only)
        s.query(WithdrawalRow).delete()
        s.query(TimeDepositRow).delete()

        # deposits chosen to exercise each rule path
        deposits = [
            # basic > 30 days => 1%/12 applies
            TimeDepositRow(id=1, planType="basic", days=45, balance=1234567.00),
            # student < 366 days => 3%/12 applies
            TimeDepositRow(id=2, planType="student", days=200, balance=20000.00),
            # student >= 366 days => no interest
            TimeDepositRow(id=3, planType="student", days=500, balance=15000.00),
            # premium > 45 days => 5%/12 applies
            TimeDepositRow(id=4, planType="premium", days=46, balance=100000.00),
            # premium <= 45 days => no interest
            TimeDepositRow(id=5, planType="premium", days=40, balance=100000.00),
            # any plan <= 30 days => no interest
            TimeDepositRow(id=6, planType="basic", days=25, balance=5000.00),
        ]
        s.add_all(deposits)
        s.flush()

        # withdrawals just to populate the relationship (not used in calc)
        withdrawals = [
            WithdrawalRow(timeDepositId=1, amount=250.00, date=date(2025, 1, 15)),
            WithdrawalRow(timeDepositId=1, amount=125.00, date=date(2025, 5, 10)),
            WithdrawalRow(timeDepositId=4, amount=1000.00, date=date(2025, 2, 2)),
        ]
        s.add_all(withdrawals)

        s.commit()
        print("Seeded: {} deposits, {} withdrawals".format(len(deposits), len(withdrawals)))

if __name__ == "__main__":
    reset_and_seed()
