from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text  # IMPORTANTE: Adicionado para executar os INSERTs no banco

from app.config import VERIFY_TOKEN
from app.database import get_db
from app.models import Merchant
from app.services.openai_service import analisar_mensagem_com_ia
from app.services.whatsapp_service import enviar_mensagem_whatsapp
from app.services.session_service import get_sessao_cliente, salvar_sessao_cliente, encerrar_sessao_cliente

router = APIRouter(tags=["Webhook"])


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

                            # 3. PROCESSAR COM IA
                            if schema_alvo:
                                # 1. RECUPERANDO A MEMÓRIA DA SESSÃO 🧠
                                sessao_atual = get_sessao_cliente(db, telefone_cliente)

                                if not sessao_atual:
                                    historico = []
                                else:
                                    # Pega o histórico existente ou cria uma lista vazia se não houver
                                    historico = sessao_atual.dados_sessao.get("historico", []) if sessao_atual.dados_sessao else []

                                # 2. ANOTANDO A MENSAGEM NOVA DO CLIENTE
                                historico.append({"role": "user", "content": mensagem_usuario})

                                # 3. ENVIANDO O HISTÓRICO COMPLETO PARA A IA LER
                                dados_ia = await analisar_mensagem_com_ia(historico)

                                if isinstance(dados_ia, dict):
                                    # 4. EXTRAINDO A RESPOSTA GERADA
                                    texto_ia = dados_ia.get("mensagem_resposta", "Entendi! Para prosseguir com o agendamento, qual seria o serviço e a data desejada?")
                                    intencao = dados_ia.get("intencao", "")
                                    servico = dados_ia.get("servico")
                                    data_br = dados_ia.get("data")
                                    hora = dados_ia.get("hora")
                                    nome_cliente = dados_ia.get("nome_cliente", "Cliente") # Pega o nome ou usa "Cliente"

                                    # 5. ANOTANDO A RESPOSTA DA IA NO HISTÓRICO
                                    historico.append({"role": "assistant", "content": texto_ia})

                                    # 6. LÓGICA DE AGENDAMENTO E SALVAMENTO NO BANCO 💾
                                    # Se for agendamento E tivermos todos os dados (serviço, data e hora)
                                    if intencao == "agendamento" and servico and data_br and hora:
                                        try:
                                            print(f"🎯 INICIANDO SALVAMENTO: {servico} | {data_br} às {hora}")
                                            
                                            from datetime import datetime
                                            # Converte a data do padrão BR (DD-MM-YYYY) para SQL (YYYY-MM-DD)
                                            data_pg = datetime.strptime(data_br, "%d-%m-%Y").strftime("%Y-%m-%d")
                                            
                                            # Comando 1: Inserir o Cliente (Se não existir, não faz nada)
                                            db.execute(
                                                text(f"INSERT INTO {schema_alvo}.customers (nome, telefone) VALUES (:nome, :telefone) ON CONFLICT DO NOTHING"),
                                                {"nome": nome_cliente, "telefone": telefone_cliente}
                                            )
                                            
                                            # Pegar o ID do Cliente
                                            resultado_cliente = db.execute(
                                                text(f"SELECT id FROM {schema_alvo}.customers WHERE telefone = :telefone"),
                                                {"telefone": telefone_cliente}
                                            ).fetchone()
                                            
                                            cliente_id = resultado_cliente if resultado_cliente else None

                                            if cliente_id:
                                                # Comando 2: Inserir Agendamento
                                                db.execute(
                                                    text(f"INSERT INTO {schema_alvo}.appointments (customer_id, servico, data_agendamento, hora_agendamento) VALUES (:c_id, :serv, :dt, :hr)"),
                                                    {"c_id": cliente_id, "serv": servico, "dt": data_pg, "hr": hora}
                                                )
                                                db.commit()
                                                print("✅ Agendamento salvo com sucesso no banco de dados!")
                                                
                                                # Limpa o histórico após fechar a venda, para a IA não misturar se ele quiser marcar outro no mesmo dia.
                                                salvar_sessao_cliente(db, telefone_cliente, schema_alvo, {"historico": []})
                                                enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=texto_ia)
                                            else:
                                                print("❌ Erro: Não foi possível obter o ID do cliente.")
                                                enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto="Tivemos um problema ao salvar seu cadastro. Tente novamente.")
                                                
                                        except Exception as e:
                                            db.rollback() # Desfaz alterações em caso de erro
                                            print(f"❌ ERRO AO SALVAR NO BANCO: {e}")
                                            enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto="Desculpe, ocorreu um erro ao salvar o seu agendamento no nosso sistema.")
                                            
                                    # Se a intenção for encerramento (o cliente disse 'tchau' ou 'obrigado')
                                    elif intencao == "encerramento":
                                        print("🧹 Atendimento finalizado. Sessão inativada...")
                                        salvar_sessao_cliente(db, telefone_cliente, schema_alvo, {"historico": historico})
                                        encerrar_sessao_cliente(db, telefone_cliente)
                                        enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=texto_ia)
                                        
                                    # Se for só bate-papo, dúvida, ou ainda falta pedir a hora (A Boca do Robô Normal)
                                    else:
                                        salvar_sessao_cliente(db, telefone_cliente, schema_alvo, {"historico": historico})
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
