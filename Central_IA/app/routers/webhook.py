import logging
import re
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import VERIFY_TOKEN
from app.database import get_db, validar_schema
from app.models import Merchant
from app.services.openai_service import analisar_mensagem_com_ia
from app.services.whatsapp_service import enviar_mensagem_whatsapp
from app.services.push_service import enviar_notificacao_push
from app.services.session_service import get_sessao_cliente, salvar_sessao_cliente, encerrar_sessao_cliente

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Webhook"])

# =========================================================
# DEDUPLICAÇÃO DE MENSAGENS (evita loop por retries da Meta)
# Nota: em memória — sobrevive apenas enquanto o processo está vivo.
# Para multi-worker/produção, migrar para Redis.
# =========================================================
_mensagens_processadas: dict[str, float] = {}

def _ja_processou(message_id: str) -> bool:
    """Retorna True se a mensagem já foi processada. Limpa IDs antigos (>5min)."""
    agora = datetime.now().timestamp()
    ids_antigos = [mid for mid, ts in _mensagens_processadas.items() if agora - ts > 300]
    for mid in ids_antigos:
        del _mensagens_processadas[mid]
    
    if message_id in _mensagens_processadas:
        return True
    _mensagens_processadas[message_id] = agora
    return False

# =========================================================
# ROTEAMENTO DE LOJISTA POR NOME (palavra inteira)
# =========================================================
def _encontrar_lojista(texto: str, lojistas: list[Merchant]) -> Merchant | None:
    """
    Procura o nome do lojista no texto usando correspondência de palavra inteira
    para evitar falsos positivos (ex: "bar" em "barbeamento").
    """
    texto_lower = texto.lower()
    for lojista in lojistas:
        # Escapa caracteres especiais do nome e exige palavra inteira
        nome_escaped = re.escape(lojista.nome_loja.lower())
        if re.search(rf'\b{nome_escaped}\b', texto_lower):
            return lojista
    return None

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
# ROTA DE VALIDAÇÃO DO WEBHOOK (VERIFICAÇÃO DA META)
# =========================================================
@router.get("/webhook")
async def verify_webhook(request: Request):
    hub_mode = request.query_params.get("hub.mode")
    hub_verify_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")

    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        logger.info("Webhook verificado com sucesso pela Meta.")
        return PlainTextResponse(content=hub_challenge, status_code=200)
    
    logger.warning("Falha na verificação do Webhook — token inválido.")
    return JSONResponse(content={"detail": "Verification failed"}, status_code=403)

