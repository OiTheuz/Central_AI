import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import VERIFY_TOKEN
from app.database import get_db, SessionLocal
from app.services.openai_service import analisar_mensagem_com_ia
from app.services.whatsapp_service import enviar_mensagem_whatsapp
from app.services.session_service import get_sessao_cliente, salvar_sessao_cliente, encerrar_sessao_cliente

router = APIRouter(tags=["Webhook"])

# =========================================================
# FUNÇÃO AUXILIAR: SIMULADOR DE CONFIRMAÇÃO DO LOJISTA
# =========================================================
async def simular_confirmacao_lojista(telefone: str, servico: str, data: str, hora: str, schema_alvo: str):
    await asyncio.sleep(5)
    db_async = SessionLocal()
    try:
        db_async.execute(text(f"SET search_path TO {schema_alvo}"))
        db_async.execute(text("""
            UPDATE appointments 
            SET status = 'confirmado' 
            WHERE status = 'pendente' 
            AND customer_id = (SELECT id FROM customers WHERE telefone = :tel LIMIT 1)
        """), {"tel": telefone})
        db_async.commit()
        
        mensagem_sucesso = f"✅ Tudo certo! Seu agendamento de {servico} foi confirmado para {data} às {hora}! Posso te ajudar com mais alguma coisa?"
        enviar_mensagem_whatsapp(numero_destino=telefone, texto=mensagem_sucesso)
        print(f"🎯 [MOCK] Agendamento de {telefone} confirmado automaticamente com sucesso.")
    except Exception as e:
        print(f"❌ Erro no mock de confirmação automática: {str(e)}")
    finally:
        db_async.close()

# =========================================================
# WEBHOOK META - VERIFICAÇÃO (GET)
# =========================================================
@router.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(content=challenge, status_code=200)
    return JSONResponse(content={"error": "Token invalido"}, status_code=403)

