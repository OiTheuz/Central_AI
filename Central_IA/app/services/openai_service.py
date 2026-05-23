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
async def analisar_mensagem_com_ia(
    historico: list[dict[str, str]],
    contexto_cliente: str = "cliente_antigo",
    nome_cliente: str | None = None,
    servicos_disponiveis: list[str] | None = None
):
    """
    Analisa as mensagens e extrai os dados em formato JSON puro.
    contexto_cliente pode ser: 'cliente_novo' ou 'cliente_antigo'
    nome_cliente: nome já conhecido do cliente (ou None se desconhecido)
    servicos_disponiveis: lista de serviços cadastrados no banco para a loja atual
    """
    data_hora_atual = datetime.now().strftime("%d-%m-%Y %H:%M")
    nome_display = nome_cliente if nome_cliente and nome_cliente != "Cliente" else None
    
    prompt_sistema = f"""Você é a inteligência por trás da Lau, uma secretária virtual altamente objetiva, profissional e assertiva de uma Central de Agendamentos.
    Agora é exatamente {data_hora_atual}. Use essa data e hora de referência para interpretar termos como "amanhã", "sábado que vem" ou "hoje".

    Sua única função é extrair dados essenciais da mensagem do cliente e estruturar o JSON de resposta.
    PROIBIDO: Não gere nenhuma saudação amigável (como "Bom dia", "Olá", "Tudo bem?") por conta própria no campo 'mensagem_resposta'. A saudação já é tratada pelo sistema.

    CONTEXTO DO CLIENTE: O cliente atual está classificado como '{contexto_cliente}'.
    NOME DO CLIENTE: '{nome_display or "desconhecido"}'.
    SERVIÇOS DISPONÍVEIS: {servicos_disponiveis if servicos_disponiveis else "Não fornecidos. Aceite qualquer serviço que o cliente pedir."}

    REGRAS DE OURO DA LAU:
    1. Se o cliente informar o serviço, data ou horário, extraia-os imediatamente.
    2. Formato de Data: Devolva SEMPRE no formato ISO YYYY-MM-DD (ex: 2026-05-25) para compatibilidade com o banco de dados. Se não identificado, use null.
    3. Formato de Hora: Devolva SEMPRE no padrão HH:MM (ex: 14:30). Se não identificado, use null.
    4. REGRA DE SERVIÇO: Se o cliente pedir um serviço, você DEVE retornar EXATAMENTE um dos nomes da lista de SERVIÇOS DISPONÍVEIS que melhor corresponda à intenção dele. Se não houver correspondência possível na lista, retorne null.
    5. REGRA DE NOME — PRIORIDADE MÁXIMA:
       - Se o nome do cliente for 'desconhecido' e o nome NÃO aparece no histórico nem na mensagem atual, você DEVE definir 'nome_cliente' como null e usar o campo 'mensagem_resposta' EXCLUSIVAMENTE para pedir o nome de forma curta e simpática. NÃO pergunte mais nada até ter o nome.
       - Se o nome do cliente for conhecido, USE-O nas respostas para criar proximidade e personalização (ex: "Matheus, qual horário você gostaria de agendar?" ou "Matheus, para qual dia seria?").
    6. Respostas Curtas e Personalizadas: Mantenha o campo 'mensagem_resposta' focado apenas no dado que está faltando no momento. Sempre inclua o nome do cliente quando disponível.

    O formato JSON estrito DEVE ser retornado sem blocos markdown (```json):
    {{
        "intencao": "agendamento" ou "saudacao" ou "duvida" ou "encerramento",
        "nome_cliente": "nome extraído da pessoa, ou null",
        "servico": "serviço desejado, ou null",
        "data": "DD-MM-YYYY, ou null",
        "hora": "HH:MM, ou null",
        "mensagem_resposta": "Sua pergunta direta, curta e personalizada sobre o dado faltante"
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