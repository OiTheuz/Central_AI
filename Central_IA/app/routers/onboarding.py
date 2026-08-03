from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
import re

from app.database import get_public_db
from app.models.merchant import Merchant
from app.models.whatsapp_log import WhatsappMessageLog
from app.models.lead import Lead
from app.services.auth_service import hash_senha
from app.services.schema_service import criar_novo_estabelecimento
from app.services.asaas_service import criar_cliente, criar_assinatura_pix

router = APIRouter(
    prefix="/api/onboarding",
    tags=["Onboarding"],
)

class SimulatePaymentRequest(BaseModel):
    nome_loja: str
    email: str
    senha: str
    cpf: str
    nicho: str
    telefone: str = None
    cupom: str = None
    como_conheceu: str = None
    recaptcha_token: str = None

class PartialLeadRequest(BaseModel):
    nome: str = None
    telefone: str = None
    email: str = None
    nicho: str = None
    como_conheceu: str = None

@router.post("/lead")
def save_partial_lead(body: PartialLeadRequest, db: Session = Depends(get_public_db)):
    """Salva os dados digitados do lead antes da finalização do cadastro."""
    if not body.email and not body.telefone:
        return {"status": "ignorado"}
        
    lead = None
    if body.email:
        lead = db.query(Lead).filter(Lead.email == body.email).first()
    
    if not lead and body.telefone:
        lead = db.query(Lead).filter(Lead.telefone == body.telefone).first()
        
    if lead:
        if body.nome: lead.nome = body.nome
        if body.telefone: lead.telefone = body.telefone
        if body.email: lead.email = body.email
        if body.nicho: lead.nicho = body.nicho
        if body.como_conheceu: lead.como_conheceu = body.como_conheceu
    else:
        lead = Lead(
            nome=body.nome,
            telefone=body.telefone,
            email=body.email,
            nicho=body.nicho,
            como_conheceu=body.como_conheceu
        )
        db.add(lead)
        
    db.commit()
    return {"status": "salvo"}

