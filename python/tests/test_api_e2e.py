import os
import importlib
from datetime import date
from testcontainers.postgres import PostgresContainer
from fastapi.testclient import TestClient


def test_endpoints_e2e():
    # Start Postgres in Docker
    with PostgresContainer("postgres:16-alpine") as pg:
        # Point app at container DB (SQLAlchemy needs +psycopg2)
        url = pg.get_connection_url().replace("postgresql://", "postgresql+psycopg2://")
        os.environ["DATABASE_URL"] = url

        # Import (or reload) persistence AFTER setting DATABASE_URL so the engine binds correctly
        from app.adapters import persistence as p
        importlib.reload(p)
        p.init_db()

        # Seed minimal data directly via SQLAlchemy session
        with p.SessionLocal() as s:
            s.query(p.WithdrawalRow).delete()
            s.query(p.TimeDepositRow).delete()
            s.add_all([
                p.TimeDepositRow(id=1, planType="basic", days=45, balance=1000.00),
                p.TimeDepositRow(id=2, planType="premium", days=46, balance=5000.00),
            ])
            s.add_all([
                p.WithdrawalRow(timeDepositId=1, amount=50.0, date=date(2025, 1, 1)),
            ])
            s.commit()

        # Import app AFTER persistence so startup uses the right DB
        from app import main as app_main
        importlib.reload(app_main)
        client = TestClient(app_main.app)

        # GET before update
        r = client.get("/time-deposits")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 2
        d1 = next(x for x in data if x["id"] == 1)
        d2 = next(x for x in data if x["id"] == 2)
        assert d1["withdrawals"] and d1["withdrawals"][0]["amount"] == 50.0

        # POST update-balances
        r = client.post("/time-deposits/update-balances")
        assert r.status_code == 200
        assert r.json()["updated"] == 2

        # GET after update – verify interest rules applied & rounded to 2dp
        r = client.get("/time-deposits")
        data = r.json()
        d1 = next(x for x in data if x["id"] == 1)  # basic 1%/12 since > 30 days
        d2 = next(x for x in data if x["id"] == 2)  # premium 5%/12 since > 45 days

        assert d1["balance"] == 1000.83  # 1000 + (1000*0.01)/12 = 1000.8333 -> 1000.83
        assert d2["balance"] == 5020.83  # 5000 + (5000*0.05)/12 = 20.8333 -> 5020.83
