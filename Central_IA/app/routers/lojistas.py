import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_public_db, validar_schema
from app.models import Merchant
from app.schemas import MerchantCreate, MerchantResponse
from app.schemas.merchant import MerchantUpdate, SubUsuarioCreate
from app.services.auth_service import get_lojista_atual, hash_senha
from app.services.schema_service import criar_novo_estabelecimento

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Lojistas"])

# =========================================================
# CRIAR LOJISTA PRINCIPAL (admin mestre apenas)

@router.post("/lojistas/", response_model=MerchantResponse)
def criar_lojista(
    merchant: MerchantCreate,
    db: Session = Depends(get_public_db),
    admin: Merchant = Depends(get_lojista_atual),
):
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem criar lojistas.")

    db_merchant = db.query(Merchant).filter(
        (Merchant.codigo_loja == merchant.codigo_loja) |
        (Merchant.nome_do_schema == merchant.nome_do_schema) |
        (Merchant.email == merchant.email)
    ).first()

    if db_merchant:
        raise HTTPException(status_code=400, detail="Lojista, Schema ou E-mail já existe.")

    dados = merchant.model_dump(exclude={"senha"})
    dados["senha_hash"] = hash_senha(merchant.senha)

    novo_lojista = Merchant(**dados)
    db.add(novo_lojista)
    db.commit()
    db.refresh(novo_lojista)

    try:
        schema_nome = validar_schema(merchant.nome_do_schema)
        criar_novo_estabelecimento(schema_nome, ["appointments", "customers", "services"])
        logger.info("Schema %s criado para lojista %s", schema_nome, merchant.nome_loja)
    except ValueError as e:
        logger.error("Nome do schema inválido: %s", e)
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("Schema pode já existir ou erro não fatal: %s", e)

    return novo_lojista

# =========================================================
# LISTAR LOJISTAS PRINCIPAIS (admin mestre apenas)

@router.get("/lojistas/", response_model=list[MerchantResponse])
def listar_lojistas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_public_db),
    admin: Merchant = Depends(get_lojista_atual),
):
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem listar lojistas.")

    # Retorna apenas lojistas principais (sem loja_pai_id)
    lojistas = db.query(Merchant)\
        .filter(Merchant.loja_pai_id == None)\
        .offset(skip)\
        .limit(limit)\
        .all()

    return lojistas

# =========================================================
# EDITAR LOJISTA OU SUB-USUÁRIO (admin mestre apenas)

@router.patch("/lojistas/{lojista_id}", response_model=MerchantResponse)
def editar_lojista(
    lojista_id: int,
    dados: MerchantUpdate,
    db: Session = Depends(get_public_db),
    admin: Merchant = Depends(get_lojista_atual),
):
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem editar lojistas.")

    lojista = db.query(Merchant).filter(Merchant.id == lojista_id).first()
    if not lojista:
        raise HTTPException(status_code=404, detail="Lojista não encontrado.")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(lojista, campo, valor)

    db.commit()
    db.refresh(lojista)
    logger.info("Lojista %s atualizado pelo admin %s", lojista_id, admin.id)
    return lojista

# =========================================================
# LISTAR SUB-USUÁRIOS DE UMA LOJA (admin mestre apenas)

@router.get("/lojistas/{lojista_id}/usuarios", response_model=list[MerchantResponse])
def listar_sub_usuarios(
    lojista_id: int,
    db: Session = Depends(get_public_db),
    admin: Merchant = Depends(get_lojista_atual),
):
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem listar sub-usuários.")

    loja = db.query(Merchant).filter(Merchant.id == lojista_id).first()
    if not loja:
        raise HTTPException(status_code=404, detail="Loja não encontrada.")

    usuarios = db.query(Merchant)\
        .filter(Merchant.loja_pai_id == lojista_id)\
        .all()

    return usuarios

# =========================================================
# CRIAR SUB-USUÁRIO PARA UMA LOJA (admin mestre apenas)

