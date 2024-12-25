from sqlalchemy import Column, Integer, String, Float, Boolean, create_engine, ForeignKey
from src.core.database_setup import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    paid_amount = Column(Float, default=0)  # Amount user paid
    remaining_tokens = Column(Integer, default=0)  # Tokens user can use
