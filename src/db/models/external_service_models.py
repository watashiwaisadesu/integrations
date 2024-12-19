from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from src.core.database_setup import Base

class ExternalServiceApp(Base):
    __tablename__ = "external_service_app"

    id = Column(Integer, primary_key=True, autoincrement=True)
    external_service_base_url = Column(String(255))