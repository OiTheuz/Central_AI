from pydantic import BaseModel
from typing import Optional


class MerchantBase(BaseModel):
    nome_loja: str
    nome_usuario: Optional[str] = None
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
    pode_editar_servicos: bool = True


class SubUsuarioCreate(BaseModel):
    """Cria um sub-usuário vinculado a uma loja já existente.
    Não cria um schema novo — herda o da loja pai."""
    nome_loja: str           # Nome/apelido da funcionária (exibido no app se nome_usuario estiver vazio)
    nome_usuario: Optional[str] = None
    email: str
    senha: str
    tem_dashboard: bool = False
    pode_editar_servicos: bool = True


class MerchantUpdate(BaseModel):
    """Editar permissões e dados de um lojista ou sub-usuário."""
    nome_loja: Optional[str] = None
    nome_usuario: Optional[str] = None
    email: Optional[str] = None
    senha: Optional[str] = None
    tem_dashboard: Optional[bool] = None
    is_admin: Optional[bool] = None
    area_atuacao: Optional[str] = None
    pode_editar_servicos: Optional[bool] = None
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
