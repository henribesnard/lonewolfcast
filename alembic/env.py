import os
import sys
from logging.config import fileConfig
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Créer le dossier data
data_dir = root_dir / "data"
data_dir.mkdir(exist_ok=True)

# Import des modèles
from app.models.base import Base
from app.models.league import League, Season
from app.models.match import Match
from app.models.odds import OddsBookmaker, OddsValue
from app.models.prediction import Prediction, SelectedPrediction
from app.models.team_prediction import PredictionTeam
from app.models.h2h import H2HMatch

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# target metadata
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = "sqlite:///data/football.db"
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={"check_same_thread": False}
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()