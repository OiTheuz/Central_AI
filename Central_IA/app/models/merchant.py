from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text

from app.database import Base


class Merchant(Base):
    __tablename__ = "merchant"

    id = Column(Integer, primary_key=True, index=True)
    nome_loja = Column(String(255), nullable=False)  # not unique: sub-users share the store name
    nome_usuario = Column(String(255), nullable=True)
    codigo_loja = Column(String(50), unique=True, index=True)
    telefone_contato = Column(String(50))
    numero_whatsapp = Column(String(20), nullable=True)  # not unique: sub-users share None
    numero_chefe = Column(String(20), nullable=True)     # boss/assistant number
    nome_chefe = Column(String(100), nullable=True)      # boss/assistant name
    nome_do_schema = Column(String(50), unique=True, nullable=False)
    area_atuacao = Column(String(100))
    foto_perfil = Column(String(500), nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False, server_default="false")
    tem_dashboard = Column(Boolean, default=False, nullable=False, server_default="false")
    pode_editar_servicos = Column(Boolean, default=True, nullable=False, server_default="true")
    loja_pai_id = Column(Integer, ForeignKey('merchant.id'), nullable=True)

    # Marketing e Onboarding
    cupom_usado = Column(String(50), nullable=True)
    como_conheceu = Column(String(100), nullable=True)

    # Assinatura SaaS (Asaas)
    asaas_customer_id = Column(String(255), nullable=True)
    asaas_subscription_id = Column(String(255), nullable=True)
    status_assinatura = Column(String(50), default="ativo", nullable=False, server_default="ativo")
    data_vencimento = Column(String(50), nullable=True) # ou DateTime

    # Autenticação (login do lojista no app)
    email = Column(String(255), unique=True, nullable=True)
    senha_hash = Column(String(255), nullable=True)
    deve_trocar_senha = Column(Boolean, default=False, nullable=False, server_default="false")
    
    # Notificações Push
    push_token = Column(String(255), nullable=True)
    notificacoes_push_enabled = Column(Boolean, default=True, nullable=False, server_default="true")
    notificacoes_novos = Column(Boolean, default=True, nullable=False, server_default="true")
    notificacoes_cancelamentos = Column(Boolean, default=True, nullable=False, server_default="true")
    notificacoes_lembretes = Column(Boolean, default=True, nullable=False, server_default="true")

    # Configurações de agendamento
    permitir_sobreposicao = Column(Boolean, default=False, nullable=False, server_default="false")
    horario_abertura = Column(String(5), default="08:00", nullable=False, server_default="08:00")
    horario_fechamento = Column(String(5), default="18:00", nullable=False, server_default="18:00")
    
    # Comportamento da IA
    instrucoes_ia = Column(Text, nullable=True)
    
    # Bloqueios e Almoço
    dias_fechados = Column(String(50), nullable=True)  # "0,6" onde 0=Segunda, 6=Domingo
    horario_almoco_inicio = Column(String(5), nullable=True)
    horario_almoco_fim = Column(String(5), nullable=True)

    # Termos e Política
    politica_aceita = Column(Boolean, default=False, nullable=False, server_default="false")

    # Credenciais WhatsApp Business (por lojista — fallback para .env se NULL)
    meta_access_token = Column(String(500), nullable=True)
    meta_phone_id = Column(String(50), nullable=True)
