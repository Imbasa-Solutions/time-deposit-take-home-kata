from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.adapters.persistence import SqlAlchemyTimeDepositRepository, SessionLocal
from app.application.services import UpdateBalancesService

router = APIRouter()

class WithdrawalOut(BaseModel):
    amount: float
    date: str

class TimeDepositOut(BaseModel):
    id: int
    planType: str
    balance: float
    days: int
    withdrawals: List[WithdrawalOut] = Field(default_factory=list)

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/time-deposits", response_model=List[TimeDepositOut])
def list_time_deposits(session: Session = Depends(get_session)):
    repo = SqlAlchemyTimeDepositRepository(session)
    rows = repo.list_all_with_withdrawals()
    return [
        TimeDepositOut(
            id=d.id, planType=d.planType, balance=d.balance, days=d.days,
            withdrawals=[WithdrawalOut(**w) for w in ws]
        )
        for (d, ws) in rows
    ]

@router.post("/time-deposits/update-balances")
def update_all_time_deposits(session: Session = Depends(get_session)):
    repo = SqlAlchemyTimeDepositRepository(session)
    svc = UpdateBalancesService(repo)
    updated = svc.run()
    return {"updated": updated}
