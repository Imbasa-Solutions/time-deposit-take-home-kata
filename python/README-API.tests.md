# Tests (optional but recommended)

These end-to-end tests use **Testcontainers** to start a Postgres DB in Docker, bind the app to it, seed rows, and hit both endpoints via FastAPI TestClient.

## Prereqs
- Docker running locally
- Python venv activated
- `pip install -r requirements.txt`

## Run
```bash
cd python
pytest -q tests/test_api_e2e.py
```

The test will:
1. Start Postgres 16 in Docker.
2. Set `DATABASE_URL` for SQLAlchemy.
3. Create tables, seed data.
4. Call **GET `/time-deposits`** and **POST `/time-deposits/update-balances`**.
5. Assert balances changed according to the business rules.
