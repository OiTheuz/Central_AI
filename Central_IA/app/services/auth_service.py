# ============================================================
# Serviço de Autenticação — JWT + Hashing de Senha
# ============================================================

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRA_HORAS
from app.database import get_public_db
from app.models import Merchant

import bcrypt

def hash_senha(senha: str) -> str:
    """Gera o hash bcrypt de uma senha em texto puro."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(senha.encode('utf-8'), salt).decode('utf-8')

def verificar_senha(senha_pura: str, senha_hash: str) -> bool:
    """Compara senha em texto puro com o hash armazenado."""
    try:
        return bcrypt.checkpw(senha_pura.encode('utf-8'), senha_hash.encode('utf-8'))
    except (ValueError, TypeError):
        return False


# ─── JWT ─────────────────────────────────────────────────────

def criar_token_jwt(data: dict) -> str:
    """Cria um token JWT com expiração configurável."""
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRA_HORAS)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decodificar_token_jwt(token: str) -> dict:
    """Decodifica e valida um token JWT. Levanta exceção se inválido."""
    try:
        return dict(jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM]))
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
        )


# ─── Dependency — Obter lojista autenticado ──────────────────

security = HTTPBearer()


def get_lojista_atual(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_public_db),
) -> Merchant:
    """
    Dependency do FastAPI: extrai o Bearer token, decodifica o JWT,
    e retorna o Merchant correspondente.
    Todas as rotas protegidas devem usar Depends(get_lojista_atual).
    """
    payload = decodificar_token_jwt(credentials.credentials)
    merchant_id = payload.get("merchant_id")

    if merchant_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não contém merchant_id.",
        )

    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()

    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lojista não encontrado.",
        )

    acting_as = payload.get("acting_as")
    if merchant.is_admin and acting_as and acting_as != merchant.codigo_loja:
        target_merchant = db.query(Merchant).filter(Merchant.codigo_loja == acting_as).first()
        if target_merchant:
            # Detach from session to prevent accidental commits of these changes
            db.expunge(merchant)
            merchant.codigo_loja = target_merchant.codigo_loja
            merchant.nome_do_schema = target_merchant.nome_do_schema
            merchant.nome_loja = target_merchant.nome_loja
            merchant.area_atuacao = target_merchant.area_atuacao
            merchant.telefone_contato = target_merchant.telefone_contato
    elif merchant.loja_pai_id:
        schema = payload.get("schema")
        print(f"!!! DEBUG AUTH: schema do token={schema}, merchant.loja_pai_id={merchant.loja_pai_id}", flush=True)
        # Fallback para tokens antigos que não possuem o schema ou possuem schema "sub_..."
        if not schema or schema.startswith("sub_"):
            loja_pai = db.query(Merchant).filter(Merchant.id == merchant.loja_pai_id).first()
            if loja_pai:
                schema = loja_pai.nome_do_schema
                print(f"!!! DEBUG AUTH: Fallback executado. Novo schema={schema}", flush=True)
        
        print(f"!!! DEBUG AUTH: comparando schema={schema} com merchant={merchant.nome_do_schema}", flush=True)
        if schema and schema != merchant.nome_do_schema:
            db.expunge(merchant)
            merchant.nome_do_schema = schema
            print(f"!!! DEBUG AUTH: expunged! merchant agora tem schema={merchant.nome_do_schema}", flush=True)

    return merchant
