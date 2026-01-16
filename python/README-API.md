# Time Deposit API (Python subfolder)

This commit is just the scaffold (no endpoints yet).

## Run (from this `python/` folder)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# Swagger UI: http://127.0.0.1:8000/docs (empty for now)
```
