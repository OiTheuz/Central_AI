from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from datetime import datetime, timezone

from app.database import Base


class WhatsappMessageLog(Base):
    __tablename__ = "whatsapp_message_log"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey('merchant.id'), nullable=False, index=True)
    recipient = Column(String(50), nullable=False)
    message_type = Column(String(50), nullable=False)  # "service", "utility", "marketing"
    sent_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    cost_estimated = Column(Float, default=0.0, nullable=False)
