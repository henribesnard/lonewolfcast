web: uvicorn app.main:app --host=0.0.0.0 
worker: python -m app.worker.celery_worker
release: alembic upgrade head