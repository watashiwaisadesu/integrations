from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.core.database_setup import Base


class TelegramApp(Base):
    __tablename__ = 'telegram_app'

    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(String, unique=True, nullable=False)
    api_hash = Column(String, nullable=False)
    users = relationship(
        "TelegramUser",
        back_populates="app",
        passive_deletes=True,
        cascade="all, delete-orphan"
    )


class TelegramUser(Base):
    __tablename__ = 'telegram_users'

    id = Column(Integer, primary_key=True, index=True)
    session = Column(String, nullable=True)  # Will be None until logged in
    phone_number = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=True)
    user_id = Column(String, nullable=True)
    phone_code_hash = Column(String, nullable=True)  # New column for code hash storage
    bot_id = Column(String, nullable=True)

    app_id = Column(Integer, ForeignKey('telegram_app.id', ondelete='CASCADE'), nullable=True)
    app = relationship("TelegramApp", back_populates="users")

