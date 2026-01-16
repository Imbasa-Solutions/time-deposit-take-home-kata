from fastapi import FastAPI
from app.adapters.api import router as api_router

app = FastAPI(title="Time Deposit API (Python folder)", version="0.1.0")
app.include_router(api_router)
