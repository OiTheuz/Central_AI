from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy.orm import Session

from app.config import VERIFY_TOKEN
from app.database import get_db
from app.models import Merchant
from app.services.openai_service import analisar_mensagem_com_ia
from app.services.whatsapp_service import enviar_mensagem_whatsapp
from app.services.session_service import get_sessao_cliente, salvar_sessao_cliente

router = APIRouter(tags=["Webhook"])

# =========================================================
# WEBHOOK META - VERIFICAÇÃO (GET)

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
                                schema_alvo = sessao_ativa.loja_atual
                                print(f"🧠 Memória Ativa: Cliente em atendimento com -> {schema_alvo}")
                            else:
                                merchants = db.query(Merchant).all()
                                for m in merchants:
                                    if m.nome_loja.lower() in mensagem_usuario.lower() or m.codigo_loja.lower() in mensagem_usuario.lower():
                                        schema_alvo = m.nome_do_schema
                                        salvar_sessao_cliente(db, telefone_cliente, schema_alvo)
                                        print(f"🆕 Nova sessão iniciada com -> {schema_alvo}")
                                        break

                            # 3. PROCESSAR COM IA
                            if schema_alvo:
                                dados_ia = await analisar_mensagem_com_ia(mensagem_usuario)
                                
                                # AQUI ESTÁ A CORREÇÃO: Garante que a IA não devolveu uma lista
                                if isinstance(dados_ia, dict):
                                    if dados_ia.get("servico") and dados_ia.get("data"):
                                        print(f"🎯 Agendamento detectado: {dados_ia}")
                                        # (AQUI ENTRA O SEU INSERT NO BANCO QUE FIZEMOS ANTES)
                                        
                                        # 👉 ROBÔ RESPONDE (Com dados detectados)
                                        texto_confirmacao = f"Perfeito! Entendi que você deseja um(a) {dados_ia.get('servico')} para a data {dados_ia.get('data')}. Vou verificar a disponibilidade na agenda!"
                                        enviar_mensagem_whatsapp(numero_destino=telefone_cliente, texto=texto_confirmacao)
                                        
                                    else:
                                        print("⏳ IA ainda coletando informações do cliente...")
                                        
                                        # 👉 A BOCA DO ROBÔ ESTÁ AQUI (IA fazendo perguntas)
                                        # Pega a resposta gerada pela IA (se ela enviar a chave 'resposta'), senão envia um texto padrão
                                        texto_ia = dados_ia.get("mensagem_resposta", "Entendi! Para prosseguir com o agendamento, qual seria o serviço e a data desejada?")
                                        
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
