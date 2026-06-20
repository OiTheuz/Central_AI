import json
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import cast

from openai import AsyncOpenAI, RateLimitError, APIStatusError, APIConnectionError
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam

from app.config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

# =========================================================
# CLIENTE OPENAI
# =========================================================
# timeout configurado no cliente — compatível com todas as versões do SDK.
# Não passe timeout dentro de create() pois em certas versões do SDK isso
# pode ser mal interpretado e retornar AsyncStream ao invés de ChatCompletion.
client_ai = AsyncOpenAI(api_key=OPENAI_API_KEY, timeout=30.0)

# =========================================================
# ANÁLISE DE MENSAGEM COM IA
# =========================================================
async def analisar_mensagem_com_ia(
    historico: list[dict[str, str]],
    contexto_cliente: str = "cliente_antigo",
    nome_cliente: str | None = None,
    servicos_disponiveis: str = "",
    nome_loja: str = "Loja",
    data_nascimento_conhecida: bool = False
) -> dict:
    """
    Analisa as mensagens e extrai os dados em formato JSON puro.
    contexto_cliente pode ser: 'cliente_novo' ou 'cliente_antigo'
    nome_cliente: nome já conhecido do cliente (ou None se desconhecido)
    servicos_disponiveis: lista de serviços cadastrados no banco para a loja atual

    Retorna um dicionário com os campos extraídos pela IA, ou um fallback
    seguro em caso de erro de API ou JSON inválido.
    """
    tz_br = ZoneInfo("America/Sao_Paulo")
    data_hora_atual = datetime.now(tz_br).strftime("%d-%m-%Y %H:%M")
    nome_display = nome_cliente if nome_cliente and nome_cliente != "Cliente" else None

    # Gerar referência dos próximos 14 dias com nomes dos dias da semana em pt-BR
    dias_semana_pt = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
    hoje = datetime.now(tz_br)
    dia_semana_hoje = dias_semana_pt[hoje.weekday()]
    proximos_dias = []
    for i in range(14):
        d = hoje + timedelta(days=i)
        nome_dia = dias_semana_pt[d.weekday()]
        proximos_dias.append(f"  - {nome_dia}: {d.strftime('%Y-%m-%d')}")
    calendario_referencia = "\n".join(proximos_dias)
    
    prompt_sistema = f"""Você é a Lau, a secretária virtual exclusiva e oficial da loja '{nome_loja}'.
    Você é altamente objetiva, profissional e assertiva em agendamentos.
    Agora é exatamente {data_hora_atual}. Hoje é {dia_semana_hoje}.

    CALENDÁRIO DE REFERÊNCIA (próximos 14 dias):
{calendario_referencia}

    Use essa referência para interpretar expressões como:
    - "hoje" → {hoje.strftime('%Y-%m-%d')}
    - "amanhã" → {(hoje + timedelta(days=1)).strftime('%Y-%m-%d')}
    - "essa quinta", "quinta-feira", "quinta" → a PRÓXIMA quinta-feira a partir de hoje (inclusive hoje se for quinta)
    - "esse sábado", "sábado" → o PRÓXIMO sábado a partir de hoje
    - "próxima terça", "terça que vem" → a terça-feira da SEMANA QUE VEM (nunca esta semana)
    - "semana que vem" sem dia específico → pergunte qual dia da semana
    REGRA: quando o cliente diz "essa [dia]" ou apenas o nome do dia, SEMPRE use a PRÓXIMA ocorrência futura desse dia. Se hoje JÁ for esse dia, use hoje.
    REGRA CRÍTICA: A data atual é {hoje.strftime('%Y-%m-%d')}. É PROIBIDO aceitar qualquer data anterior a hoje. Se o cliente pedir uma data no passado (mesmo que apenas indique o dia e mês que já passaram neste ano, ou um ano anterior), NEGUE CORDIALMENTE e peça para escolher uma data válida (de hoje em diante).

    Sua única função é extrair dados essenciais da mensagem do cliente e estruturar o JSON de resposta.
    PROIBIDO: Não gere nenhuma saudação amigável (como "Bom dia", "Olá", "Tudo bem?") por conta própria no campo 'mensagem_resposta'. A saudação já é tratada pelo sistema.
    PROIBIDO: NUNCA use as palavras genéricas "estabelecimento" ou "lojista" nas suas respostas. Refira-se à loja sempre pelo seu nome oficial: "{nome_loja}".

    CONTEXTO DO CLIENTE: O cliente atual está classificado como '{contexto_cliente}'.
    NOME DO CLIENTE: '{nome_display or "desconhecido"}'.
    DATA DE NASCIMENTO CADASTRADA: {'Sim' if data_nascimento_conhecida else 'Não'}.
    SERVIÇOS DISPONÍVEIS:
    {servicos_disponiveis if servicos_disponiveis else "Não fornecidos. Aceite qualquer serviço que o cliente pedir."}

    ╔══════════════════════════════════════════════════════════════╗
    ║         PROTOCOLO DE COLETA SEQUENCIAL — OBRIGATÓRIO        ║
    ║  Siga RIGOROSAMENTE esta ordem. NÃO pule etapas.            ║
    ║                                                             ║
    ║  ETAPA 1A — NOME                                            ║
    ║    → Se o nome for 'desconhecido', você DEVE perguntar o    ║
    ║      nome ANTES de perguntar a data de nascimento ou        ║
    ║      falar sobre serviços.                                  ║
    ║    → "Para iniciarmos, como posso te chamar?"               ║
    ║                                                             ║
    ║  ETAPA 1B — DATA DE NASCIMENTO                              ║
    ║    → Se o nome JÁ for conhecido, mas a DATA DE NASCIMENTO   ║
    ║      CADASTRADA for 'Não', você DEVE perguntar a data ANTES ║
    ║      de avançar para os serviços.                           ║
    ║    → "[Nome], qual a sua data de nascimento para            ║
    ║      atualizarmos seu cadastro?"                            ║
    ║                                                             ║
    ║    ⚠ BLOQUEIO ABSOLUTO: Você NÃO PODE listar serviços,      ║
    ║      perguntar horários, nem avançar para NENHUMA outra     ║
    ║      etapa enquanto não tiver coletado o NOME e a DATA DE   ║
    ║      NASCIMENTO (um por vez).                               ║
    ║                                                             ║
    ║  ETAPA 2 — SERVIÇO                                          ║
    ║    → Pergunte se o cliente já conhece os serviços da        ║
    ║      loja ou se prefere que você envie a lista de           ║
    ║      serviços disponíveis.                                  ║
    ║    → SÓ LISTE OS SERVIÇOS se o cliente pedir a lista ou     ║
    ║      disser que não conhece.                                ║
    ║    → Não avance para a ETAPA 3 sem um serviço confirmado.   ║
    ║                                                             ║
    ║  ETAPA 3 — DATA E HORÁRIO                                   ║
    ║    → Com o serviço confirmado, pergunte a data E o horário  ║
    ║      desejado numa única mensagem.                          ║
    ║    → Não tente confirmar o agendamento. Apenas colete.      ║
    ║                                                             ║
    ║  TRAVA ANTI-LOOP: Se algum dado já foi coletado (está no    ║
    ║  histórico ou foi extraído desta mensagem), NÃO pergunte    ║
    ║  novamente. Vá direto para o próximo dado faltante.         ║
    ║                                                             ║
    ║  PROIBIÇÃO ABSOLUTA: Você JAMAIS deve confirmar o           ║
    ║  agendamento para o cliente. Frases como "Agendamento       ║
    ║  realizado!", "Pronto, agendei!" são ESTRITAMENTE           ║
    ║  PROIBIDAS. O sistema é quem confirma, não você.            ║
    ╚══════════════════════════════════════════════════════════════╝

    REGRAS DE OURO DA LAU:
    1. Se o cliente informar o serviço, data ou horário, extraia-os imediatamente.
    2. Formato de Data (Agendamento): Devolva SEMPRE no formato ISO YYYY-MM-DD (ex: 2026-05-25) para compatibilidade com o banco de dados. Se não identificado, use null.
    2b. Formato de Data (Nascimento): Se o cliente informar a data de nascimento de qualquer jeito (ex: "10 de maio", "10/05/98"), converta SEMPRE para o formato completo DD/MM/YYYY (ex: 10/05/1998). Se ele não disser o ano, converta para DD/MM/YYYY usando um ano padrão como 2000 ou pergunte o ano. O padrão retornado no JSON deve ser obrigatoriamente DD/MM/YYYY.
    3. Formato de Hora: Devolva SEMPRE no padrão HH:MM (ex: 14:30). Se não identificado, use null.
    4. REGRA DE SERVIÇO: Se o cliente pedir um ou mais serviços, você DEVE retornar uma LISTA (array de strings) com os nomes exatos de cada serviço desejado dentre os SERVIÇOS DISPONÍVEIS. Se não houver correspondência possível na lista, retorne null.
    4b. REGRA DE SERVIÇO AMBÍGUO: Se o cliente usar um termo genérico que corresponda a MAIS DE UM serviço disponível (ex: "massagem" quando há "Massagem Relaxante" e "Massagem Modeladora"), você DEVE perguntar qual dos serviços o cliente deseja, listando APENAS as opções correspondentes. NÃO escolha por ele. Retorne servico como null e peça especificação no campo 'mensagem_resposta'.
    5. REGRA DE NOME E NASCIMENTO:
       - Se nome ou data de nascimento faltarem, a ETAPA 1 é bloqueante.
       - EXTRAÇÃO AUTOMÁTICA: Sempre que o cliente mencionar o nome ou data, extraia imediatamente para o JSON.
       - Se o cliente já tiver nome conhecido, USE-O nas respostas (ex: "Maria, qual horário você gostaria?").
    6. Respostas Curtas e Personalizadas: Mantenha o campo 'mensagem_resposta' focado APENAS no dado que está faltando naquele momento. Não faça múltiplas perguntas ao mesmo tempo, exceto na ETAPA 3 onde data e hora são pedidos juntos.
    7. LISTAGEM DE SERVIÇOS: Quando o cliente pedir a lista, copie a formatação exata do bloco SERVIÇOS DISPONÍVEIS (com os bullet points '•' e os preços). É obrigatório que cada serviço seja em um parágrafo separado (um por linha). É ESTRITAMENTE PROIBIDO exibir o bloco "[Duração interna: X]" para o cliente.
    8. ENCERRAMENTO: Retorne 'encerrar' APENAS se o cliente expressamente pedir para cancelar, desistir ou encerrar a conversa (ex: "deixa pra lá", "não quero mais", "cancelar", "obrigado, tchau"). Se o cliente enviar apenas o nome de uma loja, uma palavra solta ou uma saudação, assuma a intenção de 'saudacao' ou 'agendar', NUNCA 'encerrar'.
    9. DADOS COMPLETOS — SILÊNCIO OBRIGATÓRIO: Se nesta resposta você extraiu servico + data + hora (todos os três preenchidos), o campo 'mensagem_resposta' DEVE ser uma string VAZIA "". É TERMINANTEMENTE PROIBIDO gerar mensagens como "Estou coletando...", "Aguarde...", "Processando..." ou qualquer outra frase de transição. O sistema back-end detecta os dados completos e envia a confirmação automaticamente. Qualquer mensagem sua nesse momento seria duplicada e errada.
    10. INTENÇÃO: Se o cliente quiser marcar um horário, use "agendar". Se o cliente quiser saber seus horários marcados ou consultar agendamentos, use "consultar".

    O formato JSON estrito DEVE ser retornado sem blocos markdown (```json):
    {{
        "intencao": "agendar" ou "consultar" ou "saudacao" ou "duvida" ou "encerrar",
        "nome_cliente": "nome extraído da pessoa, ou null",
        "data_nascimento": "DD/MM/YYYY ou null se o cliente falar a data de nascimento",
        "servico": ["serviço 1", "serviço 2"] ou null,
        "data": "YYYY-MM-DD, ou null",
        "hora": "HH:MM, ou null",
        "mensagem_resposta": "Sua pergunta direta, curta e personalizada sobre o dado faltante. VAZIO se todos os dados (servico+data+hora) já foram coletados."
    }}"""
    
    messages_payload = cast(list[ChatCompletionMessageParam], [
        {"role": "system", "content": prompt_sistema},
        *historico
    ])

    # ── Fallback seguro em caso de falha ──
    fallback = {
        "intencao": "duvida",
        "nome_cliente": None,
        "data_nascimento": None,
        "servico": None,
        "data": None,
        "hora": None,
        "mensagem_resposta": "Desculpe, tive uma dificuldade técnica. Pode repetir o que precisa?"
    }

    try:
        # cast() é necessário pois o Pylance não resolve o overload de create()
        # corretamente a partir dos type stubs do SDK — em runtime, stream=False
        # garante que o retorno é sempre ChatCompletion.
        response = cast(
            ChatCompletion,
            await client_ai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages_payload,
                response_format={"type": "json_object"},
                temperature=0.1,
                stream=False,
            )
        )
        
        conteudo_texto = response.choices[0].message.content
        if not conteudo_texto:
            logger.warning("OpenAI retornou resposta vazia")
            return fallback

        resultado = json.loads(conteudo_texto)
        return resultado

    except RateLimitError:
        logger.error("OpenAI: rate limit atingido — aguarde e tente novamente")
        return fallback

    except APIConnectionError as e:
        logger.error("OpenAI: falha de conexão: %s", e)
        return fallback

    except APIStatusError as e:
        logger.error("OpenAI: erro de API (status %s): %s", e.status_code, e.message)
        return fallback

    except json.JSONDecodeError as e:
        logger.error("OpenAI: JSON inválido na resposta: %s", e)
        return fallback

    except Exception as e:
        logger.error("OpenAI: erro inesperado: %s", e)
        return fallback


