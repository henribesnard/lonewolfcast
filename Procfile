web: uvicorn app.main:app --host=0.0.0.0 --port=$PORT --ssl-keyfile=None --ssl-certfile=None
worker: python -m app.worker.celery_worker
release: alembic upgrade head