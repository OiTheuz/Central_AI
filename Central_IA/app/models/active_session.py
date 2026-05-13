from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database import Base


class ActiveSession(Base):
    __tablename__ = "active_sessions"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    telefone_cliente = Column(String, unique=True, nullable=False)
    loja_atual = Column(String, nullable=False)
    ultima_interacao = Column(DateTime, server_default=func.now(), onupdate=func.now())
