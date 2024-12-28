from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from datetime import datetime

from src.core.database_setup import Base

class LogEntry(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)
    log_level = Column(String(10))
    source = Column(String(255))
    message = Column(Text)
