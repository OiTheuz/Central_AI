from sqlalchemy import text, Column, Integer, String, DateTime
from sqlalchemy.sql import func
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

class ActiveSession(models.Base):
    __tablename__ = "active_sessions"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    telefone_cliente = Column(String, unique=True, nullable=False)
    loja_atual = Column(String, nullable=False)
    ultima_interacao = Column(DateTime, server_default=func.now(), onupdate=func.now())

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
# FUNÇÕES DE MEMÓRIA DO BOT

def get_sessao_cliente(db: Session, telefone: str):
    return db.query(ActiveSession).filter(ActiveSession.telefone_cliente == telefone).first()

def salvar_sessao_cliente(db: Session, telefone: str, schema_loja: str):
    sessao = get_sessao_cliente(db, telefone)
    if sessao:
        sessao.loja_atual = schema_loja
    else:
        nova_sessao = ActiveSession(telefone_cliente=telefone, loja_atual=schema_loja)
        db.add(nova_sessao)
    db.commit()

def deletar_sessao_cliente(db: Session, telefone: str):
    db.query(ActiveSession).filter(ActiveSession.telefone_cliente == telefone).delete()
    db.commit()

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
    # 1. Pega a data exata de hoje
    data_atual = datetime.now().strftime("%d-%m-%Y")
    
    # 2. Somamos a regra da data com o seu prompt original
    prompt_sistema = f"⚠️ INFORMAÇÃO CRUCIAL: Hoje é dia {data_atual}. Use essa data como referência exata para calcular dias como 'amanhã', 'próxima semana', 'quinta-feira', etc.\n\n" + """
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
    
    
    # Acessamos o conteúdo de texto da mensagem primeiro
    conteudo_texto = response.choices[0].message.content
    
    # Agora convertemos esse texto para um dicionário Python
    dados_extraidos = json.loads(conteudo_texto)
    
    return dados_extraidos

def enviar_mensagem_whatsapp(numero_destino: str, texto: str):
    # Vai buscar as credenciais de forma segura ao arquivo .env
    TOKEN_META = os.getenv("TOKEN_META")
    PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
    
    # Prevenção: Avisa no terminal se você esquecer de preencher o .env
    if not TOKEN_META or not PHONE_NUMBER_ID:
        print("❌ ERRO: TOKEN_META ou PHONE_NUMBER_ID não estão configurados no ficheiro .env!")
        return

    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {TOKEN_META}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": numero_destino,
        "type": "text",
        "text": {"body": texto}
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"↗️ Status do Envio: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")
        
    return response.json()

# =========================================================
# WEBHOOK META - RECEBER MENSAGENS (POST)

@app.post("/webhook")
async def recebe_mensagem_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
        
        # 1. Padrão Oficial Meta: Usar loops para navegar com segurança no JSON
        if body.get("object") == "whatsapp_business_account":
            for entry in body.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    
                    # Verifica se realmente existe uma mensagem (e não um status de 'entregue')
                    if "messages" in value:
                        for mensagem in value["messages"]:
                            
                            # Ignora se não for mensagem de texto (ex: áudio, imagem)
                            if mensagem.get("type") != "text":
                                continue

                            telefone_cliente = mensagem.get("from")
                            mensagem_usuario = mensagem.get("text", {}).get("body", "")

                            print(f"\n📩 Mensagem de {telefone_cliente}: {mensagem_usuario}")

                            # 2. LÓGICA DE MEMÓRIA
                            schema_alvo = None
                            sessao_ativa = get_sessao_cliente(db, telefone_cliente)

                            if sessao_ativa:
                                schema_alvo = sessao_ativa.loja_atual
                                print(f"🧠 Memória Ativa: Cliente em atendimento com -> {schema_alvo}")
                            else:
                                merchants = db.query(models.Merchant).all()
                                for m in merchants:
                                    if m.nome_loja.lower() in mensagem_usuario.lower() or m.codigo_loja.lower() in mensagem_usuario.lower():
                                        schema_alvo = m.nome_do_schema
                                        salvar_sessao_cliente(db, telefone_cliente, schema_alvo)
                                        print(f"🆕 Nova sessão iniciada com -> {schema_alvo}")
                                        break

                            # 3. PROCESSAR COM IA
                            if schema_alvo:
                                dados_ia = await analisar_mensagem_com_ia(mensagem_usuario)
                                
                                # AQUI ESTÁ A CORREÇÃO: Garante que a IA não devolveu uma lista
                                if isinstance(dados_ia, dict):
                                    if dados_ia.get("servico") and dados_ia.get("data"):
                                        print(f"🎯 Agendamento detectado: {dados_ia}")
                                        # (AQUI ENTRA O SEU INSERT NO BANCO QUE FIZEMOS ANTES)
                                        
                                        # 👉 ROBÔ RESPONDE (Com dados detectados)
                                        texto_confirmacao = f"Perfeito! Entendi que você deseja um(a) {dados_ia.get('servico')} para a data {dados_ia.get('data')}. Vou verificar a disponibilidade na agenda!"
                                        enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=texto_confirmacao)
                                        
                                    else:
                                        print("⏳ IA ainda coletando informações do cliente...")
                                        
                                        # 👉 A BOCA DO ROBÔ ESTÁ AQUI (IA fazendo perguntas)
                                        # Pega a resposta gerada pela IA (se ela enviar a chave 'resposta'), senão envia um texto padrão
                                        texto_ia = dados_ia.get("resposta", "Entendi! Para prosseguir com o agendamento no Moura, qual seria o serviço e a data desejada?")
                                        
                                        enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=texto_ia)
                                        
                                else:
                                    print("⚠️ A IA devolveu um formato inesperado. Ignorando...")
                            else:
                                print("🤷 Não conseguimos identificar a loja. Aguardando o cliente mencionar.")

            # Retorna 200 OK para a Meta
            return JSONResponse(content={"status": "sucesso"}, status_code=200)

    except Exception as e:
        print(f"❌ Erro interno tratado: {str(e)}")
        # A REGRÁ DE OURO DOS WEBHOOKS: Sempre retorne 200 no except!
        # Assim a Meta entende que você recebeu e para de "flodar" o seu terminal.
        return JSONResponse(content={"status": "erro_interno_tratado"}, status_code=200)
    
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