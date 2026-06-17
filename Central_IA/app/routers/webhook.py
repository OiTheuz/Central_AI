import logging
import re
from collections import OrderedDict
from datetime import datetime, time as time_type, timedelta
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import VERIFY_TOKEN
from app.database import get_public_db, validar_schema
from app.models import Merchant
from app.services.openai_service import analisar_mensagem_com_ia, extrair_data_hora_com_ia
from app.services.whatsapp_service import (
    enviar_mensagem_whatsapp, 
    enviar_menu_intencao_whatsapp,
    enviar_menu_servicos_whatsapp
)
from app.services.push_service import enviar_notificacao_push
from app.services.session_service import get_sessao_cliente, salvar_sessao_cliente, encerrar_sessao_cliente

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Webhook"])

# =========================================================
# DEDUPLICAÇÃO DE MENSAGENS (evita loop por retries da Meta)
# Nota: em memória — sobrevive apenas enquanto o processo está vivo.
# Para multi-worker/produção, migrar para Redis.
# =========================================================
_mensagens_processadas: OrderedDict[str, float] = OrderedDict()
_MAX_CACHE_SIZE = 10_000

def _ja_processou(message_id: str) -> bool:
    """Retorna True se a mensagem já foi processada. Limpa IDs antigos (>5min)
    e mantém o cache com no máximo _MAX_CACHE_SIZE entradas."""
    agora = datetime.now().timestamp()
    # Limpa entradas expiradas (> 5 min)
    while _mensagens_processadas:
        oldest_id, oldest_ts = next(iter(_mensagens_processadas.items()))
        if agora - oldest_ts > 300:
            del _mensagens_processadas[oldest_id]
        else:
            break
    
    if message_id in _mensagens_processadas:
        return True
    
    _mensagens_processadas[message_id] = agora
    # Evita crescimento ilimitado
    while len(_mensagens_processadas) > _MAX_CACHE_SIZE:
        _mensagens_processadas.popitem(last=False)
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
        # Correspondência exata por ID do menu interativo do WhatsApp
        if texto.strip() == f"LOJA_{lojista.codigo_loja}":
            return lojista
        
        # Correspondência por palavra inteira no nome da loja
        if lojista.nome_loja:
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
async def receive_message(request: Request, db: Session = Depends(get_public_db)):
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
            elif mensagem["type"] == "interactive" and mensagem["interactive"]["type"] == "list_reply":
                texto_cliente = mensagem["interactive"]["list_reply"]["id"]
            else:
                return JSONResponse(content={"status": "tipo de mensagem não suportado"}, status_code=200)

            logger.info("Mensagem recebida de %s: %s", telefone_cliente, texto_cliente[:80])

            # =========================================================
            # ROTEAMENTO WHITE-LABEL (Por Número de Destino)
            # =========================================================
            numero_destino = value.get("metadata", {}).get("display_phone_number")
            if not numero_destino:
                logger.error("Payload não contém metadata.display_phone_number. Impossível rotear.")
                return JSONResponse(content={"status": "erro_roteamento"}, status_code=200)
            
            # Limpa qualquer formatação que a Meta possa mandar (+, espaços)
            numero_destino_limpo = re.sub(r'\D', '', str(numero_destino))
            
            db.execute(text("SET search_path TO public"))
            lojista = db.query(Merchant).filter(Merchant.numero_whatsapp == numero_destino_limpo).first()
            
            if not lojista:
                logger.warning("Mensagem recebida para número não registrado: %s", numero_destino_limpo)
                # Responde 200 para que a Meta não fique retentando indefinidamente
                return JSONResponse(content={"status": "numero_nao_registrado"}, status_code=200)
            
            schema_alvo = lojista.nome_do_schema
            nome_loja = lojista.nome_loja

            # =========================================================
            # GERENCIAMENTO DE SESSÃO E TIMEOUT
            # =========================================================
            sessao_atual = get_sessao_cliente(db, telefone_cliente)
            
            # Se o cliente mandou mensagem para uma loja diferente da que ele estava, reseta a sessão
            if sessao_atual and sessao_atual.loja_atual != schema_alvo:
                logger.info("Cliente %s mudou da loja %s para a loja %s. Resetando sessão.", 
                            telefone_cliente, sessao_atual.loja_atual, schema_alvo)
                encerrar_sessao_cliente(db, telefone_cliente)
                sessao_atual = None

            if sessao_atual:
                ultima = sessao_atual.ultima_interacao
                if ultima:
                    # Garante comparação sempre entre datetimes sem timezone (naive)
                    # para evitar TypeError entre offset-aware e offset-naive
                    ultima_naive = ultima.replace(tzinfo=None) if ultima.tzinfo else ultima
                    agora_naive = datetime.now()
                    if (agora_naive - ultima_naive) >= timedelta(hours=1):
                        logger.info("Sessao expirada para %s (mais de 1h).", telefone_cliente)
                        encerrar_sessao_cliente(db, telefone_cliente)
                        sessao_atual = None
            
            dados_sessao = sessao_atual.dados_sessao if sessao_atual and isinstance(sessao_atual.dados_sessao, dict) else {}
            estado_atual = dados_sessao.get("state")
            
            # =========================================================
            # MÁQUINA DE ESTADOS DO ATENDIMENTO INICIAL
            # =========================================================
            
            # Intercepta se não for LLM_CONVERSATION
            if not sessao_atual or estado_atual != "LLM_CONVERSATION":
                saudacao = _saudacao_por_horario()
                
                # Estado Inicial: Cliente mandou primeira mensagem
                if not sessao_atual:
                    texto_pergunta = (
                        f"{saudacao}! 🌻 Que bom ter você por aqui.\n\n"
                        f"Eu sou a Lau, a secretária virtual exclusiva da {nome_loja}. "
                        f"Estou aqui para organizar o seu atendimento num piscar de olhos! \n\n"
                        f"Você gostaria de agendar um horário ou consultar seus agendamentos?"
                    )
                    enviar_menu_intencao_whatsapp(telefone_cliente, texto_pergunta)
                    salvar_sessao_cliente(db, telefone_cliente, schema_alvo, dados_sessao={"state": "AGUARDANDO_INTENCAO"})
                    return JSONResponse(content={"status": "recebido"}, status_code=200)

                # Processar estados intermediários
                if estado_atual == "AGUARDANDO_INTENCAO":
                    if texto_cliente in ["INTENT_AGENDAR", "INTENT_CONSULTAR"]:
                        dados_sessao["intencao"] = texto_cliente
                        dados_sessao["state"] = "LLM_CONVERSATION"
                        salvar_sessao_cliente(db, telefone_cliente, schema_alvo, dados_sessao)
                        
                        if texto_cliente == "INTENT_CONSULTAR":
                            # Se quer consultar, não precisa de serviço. Passa direto pra IA
                            texto_cliente = "Gostaria de consultar o status dos meus agendamentos."
                            # Deixa cair pro fluxo LLM abaixo
                        else:
                            # Quer agendar. Verifica se tem serviços antes de mandar pra IA.
                            schema_alvo_seguro = validar_schema(schema_alvo)
                            db.execute(text(f"SET search_path TO {schema_alvo_seguro}, public"))
                            try:
                                servicos_rows = db.execute(text("SELECT id FROM services")).fetchall()
                                if not servicos_rows:
                                    enviar_mensagem_whatsapp(telefone_cliente, "Este estabelecimento ainda não possui serviços disponíveis no momento.")
                                    return JSONResponse(content={"status": "recebido"}, status_code=200)
                                
                                # Forja a mensagem para que a IA inicie listando os serviços disponíveis
                                texto_cliente = "Quero fazer um agendamento. Pode me listar quais serviços vocês têm disponíveis?"
                                # Deixa cair pro fluxo LLM abaixo
                            except Exception as e:
                                logger.error("Erro ao buscar serviços: %s", e)
                                enviar_mensagem_whatsapp(telefone_cliente, "Ocorreu um erro ao buscar os serviços.")
                                return JSONResponse(content={"status": "recebido"}, status_code=200)
                    else:
                        enviar_menu_intencao_whatsapp(telefone_cliente, "Por favor, selecione uma das opções abaixo usando os botões:")
                        return JSONResponse(content={"status": "recebido"}, status_code=200)

                # ── Estado: Aguardando resposta pós-consulta (quer fazer alteração?) ──
                if estado_atual == "AGUARDANDO_POS_CONSULTA":
                    resposta_lower = texto_cliente.lower().strip()
                    palavras_sim = ["sim", "quero", "gostaria", "pode", "s", "yes", "ok", "claro", "vou", "quero sim"]
                    palavras_nao = ["não", "nao", "n", "no", "obrigado", "obrigada", "tá bom", "ta bom", "tudo bem", "tudo certo", "pode ser", "até", "ate"]
                    
                    quer_alterar = any(p in resposta_lower for p in palavras_sim)
                    nao_quer_alterar = any(p in resposta_lower for p in palavras_nao)
                    
                    if nao_quer_alterar and not quer_alterar:
                        encerrar_sessao_cliente(db, telefone_cliente)
                        enviar_mensagem_whatsapp(
                            numero_destino=telefone_cliente,
                            texto="Tudo bem! 😊 Qualquer coisa é só mandar um *Oi* que estarei aqui. Até logo! 👋"
                        )
                        return JSONResponse(content={"status": "sucesso"}, status_code=200)
                    elif quer_alterar:
                        dados_sessao["state"] = "AGUARDANDO_TIPO_SOLICITACAO"
                        salvar_sessao_cliente(db, telefone_cliente, schema_alvo, dados_sessao)
                        enviar_mensagem_whatsapp(
                            numero_destino=telefone_cliente,
                            texto="Entendido! Você gostaria de solicitar um *Reagendamento* ou um *Cancelamento*?\n\n"
                                  "Digite a opção desejada."
                        )
                        return JSONResponse(content={"status": "sucesso"}, status_code=200)
                    else:
                        # Resposta ambígua — pede confirmação
                        enviar_mensagem_whatsapp(
                            numero_destino=telefone_cliente,
                            texto="Desculpe, não entendi bem. 😊 Você gostaria de fazer alguma alteração em seus agendamentos? Responda *Sim* ou *Não*."
                        )
                        return JSONResponse(content={"status": "sucesso"}, status_code=200)

                # ── Estado: Aguardando tipo da solicitação (cancelamento ou reagendamento) ──
                if estado_atual == "AGUARDANDO_TIPO_SOLICITACAO":
                    resposta_lower = texto_cliente.lower().strip()
                    
                    is_cancelamento = "cancel" in resposta_lower
                    is_reagendamento = "reagen" in resposta_lower or "remarc" in resposta_lower or "mudar" in resposta_lower or "alterar" in resposta_lower
                    
                    if is_cancelamento or is_reagendamento:
                        tipo = "cancelamento" if is_cancelamento else "reagendamento"
                        dados_sessao["tipo_solicitacao"] = tipo
                        dados_sessao["state"] = "AGUARDANDO_TICKET"
                        salvar_sessao_cliente(db, telefone_cliente, schema_alvo, dados_sessao)
                        
                        # Reexibe a lista de agendamentos com tickets para facilitar
                        schema_alvo_seguro = validar_schema(str(schema_alvo))
                        db.execute(text(f"SET search_path TO {schema_alvo_seguro}, public"))
                        query_tickets = text("""
                            SELECT a.numero_ticket, a.data_agendamento, a.horario_agendamento, a.status, s.nome AS servico
                            FROM appointments a
                            LEFT JOIN services s ON a.service_id = s.id
                            LEFT JOIN customers c ON a.customer_id = c.id
                            WHERE c.telefone_whatsapp = :tel
                              AND a.data_agendamento >= CURRENT_DATE
                              AND a.status IN ('pendente', 'aprovado', 'confirmado')
                              AND (a.tipo_pendencia IS NULL)
                            ORDER BY a.data_agendamento, a.horario_agendamento
                        """)
                        ags_ticket = db.execute(query_tickets, {"tel": telefone_cliente}).mappings().fetchall()
                        
                        tipo_label = "cancelamento" if tipo == "cancelamento" else "reagendamento"
                        if ags_ticket:
                            linhas = [f"Qual agendamento você gostaria de solicitar o {tipo_label}?\n\nInforme o *número do ticket*:\n"]
                            for ag in ags_ticket:
                                ticket = ag["numero_ticket"] or "?"
                                data_str = ag["data_agendamento"].strftime("%d/%m/%Y") if ag["data_agendamento"] else "???"
                                hora_str = ag["horario_agendamento"].strftime("%H:%M") if ag["horario_agendamento"] else "???"
                                servico_nome = ag["servico"] or "Serviço"
                                status_str = ag["status"].capitalize()
                                linhas.append(f"🎫 Ticket *#{ticket}* — {servico_nome}\n   📅 {data_str} às {hora_str} | {status_str}")
                            enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto="\n\n".join(linhas))
                        else:
                            encerrar_sessao_cliente(db, telefone_cliente)
                            enviar_mensagem_whatsapp(
                                numero_destino=telefone_cliente,
                                texto="Parece que não há agendamentos futuros para alterar. Qualquer coisa é só mandar um *Oi*! 👋"
                            )
                        return JSONResponse(content={"status": "sucesso"}, status_code=200)
                    else:
                        enviar_mensagem_whatsapp(
                            numero_destino=telefone_cliente,
                            texto="Não entendi. 😊 Por favor, responda *Cancelamento* ou *Reagendamento*."
                        )
                        return JSONResponse(content={"status": "sucesso"}, status_code=200)

                # ── Estado: Aguardando número do ticket ──
                if estado_atual == "AGUARDANDO_TICKET":
                    # Tenta extrair um número da mensagem do cliente
                    numeros_encontrados = re.findall(r'\d+', texto_cliente)
                    if not numeros_encontrados:
                        enviar_mensagem_whatsapp(
                            numero_destino=telefone_cliente,
                            texto="Por favor, informe o *número do ticket* do agendamento (somente o número). 🎫"
                        )
                        return JSONResponse(content={"status": "sucesso"}, status_code=200)
                    
                    ticket_informado = int(numeros_encontrados[0])
                    tipo_solicitacao = dados_sessao.get("tipo_solicitacao", "cancelamento")
                    
                    # Valida se o ticket pertence ao cliente e está em um status válido
                    schema_alvo_seguro = validar_schema(str(schema_alvo))
                    db.execute(text(f"SET search_path TO {schema_alvo_seguro}, public"))
                    ag_encontrado = db.execute(text("""
                        SELECT a.id, a.numero_ticket, a.data_agendamento, a.horario_agendamento,
                               a.status, s.nome AS servico, c.nome AS cliente_nome
                        FROM appointments a
                        LEFT JOIN services s ON a.service_id = s.id
                        LEFT JOIN customers c ON a.customer_id = c.id
                        WHERE c.telefone_whatsapp = :tel
                          AND a.numero_ticket = :ticket
                          AND a.data_agendamento >= CURRENT_DATE
                          AND a.status IN ('pendente', 'aprovado', 'confirmado')
                          AND (a.tipo_pendencia IS NULL)
                    """), {"tel": telefone_cliente, "ticket": ticket_informado}).mappings().fetchone()
                    
                    if not ag_encontrado:
                        enviar_mensagem_whatsapp(
                            numero_destino=telefone_cliente,
                            texto=f"Não encontrei nenhum agendamento com o ticket *#{ticket_informado}* nos seus próximos compromissos. 🤔\n\nVerifique o número e tente novamente."
                        )
                        return JSONResponse(content={"status": "sucesso"}, status_code=200)
                    
                    # Salva o agendamento alvo na sessão
                    dados_sessao["agendamento_id_alvo"] = ag_encontrado["id"]
                    dados_sessao["ticket_alvo"] = ticket_informado
                    
                    data_fmt = ag_encontrado["data_agendamento"].strftime("%d/%m/%Y") if ag_encontrado["data_agendamento"] else "???"
                    hora_fmt = ag_encontrado["horario_agendamento"].strftime("%H:%M") if ag_encontrado["horario_agendamento"] else "???"
                    servico_fmt = ag_encontrado["servico"] or "Serviço"
                    
                    if tipo_solicitacao == "cancelamento":
                        # Pede motivo antes de criar a pendência
                        dados_sessao["agendamento_id_alvo"] = ag_encontrado["id"]
                        dados_sessao["ticket_alvo"] = ticket_informado
                        dados_sessao["state"] = "AGUARDANDO_MOTIVO_CANCELAMENTO"
                        salvar_sessao_cliente(db, telefone_cliente, schema_alvo, dados_sessao)
                        enviar_mensagem_whatsapp(
                            numero_destino=telefone_cliente,
                            texto=(
                                f"Entendido! Para registrar o cancelamento do seu *{servico_fmt}* "
                                f"marcado para {data_fmt} às {hora_fmt}, "
                                f"precisamos do motivo.\n\n"
                                f"Por favor, escolha uma das opções abaixo:\n\n"
                                f"1️⃣ Compromisso de última hora\n"
                                f"2️⃣ Problema de saúde\n"
                                f"3️⃣ Mudança de planos\n"
                                f"4️⃣ Não vou mais precisar do serviço\n"
                                f"5️⃣ Outro (descreva brevemente)"
                            )
                        )
                        return JSONResponse(content={"status": "sucesso"}, status_code=200)
                    
                    else:  # reagendamento
                        dados_sessao["state"] = "AGUARDANDO_NOVA_DATA_HORA"
                        salvar_sessao_cliente(db, telefone_cliente, schema_alvo, dados_sessao)
                        enviar_mensagem_whatsapp(
                            numero_destino=telefone_cliente,
                            texto=(
                                f"Entendido! Vou solicitar o reagendamento do seu *{servico_fmt}* "
                                f"que está marcado para {data_fmt} às {hora_fmt}.\n\n"
                                f"📅 Qual seria a nova *data e horário* de sua preferência?"
                            )
                        )
                        return JSONResponse(content={"status": "sucesso"}, status_code=200)

                # ── Estado: Aguardando motivo do cancelamento ──
                if estado_atual == "AGUARDANDO_MOTIVO_CANCELAMENTO":
                    resposta_lower = texto_cliente.strip()
                    motivos = {
                        "1": "Compromisso de última hora",
                        "2": "Problema de saúde",
                        "3": "Mudança de planos",
                        "4": "Não vou mais precisar do serviço",
                    }
                    motivo_texto = motivos.get(resposta_lower)
                    if not motivo_texto:
                        # Número 5 ou qualquer texto livre → usa o texto do cliente
                        if resposta_lower == "5":
                            dados_sessao["state"] = "AGUARDANDO_MOTIVO_LIVRE"
                            salvar_sessao_cliente(db, telefone_cliente, schema_alvo, dados_sessao)
                            enviar_mensagem_whatsapp(
                                numero_destino=telefone_cliente,
                                texto="Por favor, descreva brevemente o motivo do cancelamento:"
                            )
                            return JSONResponse(content={"status": "sucesso"}, status_code=200)
                        else:
                            # Texto livre direto — aceita como motivo
                            motivo_texto = texto_cliente.strip()

                    # Criar a pendência de cancelamento com o motivo
                    schema_alvo_seguro = validar_schema(str(schema_alvo))
                    db.execute(text(f"SET search_path TO {schema_alvo_seguro}, public"))
                    ag_id_alvo = dados_sessao.get("agendamento_id_alvo")

                    if ag_id_alvo:
                        ag_ref = db.execute(
                            text("SELECT * FROM appointments WHERE id = :id"),
                            {"id": ag_id_alvo}
                        ).mappings().fetchone()

                        if ag_ref:
                            max_ticket = db.execute(
                                text("SELECT COALESCE(MAX(numero_ticket), 0) FROM appointments")
                            ).scalar() or 0
                            novo_ticket = max_ticket + 1

                            db.execute(text("""
                                INSERT INTO appointments
                                    (customer_id, service_id, data_agendamento, horario_agendamento,
                                     status, origem, tipo_pendencia, numero_ticket, motivo_cancelamento)
                                SELECT
                                    customer_id, service_id, data_agendamento, horario_agendamento,
                                    'pendente', 'whatsapp_lau', 'cancelamento', :novo_ticket, :motivo
                                FROM appointments
                                WHERE id = :ag_id
                            """), {"ag_id": ag_id_alvo, "novo_ticket": novo_ticket, "motivo": motivo_texto})
                            db.commit()

                            # Push notification ao lojista
                            db.execute(text("SET search_path TO public"))
                            merchant_alvo = db.query(Merchant).filter(
                                Merchant.nome_do_schema == schema_alvo_seguro
                            ).first()
                            if merchant_alvo and merchant_alvo.push_token:
                                nome_push_row = db.execute(
                                    text(f"SELECT nome FROM {schema_alvo_seguro}.customers WHERE telefone_whatsapp = :tel"),
                                    {"tel": telefone_cliente}
                                ).fetchone()
                                nome_push = (nome_push_row[0] if nome_push_row else None) or "Cliente"
                                enviar_notificacao_push(
                                    push_token=merchant_alvo.push_token,
                                    titulo="Solicitação de Cancelamento 🔴",
                                    corpo=f"{nome_push} quer cancelar um agendamento. Motivo: {motivo_texto}.",
                                    dados={"tela": "pending"}
                                )

                    encerrar_sessao_cliente(db, telefone_cliente)
                    enviar_mensagem_whatsapp(
                        numero_destino=telefone_cliente,
                        texto=(
                            "Solicitação de cancelamento registrada com sucesso! ✅\n\n"
                            "O estabelecimento foi notificado e está ciente da sua solicitação. "
                            "Qualquer coisa, é só mandar um *Oi*! 👋"
                        )
                    )
                    return JSONResponse(content={"status": "sucesso"}, status_code=200)

                # ── Estado: Aguardando motivo livre do cancelamento ──
                if estado_atual == "AGUARDANDO_MOTIVO_LIVRE":
                    motivo_texto = texto_cliente.strip() or "Outro"
                    # Redireciona para o estado de AGUARDANDO_MOTIVO_CANCELAMENTO com texto livre
                    dados_sessao["state"] = "AGUARDANDO_MOTIVO_CANCELAMENTO"
                    salvar_sessao_cliente(db, telefone_cliente, schema_alvo, dados_sessao)
                    # Reprocessa como se o cliente tivesse enviado o motivo diretamente
                    # Cria a pendência com o texto livre
                    schema_alvo_seguro = validar_schema(str(schema_alvo))
                    db.execute(text(f"SET search_path TO {schema_alvo_seguro}, public"))
                    ag_id_alvo = dados_sessao.get("agendamento_id_alvo")
                    if ag_id_alvo:
                        ag_ref = db.execute(
                            text("SELECT * FROM appointments WHERE id = :id"),
                            {"id": ag_id_alvo}
                        ).mappings().fetchone()
                        if ag_ref:
                            max_ticket = db.execute(
                                text("SELECT COALESCE(MAX(numero_ticket), 0) FROM appointments")
                            ).scalar() or 0
                            novo_ticket = max_ticket + 1
                            db.execute(text("""
                                INSERT INTO appointments
                                    (customer_id, service_id, data_agendamento, horario_agendamento,
                                     status, origem, tipo_pendencia, numero_ticket, motivo_cancelamento)
                                SELECT
                                    customer_id, service_id, data_agendamento, horario_agendamento,
                                    'pendente', 'whatsapp_lau', 'cancelamento', :novo_ticket, :motivo
                                FROM appointments
                                WHERE id = :ag_id
                            """), {"ag_id": ag_id_alvo, "novo_ticket": novo_ticket, "motivo": motivo_texto})
                            db.commit()
                            db.execute(text("SET search_path TO public"))
                            merchant_alvo = db.query(Merchant).filter(
                                Merchant.nome_do_schema == schema_alvo_seguro
                            ).first()
                            if merchant_alvo and merchant_alvo.push_token:
                                nome_push_row = db.execute(
                                    text(f"SELECT nome FROM {schema_alvo_seguro}.customers WHERE telefone_whatsapp = :tel"),
                                    {"tel": telefone_cliente}
                                ).fetchone()
                                nome_push = (nome_push_row[0] if nome_push_row else None) or "Cliente"
                                enviar_notificacao_push(
                                    push_token=merchant_alvo.push_token,
                                    titulo="Solicitação de Cancelamento 🔴",
                                    corpo=f"{nome_push} quer cancelar. Motivo: {motivo_texto}.",
                                    dados={"tela": "pending"}
                                )
                    encerrar_sessao_cliente(db, telefone_cliente)
                    enviar_mensagem_whatsapp(
                        numero_destino=telefone_cliente,
                        texto=(
                            "Solicitação de cancelamento registrada com sucesso! ✅\n\n"
                            "O estabelecimento foi notificado e está ciente da sua solicitação. "
                            "Qualquer coisa, é só mandar um *Oi*! 👋"
                        )
                    )
                    return JSONResponse(content={"status": "sucesso"}, status_code=200)

                # ── Estado: Aguardando nova data/hora para reagendamento ──
                if estado_atual == "AGUARDANDO_NOVA_DATA_HORA":
                    # Usa o LLM apenas para extrair data e hora da mensagem do cliente
                    resposta_data_hora = await extrair_data_hora_com_ia(texto_cliente, nome_loja)
                    nova_data = resposta_data_hora.get("data")
                    nova_hora = resposta_data_hora.get("hora")
                    
                    if not nova_data or not nova_hora:
                        enviar_mensagem_whatsapp(
                            numero_destino=telefone_cliente,
                            texto="Não consegui identificar a data e horário. 😊 Por favor, informe no formato: *dia/mês às HH:MM* (ex: 25/07 às 14:30)."
                        )
                        return JSONResponse(content={"status": "sucesso"}, status_code=200)

                    # ── Verificação de conflito para o novo horário ──
                    schema_alvo_seguro = validar_schema(str(schema_alvo))
                    db.execute(text(f"SET search_path TO {schema_alvo_seguro}, public"))
                    db.execute(text("SET search_path TO public"))
                    merchant_config_reag = db.query(Merchant).filter(
                        Merchant.nome_do_schema == schema_alvo_seguro
                    ).first()
                    db.execute(text(f"SET search_path TO {schema_alvo_seguro}, public"))

                    duracao_reag = 30  # duração padrão
                    ag_id_alvo_check = dados_sessao.get("agendamento_id_alvo")
                    if ag_id_alvo_check:
                        s_info = db.execute(text("""
                            SELECT s.duracao_minutos FROM appointments a
                            LEFT JOIN services s ON a.service_id = s.id
                            WHERE a.id = :id
                        """), {"id": ag_id_alvo_check}).fetchone()
                        if s_info and s_info[0]:
                            duracao_reag = int(s_info[0])

                    permite_sobreposicao_reag = bool(
                        merchant_config_reag.permitir_sobreposicao if merchant_config_reag else False
                    )

                    if not permite_sobreposicao_reag:
                        hora_nova_obj = datetime.strptime(nova_hora, "%H:%M").time()
                        fim_novo = (datetime.combine(datetime.today(), hora_nova_obj) + timedelta(minutes=duracao_reag)).time()
                        ags_dia_reag = db.execute(text("""
                            SELECT a.horario_agendamento, COALESCE(s.duracao_minutos, 30) AS dur
                            FROM appointments a
                            LEFT JOIN services s ON a.service_id = s.id
                            WHERE a.data_agendamento = :data AND a.status NOT IN ('recusado', 'cancelado')
                            ORDER BY a.horario_agendamento
                        """), {"data": nova_data}).mappings().fetchall()

                        conflito_reag = False
                        for ag in ags_dia_reag:
                            ag_ini = ag["horario_agendamento"]
                            if isinstance(ag_ini, str):
                                ag_ini = datetime.strptime(ag_ini, "%H:%M").time()
                            ag_fim = (datetime.combine(datetime.today(), ag_ini) + timedelta(minutes=ag["dur"])).time()
                            if hora_nova_obj < ag_fim and fim_novo > ag_ini:
                                conflito_reag = True
                                break

                        if conflito_reag:
                            horarios_ocup = []
                            for ag in ags_dia_reag:
                                ag_ini = ag["horario_agendamento"]
                                if isinstance(ag_ini, str):
                                    ag_ini = datetime.strptime(ag_ini, "%H:%M").time()
                                ag_fim = (datetime.combine(datetime.today(), ag_ini) + timedelta(minutes=ag["dur"])).time()
                                horarios_ocup.append((ag_ini, ag_fim))

                            h_abre_r = merchant_config_reag.horario_abertura if merchant_config_reag else "08:00"
                            h_fecha_r = merchant_config_reag.horario_fechamento if merchant_config_reag else "18:00"
                            abertura_r = datetime.strptime(h_abre_r, "%H:%M").time()
                            fechamento_r = datetime.strptime(h_fecha_r, "%H:%M").time()

                            slots_antes, slots_depois = [], []
                            cursor_r = datetime.combine(datetime.today(), abertura_r)
                            fecha_r = datetime.combine(datetime.today(), fechamento_r)
                            hora_nova_dt = datetime.combine(datetime.today(), hora_nova_obj)

                            while cursor_r + timedelta(minutes=duracao_reag) <= fecha_r:
                                s_ini = cursor_r.time()
                                s_fim = (cursor_r + timedelta(minutes=duracao_reag)).time()
                                livre = all(
                                    not (s_ini < oc_fim and s_fim > oc_ini)
                                    for oc_ini, oc_fim in horarios_ocup
                                )
                                if livre:
                                    if cursor_r < hora_nova_dt:
                                        slots_antes.append(s_ini.strftime("%H:%M"))
                                    else:
                                        slots_depois.append(s_ini.strftime("%H:%M"))
                                cursor_r += timedelta(minutes=30)

                            sugestao_antes = slots_antes[-1] if slots_antes else None
                            sugestao_depois = slots_depois[0] if slots_depois else None
                            sugestoes_reag = [s for s in [sugestao_antes, sugestao_depois] if s]

                            msg_conflito_reag = f"Poxa, o horário das {nova_hora} já está ocupado nessa data. 😊 "
                            if len(sugestoes_reag) == 2:
                                msg_conflito_reag += f"Tenho disponibilidade às *{sugestoes_reag[0]}* ou às *{sugestoes_reag[1]}*. Qual você prefere?"
                            elif len(sugestoes_reag) == 1:
                                msg_conflito_reag += f"O horário mais próximo disponível é às *{sugestoes_reag[0]}*. Podemos reagendar para esse horário?"
                            else:
                                msg_conflito_reag += "Infelizmente não há mais horários disponíveis nesse dia. Que tal outra data?"

                            enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=msg_conflito_reag)
                            return JSONResponse(content={"status": "sucesso"}, status_code=200)
                    db.execute(text(f"SET search_path TO {schema_alvo_seguro}, public"))
                    ag_id_alvo = dados_sessao.get("agendamento_id_alvo")
                    
                    if ag_id_alvo:
                        ag_original = db.execute(
                            text("SELECT * FROM appointments WHERE id = :id"),
                            {"id": ag_id_alvo}
                        ).mappings().fetchone()
                        
                        if ag_original:
                            max_ticket = db.execute(
                                text("SELECT COALESCE(MAX(numero_ticket), 0) FROM appointments")
                            ).scalar()
                            novo_ticket = (max_ticket or 0) + 1
                            
                            db.execute(text("""
                                INSERT INTO appointments
                                    (customer_id, service_id, data_agendamento, horario_agendamento,
                                     status, origem, tipo_pendencia, reagendamento_data, reagendamento_hora,
                                     numero_ticket)
                                VALUES
                                    (:c_id, :s_id, :data_orig, :hora_orig,
                                     'pendente', 'whatsapp_lau', 'reagendamento', :reag_data, :reag_hora,
                                     :novo_ticket)
                            """), {
                                "c_id": ag_original["customer_id"],
                                "s_id": ag_original["service_id"],
                                "data_orig": ag_original["data_agendamento"],
                                "hora_orig": ag_original["horario_agendamento"],
                                "reag_data": nova_data,
                                "reag_hora": nova_hora,
                                "novo_ticket": novo_ticket,
                            })
                            db.commit()
                    
                    # Formata para exibição
                    try:
                        nova_data_fmt = datetime.strptime(nova_data, "%Y-%m-%d").strftime("%d/%m/%Y")
                    except (ValueError, TypeError):
                        nova_data_fmt = nova_data
                    
                    encerrar_sessao_cliente(db, telefone_cliente)
                    enviar_mensagem_whatsapp(
                        numero_destino=telefone_cliente,
                        texto=(
                            f"Solicitação de reagendamento registrada! ✅\n\n"
                            f"📅 Nova data solicitada: *{nova_data_fmt} às {nova_hora}*\n\n"
                            f"O estabelecimento irá confirmar o novo horário em breve. "
                            f"Qualquer coisa, é só mandar um *Oi*! 👋"
                        )
                    )
                    
                    # Push notification ao lojista
                    db.execute(text("SET search_path TO public"))
                    merchant_alvo = db.query(Merchant).filter(
                        Merchant.nome_do_schema == schema_alvo_seguro
                    ).first()
                    if merchant_alvo and merchant_alvo.push_token:
                        from app.services.push_service import enviar_notificacao_push
                        db.execute(text(f"SET search_path TO {schema_alvo_seguro}, public"))
                        nome_push_row = db.execute(
                            text("SELECT nome FROM customers WHERE telefone_whatsapp = :tel"),
                            {"tel": telefone_cliente}
                        ).fetchone()
                        nome_push = (nome_push_row[0] if nome_push_row else None) or "Cliente"
                        enviar_notificacao_push(
                            push_token=merchant_alvo.push_token,
                            titulo="Solicitação de Reagendamento 🟡",
                            corpo=f"{nome_push} quer reagendar para {nova_data_fmt} às {nova_hora}.",
                            dados={"tela": "pending"}
                        )
                    return JSONResponse(content={"status": "sucesso"}, status_code=200)
                
            # =========================================================
            # FLUXO LLM (Cliente já informou intenção e o roteamento foi feito)
            # =========================================================
            if not sessao_atual:
                # Sessão desapareceu após a máquina de estados — não deveria acontecer.
                # Responde 200 para a Meta não retentar (o cliente terá de recomeçar).
                logger.error("Sessao desapareceu antes do fluxo LLM para %s", telefone_cliente)
                return JSONResponse(content={"status": "erro_sessao"}, status_code=200)

            # Puxa o nome da loja para context
            db.execute(text("SET search_path TO public"))
            lojista = db.query(Merchant).filter(Merchant.nome_do_schema == schema_alvo).first()
            nome_loja = lojista.nome_loja if lojista else "Loja"

            # Busca ou cria o cliente no schema correto — UPSERT robusto
            schema_alvo_seguro = validar_schema(str(schema_alvo))
            db.execute(text(f"SET search_path TO {schema_alvo_seguro}, public"))
            
            cliente_db = db.execute(
                text("SELECT * FROM customers WHERE telefone_whatsapp = :tel"),
                {"tel": telefone_cliente}
            ).mappings().fetchone()

            if not cliente_db:
                try:
                    # UPSERT: insere ou retorna o existente em caso de conflito
                    result = db.execute(
                        text("""
                            INSERT INTO customers (nome, telefone_whatsapp) 
                            VALUES ('Cliente', :tel) 
                            ON CONFLICT (telefone_whatsapp) DO UPDATE 
                                SET telefone_whatsapp = EXCLUDED.telefone_whatsapp
                            RETURNING *
                        """),
                        {"tel": telefone_cliente}
                    )
                    db.commit()
                    cliente_db = result.mappings().fetchone()
                except Exception as e:
                    db.rollback()
                    logger.error("Erro ao criar cliente novo %s: %s", telefone_cliente, e)

                # Fallback: tenta buscar novamente após possível conflito
                if not cliente_db:
                    db.execute(text(f"SET search_path TO {schema_alvo_seguro}, public"))
                    cliente_db = db.execute(
                        text("SELECT * FROM customers WHERE telefone_whatsapp = :tel"),
                        {"tel": telefone_cliente}
                    ).mappings().fetchone()

            # Proteção final: se não conseguiu criar nem encontrar, responde ao cliente
            if not cliente_db:
                logger.error(
                    "CRÍTICO: impossível criar/encontrar cliente %s no schema %s",
                    telefone_cliente, schema_alvo
                )
                enviar_mensagem_whatsapp(
                    numero_destino=telefone_cliente,
                    texto="Desculpe, tive um problema técnico ao iniciar seu atendimento. Por favor, tente novamente em alguns instantes. 🙏"
                )
                return JSONResponse(content={"status": "erro_cliente"}, status_code=200)

            # Re-garante search_path após possível rollback/commit da criação do cliente
            db.execute(text(f"SET search_path TO {schema_alvo_seguro}, public"))

            # Contexto baseado na presença de nome REAL — não apenas na existência do registo.
            # Se o cliente existir mas o nome ainda for o placeholder 'Cliente' (ou vazio),
            # ele é tratado como 'cliente_novo' para a IA perguntar o nome corretamente.
            _nome_db = cliente_db.get("nome") if cliente_db else None
            tem_nome_real = bool(_nome_db and _nome_db.strip() and _nome_db.strip() not in ("Cliente", ""))
            contexto = "cliente_antigo" if tem_nome_real else "cliente_novo"

            nome_cliente = (
                cliente_db.get("nome")
                if cliente_db and cliente_db.get("nome") and cliente_db.get("nome") != "Cliente"
                else None
            )

            saudacao_fixa = ""

            # =========================================================
            # PASSO 5: RECUPERAR O "ESTADO" E HISTÓRICO 🧠
            # =========================================================
            dados = sessao_atual.dados_sessao if sessao_atual and isinstance(sessao_atual.dados_sessao, dict) else {}
            historico = dados.get("historico", [])
            estado = dados.get("estado", {})

            # Limita histórico a 20 mensagens para evitar crescimento ilimitado do JSON
            # e reduzir custo/latência com a OpenAI em conversas longas.
            MAX_HISTORICO = 20
            if len(historico) > MAX_HISTORICO:
                historico = historico[-MAX_HISTORICO:]

            historico.append({"role": "user", "content": texto_cliente})

            # =========================================================
            # PASSO 6: CHAMADA DA IA
            # =========================================================
            # Reafirma search_path após possíveis queries de sessão
            db.execute(text(f"SET search_path TO {schema_alvo_seguro}, public"))
            servicos_db = db.execute(text("SELECT nome, preco, duracao_minutos FROM services")).mappings().fetchall()
            servicos_lista = []
            for s in servicos_db:
                nome = s.get("nome")
                if nome:
                    preco = s.get("preco")
                    duracao = s.get("duracao_minutos")
                    try:
                        preco_float = float(preco) if preco is not None else None
                        preco_str = f"R$ {preco_float:.2f}".replace('.', ',') if preco_float is not None else "Preço a consultar"
                    except (ValueError, TypeError):
                        preco_str = "Preço a consultar"
                        
                    duracao_str = f"{duracao} min" if duracao else "Duração variável"
                    # Passamos a duração separadamente para a IA saber, mas instruímos ela a não mostrar
                    servicos_lista.append(f"• {nome} ({preco_str}) [Duração interna: {duracao_str}]")
            
            servicos_formatados = "\n".join(servicos_lista) if servicos_lista else ""
            
            resposta_ia = await analisar_mensagem_com_ia(historico, contexto, nome_cliente, servicos_disponiveis=servicos_formatados, nome_loja=nome_loja)
            
            texto_ia = resposta_ia.get("mensagem_resposta") or "Como posso te ajudar?"

            # =========================================================
            # ENCERRAMENTO DE ATENDIMENTO VOLUNTÁRIO
            # =========================================================
            if resposta_ia.get("intencao") == "encerrar":
                encerrar_sessao_cliente(db, telefone_cliente)
                
                # Resetar a última interação do cliente no banco para forçar nova saudação no futuro
                if cliente_db:
                    db.execute(
                        text(f"UPDATE {schema_alvo_seguro}.customers SET ultima_interacao = :data_passado WHERE id = :c_id"),
                        {"data_passado": datetime.now() - timedelta(hours=24), "c_id": cliente_db.get("id")}
                    )
                    db.commit()

                mensagem_despedida = "Atendimento encerrado! Se precisar de mais alguma coisa depois, estarei por aqui. Até logo! 👋"
                enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=mensagem_despedida)
                logger.info("Atendimento encerrado voluntariamente pelo cliente: %s", telefone_cliente)
                return JSONResponse(content={"status": "sucesso"}, status_code=200)

            # =========================================================
            # CONSULTA DE AGENDAMENTOS
            # =========================================================
            if resposta_ia.get("intencao") == "consultar":
                db.execute(text(f"SET search_path TO {schema_alvo_seguro}, public"))
                
                query_consulta = text("""
                    SELECT a.id, a.numero_ticket, a.data_agendamento, a.horario_agendamento,
                           a.status, s.nome AS servico
                    FROM appointments a
                    LEFT JOIN services s ON a.service_id = s.id
                    LEFT JOIN customers c ON a.customer_id = c.id
                    WHERE c.telefone_whatsapp = :tel
                      AND a.data_agendamento >= CURRENT_DATE
                      AND a.status IN ('pendente', 'aprovado', 'confirmado')
                      AND (a.tipo_pendencia IS NULL)
                    ORDER BY a.data_agendamento, a.horario_agendamento
                """)
                
                agendamentos_cliente = db.execute(query_consulta, {"tel": telefone_cliente}).mappings().fetchall()
                
                if agendamentos_cliente:
                    linhas_msg = ["Aqui estão os seus próximos agendamentos:\n"]
                    for ag in agendamentos_cliente:
                        data_str = ag["data_agendamento"].strftime("%d/%m/%Y") if ag["data_agendamento"] else "???"
                        hora_str = ag["horario_agendamento"].strftime("%H:%M") if ag["horario_agendamento"] else "???"
                        servico_nome = ag["servico"] or "Serviço não especificado"
                        status_str = ag["status"].capitalize()
                        ticket = ag["numero_ticket"] or "?"
                        linhas_msg.append(
                            f"🎫 Ticket *#{ticket}* — {servico_nome}\n"
                            f"   📅 {data_str} às {hora_str} | {status_str}"
                        )
                    linhas_msg.append("\nGostaria de fazer alguma alteração em algum dos agendamentos?")
                    msg_consulta = "\n\n".join(linhas_msg)
                    
                    # Salva estado para aguardar resposta do cliente
                    dados_sessao["state"] = "AGUARDANDO_POS_CONSULTA"
                    salvar_sessao_cliente(db, telefone_cliente, schema_alvo, dados_sessao)
                else:
                    msg_consulta = "Verifiquei aqui e você não tem nenhum agendamento futuro conosco. Deseja marcar um horário agora? 😊"
                    
                enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=msg_consulta)
                return JSONResponse(content={"status": "sucesso"}, status_code=200)

            historico.append({"role": "assistant", "content": texto_ia})

            if resposta_ia.get("servico"): estado["servico"] = resposta_ia.get("servico")
            if resposta_ia.get("data"): estado["data"] = resposta_ia.get("data")
            if resposta_ia.get("hora"): estado["hora"] = resposta_ia.get("hora")
            
            # Captura nome — salva sempre que a IA extraiu um nome E o cliente ainda não tem nome real
            nome_extraido = resposta_ia.get("nome_cliente")
            nome_db_atual = cliente_db.get("nome") if cliente_db else None
            nome_db_e_placeholder = not nome_db_atual or nome_db_atual.strip() in ("Cliente", "")
            if nome_extraido and (not nome_cliente or nome_db_e_placeholder):
                db.execute(
                    text("UPDATE customers SET nome = :nome WHERE telefone_whatsapp = :tel"),
                    {"nome": nome_extraido.strip(), "tel": telefone_cliente}
                )
                db.commit()
                nome_cliente = nome_extraido.strip()
                logger.info("Nome do cliente actualizado: '%s' para tel %s", nome_cliente, telefone_cliente)

            # Re-garante search_path antes de buscar o cliente atualizado
            db.execute(text(f"SET search_path TO {schema_alvo_seguro}, public"))
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
                and cliente and cliente.get("id")
            ):
                data_str = estado.get("data")
                try:
                    data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
                    if data_obj < datetime.now().date():
                        # Limpar a data do estado para a IA perguntar novamente na próxima
                        estado["data"] = None
                        dados_atualizados = dados_sessao.copy() if dados_sessao else {}
                        dados_atualizados["historico"] = historico
                        dados_atualizados["estado"] = estado
                        dados_atualizados["ja_saudou"] = True
                        salvar_sessao_cliente(db, telefone_cliente, schema_alvo_seguro, dados_atualizados)
                        enviar_mensagem_whatsapp(
                            numero_destino=telefone_cliente,
                            texto=f"{saudacao_fixa}Poxa, não consigo agendar em datas que já passaram. Qual seria o dia ideal para você?"
                        )
                        return JSONResponse(content={"status": "sucesso"}, status_code=200)
                except ValueError:
                    pass

                servicos_escolhidos = estado.get("servico")
                if not isinstance(servicos_escolhidos, list):
                    servicos_escolhidos = [servicos_escolhidos]
                
                servicos_encontrados = []
                nomes_nao_encontrados = []
                
                for s_nome in servicos_escolhidos:
                    s_db = db.execute(
                        text("SELECT id, nome, duracao_minutos FROM services WHERE nome ILIKE :nome LIMIT 1"),
                        {"nome": f"%{s_nome}%"}
                    ).mappings().fetchone()
                    if s_db:
                        servicos_encontrados.append(s_db)
                    else:
                        nomes_nao_encontrados.append(s_nome)

                if nomes_nao_encontrados or not servicos_encontrados:
                    str_nao_encontrados = ", ".join(nomes_nao_encontrados) if nomes_nao_encontrados else str(servicos_escolhidos)
                    dados_atualizados = dados_sessao.copy() if dados_sessao else {}
                    dados_atualizados["historico"] = historico
                    estado["servico"] = None
                    dados_atualizados["estado"] = estado
                    dados_atualizados["ja_saudou"] = True
                    salvar_sessao_cliente(db, telefone_cliente, schema_alvo_seguro, dados_atualizados)
                    enviar_mensagem_whatsapp(
                        numero_destino=telefone_cliente,
                        texto=f"{saudacao_fixa}Poxa, não encontrei o(s) serviço(s) '{str_nao_encontrados}' na nossa lista. Que outro serviço gostaria?"
                    )
                    return JSONResponse(content={"status": "sucesso"}, status_code=200)

                data = estado.get("data")
                hora = estado.get("hora")

                # ── Verificação de conflito de horário ──
                # Busca config do lojista no schema public
                db.execute(text("SET search_path TO public"))
                merchant_config = db.query(Merchant).filter(
                    Merchant.nome_do_schema == schema_alvo_seguro
                ).first()
                permite_sobreposicao = bool(
                    merchant_config.permitir_sobreposicao if merchant_config else False
                )
                # Volta para schema do lojista
                db.execute(text(f"SET search_path TO {schema_alvo_seguro}, public"))

                if not permite_sobreposicao:
                    # A duração total agora é a soma de todos os serviços solicitados
                    duracao_serv = sum([(s.get("duracao_minutos") or 30) for s in servicos_encontrados])

                    # Buscar agendamentos existentes nessa data (não recusados)
                    agendamentos_dia = db.execute(text("""
                        SELECT a.horario_agendamento, COALESCE(s.duracao_minutos, 30) AS dur
                        FROM appointments a
                        LEFT JOIN services s ON a.service_id = s.id
                        WHERE a.data_agendamento = :data
                          AND a.status NOT IN ('recusado')
                        ORDER BY a.horario_agendamento
                    """), {"data": data}).mappings().fetchall()

                    # Verificar sobreposição
                    hora_pedida = datetime.strptime(hora, "%H:%M").time()
                    fim_pedido = (datetime.combine(datetime.today(), hora_pedida) + timedelta(minutes=duracao_serv)).time()

                    conflito = False
                    for ag in agendamentos_dia:
                        ag_inicio = ag["horario_agendamento"]
                        if isinstance(ag_inicio, str):
                            ag_inicio = datetime.strptime(ag_inicio, "%H:%M").time()
                        ag_fim = (datetime.combine(datetime.today(), ag_inicio) + timedelta(minutes=ag["dur"])).time()

                        # Sobreposição: início_pedido < fim_existente AND fim_pedido > início_existente
                        if hora_pedida < ag_fim and fim_pedido > ag_inicio:
                            conflito = True
                            break

                    if conflito:
                        # Sugerir próximo horário livre
                        horarios_ocupados = []
                        for ag in agendamentos_dia:
                            ag_inicio = ag["horario_agendamento"]
                            if isinstance(ag_inicio, str):
                                ag_inicio = datetime.strptime(ag_inicio, "%H:%M").time()
                            ag_fim = (datetime.combine(datetime.today(), ag_inicio) + timedelta(minutes=ag["dur"])).time()
                            horarios_ocupados.append((ag_inicio, ag_fim))

                        # Horário de funcionamento
                        h_abre = merchant_config.horario_abertura if merchant_config else "08:00"
                        h_fecha = merchant_config.horario_fechamento if merchant_config else "18:00"
                        abertura = datetime.strptime(h_abre, "%H:%M").time()
                        fechamento = datetime.strptime(h_fecha, "%H:%M").time()

                        # Buscar slots livres e ordenar pelos mais próximos ao horário solicitado
                        slots_livres = []
                        cursor_dt = datetime.combine(datetime.today(), abertura)
                        fecha_dt = datetime.combine(datetime.today(), fechamento)
                        
                        # Varrendo de 30 em 30 min
                        passo_minutos = 30
                        
                        while cursor_dt + timedelta(minutes=duracao_serv) <= fecha_dt:
                            slot_inicio = cursor_dt.time()
                            slot_fim = (cursor_dt + timedelta(minutes=duracao_serv)).time()
                            livre = True
                            for oc_ini, oc_fim in horarios_ocupados:
                                if slot_inicio < oc_fim and slot_fim > oc_ini:
                                    livre = False
                                    break
                            if livre:
                                # Diferença absoluta em minutos
                                diff = abs(
                                    datetime.combine(datetime.today(), slot_inicio) - 
                                    datetime.combine(datetime.today(), hora_pedida)
                                ).total_seconds() / 60
                                slots_livres.append({"hora": slot_inicio.strftime("%H:%M"), "diff": diff})
                            
                            cursor_dt += timedelta(minutes=passo_minutos)

                        # Ordenar pela menor diferença de tempo e pegar os 2 melhores
                        slots_livres.sort(key=lambda x: x["diff"])
                        sugestoes = [s["hora"] for s in slots_livres[:2]]

                        msg_conflito = (
                            f"{saudacao_fixa}Poxa, o horário das {hora} já está ocupado nessa data. "
                        )
                        if len(sugestoes) > 0:
                            if len(sugestoes) == 1:
                                msg_conflito += f"O horário mais próximo disponível é às {sugestoes[0]}. Podemos agendar nesse horário?"
                            else:
                                msg_conflito += f"Tenho disponibilidade às {sugestoes[0]} ou às {sugestoes[1]}. Qual você prefere?"
                        else:
                            msg_conflito += "Infelizmente não temos mais horários disponíveis nesse dia. Que tal outra data?"

                        # Limpar a hora do estado para a IA capturar a nova escolha do cliente
                        estado["hora"] = None
                        # Manter sessão ativa para o cliente poder responder
                        dados_atualizados = dados_sessao.copy() if dados_sessao else {}
                        dados_atualizados["historico"] = historico
                        dados_atualizados["estado"] = estado
                        dados_atualizados["ja_saudou"] = True
                        salvar_sessao_cliente(db, telefone_cliente, schema_alvo_seguro, dados_atualizados)
                        enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=msg_conflito)
                        return JSONResponse(content={"status": "sucesso"}, status_code=200)

                hora_atual_obj = datetime.strptime(hora, "%H:%M")

                max_ticket = db.execute(
                    text("SELECT COALESCE(MAX(numero_ticket), 0) FROM appointments")
                ).scalar() or 0
                
                for i, s_db in enumerate(servicos_encontrados):
                    s_id = s_db.get("id")
                    hora_str = hora_atual_obj.strftime("%H:%M")
                    
                    db.execute(text("""
                        INSERT INTO appointments (customer_id, service_id, data_agendamento, horario_agendamento, status, origem, numero_ticket) 
                        VALUES (:c_id, :s_id, :data, :hora, 'pendente', 'whatsapp_lau', :numero_ticket)
                    """), {"c_id": cliente.get("id"), "s_id": s_id, "data": data, "hora": hora_str, "numero_ticket": max_ticket + i + 1})
                    
                    dur = s_db.get("duracao_minutos") or 30
                    hora_atual_obj += timedelta(minutes=dur)

                db.commit()
                
                encerrar_sessao_cliente(db, telefone_cliente)
                
                try:
                    data_exibicao = datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
                except (ValueError, TypeError):
                    data_exibicao = str(data)
                
                # ── Mensagem de confirmação ao cliente (exata conforme fluxograma) ──
                nome_final = (
                    cliente.get("nome")
                    if cliente and cliente.get("nome") and cliente.get("nome") != "Cliente"
                    else None
                )
                mensagem_envio = (
                    f"Tudo certo, {nome_final}! Salvei a sua intenção de agendamento. "
                    f"Aguarde um instante, o lojista já vai confirmar e eu te aviso aqui! ☺️"
                    if nome_final else
                    "Tudo certo! Salvei a sua intenção de agendamento. "
                    "Aguarde um instante, o lojista já vai confirmar e eu te aviso aqui! ☺️"
                )
                enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=mensagem_envio)
                
                # ── Push Notification para o app do Lojista ──
                # Refaz query no schema public para encontrar o merchant
                db.execute(text("SET search_path TO public"))
                merchant_alvo = db.query(Merchant).filter(
                    Merchant.nome_do_schema == schema_alvo_seguro
                ).first()
                nomes_servicos = ", ".join([s.get("nome") for s in servicos_encontrados])
                
                if merchant_alvo and merchant_alvo.push_token:
                    nome_push = nome_final or "Cliente"
                    enviar_notificacao_push(
                        push_token=merchant_alvo.push_token,
                        titulo="Nova Solicitação Pendente! 🔔",
                        corpo=f"{nome_push} quer agendar {nomes_servicos} para {data_exibicao} às {hora}.",
                        dados={"tela": "pending"}
                    )
                
                logger.info(
                    "Agendamento pendente criado: cliente=%s | serviço=%s | data=%s | hora=%s | loja=%s",
                    nome_final or "sem nome", nomes_servicos, data_exibicao, hora, nome_loja
                )
                
            else:
                dados_atualizados = dados_sessao.copy() if dados_sessao else {}
                dados_atualizados["historico"] = historico
                dados_atualizados["estado"] = estado
                dados_atualizados["ja_saudou"] = True
                salvar_sessao_cliente(db, telefone_cliente, schema_alvo_seguro, dados_atualizados)
                
                # Só envia se houver texto — a IA pode retornar mensagem_resposta=""
                # quando todos os dados foram coletados (Regra 9 do System Prompt)
                if texto_ia and texto_ia.strip():
                    mensagem_final = f"{saudacao_fixa}{texto_ia}"
                    enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=mensagem_final)
                else:
                    logger.warning(
                        "IA retornou mensagem vazia para %s — estado: %s. Nenhuma mensagem enviada.",
                        telefone_cliente, estado
                    )

        return JSONResponse(content={"status": "sucesso"}, status_code=200)

    except ValueError as e:
        # Schema inválido — responde 200 para não fazer a Meta retentar
        logger.error("Schema invalido no webhook: %s", e)
        return JSONResponse(content={"status": "erro_schema"}, status_code=200)

    except Exception as e:
        # Qualquer erro inesperado deve retornar 200 para a Meta NÃO reenviar a mensagem.
        # O erro completo fica no log para diagnóstico.
        logger.exception("Erro critico no webhook: %s", e)
        return JSONResponse(content={"status": "erro", "detalhe": str(e)}, status_code=200)