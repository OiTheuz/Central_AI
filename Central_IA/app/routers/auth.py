# ============================================================
# Router de Autenticação — Login do Lojista
# ============================================================

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Merchant
from app.services.auth_service import (
    verificar_senha,
    criar_token_jwt,
    hash_senha,
    get_lojista_atual,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/auth",
    tags=["Autenticação"],
)


# ─── Schemas ─────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    senha: str


class LoginResponse(BaseModel):
    token: str
    lojista: dict


class SetPasswordRequest(BaseModel):
    codigo_loja: str
    email: str
    senha: str


# ─── Rotas ───────────────────────────────────────────────────

@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """
    Autentica o lojista por email + senha.
    Retorna um JWT token + dados básicos do lojista.
    """
    merchant = db.query(Merchant).filter(Merchant.email == body.email).first()

    if not merchant or not merchant.senha_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos.",
        )

    if not verificar_senha(body.senha, merchant.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos.",
        )

    token = criar_token_jwt({
        "merchant_id": merchant.id,
        "schema": merchant.nome_do_schema,
    })

    logger.info("Login bem-sucedido: merchant_id=%s", merchant.id)

    return {
        "token": token,
        "lojista": {
            "id": merchant.id,
            "nome_loja": merchant.nome_loja,
            "codigo_loja": merchant.codigo_loja,
            "nome_do_schema": merchant.nome_do_schema,
            "area_atuacao": merchant.area_atuacao,
            "telefone_contato": merchant.telefone_contato,
        },
    }


@router.get("/me")
def me(merchant: Merchant = Depends(get_lojista_atual)):
    """Retorna dados do lojista autenticado (protegido por JWT)."""
    return {
        "id": merchant.id,
        "nome_loja": merchant.nome_loja,
        "codigo_loja": merchant.codigo_loja,
        "nome_do_schema": merchant.nome_do_schema,
        "area_atuacao": merchant.area_atuacao,
        "telefone_contato": merchant.telefone_contato,
    }


# ─── Definição de senha — protegida por JWT do lojista ───────
# Exige autenticação prévia (lojista já logado via token temporário).
# Para o primeiro acesso, usar o script add_push_token.py ou um
# processo de onboarding administrativo separado.

@router.post("/set-password")
def set_password(
    body: SetPasswordRequest,
    db: Session = Depends(get_db),
    # ⚠️ Rota agora exige JWT válido: somente o próprio lojista
    # (ou um admin com token) pode redefinir a senha.
    merchant_autenticado: Merchant = Depends(get_lojista_atual),
):
    """
    Permite que o lojista autenticado redefina sua própria senha.
    Requer JWT válido — não é mais acessível sem autenticação.
    """
    # Garante que o lojista só possa alterar suas próprias credenciais
    if merchant_autenticado.codigo_loja != body.codigo_loja:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode alterar as credenciais da sua própria conta.",
        )

    # Verificar se email já está em uso por outro merchant
    email_existente = db.query(Merchant).filter(
        Merchant.email == body.email,
        Merchant.id != merchant_autenticado.id,
    ).first()

    if email_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este email já está em uso.",
        )

    merchant_autenticado.email = body.email  # type: ignore[assignment]
    merchant_autenticado.senha_hash = hash_senha(body.senha)  # type: ignore[assignment]
    db.commit()

    logger.info("Credenciais atualizadas para merchant_id=%s", merchant_autenticado.id)
    return {"mensagem": f"Credenciais atualizadas para {merchant_autenticado.nome_loja}!"}
