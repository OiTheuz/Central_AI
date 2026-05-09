from sqlalchemy import text  # <-- CORREÇÃO 1: Importação correta!
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import engine, SessionLocal
from datetime import datetime

# Cria as tabelas reais no banco
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Central de Agendamento")

# Função para conectar ao banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ROTA 1: Cadastrar um novo Lojista
@app.post("/lojistas/", response_model=schemas.MerchantResponse)
def criar_lojista(merchant: schemas.MerchantCreate, db: Session = Depends(get_db)):
    # 1. Verifica se já existe (CORREÇÃO 2: codigo_loja arrumado)
    db_merchant = db.query(models.Merchant).filter(
        (models.Merchant.codigo_loja == merchant.codigo_loja) | 
        (models.Merchant.nome_do_schema == merchant.nome_do_schema)
    ).first()
    
    if db_merchant:
        raise HTTPException(status_code=400, detail="Lojista ou Schema já existe.")
    
    # 2. Salva o registro na tabela principal (Pública)
    novo_lojista = models.Merchant(**merchant.model_dump())
    db.add(novo_lojista)
    db.commit()
    db.refresh(novo_lojista)

    # 3. MÁGICA: Cria o Schema físico no PostgreSQL
    try:
        schema_nome = merchant.nome_do_schema
        # Cria a gaveta
        db.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_nome}").execution_options(isolation_level="AUTOCOMMIT"))
        
        # <-- CORREÇÃO 3: Cria a tabela de agendamentos dentro da gaveta recém-criada
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

# ROTA 2: Listar os Lojistas
@app.get("/lojistas/", response_model=list[schemas.MerchantResponse])
def listar_lojistas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    lojistas = db.query(models.Merchant).offset(skip).limit(limit).all()
    return lojistas

# ROTA 3: Criar um Agendamento
@app.post("/agendamentos/")
def criar_agendamento(agendamento: schemas.AgendamentoCreate, db: Session = Depends(get_db)):
    merchant = db.query(models.Merchant).filter(models.Merchant.codigo_loja == agendamento.codigo_loja).first()
    
    if not merchant:
        raise HTTPException(status_code=404, detail="Lojista não encontrado. Verifique o código.")
    
    schema_name = merchant.nome_do_schema
    
    try:
        # 1. Preparamos o comando SQL
        comando_sql = text(f"""
            INSERT INTO {schema_name}.agendamentos (cliente_nome, cliente_whatsapp, data_horario, servico)
            VALUES (:nome, :whatsapp, :data_hora, :serv)
        """)
        
        # 2. Separamos os dados em uma variável totalmente isolada para evitar erros de parênteses
        parametros = {
            "nome": agendamento.cliente_nome,
            "whatsapp": agendamento.cliente_whatsapp,
            "data_hora": agendamento.data_horario,
            "serv": agendamento.servico
        }
        
        # 3. Executamos passando as duas variáveis separadas
        db.execute(comando_sql, parametros)
        db.commit()
        
        return {"mensagem": f"Agendamento para {agendamento.cliente_nome} salvo com sucesso na loja {merchant.nome_loja}!"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar agendamento: {str(e)}")
    
    # ROTA 4: Listar Agendamentos de um Lojista Específico
@app.get("/agendamentos/{codigo_loja}")
def listar_agendamentos(codigo_loja: str, db: Session = Depends(get_db)):
    # 1. Encontra o lojista
    merchant = db.query(models.Merchant).filter(models.Merchant.codigo_loja == codigo_loja).first()
    
    if not merchant:
        raise HTTPException(status_code=404, detail="Lojista não encontrado.")
    
    schema_name = merchant.nome_do_schema
    
    # 2. Busca os dados na gaveta correta
    try:
        comando_sql = text(f"""
            SELECT id, cliente_nome, cliente_whatsapp, data_horario, servico 
            FROM {schema_name}.agendamentos
            ORDER BY data_horario ASC
        """)
        
        # O .mappings().all() transforma o resultado do banco em uma lista que o FastAPI entende
        resultados = db.execute(comando_sql).mappings().all()
        return resultados
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar agendamentos: {str(e)}")