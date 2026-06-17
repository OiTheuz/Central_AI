from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

from app.database import Base


class Merchant(Base):
    __tablename__ = "merchant"

    id = Column(Integer, primary_key=True, index=True)
    nome_loja = Column(String(255), unique=True, nullable=False)
    codigo_loja = Column(String(50), unique=True, index=True)
    telefone_contato = Column(String(50))
    numero_whatsapp = Column(String(20), unique=True)
    nome_do_schema = Column(String(50), unique=True, nullable=False)
    area_atuacao = Column(String(100))
    is_admin = Column(Boolean, default=False, nullable=False, server_default="false")
    tem_dashboard = Column(Boolean, default=False, nullable=False, server_default="false")
    loja_pai_id = Column(Integer, ForeignKey('merchant.id'), nullable=True)


    # Autenticação (login do lojista no app)
    email = Column(String(255), unique=True, nullable=True)
    senha_hash = Column(String(255), nullable=True)
    
    # Notificações Push
    push_token = Column(String(255), nullable=True)

    # Configurações de agendamento
    permitir_sobreposicao = Column(Boolean, default=False, nullable=False, server_default="false")
    horario_abertura = Column(String(5), default="08:00", nullable=False, server_default="08:00")
    horario_fechamento = Column(String(5), default="18:00", nullable=False, server_default="18:00")

