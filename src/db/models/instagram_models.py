from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from src.core.database_setup import Base

class InstagramApp(Base):
    __tablename__ = "instagram_app"

    id = Column(Integer, primary_key=True, default=1, unique=True)  # Single row
    inst_app_id = Column(String(255))
    inst_app_secret = Column(String(255))
    webhook_callback_url = Column(String(255))
    webhook_verify_token = Column(String(255))
    handle_code_url = Column(String(255))
    embed_url = Column(String(800))


class InstagramUser(Base):
    __tablename__ = "instagram_users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False)
    access_token = Column(Text, nullable=False)
    username = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)


