from sqlalchemy import text
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv

import models
import schemas
import os
load_dotenv()

from database import engine, SessionLocal

# =========================================================
# CRIA TABELAS

models.Base.metadata.create_all(bind=engine)

# =========================================================
# APP

app = FastAPI(title="API Central de Agendamento")

# =========================================================
# CONFIG META

VERIFY_TOKEN = "AgendAI_Meta_9f2a8b3c7e5d10a4f6b2"

# =========================================================
# DATABASE

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================================================
# HEALTH CHECK

@app.get("/")
def home():
    return {
        "status": "online",
        "api": "API Central de Agendamento"
    }

# =========================================================
# WEBHOOK META - VERIFICAÇÃO (GET)

@app.get("/webhook")
async def verify_webhook(request: Request):

    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    print("======== META WEBHOOK VERIFY ========")
    print(f"mode: {mode}")
    print(f"token: {token}")
    print(f"challenge: {challenge}")
    print("=====================================")

    if mode == "subscribe" and token == VERIFY_TOKEN:

        print("✅ WEBHOOK VERIFICADO COM SUCESSO")

        # META EXIGE TEXTO PURO
        return PlainTextResponse(
            content=str(challenge),
            status_code=200
        )

    print("❌ TOKEN INVALIDO")

    raise HTTPException(
        status_code=403,
        detail="Token de verificação inválido"
    )

# =========================================================
# WEBHOOK META - RECEBER MENSAGENS (POST)
# ---> AQUI FIZEMOS A MÁGICA DA LEITURA DE DADOS <---

@app.post("/webhook")
async def receive_messages(request: Request):
    try:
        body = await request.json()

        # Verifica se a notificação vem realmente de uma conta do WhatsApp
        if body.get("object") == "whatsapp_business_account":
            
            # A Meta envia as mensagens dentro de "entry" e "changes"
            for entry in body.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    
                    # Verifica se o evento contém mensagens
                    if "messages" in value:
                        for message in value["messages"]:
                            
                            # Extrai o número do telefone do cliente
                            telefone_cliente = message.get("from")
                            
                            # Filtramos para capturar apenas mensagens de texto (ignoramos áudio, foto, etc por enquanto)
                            if message.get("type") == "text":
                                texto_mensagem = message["text"]["body"]
                                
                                print("======== NOVA MENSAGEM META ========")
                                print(f"📱 Cliente: {telefone_cliente}")
                                print(f"💬 Mensagem: {texto_mensagem}")
                                print("====================================")
                                
                                # TODO: PRÓXIMO PASSO
                                # Aqui vamos chamar a função para identificar o lojista e acionar a IA
        
        # Respondemos rapidamente para a Meta saber que recebemos
        return JSONResponse(
            content={"status": "recebido"},
            status_code=200
        )

    except Exception as e:
        print(f"❌ ERRO WEBHOOK: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

# =========================================================
# LOJISTAS

@app.post("/lojistas/", response_model=schemas.MerchantResponse)
def criar_lojista(
    merchant: schemas.MerchantCreate,
    db: Session = Depends(get_db)
):

    db_merchant = db.query(models.Merchant).filter(
        (models.Merchant.codigo_loja == merchant.codigo_loja) |
        (models.Merchant.nome_do_schema == merchant.nome_do_schema)
    ).first()

    if db_merchant:
        raise HTTPException(
            status_code=400,
            detail="Lojista ou Schema já existe."
        )

    novo_lojista = models.Merchant(**merchant.model_dump())

    db.add(novo_lojista)
    db.commit()
    db.refresh(novo_lojista)

    try:

        schema_nome = merchant.nome_do_schema

        db.execute(
            text(f"CREATE SCHEMA IF NOT EXISTS {schema_nome}")
        )

        db.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {schema_nome}.agendamentos (
                id SERIAL PRIMARY KEY,
                cliente_nome VARCHAR(100),
                cliente_whatsapp VARCHAR(20),
                data_horario TIMESTAMP,
                servico VARCHAR(100)
            )
        """))

        db.commit()

        print(f"✅ Schema {schema_nome} criado com sucesso")

    except Exception as e:

        db.rollback()

        print(f"❌ ERRO AO CRIAR SCHEMA: {e}")

    return novo_lojista

# =========================================================
# LISTAR LOJISTAS

@app.get("/lojistas/", response_model=list[schemas.MerchantResponse])
def listar_lojistas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):

    lojistas = db.query(models.Merchant)\
        .offset(skip)\
        .limit(limit)\
        .all()

    return lojistas

# =========================================================
# CRIAR AGENDAMENTO

@app.post("/agendamentos/")
def criar_agendamento(
    agendamento: schemas.AgendamentoCreate,
    db: Session = Depends(get_db)
):

    merchant = db.query(models.Merchant).filter(
        models.Merchant.codigo_loja == agendamento.codigo_loja
    ).first()

    if not merchant:
        raise HTTPException(
            status_code=404,
            detail="Lojista não encontrado."
        )

    schema_name = merchant.nome_do_schema

    try:

        comando_sql = text(f"""
            INSERT INTO {schema_name}.agendamentos
            (
                cliente_nome,
                cliente_whatsapp,
                data_horario,
                servico
            )
            VALUES
            (
                :nome,
                :whatsapp,
                :data_hora,
                :serv
            )
        """)

        parametros = {
            "nome": agendamento.cliente_nome,
            "whatsapp": agendamento.cliente_whatsapp,
            "data_hora": agendamento.data_horario,
            "serv": agendamento.servico
        }

        db.execute(comando_sql, parametros)

        db.commit()

        return {
            "mensagem": f"Agendamento para {agendamento.cliente_nome} salvo com sucesso!"
        }

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# =========================================================
# LISTAR AGENDAMENTOS

@app.get("/agendamentos/{codigo_loja}")
def listar_agendamentos(
    codigo_loja: str,
    db: Session = Depends(get_db)
):

    merchant = db.query(models.Merchant).filter(
        models.Merchant.codigo_loja == codigo_loja
    ).first()

    if not merchant:
        raise HTTPException(
            status_code=404,
            detail="Lojista não encontrado."
        )

    schema_name = merchant.nome_do_schema

    try:

        comando_sql = text(f"""
            SELECT *
            FROM {schema_name}.agendamentos
            ORDER BY data_horario ASC
        """)

        resultados = db.execute(comando_sql).mappings().all()

        return resultados

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )