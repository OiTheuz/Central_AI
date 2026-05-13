from pydantic import BaseModel
from datetime import datetime


# NOVOS SCHEMAS PARA AGENDAMENTO
class AgendamentoCreate(BaseModel):
    codigo_loja: str  # Fundamental para a API saber em qual gaveta guardar!
    cliente_nome: str
    cliente_whatsapp: str
    data_horario: datetime
    servico: str
