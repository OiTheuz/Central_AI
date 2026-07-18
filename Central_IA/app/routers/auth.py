# ============================================================
# Router de Autenticação — Login do Lojista
# ============================================================

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_public_db
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
    must_change_password: bool = False


class SetPasswordRequest(BaseModel):
    codigo_loja: str
    email: str
    senha: str


class ChangePasswordRequest(BaseModel):
    nova_senha: str


class ImpersonateRequest(BaseModel):
    target_merchant_id: int


# ─── Rotas ───────────────────────────────────────────────────

@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_public_db)):
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

    # Se é sub-usuário, buscar o schema da loja pai
    schema = merchant.nome_do_schema
    if merchant.loja_pai_id:
        loja_pai = db.query(Merchant).filter(Merchant.id == merchant.loja_pai_id).first()
        if loja_pai:
            schema = loja_pai.nome_do_schema

    token = criar_token_jwt({
        "merchant_id": merchant.id,
        "schema": schema,
    })

    logger.info("Login bem-sucedido: merchant_id=%s", merchant.id)

    # Para sub-usuários, exibir o nome do estabelecimento pai no card
    nome_loja_exibicao = merchant.nome_loja
    if merchant.loja_pai_id:
        loja_pai_exib = db.query(Merchant).filter(Merchant.id == merchant.loja_pai_id).first()
        if loja_pai_exib:
            nome_loja_exibicao = loja_pai_exib.nome_loja

    return {
        "token": token,
        "lojista": {
            "id": merchant.id,
            "nome_usuario": merchant.nome_usuario,
            "nome_loja": nome_loja_exibicao,
            "codigo_loja": merchant.codigo_loja,
            "nome_do_schema": schema,
            "area_atuacao": merchant.area_atuacao,
            "telefone_contato": merchant.telefone_contato,
            "is_admin": merchant.is_admin,
            "tem_dashboard": getattr(merchant, 'tem_dashboard', False),
            "pode_editar_servicos": getattr(merchant, 'pode_editar_servicos', True),
            "politica_aceita": getattr(merchant, 'politica_aceita', False),
            "loja_pai_id": merchant.loja_pai_id,
            "foto_perfil": getattr(merchant, 'foto_perfil', None),
        },
        "must_change_password": getattr(merchant, 'deve_trocar_senha', False)
    }



@router.get("/me")
def me(
    merchant: Merchant = Depends(get_lojista_atual),
    db: Session = Depends(get_public_db)
):
    """Retorna dados do lojista autenticado (protegido por JWT)."""
    nome_estabelecimento = merchant.nome_loja
    if getattr(merchant, "loja_pai_id", None):
        parent = db.query(Merchant).filter(Merchant.id == merchant.loja_pai_id).first()
        if parent:
            nome_estabelecimento = parent.nome_loja

    return {
        "id": merchant.id,
        "nome_usuario": merchant.nome_usuario,
        "nome_loja": nome_estabelecimento,
        "codigo_loja": merchant.codigo_loja,
        "nome_do_schema": merchant.nome_do_schema,
        "area_atuacao": merchant.area_atuacao,
        "telefone_contato": merchant.telefone_contato,
        "is_admin": merchant.is_admin,
        "tem_dashboard": getattr(merchant, 'tem_dashboard', False),
        "pode_editar_servicos": getattr(merchant, 'pode_editar_servicos', True),
        "politica_aceita": getattr(merchant, 'politica_aceita', False),
        "foto_perfil": getattr(merchant, 'foto_perfil', None),
        "notificacoes_push_enabled": getattr(merchant, 'notificacoes_push_enabled', True),
        "notificacoes_novos": getattr(merchant, 'notificacoes_novos', True),
        "notificacoes_cancelamentos": getattr(merchant, 'notificacoes_cancelamentos', True),
        "notificacoes_lembretes": getattr(merchant, 'notificacoes_lembretes', True),
    }


@router.post("/aceitar-politica")
def aceitar_politica(
    merchant: Merchant = Depends(get_lojista_atual),
    db: Session = Depends(get_public_db)
):
    """Marca a política de privacidade como aceita para o lojista."""
    merchant.politica_aceita = True # type: ignore[assignment]
    db.commit()
    return {"status": "sucesso", "mensagem": "Política de privacidade aceita."}


@router.post("/change-password")
def change_password(
    body: ChangePasswordRequest,
    merchant: Merchant = Depends(get_lojista_atual),
    db: Session = Depends(get_public_db)
):
    """Permite ao usuário logado alterar sua própria senha."""
    merchant.senha_hash = hash_senha(body.nova_senha)  # type: ignore[assignment]
    db.commit()
    return {"status": "sucesso", "mensagem": "Senha alterada com sucesso!"}

class UpdateMetaTokenRequest(BaseModel):
    meta_access_token: str
    meta_phone_id: str

@router.post("/update-meta-token")
def update_meta_token(
    body: UpdateMetaTokenRequest,
    merchant: Merchant = Depends(get_lojista_atual),
    db: Session = Depends(get_public_db)
):
    """Atualiza as credenciais do WhatsApp Oficial (Token e Phone ID)."""
    merchant.meta_access_token = body.meta_access_token
    merchant.meta_phone_id = body.meta_phone_id
    db.commit()
    return {"status": "sucesso", "mensagem": "WhatsApp conectado com sucesso!"}



# ─── Definição de senha — protegida por JWT do lojista ───────
# Exige autenticação prévia (lojista já logado via token temporário).
# Para o primeiro acesso, usar o script add_push_token.py ou um
# processo de onboarding administrativo separado.