# =========================================================
# EXTRAÇÃO SIMPLES DE DATA E HORA
# =========================================================
async def extrair_data_hora_com_ia(texto_cliente: str, nome_loja: str) -> dict:
    """
    Função dedicada exclusivamente a extrair data e hora de uma string solta
    (ex: "amanhã às 15h"). Ignora regras de nome ou serviço.
    """
    tz_br = ZoneInfo("America/Sao_Paulo")
    data_hora_atual = datetime.now(tz_br).strftime("%d-%m-%Y %H:%M")
    dias_semana_pt = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
    hoje = datetime.now(tz_br)
    dia_semana_hoje = dias_semana_pt[hoje.weekday()]
    proximos_dias = []
    for i in range(14):
        d = hoje + timedelta(days=i)
        proximos_dias.append(f"  - {dias_semana_pt[d.weekday()]}: {d.strftime('%Y-%m-%d')}")
    calendario_referencia = "\n".join(proximos_dias)

    prompt_sistema = f"""Você é a Lau, assistente da loja '{nome_loja}'.
    Sua ÚNICA função é extrair a data e o horário solicitados pelo cliente para reagendamento/cancelamento.
    Agora é exatamente {data_hora_atual}. Hoje é {dia_semana_hoje}.

    CALENDÁRIO DE REFERÊNCIA (próximos 14 dias):
{calendario_referencia}

    Regras de Interpretação:
    - "hoje" → {hoje.strftime('%Y-%m-%d')}
    - "amanhã" → {(hoje + timedelta(days=1)).strftime('%Y-%m-%d')}
    - Nomes de dias da semana referem-se à PRÓXIMA ocorrência.
    - O ANO ATUAL é {hoje.year}. Se o cliente não especificar o ano, assuma {hoje.year}.
    - Se o cliente informar apenas dia e mês (ex: "25/01", "dia 15 de março"): se a data resultante já passou no ano atual, assuma AUTOMATICAMENTE que ele está falando do ANO QUE VEM.
    - Se o cliente informar APENAS O DIA (ex: "dia 10") e o dia 10 deste mês já passou, assuma AUTOMATICAMENTE o PRÓXIMO MÊS.
    - REGRA CRÍTICA: É PROIBIDO retornar qualquer data anterior a {hoje.strftime('%Y-%m-%d')}. Se a data resultante (mesmo com ajustes) for no passado, retorne null para o campo "data".

    Formato de Saída (JSON Estrito):
    {{
        "data": "YYYY-MM-DD" ou null se não houver data explícita ou dedutível,
        "hora": "HH:MM" ou null se não houver horário explícito
    }}
    Retorne APENAS o JSON, sem markdown.
    """

    messages_payload = cast(list[ChatCompletionMessageParam], [
        {"role": "system", "content": prompt_sistema},
        {"role": "user", "content": texto_cliente}
    ])

    fallback = {"data": None, "hora": None}

    try:
        response = cast(
            ChatCompletion,
            await client_ai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages_payload,
                response_format={"type": "json_object"},
                temperature=0.1,
                stream=False,
            )
        )
        conteudo = response.choices[0].message.content
        if not conteudo: return fallback
        return json.loads(conteudo)
    except Exception as e:
        logger.error("OpenAI erro na extração de data/hora: %s", e)
        return fallback