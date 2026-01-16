from fastapi import FastAPI
from app.adapters.persistence import init_db
from app.adapters.api import router as api_router

# Create tables on startup (SQLite by default; can override DATABASE_URL env var)
init_db()

app = FastAPI(title="Time Deposit API (Python folder)", version="1.0.0")
app.include_router(api_router)
