import asyncio
from datetime import datetime, timedelta, timezone
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
# DEDUPLICAÇÃO DE MENSAGENS (evita loop por retries da Meta)
# =========================================================
_mensagens_processadas: dict[str, float] = {}

def _ja_processou(message_id: str) -> bool:
    """Retorna True se a mensagem já foi processada. Limpa IDs antigos (>5min)."""
    agora = datetime.now().timestamp()
    # Limpar IDs com mais de 5 minutos
    ids_antigos = [mid for mid, ts in _mensagens_processadas.items() if agora - ts > 300]
    for mid in ids_antigos:
        del _mensagens_processadas[mid]
    
    if message_id in _mensagens_processadas:
        return True
    _mensagens_processadas[message_id] = agora
    return False

# =========================================================
# FUNÇÃO AUXILIAR: SAUDAÇÃO POR HORÁRIO
# =========================================================
def _saudacao_por_horario() -> str:
    hora = datetime.now().hour
    if hora < 12:
        return "Bom dia"
    elif hora < 18:
        return "Boa tarde"
    else:
        return "Boa noite"

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
        
        mensagem_sucesso = f"✅ Seu agendamento para {servico} no dia {data} às {hora} foi confirmado pelo lojista!"
        enviar_mensagem_whatsapp(numero_destino=telefone, texto=mensagem_sucesso)
    finally:
        db_async.close()

# =========================================================
# ROTA DE VALIDAÇÃO DO WEBHOOK (VERIFICAÇÃO DA META)
# =========================================================
@router.get("/webhook")
async def verify_webhook(request: Request):
    hub_mode = request.query_params.get("hub.mode")
    hub_verify_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")

    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        print("✅ Webhook verificado com sucesso!")
        return PlainTextResponse(content=hub_challenge, status_code=200)
    
    print("❌ Falha na verificação do Webhook.")
    return JSONResponse(content={"detail": "Verification failed"}, status_code=403)

