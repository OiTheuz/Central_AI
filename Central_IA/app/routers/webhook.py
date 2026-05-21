import asyncio
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text  # IMPORTANTE: Adicionado para executar os INSERTs no banco

from app.config import VERIFY_TOKEN
from app.database import get_db, SessionLocal
from app.models import Merchant
from app.services.openai_service import analisar_mensagem_com_ia
from app.services.whatsapp_service import enviar_mensagem_whatsapp
from app.services.session_service import get_sessao_cliente, salvar_sessao_cliente, encerrar_sessao_cliente

router = APIRouter(tags=["Webhook"])


# =========================================================
# HELPERS — Saudação e Consultas no Schema do Lojista
# =========================================================

def _calcular_saudacao() -> str:
    """Retorna 'Bom dia', 'Boa tarde' ou 'Boa noite' baseado na hora atual."""
    hora_atual = datetime.now().hour
    if 6 <= hora_atual < 12:
        return "Bom dia"
    elif 12 <= hora_atual < 18:
        return "Boa tarde"
    else:
        return "Boa noite"


def _buscar_cliente_por_telefone(db: Session, schema: str, telefone: str) -> dict | None:
    """Busca um cliente no schema do lojista pelo telefone. Retorna dict ou None."""
    resultado = db.execute(
        text(f"SELECT id, nome, telefone, ultima_interacao FROM {schema}.customers WHERE telefone = :telefone"),
        {"telefone": telefone}
    ).fetchone()

    if resultado:
        return {
            "id": resultado[0],
            "nome": resultado[1],
            "telefone": resultado[2],
            "ultima_interacao": resultado[3]
        }
    return None


def _verificar_agendamento_pendente(db: Session, schema: str, customer_id: int) -> bool:
    """Verifica se existe algum agendamento com status 'pendente' para o customer_id."""
    resultado = db.execute(
        text(f"SELECT id FROM {schema}.appointments WHERE customer_id = :cid AND status = 'pendente' LIMIT 1"),
        {"cid": customer_id}
    ).fetchone()
    return resultado is not None


def _atualizar_ultima_interacao(db: Session, schema: str, telefone: str):
    """Atualiza o campo ultima_interacao do cliente para NOW()."""
    db.execute(
        text(f"UPDATE {schema}.customers SET ultima_interacao = NOW() WHERE telefone = :telefone"),
        {"telefone": telefone}
    )
    db.commit()


def _deve_saudar(ultima_interacao) -> bool:
    """Retorna True se a última interação foi há mais de 2 horas (ou se não existir)."""
    if ultima_interacao is None:
        return True
    limite = datetime.now() - timedelta(hours=2)
    return ultima_interacao < limite


def _buscar_nome_lojista(db: Session, schema_alvo: str) -> str:
    """Busca o nome da loja no Merchant pelo nome_do_schema."""
    merchant = db.query(Merchant).filter(Merchant.nome_do_schema == schema_alvo).first()
    return merchant.nome_loja if merchant else "nosso parceiro"


# =========================================================
# MOCK — Confirmação Automática do Lojista (Para Testes)
# =========================================================

async def mock_confirmacao_lojista(
    schema: str,
    appointment_id: int,
    telefone_cliente: str,
    servico: str,
    data_agendamento: str,
    hora_agendamento: str
):
    """
    Simula a confirmação do lojista após 5 segundos.
    - Atualiza o status do agendamento para 'confirmado'
    - Envia mensagem de confirmação ao cliente via WhatsApp
    """
    await asyncio.sleep(5)

    # Cria uma sessão separada para a task em background
    db = SessionLocal()
    try:
        db.execute(
            text(f"UPDATE {schema}.appointments SET status = 'confirmado' WHERE id = :aid"),
            {"aid": appointment_id}
        )
        db.commit()
        print(f"✅ [MOCK] Agendamento #{appointment_id} confirmado automaticamente!")

        # Envia mensagem de confirmação ao cliente
        mensagem_confirmacao = (
            f"✅ Tudo certo! Seu agendamento de {servico} foi confirmado "
            f"para {data_agendamento} às {hora_agendamento}! "
            f"Posso te ajudar com mais alguma coisa?"
        )
        enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=mensagem_confirmacao)
        print(f"📤 [MOCK] Mensagem de confirmação enviada para {telefone_cliente}")

    except Exception as e:
        db.rollback()
        print(f"❌ [MOCK] Erro na confirmação automática: {e}")
    finally:
        db.close()


