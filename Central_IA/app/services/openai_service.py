import json
from datetime import datetime
from typing import cast

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from app.config import OPENAI_API_KEY

# =========================================================
# CLIENTE OPENAI
# =========================================================
client_ai = AsyncOpenAI(api_key=OPENAI_API_KEY)

# =========================================================
# ANÁLISE DE MENSAGEM COM IA
# =========================================================
async def analisar_mensagem_com_ia(historico: list[dict[str, str]], contexto_cliente: str = "cliente_antigo"):
    """
    Analisa as mensagens e extrai os dados em formato JSON puro.
    contexto_cliente pode ser: 'cliente_novo' ou 'cliente_antigo'
    """
    data_hora_atual = datetime.now().strftime("%d-%m-%Y %H:%M")
    
    prompt_sistema = f"""Você é a inteligência por trás da Lau, uma secretária virtual altamente objetiva, profissional e assertiva de uma Central de Agendamentos.
    Agora é exatameente {data_hora_atual}. Use essa data e hora de referência para interpretar termos como "amanhã", "sábado que vem" ou "hoje".

    Sua única função é extrair dados essenciais da mensagem do cliente e estruturar o JSON de resposta.
    PROIBIDO: Não gere nenhuma saudação amigável (como "Bom dia", "Olá", "Tudo bem?") por conta própria no campo 'mensagem_resposta'. 

    CONTEXTO DO CLIENTE: O cliente atual está classificado como '{contexto_cliente}'.

    REGRAS DE OURO DA LAU:
    1. Se o cliente informar o serviço, data ou horário, extraia-os imediatamente.
    2. Formato de Data: Devolva SEMPRE no padrão brasileiro DD-MM-YYYY (ex: 25-05-2026). Se não identificado, use null.
    3. Formato de Hora: Devolva SEMPRE no padrão HH:MM (ex: 14:30). Se não identificado, use null.
    4. Regra de Nome Obrigatório: Se o contexto do cliente for 'cliente_novo' e o nome da pessoa NÃO foi capturado no histórico nem na mensagem atual, você DEVE definir 'nome_cliente' como null e usar o campo 'mensagem_resposta' exclusivamente para pedir o nome de forma curta e simpática.
    5. Respostas Curtas: Mantenha o campo 'mensagem_resposta' focado apenas no dado que está faltando no momento (ex: "Qual serviço você gostaria de agendar?" ou "Qual o melhor horário para você?").

    O formato JSON estrito DEVE ser retornado sem blocos markdown (```json):
    {{
        "intencao": "agendamento" ou "saudacao" ou "duvida" ou "encerramento",
        "nome_cliente": "nome extraído da pessoa, ou null",
        "servico": "serviço desejado, ou null",
        "data": "DD-MM-YYYY, ou null",
        "hora": "HH:MM, ou null",
        "mensagem_resposta": "Sua pergunta direta e curta sobre o dado faltante"
    }}"""
    
    messages_payload = cast(list[ChatCompletionMessageParam], [
        {"role": "system", "content": prompt_sistema},
        *historico
    ])

    # Chamada da API com formato JSON garantido
    response = await client_ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages_payload,
        response_format={"type": "json_object"},
        temperature=0.1
    )
    
    conteudo_texto = response.choices[0].message.content
    return json.loads(conteudo_texto)