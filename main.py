from sqlalchemy import text
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from openai import AsyncOpenAI
from datetime import datetime

import requests
import json
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
# CONFIGURAÇÃO OPENAI 

# Inicializa o cliente da OpenAI pegando a chave do .env
client_ai = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def analisar_mensagem_com_ia(texto_cliente: str):
    prompt_sistema = """
    Você é um assistente inteligente de uma Central de Agendamentos.
    Sua única função é ler a mensagem do cliente e extrair os dados em formato JSON.
    
    O formato JSON estrito DEVE ser:
    {
        "intencao": "agendamento" ou "saudacao" ou "duvida",
        "nome_cliente": "nome da pessoa, ou null",
        "servico": "serviço desejado, ou null",
        "data": "DD-MM-YYYY, ou null",
        "hora": "HH:MM, ou null"
    }
    """
    
    # Chama a API
    response = await client_ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": texto_cliente}
        ],
        response_format={ "type": "json_object" },
        temperature=0.1
    )
    
    # A CORREÇÃO ESTÁ AQUI:
    # Acessamos o conteúdo de texto da mensagem primeiro
    conteudo_texto = response.choices[0].message.content
    
    # Agora convertemos esse texto para um dicionário Python
    dados_extraidos = json.loads(conteudo_texto)
    
    return dados_extraidos

def enviar_mensagem_whatsapp(telefone_destino: str, texto_mensagem: str):
    token = os.getenv("META_ACCESS_TOKEN")
    phone_id = os.getenv("META_PHONE_ID")
    
    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": telefone_destino,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": texto_mensagem
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        print("✅ Mensagem ENVIADA com sucesso pelo bot!")
    else:
        print(f"❌ Erro ao enviar mensagem: {response.text}")
        
    return response.json()

# =========================================================
# WEBHOOK META - RECEBER MENSAGENS (POST)

@app.post("/webhook")
async def receive_messages(
    request: Request, 
    db: Session = Depends(get_db) # <-- ADICIONAMOS A CONEXÃO COM O BANCO AQUI
):
    try:
        body = await request.json()

        if body.get("object") == "whatsapp_business_account":
            for entry in body.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    
                    if "messages" in value:
                        for message in value["messages"]:
                            telefone_cliente = message.get("from")
                            
                            if message.get("type") == "text":
                                texto_mensagem = message["text"]["body"]
                                
                                print("======== NOVA MENSAGEM META ========")
                                print(f"📱 Cliente: {telefone_cliente}")
                                print(f"💬 Mensagem: {texto_mensagem}")
                                
                                # === NOVA LÓGICA DE IDENTIFICAÇÃO (ROTEAMENTO) ===
                                texto_minusculo = texto_mensagem.lower()
                                lojista_encontrado = None

                                # 1. Puxa todos os lojistas do banco de dados
                                lojistas_cadastrados = db.query(models.Merchant).all()

                                # 2. Procura se o nome de alguma loja está dentro do texto que o cliente mandou
                                for loja in lojistas_cadastrados:
                                    if loja.nome_loja.lower() in texto_minusculo:
                                        lojista_encontrado = loja
                                        break
                                
                                # 3. Verifica o resultado
                                telefone_cliente = message.get("from")
                            
                            if message.get("type") == "text":
                                texto_mensagem = message["text"]["body"]
                                
                                print("======== NOVA MENSAGEM META ========")
                                print(f"📱 Cliente: {telefone_cliente}")
                                print(f"💬 Mensagem: {texto_mensagem}")
                                
                                # === LÓGICA DE IDENTIFICAÇÃO (ROTEAMENTO) ===
                                texto_minusculo = texto_mensagem.lower()
                                lojista_encontrado = None
                                lojistas_cadastrados = db.query(models.Merchant).all()

                                for loja in lojistas_cadastrados:
                                    if loja.nome_loja.lower() in texto_minusculo:
                                        lojista_encontrado = loja
                                        break
                                
                                # === CONECTANDO A INTELIGÊNCIA ARTIFICIAL ===
                                
                                if lojista_encontrado:
                                    print(f"🎯 Lojista Encontrado: {lojista_encontrado.nome_loja}")
                                    print("🧠 Enviando mensagem para a IA analisar...")
                                    
                                    # Aqui chamamos a função que você corrigiu no topo do arquivo
                                    dados_extraidos = await analisar_mensagem_com_ia(texto_mensagem)
                                    
                                    # O pulo do gato: A função já retorna o JSON pronto, 
                                    # então agora é só usar os .get()
                                    intencao = dados_extraidos.get("intencao")
                                    nome = dados_extraidos.get("nome_cliente")
                                    servico = dados_extraidos.get("servico")
                                    data = dados_extraidos.get("data")
                                    hora = dados_extraidos.get("hora")

                                    # Defina data_br antes de usar
                                    data_br = "25-12-2024"  # Exemplo de entrada no formato DD-MM-YYYY

                                    # =============== BLOCO DE TRADUÇÃO ============================
                                    data_sql = None
                                    if data_br:
                                        try:
                                            data_obj = datetime.strptime(data_br, "%d-%m-%Y")
                                            data_sql = data_obj.strftime("%Y-%m-%d")
                                        except ValueError as e:  # Capture a exceção com 'as e'
                                            print(f"Erro na conversão: {e}")
                                            data_sql = None
                                    # =============== BLOCO DE TRADUÇÃO ============================

                                    # Monta a resposta
                                    if intencao == "agendamento" and nome and data and hora:
                                        mensagem_resposta = (
                                            f"Olá, {nome}! Agendamento para {servico} no dia {data} às {hora} no {lojista_encontrado.nome_loja} anotado! Vou confirmar a vaga."
                                        )
                                    elif not nome:
                                        mensagem_resposta = (
                                            f"Olá! Notei que quer agendar no {lojista_encontrado.nome_loja}. Qual seu nome, por favor?"
                                        )
                                    else:
                                        mensagem_resposta = (
                                            f"Oi! Como posso ajudar você hoje no {lojista_encontrado.nome_loja}?"
                                        )

                                    # Envia pro WhatsApp
                                    enviar_mensagem_whatsapp(telefone_cliente, mensagem_resposta)
                                else:
                                    print("🤷 Não conseguimos identificar de qual loja o cliente está falando.")
                                    
                                print("====================================")
        
        return JSONResponse(content={"status": "recebido"}, status_code=200)

    except Exception as e:
        print(f"❌ ERRO WEBHOOK: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
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