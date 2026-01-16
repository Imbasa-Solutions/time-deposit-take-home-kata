# Seeding data (dev only)

This adds a small dataset to exercise the rules

```bash
# from python/
source .venv/bin/activate
export DATABASE_URL="sqlite:///./app.db" 
python -m seed.seed_data
```

Then open Swagger and test:
- GET  /time-deposits
- POST /time-deposits/update-balances
