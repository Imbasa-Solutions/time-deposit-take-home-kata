from __future__ import annotations
from typing import List, Tuple
import os

from sqlalchemy import create_engine, Column, Integer, String, Numeric, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship, Session, sessionmaker

from time_deposit import TimeDeposit
from app.application.ports import TimeDepositRepository

#Can point to Postgres for tests. Defaults to local SQLite file for dev
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

Base = declarative_base()

class TimeDepositRow(Base):
    __tablename__ = "timeDeposits"
    id = Column(Integer, primary_key=True)
    planType = Column(String, nullable=False)
    days = Column(Integer, nullable=False)
    balance = Column(Numeric(18, 2), nullable=False)

    withdrawals = relationship(
        "WithdrawalRow",
        back_populates="timeDeposit",
        cascade="all, delete-orphan",
    )

class WithdrawalRow(Base):
    __tablename__ = "withdrawals"
    id = Column(Integer, primary_key=True)
    timeDepositId = Column(Integer, ForeignKey("timeDeposits.id"), nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
    date = Column(Date, nullable=False)

    timeDeposit = relationship("TimeDepositRow", back_populates="withdrawals")

def init_db() -> None:
    """Create tables if they don't exist."""
    Base.metadata.create_all(bind=engine)

class SqlAlchemyTimeDepositRepository(TimeDepositRepository):
    """Adapter implementing the port with SQLAlchemy."""
    def __init__(self, session: Session):
        self.session = session

    def list_all_with_withdrawals(self) -> List[Tuple[TimeDeposit, list]]:
        items: List[Tuple[TimeDeposit, list]] = []
        rows = self.session.query(TimeDepositRow).all()
        for r in rows:
            # Map ORM row to domain object from the original file
            domain = TimeDeposit(
                id=r.id,
                planType=r.planType,
                balance=float(r.balance),
                days=r.days,
            )
            # Spec only says withdrawals must be present. Return an array of {amount, date}
            ws = [
                {"amount": float(w.amount), "date": w.date.isoformat()}
                for w in r.withdrawals
            ]
            items.append((domain, ws))
        return items

    def update_balances(self, items: List[TimeDeposit]) -> int:
        ids = {d.id for d in items}
        if not ids:
            return 0
        rows = (
            self.session
            .query(TimeDepositRow)
            .filter(TimeDepositRow.id.in_(ids))
            .all()
        )
        by_id = {d.id: d for d in items}
        for row in rows:
            row.balance = by_id[row.id].balance
        self.session.commit()
        return len(rows)