# =========================================================
# WEBHOOK META - VERIFICAÇÃO (GET)
# =========================================================

@router.get("/webhook")
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
# WEBHOOK META - RECEBER MENSAGENS (POST)
# =========================================================

@router.post("/webhook")
async def recebe_mensagem_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
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
                                schema_alvo = str(sessao_ativa.loja_atual)
                                print(f"🧠 Memória Ativa: Cliente em atendimento com -> {schema_alvo}")
                            else:
                                merchants = db.query(Merchant).all()
                                for m in merchants:
                                    if m.nome_loja.lower() in mensagem_usuario.lower() or m.codigo_loja.lower() in mensagem_usuario.lower():
                                        schema_alvo = str(m.nome_do_schema)
                                        salvar_sessao_cliente(db, telefone_cliente, schema_alvo)
                                        print(f"🆕 Nova sessão iniciada com -> {schema_alvo}")
                                        break

                            # 3. PROCESSAR — Só se tivermos um schema identificado
                            if schema_alvo:

                                # =============================================
                                # TAREFA 3: SAUDAÇÃO FIXA (Python controla)
                                # =============================================
                                cliente_db = _buscar_cliente_por_telefone(db, schema_alvo, telefone_cliente)
                                saudacao_prefix = ""
                                contexto_cliente = "cliente_existente"

                                if cliente_db:
                                    # Cliente existe — verifica se precisa saudar
                                    if _deve_saudar(cliente_db["ultima_interacao"]):
                                        nome_lojista = _buscar_nome_lojista(db, schema_alvo)
                                        saudacao_prefix = (
                                            f"Olá, {_calcular_saudacao()}! ☀️\n"
                                            f"Eu sou a Lau, secretária Virtual de {nome_lojista}.\n\n"
                                        )
                                    # Atualiza ultima_interacao
                                    _atualizar_ultima_interacao(db, schema_alvo, telefone_cliente)
                                else:
                                    # Cliente novo — sempre saúda
                                    contexto_cliente = "cliente_novo"
                                    nome_lojista = _buscar_nome_lojista(db, schema_alvo)
                                    saudacao_prefix = (
                                        f"Olá, {_calcular_saudacao()}! ☀️\n"
                                        f"Eu sou a Lau, secretária Virtual de {nome_lojista}.\n\n"
                                    )

                                # =============================================
                                # TAREFA 4: TRAVA DE AGENDAMENTO PENDENTE
                                # =============================================
                                if cliente_db and _verificar_agendamento_pendente(db, schema_alvo, cliente_db["id"]):
                                    print("🔒 Cliente possui agendamento pendente. Bloqueando chamada da IA.")
                                    mensagem_trava = (
                                        f"{saudacao_prefix}"
                                        "Seu agendamento ainda está em análise pelo lojista. "
                                        "Assim que for confirmado, te aviso aqui! 😉"
                                    )
                                    enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=mensagem_trava)
                                    continue  # Pula para a próxima mensagem

                                # =============================================
                                # LÓGICA DE MEMÓRIA DA SESSÃO 🧠
                                # =============================================
                                sessao_atual = get_sessao_cliente(db, telefone_cliente)

                                if not sessao_atual:
                                    historico = []
                                else:
                                    historico = sessao_atual.dados_sessao.get("historico", []) if sessao_atual.dados_sessao else []

                                # Anotando a mensagem nova do cliente
                                historico.append({"role": "user", "content": mensagem_usuario})

                                # =============================================
                                # CHAMADA DA IA (com contexto_cliente)
                                # =============================================
                                dados_ia = await analisar_mensagem_com_ia(historico, contexto_cliente)

                                if isinstance(dados_ia, dict):
                                    # Extraindo a resposta gerada
                                    texto_ia = dados_ia.get("mensagem_resposta", "Para prosseguir com o agendamento, qual seria o serviço e a data desejada?")
                                    intencao = dados_ia.get("intencao", "")
                                    servico = dados_ia.get("servico")
                                    data_agendamento = dados_ia.get("data")
                                    hora = dados_ia.get("hora")
                                    nome_cliente = dados_ia.get("nome_cliente", "Cliente")

                                    # Anotando a resposta da IA no histórico
                                    historico.append({"role": "assistant", "content": texto_ia})

                                    # Concatena saudação + resposta da IA
                                    resposta_final = f"{saudacao_prefix}{texto_ia}"

                                    # =============================================
                                    # TAREFA 5: AGENDAMENTO + MOCK CONFIRMAÇÃO
                                    # =============================================
                                    if intencao == "agendamento" and servico and data_agendamento and hora:
                                        try:
                                            print(f"🎯 INICIANDO SALVAMENTO: {servico} | {data_agendamento} às {hora}")

                                            # Se nome_cliente veio null da IA, usa "Cliente"
                                            if not nome_cliente:
                                                nome_cliente = "Cliente"

                                            # Comando 1: Inserir o Cliente (Se não existir, não faz nada)
                                            db.execute(
                                                text(f"INSERT INTO {schema_alvo}.customers (nome, telefone, ultima_interacao) VALUES (:nome, :telefone, NOW()) ON CONFLICT (telefone) DO UPDATE SET ultima_interacao = NOW()"),
                                                {"nome": nome_cliente, "telefone": telefone_cliente}
                                            )

                                            # Pegar o ID do Cliente
                                            resultado_cliente = db.execute(
                                                text(f"SELECT id FROM {schema_alvo}.customers WHERE telefone = :telefone"),
                                                {"telefone": telefone_cliente}
                                            ).fetchone()

                                            cliente_id = resultado_cliente[0] if resultado_cliente else None

                                            if cliente_id:
                                                # Comando 2: Inserir Agendamento com status 'pendente'
                                                db.execute(
                                                    text(f"INSERT INTO {schema_alvo}.appointments (customer_id, servico, data_agendamento, hora_agendamento, status) VALUES (:c_id, :serv, :dt, :hr, 'pendente')"),
                                                    {"c_id": cliente_id, "serv": servico, "dt": data_agendamento, "hr": hora}
                                                )
                                                db.commit()

                                                # Pegar o ID do agendamento recém-criado
                                                resultado_appointment = db.execute(
                                                    text(f"SELECT id FROM {schema_alvo}.appointments WHERE customer_id = :cid ORDER BY criado_em DESC LIMIT 1"),
                                                    {"cid": cliente_id}
                                                ).fetchone()

                                                appointment_id = resultado_appointment[0] if resultado_appointment else None

                                                print("✅ Agendamento salvo com sucesso no banco de dados!")

                                                # Resposta fixa para o cliente (não usa texto da IA)
                                                resposta_agendamento = (
                                                    f"{saudacao_prefix}"
                                                    "Tudo certo! Enviei o seu pedido para o lojista "
                                                    "e estou aguardando a confirmação. Te aviso já já!"
                                                )

                                                # Limpa o histórico após fechar a venda
                                                salvar_sessao_cliente(db, telefone_cliente, schema_alvo, {"historico": []})
                                                enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=resposta_agendamento)

                                                # =============================================
                                                # MOCK: Dispara confirmação após 5 segundos
                                                # =============================================
                                                if appointment_id:
                                                    background_tasks.add_task(
                                                        mock_confirmacao_lojista,
                                                        schema=schema_alvo,
                                                        appointment_id=appointment_id,
                                                        telefone_cliente=telefone_cliente,
                                                        servico=servico,
                                                        data_agendamento=data_agendamento,
                                                        hora_agendamento=hora
                                                    )
                                                    print("⏳ [MOCK] Confirmação automática agendada para 5 segundos...")
                                            else:
                                                print("❌ Erro: Não foi possível obter o ID do cliente.")
                                                enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto="Tivemos um problema ao salvar seu cadastro. Tente novamente.")

                                        except Exception as e:
                                            db.rollback()  # Desfaz alterações em caso de erro
                                            print(f"❌ ERRO AO SALVAR NO BANCO: {e}")
                                            enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto="Desculpe, ocorreu um erro ao salvar o seu agendamento no nosso sistema.")

                                    # Se a intenção for encerramento (o cliente disse 'tchau' ou 'obrigado')
                                    elif intencao == "encerramento":
                                        print("🧹 Atendimento finalizado. Sessão inativada...")
                                        salvar_sessao_cliente(db, telefone_cliente, schema_alvo, {"historico": historico})
                                        encerrar_sessao_cliente(db, telefone_cliente)
                                        enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=resposta_final)

                                    # Se for coleta_dados, dúvida, ou ainda falta algum dado
                                    else:
                                        salvar_sessao_cliente(db, telefone_cliente, schema_alvo, {"historico": historico})
                                        enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=resposta_final)

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