# =========================================================
# ROTA DE RECEBIMENTO DE MENSAGENS DO WHATSAPP
# =========================================================
@router.post("/webhook")
async def receive_message(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        body = await request.json()
        
        # Estrutura básica do payload da Meta (entry e changes são LISTAS)
        entry_list = body.get("entry")
        if not entry_list or not isinstance(entry_list, list):
            return JSONResponse(content={"status": "ignorado"}, status_code=200)
        
        entry = entry_list[0]
        changes_list = entry.get("changes")
        if not changes_list or not isinstance(changes_list, list):
            return JSONResponse(content={"status": "ignorado"}, status_code=200)
        
        value = changes_list[0].get("value")
        if not value:
            return JSONResponse(content={"status": "ignorado"}, status_code=200)
        
        # Ignora mensagens de status de envio (entregue, lida)
        if "statuses" in value:
            return JSONResponse(content={"status": "status atualizado"}, status_code=200)

        if "messages" in value:
            mensagem = value["messages"][0]  # messages também é uma lista
            message_id = mensagem.get("id", "")
            telefone_cliente = mensagem["from"]
            
            # Proteção 1: Ignorar mensagens antigas (retries da Meta após restart)
            msg_timestamp = int(mensagem.get("timestamp", 0))
            agora_unix = int(datetime.now().timestamp())
            if msg_timestamp > 0 and (agora_unix - msg_timestamp) > 30:
                print(f"⏭️ Mensagem antiga ignorada ({agora_unix - msg_timestamp}s atrás): {message_id}")
                return JSONResponse(content={"status": "antiga"}, status_code=200)
            
            # Proteção 2: Deduplicação por message_id
            if _ja_processou(message_id):
                print(f"⏭️ Mensagem duplicada ignorada: {message_id}")
                return JSONResponse(content={"status": "duplicada"}, status_code=200)
            
            if mensagem["type"] == "text":
                texto_cliente = mensagem["text"]["body"]
            else:
                return JSONResponse(content={"status": "tipo de mensagem não suportado"}, status_code=200)

            print(f"\n📩 Mensagem Recebida de {telefone_cliente}: {texto_cliente}")

            # =========================================================
            # PASSO 1: IDENTIFICAR O LOJISTA (ROTEAMENTO)
            # =========================================================
            texto_lower = texto_cliente.lower()
            lojista_encontrado = None

            # Garante que estamos no schema público para consultar merchants
            db.execute(text("SET search_path TO public"))
            todos_lojistas = db.query(Merchant).all()
            for lojista in todos_lojistas:
                if lojista.nome_loja.lower() in texto_lower:
                    lojista_encontrado = lojista
                    print(f"🎯 Lojista Encontrado: {lojista.nome_loja}")
                    break
                    
            # =========================================================
            # PASSO 2: GERENCIAMENTO DE SESSÃO
            # =========================================================
            sessao_atual = get_sessao_cliente(db, telefone_cliente)
            trocou_de_loja = False
            
            if lojista_encontrado:
                if sessao_atual and sessao_atual.loja_atual != lojista_encontrado.nome_do_schema:
                    encerrar_sessao_cliente(db, telefone_cliente)
                    trocou_de_loja = True
                    sessao_atual = None 
                schema_alvo = lojista_encontrado.nome_do_schema
                nome_loja = lojista_encontrado.nome_loja
            elif sessao_atual:
                schema_alvo = sessao_atual.loja_atual
                lojista = db.query(Merchant).filter(Merchant.nome_do_schema == schema_alvo).first()
                nome_loja = lojista.nome_loja if lojista else "Loja"
            else:
                saudacao = _saudacao_por_horario()
                enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=f"{saudacao}! 🌻 Eu sou a Lau, secretária virtual. Para começarmos, me diga qual estabelecimento você procura.")
                return JSONResponse(content={"status": "recebido"}, status_code=200)

            # =========================================================
            # PASSO 3: BUSCAR CLIENTE NO SCHEMA DO LOJISTA
            # =========================================================
            db.execute(text(f"SET search_path TO {schema_alvo}"))
            cliente_db = db.execute(text("SELECT * FROM customers WHERE telefone_whatsapp = :tel"), {"tel": telefone_cliente}).fetchone()

            if not cliente_db:
                db.execute(text("INSERT INTO customers (nome, telefone_whatsapp) VALUES ('Cliente', :tel) ON CONFLICT DO NOTHING"), {"tel": telefone_cliente})
                db.commit()
                cliente_db = db.execute(text("SELECT * FROM customers WHERE telefone_whatsapp = :tel"), {"tel": telefone_cliente}).fetchone()
                contexto = "cliente_novo"
            else:
                contexto = "cliente_antigo"

            # Nome do cliente (None se desconhecido ou genérico)
            nome_cliente = cliente_db.nome if cliente_db and cliente_db.nome and cliente_db.nome != "Cliente" else None

            # =========================================================
            # PASSO 4: SAUDAÇÃO INTELIGENTE 🌻
            # =========================================================
            saudacao = _saudacao_por_horario()
            nome_para_saudar = f", {nome_cliente}" if nome_cliente else ""

            if not sessao_atual or trocou_de_loja:
                if lojista_encontrado and not trocou_de_loja:
                    # Loja mencionada na mensagem sem sessão prévia → usuário respondeu ao "qual estabelecimento?"
                    # A Lau já se apresentou na mensagem anterior, não repetir saudação
                    tipo_saudacao = "continuacao"
                    saudacao_fixa = ""
                else:
                    # TROCA DE LOJA → Saudação com apresentação
                    tipo_saudacao = "primeira_vez"
                    saudacao_fixa = f"{saudacao}{nome_para_saudar}! 🌻 Eu sou a Lau, secretária virtual. Como posso te ajudar hoje?\n\n"
            else:
                # Sessão ativa — verificar tempo desde última interação
                ultima = sessao_atual.ultima_interacao
                agora = datetime.now()
                
                # Tratar timezone: se ultima_interacao tem timezone, usar UTC aware
                if ultima and ultima.tzinfo is not None:
                    agora = datetime.now(timezone.utc)
                
                if ultima and (agora - ultima) >= timedelta(hours=2):
                    # RETORNO LONGO (≥ 2h) → Nova saudação por horário
                    tipo_saudacao = "retorno_longo"
                    saudacao_fixa = f"{saudacao}{nome_para_saudar}! 🌻 Eu sou a Lau, secretária virtual. Como posso te ajudar hoje?\n\n"
                else:
                    # RETORNO RÁPIDO (< 2h) ou conversa em andamento
                    tipo_saudacao = "retorno_rapido"
                    dados_sessao = sessao_atual.dados_sessao if isinstance(sessao_atual.dados_sessao, dict) else {}
                    ja_saudou = dados_sessao.get("ja_saudou", False)
                    
                    if not ja_saudou:
                        # Primeira msg desta "janela" de retorno rápido
                        if nome_cliente:
                            saudacao_fixa = f"Que bom que retornou, {nome_cliente}! Como posso te ajudar dessa vez?\n\n"
                        else:
                            saudacao_fixa = "Que bom que retornou! Como posso te ajudar dessa vez?\n\n"
                    else:
                        # Conversa em andamento, sem saudação
                        saudacao_fixa = ""

            print(f"🧠 Tipo saudação: {tipo_saudacao} | Nome: {nome_cliente or 'desconhecido'} | Loja: {nome_loja}")

            # =========================================================
            # PASSO 5: RECUPERAR O "ESTADO" E HISTÓRICO 🧠
            # =========================================================
            dados = sessao_atual.dados_sessao if sessao_atual and isinstance(sessao_atual.dados_sessao, dict) else {}
            
            # Em retorno longo ou troca de loja, limpar histórico e estado
            if tipo_saudacao in ("primeira_vez", "retorno_longo"):
                historico = []
                estado = {}
            else:
                historico = dados.get("historico", [])
                estado = dados.get("estado", {})

            historico.append({"role": "user", "content": texto_cliente})

            # =========================================================
            # PASSO 6: CHAMADA DA IA
            # =========================================================
            db.execute(text(f"SET search_path TO {schema_alvo}"))
            servicos_db = db.execute(text("SELECT nome FROM services")).fetchall()
            servicos_lista = [s.nome for s in servicos_db]
            
            resposta_ia = await analisar_mensagem_com_ia(historico, contexto, nome_cliente, servicos_disponiveis=servicos_lista)
            
            texto_ia = resposta_ia.get("mensagem_resposta") or "Como posso te ajudar?"
            historico.append({"role": "assistant", "content": texto_ia})

            if resposta_ia.get("servico"): estado["servico"] = resposta_ia.get("servico")
            if resposta_ia.get("data"): estado["data"] = resposta_ia.get("data")
            if resposta_ia.get("hora"): estado["hora"] = resposta_ia.get("hora")
            
            # Captura nome — funciona tanto para cliente novo quanto antigo sem nome
            if resposta_ia.get("nome_cliente") and (not nome_cliente):
                db.execute(text("UPDATE customers SET nome = :nome WHERE telefone_whatsapp = :tel"), {"nome": resposta_ia["nome_cliente"], "tel": telefone_cliente})
                db.commit()
                nome_cliente = resposta_ia["nome_cliente"]

            cliente = db.execute(text("SELECT * FROM customers WHERE telefone_whatsapp = :tel"), {"tel": telefone_cliente}).fetchone()

            # =========================================================
            # PASSO 7: VALIDAÇÃO FINAL E AGENDAMENTO
            # =========================================================
            print(f"📦 Estado Acumulado: {estado}")
            
            if estado.get("servico") and estado.get("data") and estado.get("hora") and cliente.nome and cliente.nome != "Cliente":
                
                servico_escolhido = estado.get("servico")
                servico_db = db.execute(text("SELECT id FROM services WHERE nome ILIKE :nome LIMIT 1"), {"nome": f"%{servico_escolhido}%"}).fetchone()
                
                if not servico_db:
                    salvar_sessao_cliente(db, telefone_cliente, schema_alvo, {"historico": historico, "estado": estado, "ja_saudou": True})
                    enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=f"{saudacao_fixa}Poxa, não encontrei o serviço '{servico_escolhido}' na nossa lista. Que outro serviço gostaria?")
                    return JSONResponse(content={"status": "sucesso"}, status_code=200)
                    
                service_id = servico_db.id
                data = estado.get("data")
                hora = estado.get("hora")

                db.execute(text("""
                    INSERT INTO appointments (customer_id, service_id, data_agendamento, horario_agendamento, status) 
                    VALUES (:c_id, :s_id, :data, :hora, 'pendente')
                """), {"c_id": cliente.id, "s_id": service_id, "data": data, "hora": hora})
                db.commit()
                
                encerrar_sessao_cliente(db, telefone_cliente)
                
                # Formatar data para exibição ao usuário (YYYY-MM-DD -> DD/MM/YYYY)
                try:
                    data_exibicao = datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
                except ValueError:
                    data_exibicao = data
                
                nome_final = cliente.nome if cliente.nome and cliente.nome != "Cliente" else ""
                mensagem_envio = f"{saudacao_fixa}Tudo certo, {nome_final}! Enviei o seu pedido de {servico_escolhido} para o dia {data_exibicao} às {hora} ao lojista e estou a aguardar a confirmação. Aviso já já!"
                enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=mensagem_envio)
                
                background_tasks.add_task(simular_confirmacao_lojista, telefone_cliente, servico_escolhido, data_exibicao, hora, schema_alvo)
                print("⏳ [MOCK] Confirmação automática agendada...")
                
            else:
                salvar_sessao_cliente(db, telefone_cliente, schema_alvo, {"historico": historico, "estado": estado, "ja_saudou": True})
                mensagem_final = f"{saudacao_fixa}{texto_ia}" if saudacao_fixa else texto_ia
                enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=mensagem_final)

        return JSONResponse(content={"status": "sucesso"}, status_code=200)

    except Exception as e:
        print(f"❌ Erro crítico tratado no Webhook principal: {str(e)}")
        return JSONResponse(content={"status": "erro", "detalhe": str(e)}, status_code=500)