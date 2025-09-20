.PHONY: dev run seed build-index test frontend-test

dev:
docker-compose up --build

run:
uvicorn app.main:app --host 0.0.0.0 --port 8000

seed:
python scripts/seed_db.py

build-index:
python -m app.cli build-index

test:
pytest

frontend-test:
cd frontend && npm install && npm run test