@router.post("/trocar-senha")
def trocar_senha_obrigatoria(body: ChangePasswordRequest, db: Session = Depends(get_public_db), merchant: Merchant = Depends(get_lojista_atual)):
    """
    Permite a troca da senha provisória logo no primeiro login.
    """
    if not body.nova_senha or len(body.nova_senha) < 6:
        raise HTTPException(status_code=400, detail="Senha deve ter no mínimo 6 caracteres.")
        
    merchant.senha_hash = hash_senha(body.nova_senha)
    merchant.deve_trocar_senha = False
    db.commit()
    
    return {"status": "sucesso", "mensagem": "Senha alterada com sucesso!"}

@router.post("/set-password")
def set_password(
    body: SetPasswordRequest,
    db: Session = Depends(get_public_db),
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


# ─── ADMIN: Troca de Loja ────────────────────────────────────

class AdminSwitchRequest(BaseModel):
    codigo_loja: str

@router.get("/admin/stores")
def admin_list_stores(
    merchant_autenticado: Merchant = Depends(get_lojista_atual),
    db: Session = Depends(get_public_db),
):
    """
    Retorna a lista de todas as lojas disponíveis.
    Apenas para usuários com is_admin = True.
    """
    if not merchant_autenticado.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem listar lojas.",
        )
    
    lojas = db.query(Merchant).filter(Merchant.loja_pai_id.is_(None)).all()
    return [{
        "id": l.id,
        "nome_loja": l.nome_loja,
        "codigo_loja": l.codigo_loja,
        "nome_do_schema": l.nome_do_schema,
    } for l in lojas]

@router.post("/admin/switch", response_model=LoginResponse)
def admin_switch_store(
    body: AdminSwitchRequest,
    merchant_autenticado: Merchant = Depends(get_lojista_atual),
    db: Session = Depends(get_public_db),
):
    """
    Permite que um administrador troque de loja sem precisar da senha.
    Retorna um novo JWT token com o schema da loja solicitada.
    """
    if not merchant_autenticado.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem trocar de loja.",
        )
    
    # Buscar a loja solicitada
    nova_loja = db.query(Merchant).filter(Merchant.codigo_loja == body.codigo_loja).first()
    if not nova_loja:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loja não encontrada.",
        )
    
    admin_id = getattr(merchant_autenticado, "admin_original_id", merchant_autenticado.id)
    admin_schema = getattr(merchant_autenticado, "admin_original_schema", merchant_autenticado.nome_do_schema)
    
    token = criar_token_jwt({
        "merchant_id": admin_id,
        "schema": admin_schema,
        "acting_as": nova_loja.codigo_loja,
    })

    return {
        "token": token,
        "lojista": {
            "id": admin_id, # Keep original ID
            "nome_usuario": getattr(merchant_autenticado, "nome_usuario", "Admin"),
            "nome_loja": nova_loja.nome_loja,
            "codigo_loja": nova_loja.codigo_loja,
            "nome_do_schema": nova_loja.nome_do_schema,
            "area_atuacao": nova_loja.area_atuacao,
            "telefone_contato": nova_loja.telefone_contato,
            "is_admin": True,
            "tem_dashboard": True, # Admins always have dashboard
            "pode_editar_servicos": True, # Admins always can edit services
        }
    }

@router.get("/update-admin-email")
def update_admin_email(db: Session = Depends(get_public_db)):
    from sqlalchemy import text
    db.execute(text("UPDATE merchant SET email = 'admin' WHERE email = 'admin@lautz.tech'"))
    db.commit()
    return {"status": "ok"}

@router.post("/impersonate", response_model=LoginResponse)
def impersonate(
    body: ImpersonateRequest,
    db: Session = Depends(get_public_db),
    admin: Merchant = Depends(get_lojista_atual)
):
    """
    Permite que um administrador obtenha um token JWT como se fosse outro lojista.
    """
    if not admin.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem acessar outras lojas.",
        )
    
    merchant = db.query(Merchant).filter(Merchant.id == body.target_merchant_id).first()
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lojista não encontrado.",
        )

    schema = merchant.nome_do_schema
    if merchant.loja_pai_id:
        loja_pai = db.query(Merchant).filter(Merchant.id == merchant.loja_pai_id).first()
        if loja_pai:
            schema = loja_pai.nome_do_schema

    token = criar_token_jwt({
        "merchant_id": merchant.id,
        "schema": schema,
    })

    logger.info("Admin %s (%s) entrou na loja %s (%s)", admin.id, admin.email, merchant.id, merchant.nome_loja)

    nome_loja_exibicao = merchant.nome_loja
    if merchant.loja_pai_id:
        loja_pai_exib = db.query(Merchant).filter(Merchant.id == merchant.loja_pai_id).first()
        if loja_pai_exib:
            nome_loja_exibicao = loja_pai_exib.nome_loja

    return {
        "token": token,
        "lojista": {
            "id": merchant.id,
            "nome_usuario": merchant.nome_usuario,
            "nome_loja": nome_loja_exibicao,
            "codigo_loja": merchant.codigo_loja,
            "nome_do_schema": schema,
            "area_atuacao": merchant.area_atuacao,
            "telefone_contato": merchant.telefone_contato,
            "is_admin": merchant.is_admin,
            "tem_dashboard": getattr(merchant, 'tem_dashboard', False),
            "pode_editar_servicos": getattr(merchant, 'pode_editar_servicos', True),
            "politica_aceita": getattr(merchant, 'politica_aceita', False),
            "loja_pai_id": merchant.loja_pai_id,
            "foto_perfil": getattr(merchant, 'foto_perfil', None),
        },
    }
