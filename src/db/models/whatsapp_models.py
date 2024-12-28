from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, BigInteger
from sqlalchemy.orm import relationship, declarative_base
from src.core.database_setup import Base


class WhatsAppUser(Base):
    __tablename__ = 'whatsapp_users'

    id = Column(Integer, primary_key=True, index=True)
    api_url = Column(String, nullable=False)
    id_instance = Column(BigInteger, nullable=False, unique=True)
    api_token = Column(String, nullable=False)
    callback_url = Column(String, nullable=False)
    phone_number = Column(String, nullable=True, unique=True)
    order_id = Column(String, nullable=False)
    bot_id = Column(String, nullable=True, unique=True)

