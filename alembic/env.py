import os
from logging.config import fileConfig
from sqlalchemy import pool, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from alembic import context
from app.models.base import Base
from app.core.config import settings
from app.core.settings import DEFAULT_ENGINE_KWARGS
import ssl

from app.models import (
    League, Match, OddsBookmaker, OddsValue, 
    Prediction, SelectedPrediction, BankrollHistory,
    BankrollTransaction, H2HMatch, PredictionTeam, api_usage
)

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata

ssl_context = None
if hasattr(settings, 'DATABASE_SSL_REQUIRED') and settings.DATABASE_SSL_REQUIRED:
    ssl_context = settings.get_ssl_context()

def run_migrations_offline() -> None:
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable: AsyncEngine = create_async_engine(
        settings.ASYNC_DATABASE_URL,
        **DEFAULT_ENGINE_KWARGS,
        connect_args={"ssl": ssl_context} if ssl_context else {},
    )
    async def do_migrations():
        async with connectable.connect() as connection:
            await connection.run_sync(
                lambda sync_connection: context.configure(
                    connection=sync_connection, target_metadata=target_metadata, render_as_batch=True
                )
            )
            async with connection.begin():
                await connection.run_sync(lambda sync_connection: context.run_migrations())
    import asyncio
    asyncio.run(do_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()