from pydantic import BaseModel
from typing import Optional


class MerchantBase(BaseModel):
    nome_loja: str
    codigo_loja: str
    telefone_contato: Optional[str] = None
    numero_whatsapp: Optional[str] = None
    nome_do_schema: str
    area_atuacao: Optional[str] = None


class MerchantCreate(MerchantBase):
    email: str
    senha: str
    is_admin: bool = False
    tem_dashboard: bool = False


class SubUsuarioCreate(BaseModel):
    """Cria um sub-usuário vinculado a uma loja já existente.
    Não cria um schema novo — herda o da loja pai."""
    nome_loja: str           # Nome/apelido da funcionária (exibido no app)
    email: str
    senha: str
    tem_dashboard: bool = False


class MerchantUpdate(BaseModel):
    """Editar permissões e dados de um lojista ou sub-usuário."""
    tem_dashboard: Optional[bool] = None
    is_admin: Optional[bool] = None
    area_atuacao: Optional[str] = None
    telefone_contato: Optional[str] = None
    numero_whatsapp: Optional[str] = None


class MerchantResponse(MerchantBase):
    id: int
    is_admin: bool
    tem_dashboard: bool
    email: Optional[str] = None
    loja_pai_id: Optional[int] = None

    class Config:
        from_attributes = True
