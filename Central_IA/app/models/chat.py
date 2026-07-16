from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from datetime import datetime, timezone

from app.database import Base


class ClientChatState(Base):
    __tablename__ = "client_chat_state"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey('merchant.id'), nullable=False, index=True)
    client_phone = Column(String(50), nullable=False, index=True)
    client_name = Column(String(255), nullable=True)
    is_human_service = Column(Boolean, default=False, nullable=False, server_default="false")
    human_service_started_at = Column(DateTime(timezone=True), nullable=True)


class ChatMessage(Base):
    __tablename__ = "chat_message"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey('merchant.id'), nullable=False, index=True)
    client_phone = Column(String(50), nullable=False, index=True)
    message_content = Column(String(2000), nullable=False)
    sender = Column(String(50), nullable=False) # 'client' ou 'merchant'
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    read = Column(Boolean, default=False, nullable=False, server_default="false")