@router.post("/simulate-payment")
def simulate_payment(body: SimulatePaymentRequest, db: Session = Depends(get_public_db)):
    """
    Simula o recebimento de um webhook de pagamento (Stripe/Asaas).
    1. Verifica se email existe.
    2. Cria o schema da loja e copia tabelas.
    3. Registra na tabela public.merchant.
    """
    import os
    import requests

    # 0. Valida reCAPTCHA se o token e a chave secreta existirem
    secret_key = os.getenv("RECAPTCHA_SECRET_KEY")
    if secret_key and body.recaptcha_token:
        try:
            r = requests.post("https://www.google.com/recaptcha/api/siteverify", data={
                "secret": secret_key,
                "response": body.recaptcha_token
            })
            result = r.json()
            if not result.get("success"):
                raise HTTPException(status_code=400, detail="Falha na validação do reCAPTCHA.")
        except requests.RequestException:
            raise HTTPException(status_code=500, detail="Erro ao comunicar com o servidor de validação.")
    elif secret_key and not body.recaptcha_token:
        raise HTTPException(status_code=400, detail="Validação de segurança (reCAPTCHA) é obrigatória.")
    # 1. Verifica se email já existe
    if db.query(Merchant).filter(Merchant.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado.")

    # 2. Gera os identificadores
    slug = re.sub(r'[^a-zA-Z0-9]', '', body.nome_loja.lower())
    codigo_loja = slug
    schema_nome = f"schema_{slug}"

    # Valida colisão de codigo_loja
    if db.query(Merchant).filter(Merchant.codigo_loja == codigo_loja).first():
        codigo_loja = f"{slug}_{db.query(Merchant).count() + 1}"
        schema_nome = f"schema_{codigo_loja}"

    # 3. Cria o schema usando o schema_service
    # Copia as tabelas base
    tabelas_base = ["appointments", "customers", "services"]
    try:
        criar_novo_estabelecimento(schema_nome, tabelas_base, nicho=body.nicho)
    except Exception as e:
        erro_msg = str(e)
        if "DuplicateTable" in erro_msg or "already exists" in erro_msg or "DuplicateSchema" in erro_msg:
            raise HTTPException(status_code=400, detail="Já existe uma loja registrada com este nome exato no sistema. Por favor, adicione um sobrenome, número ou altere o nome da loja.")
        raise HTTPException(status_code=500, detail=f"Erro ao criar banco de dados: {erro_msg}")

    # 4. Integração Real Asaas ou Cupom Grátis
    is_free = body.cupom and body.cupom.upper() == "LAUTZ100"
    
    from datetime import datetime, timedelta
    vencimento_str = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    if is_free:
        asaas_customer_id = None
        subscription_id = None
        status_final = 'ativo'
    else:
        try:
            asaas_customer_id = criar_cliente(nome=body.nome_loja, email=body.email, telefone=body.telefone, cpfCnpj=body.cpf)
            # NÃO criamos a assinatura no Asaas ainda para não gerar fatura.
            subscription_id = None
            status_final = 'trial'
        except Exception as e:
            # Rollback: se der erro no Asaas, deleta a tabela/schema que acabou de criar
            from sqlalchemy import text
            db.execute(text(f"DROP SCHEMA IF EXISTS {schema_nome} CASCADE"))
            db.commit()
            raise HTTPException(status_code=502, detail=f"Erro de comunicação com Asaas: {str(e)}")

    # 5. Registra no public.merchant com status pendente (inativo) até pagar
    novo_lojista = Merchant(
        nome_loja=body.nome_loja,
        nome_usuario=body.nome_loja,
        email=body.email,
        senha_hash=hash_senha(body.senha),
        codigo_loja=codigo_loja,
        nome_do_schema=schema_nome,
        area_atuacao=body.nicho,
        telefone_contato=body.telefone,
        cupom_usado=body.cupom,
        como_conheceu=body.como_conheceu,
        is_admin=False,
        tem_dashboard=True,
        asaas_customer_id=asaas_customer_id,
        asaas_subscription_id=subscription_id,
        status_assinatura=status_final,
        data_vencimento=vencimento_str
    )
    db.add(novo_lojista)
    db.commit()
    db.refresh(novo_lojista)

    # Marca o lead como convertido
    lead = db.query(Lead).filter(Lead.email == body.email).first()
    if lead:
        lead.convertido = 1
        db.commit()

    # Dispara a mensagem de boas-vindas no WhatsApp
    numero_destino = body.telefone
    if numero_destino:
        from app.services.whatsapp_service import enviar_botao_url_whatsapp
        
        # Pega a primeira palavra do nome como primeiro nome
        primeiro_nome = body.nome_loja.split()[0] if body.nome_loja else "Cliente"
        
        mensagem_boas_vindas = (
            f"Bem-vindo(a) à *OpenChatz* 🚀\n"
            f"Olá, {primeiro_nome}. Sua conta na OpenChatz foi criada com sucesso, e seu período de teste gratuito de 7 dias já está ativo.\n\n"
            f"Queremos agradecer por escolher a OpenChatz para ajudar no dia a dia do seu negócio. Nosso foco é deixar o gerenciamento da sua agenda mais simples, organizado e automatizado, para que você tenha mais tempo para atender seus clientes.\n\n"
            f"Para começar, recomendamos que você acesse o seu painel de controle e configure a sua Inteligência Artificial para deixar tudo com a sua cara.\n\n"
            f"Qualquer dúvida ou dificuldade, pode falar com a gente por aqui mesmo. Estamos à disposição para ajudar.\n\n"
            f"Um grande abraço,\n"
            f"Equipe OpenChatz"
        )
        
        try:
            enviar_botao_url_whatsapp(
                numero_destino=numero_destino, 
                texto=mensagem_boas_vindas,
                url_botao="https://www.openchatz.com.br/portal/login",
                titulo_botao="Acessar Portal"
            )
        except Exception as e:
            # Não falhamos o cadastro só porque o WhatsApp falhou
            pass

    return {
        "status": "sucesso",
        "mensagem": "Conta criada com sucesso! Trial de 7 dias ativado.",
        "lojista_id": novo_lojista.id,
        "schema": schema_nome,
        "asaas_pix_payload": None,
        "asaas_pix_qrcode": None
    }

@router.get("/admin-merchants")
def get_admin_merchants(db: Session = Depends(get_public_db)):
    """
    Retorna todos os lojistas cadastrados para o Painel Admin do Site.
    (Em produção, proteger com API_KEY ou integrar com JWT do Admin).
    """
    lojas = db.query(Merchant).filter(Merchant.loja_pai_id.is_(None)).order_by(Merchant.id.desc()).all()
    
    total_lojas = len(lojas)
    
    # Busca mensagens reais (no banco public, tabela whatsapp_message_log)
    total_mensagens = db.query(WhatsappMessageLog).count()

    total_agendamentos = 0
    merchants_data = []

    for l in lojas:
        # Conta agendamentos reais em cada schema isolado
        agendamentos_loja = 0
        try:
            if l.nome_do_schema:
                res = db.execute(text(f"SELECT count(*) FROM {l.nome_do_schema}.appointments"))
                agendamentos_loja = res.scalar() or 0
                total_agendamentos += agendamentos_loja
        except Exception:
            pass # Ignora caso a tabela ainda não exista

        merchants_data.append({
            "id": l.id,
            "name": l.nome_loja,
            "niche": l.area_atuacao or "Geral",
            "status": "Ativo" if l.meta_access_token else "Pendente (Sem WhatsApp)",
            "date": "Cadastrado"
        })
    
    # Filtra lojas pagantes (que possuem asaas_subscription_id)
    paying_lojas = sum(1 for l in lojas if l.asaas_subscription_id is not None)
    
    return {
        "stats": {
            "total_lojas": total_lojas,
            "mensagens_processadas": total_mensagens,
            "agendamentos_hoje": total_agendamentos, # Total de agendamentos no sistema
            "receita_mrr": f"R$ {paying_lojas * 57},00" # MRR baseado apenas em lojas com assinatura real
        },
        "merchants": merchants_data
    }

from app.services.auth_service import get_lojista_atual

from typing import List

class Step1Request(BaseModel):
    tem_multiplos_profissionais: bool
    ia_pergunta_profissional: bool
    agenda_separada_por_profissional: bool
    nomes_profissionais: List[str] = []

@router.put("/step/1")
def onboarding_step_1(body: Step1Request, db: Session = Depends(get_public_db), merchant: Merchant = Depends(get_lojista_atual)):
    merchant.tem_multiplos_profissionais = body.tem_multiplos_profissionais
    merchant.ia_pergunta_profissional = body.ia_pergunta_profissional
    merchant.agenda_separada_por_profissional = body.agenda_separada_por_profissional
    merchant.onboarding_step = 2
    
    profissionais_retorno = []
    
    if body.tem_multiplos_profissionais and body.nomes_profissionais:
        from app.models.professional import Professional
        # Switch to tenant schema
        db.execute(text(f"SET search_path TO {merchant.nome_do_schema}"))
        
        # Limpa antigos se existirem (para evitar duplicidade em re-submissões)
        db.execute(text(f"TRUNCATE {merchant.nome_do_schema}.professionals CASCADE"))
        
        for nome in body.nomes_profissionais:
            prof = Professional(nome=nome)
            db.add(prof)
        db.commit()
        
        # Fetch inserted to get IDs
        profs = db.query(Professional).all()
        for p in profs:
            profissionais_retorno.append({"id": p.id, "nome": p.nome})
            
        # Switch back to public
        db.execute(text("SET search_path TO public"))
    else:
        db.commit()

    return {"status": "sucesso", "profissionais": profissionais_retorno}

@router.put("/step/2")
def onboarding_step_2(db: Session = Depends(get_public_db), merchant: Merchant = Depends(get_lojista_atual)):
    merchant.onboarding_step = 3
    db.commit()
    return {"status": "sucesso"}

@router.put("/step/3")
def onboarding_step_3(db: Session = Depends(get_public_db), merchant: Merchant = Depends(get_lojista_atual)):
    merchant.onboarding_step = 4
    db.commit()
    return {"status": "sucesso"}

class Step4Request(BaseModel):
    ia_persona: str
    instrucoes_ia: str

@router.put("/step/4")
def onboarding_step_4(body: Step4Request, db: Session = Depends(get_public_db), merchant: Merchant = Depends(get_lojista_atual)):
    merchant.ia_persona = body.ia_persona
    merchant.instrucoes_ia = body.instrucoes_ia
    merchant.onboarding_step = 5
    db.commit()
    return {"status": "sucesso"}

@router.put("/step/5")
def onboarding_step_5(db: Session = Depends(get_public_db), merchant: Merchant = Depends(get_lojista_atual)):
    merchant.onboarding_completo = True
    merchant.onboarding_step = 6
    db.commit()
    return {"status": "sucesso", "mensagem": "Onboarding concluído com sucesso!"}

@router.get("/check-payment/{lojista_id}")
def check_payment(lojista_id: int, db: Session = Depends(get_public_db)):
    """
    Retorna o status da assinatura do lojista para o front-end saber se o PIX já caiu.
    """
    merchant = db.query(Merchant).filter(Merchant.id == lojista_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Lojista não encontrado.")

    return {
        "status_assinatura": merchant.status_assinatura
    }

