import json
from datetime import datetime
from typing import cast

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from app.config import OPENAI_API_KEY

# =========================================================
# CLIENTE OPENAI

client_ai = AsyncOpenAI(api_key=OPENAI_API_KEY)

# =========================================================
# ANÁLISE DE MENSAGEM COM IA

async def analisar_mensagem_com_ia(historico: list[dict[str, str]], contexto_cliente: str = "cliente_existente"):
    """
    Envia o histórico de conversa para a IA e extrai dados de agendamento.
    
    Args:
        historico: Lista de mensagens no formato [{"role": "user/assistant", "content": "..."}]
        contexto_cliente: "cliente_novo" ou "cliente_existente"
    """
    # 1. Pega a data e a HORA exatas de agora
    data_hora_atual = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 2. Prompt de extração pura — sem saudações
    prompt_sistema = f"""⚠️ INFORMAÇÃO CRUCIAL: Agora é {data_hora_atual}. Use essa data e hora como referência para calcular datas relativas (ex: "amanhã", "segunda-feira").

    Você é uma IA EXTRATORA DE DADOS de uma Central de Agendamentos.
    Seu ÚNICO objetivo é extrair informações de agendamento da mensagem do cliente.

    ❌ REGRAS PROIBIDAS:
    - NUNCA diga "Bom dia", "Boa tarde", "Boa noite" ou qualquer saudação.
    - NUNCA crie cumprimentos por conta própria.
    - NUNCA seja excessivamente simpática ou faça bate-papo.

    ✅ SUAS REGRAS DE EXTRAÇÃO:
    1. Extraia da mensagem: serviço desejado, data, hora e nome do cliente.
    2. Se o cliente informar a data mas NÃO informar a hora, avise na 'mensagem_resposta' que o horário é obrigatório e pergunte qual horário ele prefere. Seja direta e breve.
    3. Se o contexto for "cliente_novo" e você NÃO conseguir identificar o nome do cliente na mensagem, peça educadamente o nome na 'mensagem_resposta'. Exemplo: "Para prosseguir, poderia me informar o seu nome?"
    4. Quando todos os dados (serviço, data, hora e nome) estiverem completos, defina a "intencao" como "agendamento".
    5. Se o cliente se despedir ou confirmar encerramento, defina a "intencao" como "encerramento". Na 'mensagem_resposta', agradeça brevemente e avise que pode agendar com outra loja futuramente.
    
    CONTEXTO DO CLIENTE: {contexto_cliente}

    O formato JSON estrito DEVE ser:
    {{
        "intencao": "agendamento" ou "coleta_dados" ou "duvida" ou "encerramento",
        "nome_cliente": "nome da pessoa, ou null",
        "servico": "serviço desejado, ou null",
        "data": "YYYY-MM-DD, ou null",
        "hora": "HH:MM, ou null",
        "mensagem_resposta": "Texto breve e direto para o cliente (SEM saudações)"
    }}
    """
    
    messages_payload = cast(list[ChatCompletionMessageParam], [
        {"role": "system", "content": prompt_sistema},
        *historico
    ])

    # Chama a API
    response = await client_ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages_payload,
        response_format={"type": "json_object"},
        temperature=0.1
    )
    
    # Acessamos o conteúdo de texto da mensagem primeiro
    conteudo_texto = response.choices[0].message.content
    
    # Agora convertemos esse texto para um dicionário Python
    # pyrefly: ignore [bad-argument-type]
    dados_extraidos = json.loads(conteudo_texto)
    
    return dados_extraidos
