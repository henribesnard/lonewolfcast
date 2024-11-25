from app.core.config import settings

DEFAULT_ENGINE_KWARGS = settings.engine_kwargs
DATABASE_SSL_REQUIRED = settings.DB_SSL_MODE == "require"