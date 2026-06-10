import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.models import Merchant
from app.services.auth_service import get_lojista_atual
from app.services.schema_service import criar_novo_estabelecimento

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


class NovoEstabelecimentoRequest(BaseModel):
    schema_nome: str
    tabelas: List[str] = ["appointments", "customers", "services"]  # tabelas padrão de preferências


@router.post("/estabelecimento")
def criar_estabelecimento(
    req: NovoEstabelecimentoRequest,
    admin: Merchant = Depends(get_lojista_atual),
):
    """Cria um novo schema (estabelecimento) e copia as tabelas de preferência.
    As tabelas são criadas vazias. Requer autenticação de administrador.
    """
    if not admin.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Apenas administradores podem criar estabelecimentos.",
        )

    try:
        criar_novo_estabelecimento(req.schema_nome, req.tabelas)
        return {"status": "sucesso", "mensagem": f"Schema '{req.schema_nome}' criado com {len(req.tabelas)} tabelas."}
    except Exception as e:
        logger.error("Erro ao criar estabelecimento: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
