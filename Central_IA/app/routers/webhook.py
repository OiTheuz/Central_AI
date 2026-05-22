import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import VERIFY_TOKEN
from app.database import get_db, SessionLocal
from app.models import Merchant
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
            AND customer_id = (SELECT id FROM customers WHERE telefone_whatsapp = :tel LIMIT 1)
        """), {"tel": telefone})
        db_async.commit()
        
        mensagem_sucesso = f"✅ Tudo certo! Seu agendamento de {servico} foi confirmado para {data} às {hora}! Posso te ajudar com mais alguma coisa?"
        enviar_mensagem_whatsapp(numero_destino=telefone, texto=mensagem_sucesso)
        print(f"🎯 [MOCK] Agendamento de {telefone} confirmado automaticamente com sucesso.")
    except Exception as e:
        print(f"❌ Erro no mock de confirmação automática: {str(e)}")
    finally:
        db_async.close()


def _buscar_service_id(db: Session, schema: str, nome_servico: str) -> int | None:
    """Busca o ID do serviço na tabela services pelo nome (exato ou parcial)."""
    resultado = db.execute(
        text(f"SELECT id FROM {schema}.services WHERE LOWER(nome) = LOWER(:nome) LIMIT 1"),
        {"nome": nome_servico}
    ).fetchone()
    if resultado:
        return resultado[0]

    # Busca parcial (ex: cliente diz "corte" e existe "Corte de Cabelo")
    resultado_parcial = db.execute(
        text(f"SELECT id FROM {schema}.services WHERE LOWER(nome) LIKE '%' || LOWER(:nome) || '%' LIMIT 1"),
        {"nome": nome_servico}
    ).fetchone()
    return resultado_parcial[0] if resultado_parcial else None


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
        
        # 🛡️ ESCUDO ANTI-QUEDA: Navega o JSON da Meta com segurança
        if not isinstance(body, dict) or body.get("object") != "whatsapp_business_account":
            return JSONResponse(content={"status": "ignorado"}, status_code=200)

        entry_list = body.get("entry", [])
        if not entry_list or not isinstance(entry_list, list):
            return JSONResponse(content={"status": "ignorado_sem_entry"}, status_code=200)
        
        # entry é uma LISTA — pegamos o primeiro item
        primeiro_entry = entry_list[0]
        if not isinstance(primeiro_entry, dict):
            return JSONResponse(content={"status": "ignorado_entry_invalido"}, status_code=200)

        changes_list = primeiro_entry.get("changes", [])
        if not changes_list or not isinstance(changes_list, list):
            return JSONResponse(content={"status": "ignorado_sem_changes"}, status_code=200)
        
        # changes é uma LISTA — pegamos o primeiro item
        primeiro_change = changes_list[0]
        if not isinstance(primeiro_change, dict):
            return JSONResponse(content={"status": "ignorado_change_invalido"}, status_code=200)

        value = primeiro_change.get("value", {})
        if not isinstance(value, dict) or "messages" not in value:
            # Não é mensagem (pode ser status de leitura/entrega). Ignoramos em paz.
            return JSONResponse(content={"status": "ignorado_sem_messages"}, status_code=200)

        messages_list = value["messages"]
        if not isinstance(messages_list, list) or not messages_list:
            return JSONResponse(content={"status": "ignorado_messages_vazio"}, status_code=200)

        # messages é uma LISTA — pegamos a primeira mensagem
        message_data = messages_list[0]
        if not isinstance(message_data, dict):
            return JSONResponse(content={"status": "ignorado_message_invalida"}, status_code=200)

        # Ignora se não for texto (áudio, imagem, etc.)
        if message_data.get("type") != "text":
            return JSONResponse(content={"status": "ignorado_nao_texto"}, status_code=200)

        telefone_cliente = message_data.get("from")
        texto_obj = message_data.get("text", {})
        
        if not isinstance(texto_obj, dict) or not texto_obj.get("body"):
            return JSONResponse(content={"status": "ignorado_sem_texto"}, status_code=200)
            
        mensagem_usuario = texto_obj["body"]
        print(f"📩 Mensagem recebida de {telefone_cliente}: '{mensagem_usuario}'")

        # -------------------------------------------------
        # PASSO 1: IDENTIFICAÇÃO DO LOJISTA (via sessão ou mensagem)
        # -------------------------------------------------
        schema_alvo = None
        nome_loja = ""
        
        # Verifica sessão ativa primeiro
        sessao_ativa = get_sessao_cliente(db, telefone_cliente)
        
        if sessao_ativa:
            schema_alvo = str(sessao_ativa.loja_atual)
            # Busca o nome da loja pelo schema
            merchant = db.query(Merchant).filter(Merchant.nome_do_schema == schema_alvo).first()
            nome_loja = merchant.nome_loja if merchant else ""
            print(f"🧠 Memória Ativa: Cliente em atendimento com -> {schema_alvo}")
        else:
            # Tenta identificar pela mensagem
            merchants = db.query(Merchant).all()
            for m in merchants:
                if m.nome_loja.lower() in mensagem_usuario.lower() or m.codigo_loja.lower() in mensagem_usuario.lower():
                    schema_alvo = str(m.nome_do_schema)
                    nome_loja = m.nome_loja
                    salvar_sessao_cliente(db, telefone_cliente, schema_alvo)
                    print(f"🆕 Nova sessão iniciada com -> {schema_alvo}")
                    break

        if not schema_alvo:
            mensagem_resgate = "Olá! ☀️ Eu sou a Lau, sua Central de Agendamentos. Para começarmos, com qual estabelecimento ou profissional você gostaria de agendar hoje?"
            enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=mensagem_resgate)
            return JSONResponse(content={"status": "resgate_enviado"}, status_code=200)

        # -------------------------------------------------
        # PASSO 2: CONTROLE DE SAUDAÇÃO POR TEMPO (2h)
        # -------------------------------------------------
        # Usa telefone_whatsapp (nome real da coluna no banco)
        cliente = db.execute(
            text(f"SELECT id, nome, ultima_interacao FROM {schema_alvo}.customers WHERE telefone_whatsapp = :tel"),
            {"tel": telefone_cliente}
        ).fetchone()
        
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
            # Cliente novo — registra imediatamente
            db.execute(
                text(f"INSERT INTO {schema_alvo}.customers (nome, telefone_whatsapp, ultima_interacao) VALUES ('Cliente', :tel, :now)"),
                {"tel": telefone_cliente, "now": agora}
            )
            db.commit()
            cliente = db.execute(
                text(f"SELECT id, nome FROM {schema_alvo}.customers WHERE telefone_whatsapp = :tel"),
                {"tel": telefone_cliente}
            ).fetchone()
            contexto_cliente = "cliente_novo"
        else:
            db.execute(
                text(f"UPDATE {schema_alvo}.customers SET ultima_interacao = :now WHERE id = :id"),
                {"now": agora, "id": cliente.id}
            )
            db.commit()
            contexto_cliente = "cliente_novo" if not cliente.nome or cliente.nome == "Cliente" else "cliente_antigo"

        # -------------------------------------------------
        # PASSO 3: TRAVA DE AGENDAMENTO PENDENTE
        # -------------------------------------------------
        agendamento_pendente = db.execute(
            text(f"SELECT id FROM {schema_alvo}.appointments WHERE customer_id = :c_id AND status = 'pendente'"),
            {"c_id": cliente.id}
        ).fetchone()
        
        if agendamento_pendente:
            mensagem_trava = f"{saudacao_fixa}Seu agendamento ainda está em análise pelo lojista. Assim que for confirmado, te aviso aqui! 😉"
            enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=mensagem_trava)
            return JSONResponse(content={"status": "trava_pendente"}, status_code=200)

        # -------------------------------------------------
        # PASSO 4: CHAMADA DA IA
        # -------------------------------------------------
        sessao_atual = get_sessao_cliente(db, telefone_cliente)
        if sessao_atual and sessao_atual.dados_sessao:
            historico = sessao_atual.dados_sessao.get("historico", []) if isinstance(sessao_atual.dados_sessao, dict) else []
        else:
            historico = []

        historico.append({"role": "user", "content": mensagem_usuario})
        
        resposta_ia = await analisar_mensagem_com_ia(historico, contexto_cliente)
        
        nome_cliente_extraido = resposta_ia.get("nome_cliente")
        servico = resposta_ia.get("servico")
        data = resposta_ia.get("data")
        hora = resposta_ia.get("hora")
        texto_ia = resposta_ia.get("mensagem_resposta", "Qual serviço, data e horário você gostaria?")

        # Atualiza nome do cliente se a IA extraiu
        if nome_cliente_extraido and nome_cliente_extraido != "null" and (not cliente.nome or cliente.nome == "Cliente"):
            db.execute(
                text(f"UPDATE {schema_alvo}.customers SET nome = :nome WHERE id = :id"),
                {"nome": nome_cliente_extraido, "id": cliente.id}
            )
            db.commit()
            # Recarrega cliente para ter o nome atualizado
            cliente = db.execute(
                text(f"SELECT id, nome FROM {schema_alvo}.customers WHERE id = :id"),
                {"id": cliente.id}
            ).fetchone()

        historico.append({"role": "assistant", "content": texto_ia})

        # -------------------------------------------------
        # PASSO 5: FECHAMENTO DO AGENDAMENTO + MOCK
        # -------------------------------------------------
        if servico and data and hora and cliente.nome and cliente.nome != "Cliente":
            # Buscar service_id pelo nome do serviço
            service_id = _buscar_service_id(db, schema_alvo, servico)
            
            if not service_id:
                # Serviço não encontrado — avisa o cliente
                servicos = db.execute(text(f"SELECT nome FROM {schema_alvo}.services")).fetchall()
                lista = ", ".join([s[0] for s in servicos]) if servicos else "nenhum cadastrado"
                resposta_erro = f"{saudacao_fixa}Não encontrei o serviço \"{servico}\" no catálogo. Os serviços disponíveis são: {lista}. Qual você gostaria?"
                salvar_sessao_cliente(db, telefone_cliente, schema_alvo, {"historico": historico})
                enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=resposta_erro)
                return JSONResponse(content={"status": "servico_nao_encontrado"}, status_code=200)

            # Insere o agendamento com service_id (FK)
            db.execute(text(f"""
                INSERT INTO {schema_alvo}.appointments (customer_id, service_id, data_agendamento, horario_agendamento, status) 
                VALUES (:c_id, :s_id, :data, :hora, 'pendente')
            """), {"c_id": cliente.id, "s_id": service_id, "data": data, "hora": hora})
            db.commit()
            
            # Limpa sessão
            salvar_sessao_cliente(db, telefone_cliente, schema_alvo, {"historico": []})
            
            mensagem_envio = f"{saudacao_fixa}Tudo certo! Enviei o seu pedido para o lojista e estou aguardando a confirmação. Te aviso já já!"
            enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=mensagem_envio)
            
            # Dispara mock de confirmação
            background_tasks.add_task(simular_confirmacao_lojista, telefone_cliente, servico, data, hora, schema_alvo)
            print("⏳ [MOCK] Confirmação automática agendada para 5 segundos...")
            
        else:
            # Ainda faltam dados — salva histórico e responde
            salvar_sessao_cliente(db, telefone_cliente, schema_alvo, {"historico": historico})
            mensagem_final = f"{saudacao_fixa}{texto_ia}" if saudacao_fixa else texto_ia
            enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=mensagem_final)

        return JSONResponse(content={"status": "sucesso"}, status_code=200)

    except Exception as e:
        print(f"❌ Erro crítico tratado no Webhook principal: {str(e)}")
        return JSONResponse(content={"status": "erro_interno_suprimido"}, status_code=200)