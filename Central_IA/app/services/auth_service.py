# ============================================================
# Serviço de Autenticação — JWT + Hashing de Senha
# ============================================================

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRA_HORAS
from app.database import get_db
from app.models import Merchant

# ─── Hashing de Senha ────────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_senha(senha: str) -> str:
    """Gera o hash bcrypt de uma senha em texto puro."""
    return pwd_context.hash(senha)


def verificar_senha(senha_pura: str, senha_hash: str) -> bool:
    """Compara senha em texto puro com o hash armazenado."""
    return pwd_context.verify(senha_pura, senha_hash)


# ─── JWT ─────────────────────────────────────────────────────

def criar_token_jwt(data: dict) -> str:
    """Cria um token JWT com expiração configurável."""
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRA_HORAS)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decodificar_token_jwt(token: str) -> dict:
    """Decodifica e valida um token JWT. Levanta exceção se inválido."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
        )


# ─── Dependency — Obter lojista autenticado ──────────────────

security = HTTPBearer()


def get_lojista_atual(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
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

    return merchant
