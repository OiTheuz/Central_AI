from sqlalchemy import text 
from fastapi import FastAPI, Depends, HTTPException, Request # Adicionado: Request
from fastapi.responses import PlainTextResponse # Adicionado: PlainTextResponse
from sqlalchemy.orm import Session
import models, schemas
from database import engine, SessionLocal
from datetime import datetime

# Cria as tabelas reais no banco
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Central de Agendamento")

# --- CONFIGURAÇÃO META ---
# Esta é a senha que você inventou e colocará no painel do Facebook
VERIFY_TOKEN = "senha_webhook_central"

# Função para conectar ao banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- NOVAS ROTAS PARA O WEBHOOK (META) ---

@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Rota para a Meta verificar se seu servidor está online e seguro.
    Ocorre apenas quando você clica em 'Verificar e Salvar' no painel.
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("✅ WEBHOOK VERIFICADO COM SUCESSO PELA META!")
            return PlainTextResponse(content=challenge, status_code=200)
        else:
            raise HTTPException(status_code=403, detail="Token de verificação inválido")
            
    raise HTTPException(status_code=400, detail="Faltam parâmetros")

@app.post("/webhook")
async def receive_messages(request: Request):
    """
    Esta rota é por onde as mensagens dos clientes REAIS entrarão.
    Por enquanto, vamos apenas printar no terminal para você ver o JSON.
    """
    body = await request.json()
    print(f"📩 Nova notificação recebida da Meta: {body}")
    
    # Aqui no futuro entraremos com a lógica da IA para processar a mensagem
    return {"status": "recebido"}


# --- SUAS ROTAS ORIGINAIS (MANTIDAS) ---

@app.post("/lojistas/", response_model=schemas.MerchantResponse)
def criar_lojista(merchant: schemas.MerchantCreate, db: Session = Depends(get_db)):
    db_merchant = db.query(models.Merchant).filter(
        (models.Merchant.codigo_lo_ja == merchant.codigo_loja) | 
        (models.Merchant.nome_do_schema == merchant.nome_do_schema)
    ).first()
    
    if db_merchant:
        raise HTTPException(status_code=400, detail="Lojista ou Schema já existe.")
    
    novo_lojista = models.Merchant(**merchant.model_dump())
    db.add(novo_lojista)
    db.commit()
    db.refresh(novo_lojista)

    try:
        schema_nome = merchant.nome_do_schema
        db.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_nome}").execution_options(isolation_level="AUTOCOMMIT"))
        
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
        print(f"✅ Schema {schema_nome} e tabela de agendamentos criados com sucesso!")
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao criar schema: {e}")
    
    return novo_lojista

@app.get("/lojistas/", response_model=list[schemas.MerchantResponse])
def listar_lojistas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    lojistas = db.query(models.Merchant).offset(skip).limit(limit).all()
    return lojistas

@app.post("/agendamentos/")
def criar_agendamento(agendamento: schemas.AgendamentoCreate, db: Session = Depends(get_db)):
    merchant = db.query(models.Merchant).filter(models.Merchant.codigo_loja == agendamento.codigo_loja).first()
    
    if not merchant:
        raise HTTPException(status_code=404, detail="Lojista não encontrado.")
    
    schema_name = merchant.nome_do_schema
    
    try:
        comando_sql = text(f"""
            INSERT INTO {schema_name}.agendamentos (cliente_nome, cliente_whatsapp, data_horario, servico)
            VALUES (:nome, :whatsapp, :data_hora, :serv)
        """)
        
        parametros = {
            "nome": agendamento.cliente_nome,
            "whatsapp": agendamento.cliente_whatsapp,
            "data_hora": agendamento.data_horario,
            "serv": agendamento.servico
        }
        
        db.execute(comando_sql, parametros)
        db.commit()
        
        return {"mensagem": f"Agendamento para {agendamento.cliente_nome} salvo com sucesso!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agendamentos/{codigo_loja}")
def listar_agendamentos(codigo_loja: str, db: Session = Depends(get_db)):
    merchant = db.query(models.Merchant).filter(models.Merchant.codigo_loja == codigo_loja).first()
    
    if not merchant:
        raise HTTPException(status_code=404, detail="Lojista não encontrado.")
    
    schema_name = merchant.nome_do_schema
    
    try:
        comando_sql = text(f"SELECT * FROM {schema_name}.agendamentos ORDER BY data_horario ASC")
        resultados = db.execute(comando_sql).mappings().all()
        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))