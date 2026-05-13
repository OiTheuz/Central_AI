import json
from datetime import datetime

from openai import AsyncOpenAI

from app.config import OPENAI_API_KEY

# =========================================================
# CLIENTE OPENAI

client_ai = AsyncOpenAI(api_key=OPENAI_API_KEY)

# =========================================================
# ANÁLISE DE MENSAGEM COM IA

async def analisar_mensagem_com_ia(texto_cliente: str):
    # 1. Pega a data e a HORA exatas de agora (Adicionamos o %H:%M)
    data_hora_atual = datetime.now().strftime("%d-%m-%Y %H:%M")
    
    # 2. Somamos a regra da data/hora com as novas Regras de Ouro
    prompt_sistema = f"""⚠️ INFORMAÇÃO CRUCIAL: Agora é {data_hora_atual}. Use essa data e hora como referência para calcular dias e também para decidir se diz Bom dia, Boa tarde ou Boa noite.

    Você é a secretária virtual super simpática, feliz e prestativa de uma Central de Agendamentos.
    Sua função é ler a mensagem do cliente, extrair os dados e criar uma resposta acolhedora.

    SUAS REGRAS DE OURO:
    1. Saudação Animada: Analise a hora atual. Comece SEMPRE a sua 'mensagem_resposta' com muita energia, dizendo "Bom dia! ☀️", "Boa tarde! 🌤️" ou "Boa noite! 🌙". Use emojis!
    2. Horário Obrigatório: O horário ('hora') é OBRIGATÓRIO para agendar. Se o cliente informar a data mas não a hora, avise na 'mensagem_resposta' que o horário é obrigatório para fecharmos a reserva e pergunte qual ele prefere.
    
    O formato JSON estrito DEVE ser:
    {{
        "intencao": "agendamento" ou "saudacao" ou "duvida",
        "nome_cliente": "nome da pessoa, ou null",
        "servico": "serviço desejado, ou null",
        "data": "DD-MM-YYYY, ou null",
        "hora": "HH:MM, ou null",
        "mensagem_resposta": "O texto que será enviado ao cliente (com a saudação animada e os avisos necessários)"
    }}
    """
    
    # Chama a API
    response = await client_ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": texto_cliente}
        ],
        response_format={ "type": "json_object" },
        temperature=0.1
    )
    
    # Acessamos o conteúdo de texto da mensagem primeiro
    conteudo_texto = response.choices[0].message.content
    
    # Agora convertemos esse texto para um dicionário Python
    dados_extraidos = json.loads(conteudo_texto)
    
    return dados_extraidos