# =========================================================
# WEBHOOK META - RECEBIMENTO (POST)
# =========================================================
@router.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        body = await request.json()
        
        # ESCUDO ANTI-QUEDA BLINDADO CONTRA NULOS E LISTAS
        entry = body.get("entry", [])
        if not entry or not isinstance(entry, list):
            return JSONResponse(content={"status": "evento_ignorado_sem_entry"}, status_code=200)
            
        changes = entry.get("changes", [])
        if not changes or not isinstance(changes, list):
            return JSONResponse(content={"status": "evento_ignorado_sem_changes"}, status_code=200)
            
        value = changes.get("value", {})
        if not value or not isinstance(value, dict) or not value.get("messages"):
            return JSONResponse(content={"status": "evento_ignorado_sem_messages"}, status_code=200)
            
        message_data = value["messages"]
        telefone_cliente = message_data.get("from")
        
        if not message_data.get("text") or not message_data["text"].get("body"):
            return JSONResponse(content={"status": "mensagem_sem_texto_ignorado"}, status_code=200)
            
        mensagem_usuario = message_data["text"]["body"]
        print(f"📩 Mensagem recebida de {telefone_cliente}: '{mensagem_usuario}'")

        # -------------------------------------------------
        # PASSO 1: IDENTIFICAÇÃO DO LOJISTA E BLINDAGEM DA SESSÃO
        # -------------------------------------------------
        schema_alvo = None
        nome_loja = ""
        
        # OBTÉM A SESSÃO E FORÇA ELA A SER UM DICIONÁRIO (Isto mata o erro list object has no attribute get)
        sessao_bruta = get_sessao_cliente(db, telefone_cliente)
        sessao_existente = {}
        
        if isinstance(sessao_bruta, list):
            sessao_existente = {"historico": sessao_bruta, "schema_alvo": None}
        elif isinstance(sessao_bruta, dict):
            sessao_existente = sessao_bruta
        
        lojistas = db.execute(text("SELECT codigo_loja, name FROM public.merchant")).fetchall()
        
        for loja in lojistas:
            if loja.codigo_loja and mensagem_usuario and loja.codigo_loja.lower() in mensagem_usuario.lower():
                schema_alvo = f"{loja.codigo_loja.lower()}_schema"
                nome_loja = loja.name
                break
                
        if not schema_alvo and sessao_existente:
            schema_alvo = sessao_existente.get("schema_alvo")
            if schema_alvo:
                codigo_loja_sessao = schema_alvo.replace("_schema", "")
                loja_db = db.execute(text("SELECT name FROM public.merchant WHERE codigo_loja = :code"), {"code": codigo_loja_sessao}).fetchone()
                if loja_db:
                    nome_loja = loja_db.name

        if not schema_alvo:
            mensagem_resgate = "Olá! ☀️ Eu sou a Lau, sua Central de Agendamentos. Para começarmos, com qual estabelecimento ou profissional você gostaria de agendar hoje?"
            enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=mensagem_resgate)
            return JSONResponse(content={"status": "resgate_enviado"}, status_code=200)

        db.execute(text(f"SET search_path TO {schema_alvo}"))
        db.commit()

        # -------------------------------------------------
        # PASSO 2: CONTROLE DE SAUDAÇÃO EXCLUSIVA POR TEMPO
        # -------------------------------------------------
        cliente = db.execute(text("SELECT id, nome, ultima_interacao FROM customers WHERE telefone = :tel"), {"tel": telefone_cliente}).fetchone()
        
        saudacao_fixa = ""
        agora = datetime.now()
        precisa_saudar = True
        
        if cliente and cliente.ultima_interacao:
            tempo_decorrido = agora - cliente.ultima_interacao
            if tempo_decorrido.total_seconds() < 7200:
                precisa_saudar = False

        if precisa_saudar:
            if 5 <= agora.hour < 12:
                periodo = "bom dia! ☀️"
            elif 12 <= agora.hour < 18:
                periodo = "boa tarde! 🌤️"
            else:
                periodo = "boa noite! 🌙"
            saudacao_fixa = f"Olá, {periodo}\nEu sou a Lau, secretária Virtual de {nome_loja}.\nComo posso te ajudar? 💁‍♀️\n\n"

        if not cliente:
            db.execute(text("INSERT INTO customers (telefone, ultima_interacao) VALUES (:tel, :now)"), {"tel": telefone_cliente, "now": agora})
            db.commit()
            cliente = db.execute(text("SELECT id, nome FROM customers WHERE telefone = :tel"), {"tel": telefone_cliente}).fetchone()
            contexto_cliente = "cliente_novo"
        else:
            db.execute(text("UPDATE customers SET ultima_interacao = :now WHERE id = :id"), {"now": agora, "id": cliente.id})
            db.commit()
            contexto_cliente = "cliente_novo" if not cliente.nome else "cliente_antigo"

        # -------------------------------------------------
        # PASSO 3: TRAVA DE AGENDAMENTO PENDENTE
        # -------------------------------------------------
        agendamento_pendente = db.execute(text("SELECT id FROM appointments WHERE customer_id = :c_id AND status = 'pendente'"), {"c_id": cliente.id}).fetchone()
        
        if agendamento_pendente:
            mensagem_trava = "Seu agendamento ainda está em análise pelo lojista. Assim que for confirmado, te aviso aqui! 😉"
            enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=mensagem_trava)
            return JSONResponse(content={"status": "trava_pendente_bloqueada"}, status_code=200)

        # -------------------------------------------------
        # PASSO 4: EXECUÇÃO E ANÁLISE DO MODELO DE IA
        # -------------------------------------------------
        historico = sessao_existente.get("historico", []) if sessao_existente else []
        historico.append({"role": "user", "content": mensagem_usuario})
        
        resposta_ia = await analisar_mensagem_com_ia(historico, contexto_cliente)
        
        nome_cliente_extraido = resposta_ia.get("nome_cliente")
        servico = resposta_ia.get("servico")
        data = resposta_ia.get("data")
        hora = resposta_ia.get("hora")
        texto_ia = resposta_ia.get("mensagem_resposta")

        if nome_cliente_extraido and nome_cliente_extraido != "null" and not cliente.nome:
            db.execute(text("UPDATE customers SET nome = :nome WHERE id = :id"), {"nome": nome_cliente_extraido, "id": cliente.id})
            db.commit()
            cliente = db.execute(text("SELECT id, nome FROM customers WHERE id = :id"), {"id": cliente.id}).fetchone()

        historico.append({"role": "assistant", "content": texto_ia})

        # -------------------------------------------------
        # PASSO 5: FECHAMENTO DO AGENDAMENTO E DISPARO DO MOCK
        # -------------------------------------------------
        if servico and data and hora and cliente.nome:
            db.execute(text("""
                INSERT INTO appointments (customer_id, servico, data_agendamento, hora_agendamento, status) 
                VALUES (:c_id, :servico, :data, :hora, 'pendente')
            """), {"c_id": cliente.id, "servico": servico, "data": data, "hora": hora})
            db.commit()
            
            encerrar_sessao_cliente(db, telefone_cliente)
            
            mensagem_envio = "Tudo certo! Enviei o seu pedido para o lojista e estou aguardando a confirmação. Te aviso já já!"
            enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=mensagem_envio)
            
            background_tasks.add_task(simular_confirmacao_lojista, telefone_cliente, servico, data, hora, schema_alvo)
            
        else:
            salvar_sessao_cliente(db, telefone_cliente, schema_alvo, {"historico": historico})
            mensagem_final = f"{saudacao_fixa}{texto_ia}" if saudacao_fixa else texto_ia
            enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=mensagem_final)

        return JSONResponse(content={"status": "sucesso"}, status_code=200)

    except Exception as e:
        print(f"❌ Erro crítico tratado no Webhook principal: {str(e)}")
        return JSONResponse(content={"status": "erro_interno_suprimido"}, status_code=200)