# =========================================================
# ROTA DE RECEBIMENTO DE MENSAGENS DO WHATSAPP
# =========================================================
@router.post("/webhook")
async def receive_message(request: Request, db: Session = Depends(get_db)):
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
            mensagem = value["messages"][0]
            message_id = mensagem.get("id", "")
            telefone_cliente = mensagem["from"]
            
            # Proteção 1: Ignorar mensagens muito antigas (retries da Meta após restart)
            # Aumentado para 300s (5 min) para não descartar mensagens em picos de carga.
            msg_timestamp = int(mensagem.get("timestamp", 0))
            agora_unix = int(datetime.now().timestamp())
            if msg_timestamp > 0 and (agora_unix - msg_timestamp) > 300:
                logger.info(
                    "Mensagem antiga ignorada (%ds atrás): %s",
                    agora_unix - msg_timestamp, message_id
                )
                return JSONResponse(content={"status": "antiga"}, status_code=200)
            
            # Proteção 2: Deduplicação por message_id
            if _ja_processou(message_id):
                logger.info("Mensagem duplicada ignorada: %s", message_id)
                return JSONResponse(content={"status": "duplicada"}, status_code=200)
            
            if mensagem["type"] == "text":
                texto_cliente = mensagem["text"]["body"]
            else:
                return JSONResponse(content={"status": "tipo de mensagem não suportado"}, status_code=200)

            logger.info("Mensagem recebida de %s: %s", telefone_cliente, texto_cliente[:80])

            # =========================================================
            # PASSO 1: IDENTIFICAR O LOJISTA (ROTEAMENTO)
            # =========================================================
            # Garante que estamos no schema público para consultar merchants
            db.execute(text("SET search_path TO public"))
            todos_lojistas = db.query(Merchant).all()

            lojista_encontrado = _encontrar_lojista(texto_cliente, todos_lojistas)
            if lojista_encontrado:
                logger.info("Lojista identificado: %s", lojista_encontrado.nome_loja)
                    
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
                enviar_mensagem_whatsapp(
                    numero_destino=telefone_cliente,
                    texto=f"{saudacao}! 🌻 Eu sou a Lau, secretária virtual. Para começarmos, me diga qual estabelecimento você procura."
                )
                return JSONResponse(content={"status": "recebido"}, status_code=200)

            # =========================================================
            # PASSO 3: BUSCAR CLIENTE NO SCHEMA DO LOJISTA
            # =========================================================
            # Validação anti SQL injection antes de SET search_path
            schema_alvo_seguro = validar_schema(str(schema_alvo))
            db.execute(text(f"SET search_path TO {schema_alvo_seguro}, public"))
            
            cliente_db = db.execute(
                text("SELECT * FROM customers WHERE telefone_whatsapp = :tel"),
                {"tel": telefone_cliente}
            ).mappings().fetchone()

            if not cliente_db:
                db.execute(
                    text("INSERT INTO customers (nome, telefone_whatsapp) VALUES ('Cliente', :tel) ON CONFLICT DO NOTHING"),
                    {"tel": telefone_cliente}
                )
                db.commit()
                cliente_db = db.execute(
                    text("SELECT * FROM customers WHERE telefone_whatsapp = :tel"),
                    {"tel": telefone_cliente}
                ).mappings().fetchone()
                contexto = "cliente_novo"
            else:
                contexto = "cliente_antigo"

            # Nome do cliente (None se desconhecido ou genérico)
            nome_cliente = (
                cliente_db.get("nome")
                if cliente_db and cliente_db.get("nome") and cliente_db.get("nome") != "Cliente"
                else None
            )

            # =========================================================
            # PASSO 4: SAUDAÇÃO INTELIGENTE 🌻
            # =========================================================
            saudacao = _saudacao_por_horario()
            nome_para_saudar = f", {nome_cliente}" if nome_cliente else ""

            if not sessao_atual or trocou_de_loja:
                if lojista_encontrado and not trocou_de_loja:
                    tipo_saudacao = "continuacao"
                    saudacao_fixa = ""
                else:
                    tipo_saudacao = "primeira_vez"
                    saudacao_fixa = f"{saudacao}{nome_para_saudar}! 🌻 Eu sou a Lau, secretária virtual. Como posso te ajudar hoje?\n\n"
            else:
                ultima = sessao_atual.ultima_interacao
                agora = datetime.now()
                
                if ultima and ultima.tzinfo is not None:
                    agora = datetime.now(timezone.utc)
                
                if ultima and (agora - ultima) >= timedelta(hours=2):
                    tipo_saudacao = "retorno_longo"
                    saudacao_fixa = f"{saudacao}{nome_para_saudar}! 🌻 Eu sou a Lau, secretária virtual. Como posso te ajudar hoje?\n\n"
                else:
                    tipo_saudacao = "retorno_rapido"
                    dados_sessao = sessao_atual.dados_sessao if isinstance(sessao_atual.dados_sessao, dict) else {}
                    ja_saudou = dados_sessao.get("ja_saudou", False)
                    
                    if not ja_saudou:
                        if nome_cliente:
                            saudacao_fixa = f"Que bom que retornou, {nome_cliente}! Como posso te ajudar dessa vez?\n\n"
                        else:
                            saudacao_fixa = "Que bom que retornou! Como posso te ajudar dessa vez?\n\n"
                    else:
                        saudacao_fixa = ""

            logger.info(
                "Saudação: %s | cliente=%s | loja=%s",
                tipo_saudacao, nome_cliente or "desconhecido", nome_loja
            )

            # =========================================================
            # PASSO 5: RECUPERAR O "ESTADO" E HISTÓRICO 🧠
            # =========================================================
            dados = sessao_atual.dados_sessao if sessao_atual and isinstance(sessao_atual.dados_sessao, dict) else {}
            
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
            # Reafirma search_path após possíveis queries de sessão
            db.execute(text(f"SET search_path TO {schema_alvo_seguro}, public"))
            servicos_db = db.execute(text("SELECT nome FROM services")).mappings().fetchall()
            servicos_lista = [str(s.get("nome")) for s in servicos_db if s.get("nome") is not None]
            
            resposta_ia = await analisar_mensagem_com_ia(historico, contexto, nome_cliente, servicos_disponiveis=servicos_lista)
            
            texto_ia = resposta_ia.get("mensagem_resposta") or "Como posso te ajudar?"
            historico.append({"role": "assistant", "content": texto_ia})

            if resposta_ia.get("servico"): estado["servico"] = resposta_ia.get("servico")
            if resposta_ia.get("data"): estado["data"] = resposta_ia.get("data")
            if resposta_ia.get("hora"): estado["hora"] = resposta_ia.get("hora")
            
            # Captura nome — funciona tanto para cliente novo quanto antigo sem nome
            if resposta_ia.get("nome_cliente") and (not nome_cliente):
                db.execute(
                    text("UPDATE customers SET nome = :nome WHERE telefone_whatsapp = :tel"),
                    {"nome": resposta_ia["nome_cliente"], "tel": telefone_cliente}
                )
                db.commit()
                nome_cliente = resposta_ia["nome_cliente"]

            cliente = db.execute(
                text("SELECT * FROM customers WHERE telefone_whatsapp = :tel"),
                {"tel": telefone_cliente}
            ).mappings().fetchone()

            # =========================================================
            # PASSO 7: VALIDAÇÃO FINAL E AGENDAMENTO
            # =========================================================
            logger.debug("Estado acumulado: %s", estado)
            
            if (
                estado.get("servico") and estado.get("data") and estado.get("hora")
                and cliente
                and cliente.get("nome") and cliente.get("nome") != "Cliente"
            ):
                servico_escolhido = estado.get("servico")
                servico_db = db.execute(
                    text("SELECT id FROM services WHERE nome ILIKE :nome LIMIT 1"),
                    {"nome": f"%{servico_escolhido}%"}
                ).mappings().fetchone()
                
                if not servico_db:
                    salvar_sessao_cliente(db, telefone_cliente, str(schema_alvo_seguro), {"historico": historico, "estado": estado, "ja_saudou": True})
                    enviar_mensagem_whatsapp(
                        numero_destino=telefone_cliente,
                        texto=f"{saudacao_fixa}Poxa, não encontrei o serviço '{servico_escolhido}' na nossa lista. Que outro serviço gostaria?"
                    )
                    return JSONResponse(content={"status": "sucesso"}, status_code=200)
                    
                service_id = servico_db.get("id")
                data = estado.get("data")
                hora = estado.get("hora")

                db.execute(text("""
                    INSERT INTO appointments (customer_id, service_id, data_agendamento, horario_agendamento, status) 
                    VALUES (:c_id, :s_id, :data, :hora, 'pendente')
                """), {"c_id": cliente.get("id"), "s_id": service_id, "data": data, "hora": hora})
                db.commit()
                
                encerrar_sessao_cliente(db, telefone_cliente)
                
                try:
                    data_exibicao = datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
                except (ValueError, TypeError):
                    data_exibicao = str(data)
                
                nome_final = (
                    cliente.get("nome")
                    if cliente and cliente.get("nome") and cliente.get("nome") != "Cliente"
                    else ""
                )
                mensagem_envio = (
                    f"{saudacao_fixa}Tudo certo, {nome_final}! Salvei a sua intenção de agendamento para "
                    f"{servico_escolhido} no dia {data_exibicao} às {hora}. "
                    f"Aguarde um instante, o lojista já vai confirmar a disponibilidade e eu te aviso aqui!"
                )
                enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=mensagem_envio)
                
                # Enviar Push Notification para o app do Lojista
                # Refaz query no schema public para encontrar o merchant
                db.execute(text("SET search_path TO public"))
                merchant_alvo = db.query(Merchant).filter(
                    Merchant.nome_do_schema == str(schema_alvo_seguro)
                ).first()
                if merchant_alvo and merchant_alvo.push_token:
                    enviar_notificacao_push(
                        push_token=merchant_alvo.push_token,
                        titulo="Nova Confirmação Pendente! 🔔",
                        corpo=f"{nome_final} quer agendar {servico_escolhido} para {data_exibicao} às {hora}.",
                        dados={"tela": "pending"}
                    )
                
                logger.info(
                    "Agendamento pendente criado: cliente=%s | serviço=%s | data=%s | hora=%s | loja=%s",
                    nome_final, servico_escolhido, data_exibicao, hora, nome_loja
                )
                
            else:
                salvar_sessao_cliente(db, telefone_cliente, str(schema_alvo_seguro), {"historico": historico, "estado": estado, "ja_saudou": True})
                mensagem_final = f"{saudacao_fixa}{texto_ia}" if saudacao_fixa else texto_ia
                enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=mensagem_final)

        return JSONResponse(content={"status": "sucesso"}, status_code=200)

    except ValueError as e:
        # Schema inválido — responde 200 para não fazer a Meta retentar
        logger.error("Schema inválido no webhook: %s", e)
        return JSONResponse(content={"status": "erro_schema"}, status_code=200)

    except Exception as e:
        logger.exception("Erro crítico no webhook: %s", e)
        return JSONResponse(content={"status": "erro", "detalhe": str(e)}, status_code=500)