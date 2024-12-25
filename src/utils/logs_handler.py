import logging
from sqlalchemy import create_engine

from src.db.models.log_models import LogEntry
from sqlalchemy.orm import sessionmaker
from src.core.config import SYNC_DATABASE_URL, EXTERNAL_LIBRARY_LEVEL_LOG, LOG_LEVEL


sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)
SyncSessionLocal = sessionmaker(bind=sync_engine)


class SyncDatabaseHandler(logging.Handler):
    def emit(self, record):
        if self.is_external_library(record) and record.levelno >= logging.getLevelName(EXTERNAL_LIBRARY_LEVEL_LOG):
            log_entry = self.format(record)
            add_log_to_db_sync(record.levelname, log_entry, record.name)
        elif not self.is_external_library(record):
            log_entry = self.format(record)
            add_log_to_db_sync(record.levelname, log_entry, record.name)

    def is_external_library(self, record) -> bool:
        return not record.name.startswith('src.')

def add_log_to_db_sync(log_level: str, message: str, source: str):
    # Create a new session for each log entry
    session = SyncSessionLocal()
    try:
        log_entry = LogEntry(log_level=log_level, message=message, source=source)
        session.add(log_entry)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()  # Close the session to avoid leakage

def setup_logging():
    db_handler = SyncDatabaseHandler()
    logging.getLogger().addHandler(db_handler)
    logging.getLogger().setLevel(logging.getLevelName(LOG_LEVEL))
    logging.getLogger().info("Application started")