@router.post("/lojistas/{lojista_id}/usuarios", response_model=MerchantResponse)
def criar_sub_usuario(
    lojista_id: int,
    dados: SubUsuarioCreate,
    db: Session = Depends(get_public_db),
    admin: Merchant = Depends(get_lojista_atual),
):
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem criar sub-usuários.")

    loja_pai = db.query(Merchant).filter(Merchant.id == lojista_id).first()
    if not loja_pai:
        raise HTTPException(status_code=404, detail="Loja pai não encontrada.")

    # E-mail único no sistema
    email_existe = db.query(Merchant).filter(Merchant.email == dados.email).first()
    if email_existe:
        raise HTTPException(status_code=400, detail="E-mail já está em uso por outra conta.")

    # Sub-usuário herda schema, codigo_loja e numero_whatsapp da loja pai
    # mas tem suas próprias credenciais e permissões
    sub_codigo = f"{loja_pai.codigo_loja}_user_{dados.email.split('@')[0]}"

    # nome_do_schema precisa ser único no banco — usamos o sub_codigo como valor
    # O schema real (da loja pai) é resolvido no login via loja_pai_id
    sub_schema = f"sub_{sub_codigo}"[:50]  # max 50 chars conforme o model

    sub = Merchant(
        nome_loja=dados.nome_loja,
        nome_usuario=dados.nome_usuario,
        codigo_loja=sub_codigo,
        nome_do_schema=sub_schema,          # ← schema único só para satisfazer constraint
        numero_whatsapp=None,
        area_atuacao=loja_pai.area_atuacao,
        email=dados.email,
        senha_hash=hash_senha(dados.senha),
        is_admin=False,
        tem_dashboard=dados.tem_dashboard,
        pode_editar_servicos=dados.pode_editar_servicos,
        loja_pai_id=lojista_id,             # ← vínculo com a loja pai (schema real)
    )

    db.add(sub)
    db.commit()
    db.refresh(sub)

    logger.info("Sub-usuário %s criado para loja %s pelo admin %s", sub.id, lojista_id, admin.id)
    return sub

# =========================================================
# EDITAR SUB-USUÁRIO (admin mestre apenas)

@router.put("/lojistas/{lojista_id}/usuarios/{usuario_id}", response_model=MerchantResponse)
def editar_sub_usuario(
    lojista_id: int,
    usuario_id: int,
    dados: MerchantUpdate,
    db: Session = Depends(get_public_db),
    admin: Merchant = Depends(get_lojista_atual),
):
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem editar sub-usuários.")

    usuario = db.query(Merchant).filter(
        Merchant.id == usuario_id,
        Merchant.loja_pai_id == lojista_id
    ).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Sub-usuário não encontrado nesta loja.")

    if dados.nome_loja is not None:
        usuario.nome_loja = dados.nome_loja
    if dados.email is not None:
        email_existe = db.query(Merchant).filter(Merchant.email == dados.email, Merchant.id != usuario_id).first()
        if email_existe:
            raise HTTPException(status_code=400, detail="E-mail já está em uso por outra conta.")
        usuario.email = dados.email
    if dados.senha is not None and dados.senha.strip() != "":
        usuario.senha_hash = hash_senha(dados.senha)
    if dados.tem_dashboard is not None:
        usuario.tem_dashboard = dados.tem_dashboard
    if dados.pode_editar_servicos is not None:
        usuario.pode_editar_servicos = dados.pode_editar_servicos

    db.commit()
    db.refresh(usuario)
    return usuario

# =========================================================
# REMOVER SUB-USUÁRIO (admin mestre apenas)

@router.delete("/lojistas/{lojista_id}/usuarios/{usuario_id}")
def remover_sub_usuario(
    lojista_id: int,
    usuario_id: int,
    db: Session = Depends(get_public_db),
    admin: Merchant = Depends(get_lojista_atual),
):
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem remover sub-usuários.")

    usuario = db.query(Merchant).filter(
        Merchant.id == usuario_id,
        Merchant.loja_pai_id == lojista_id
    ).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Sub-usuário não encontrado nesta loja.")

    db.delete(usuario)
    db.commit()

    logger.info("Sub-usuário %s removido da loja %s pelo admin %s", usuario_id, lojista_id, admin.id)
    return {"mensagem": "Sub-usuário removido com sucesso."}
