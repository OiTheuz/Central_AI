from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class SiteChatLog(Base):
    __tablename__ = "site_chat_log"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False) # Para agrupar as conversas de um mesmo usuário/sessão
    remetente = Column(String, nullable=False) # 'user' ou 'bot'
    mensagem = Column(String, nullable=False)
    
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
