from sqlalchemy import Column, String, Text
from src.core.database_setup import Base

class Cookies(Base):
    __tablename__ = 'cookies'

    email = Column(String, primary_key=True)
    cookies_data = Column(Text)