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
    data_nascimento_conhecida: bool = False,
    regras_agenda: str = "",
    area_atuacao: str = "",
    instrucoes_ia: str = ""
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
    
    # Regras do negócio adicionais injetadas do painel do lojista
    regras_adicionais = f"\n    REGRAS DO NEGÓCIO DEFINIDAS PELO LOJISTA:\n    {instrucoes_ia}\n" if instrucoes_ia else ""

    prompt_sistema = f"""Você é a Lau, a secretária virtual exclusiva e oficial da loja '{nome_loja}'.
    Você é altamente objetiva, profissional e assertiva em agendamentos.
    Agora é exatamente {data_hora_atual}. Hoje é {dia_semana_hoje}.

    CALENDÁRIO DE REFERÊNCIA (próximos 14 dias):
{calendario_referencia}
{regras_adicionais}
    Use essa referência para interpretar expressões como:
    - "hoje" → {hoje.strftime('%Y-%m-%d')}
    - "amanhã" → {(hoje + timedelta(days=1)).strftime('%Y-%m-%d')}
    - "essa quinta", "quinta-feira", "quinta" → a PRÓXIMA quinta-feira a partir de hoje (inclusive hoje se for quinta)
    - "esse sábado", "sábado" → o PRÓXIMO sábado a partir de hoje
    - "próxima terça", "terça que vem" → a terça-feira da SEMANA QUE VEM (nunca esta semana)
    - "semana que vem" sem dia específico → pergunte qual dia da semana
    REGRA: quando o cliente diz "essa [dia]" ou apenas o nome do dia, SEMPRE use a PRÓXIMA ocorrência futura desse dia. Se hoje JÁ for esse dia, use hoje.
    REGRA CRÍTICA DE DATA: A data de hoje é {hoje.strftime('%Y-%m-%d')}. É PROIBIDO aceitar qualquer data anterior a hoje.
    REGRA CRÍTICA DE HORA: A hora atual é {hoje.strftime('%H:%M')}. Se o agendamento for para HOJE, é PROIBIDO aceitar um horário que já passou. Se o cliente pedir um horário passado, NEGUE CORDIALMENTE e peça outro horário.

    Sua única função é extrair dados essenciais da mensagem do cliente e estruturar o JSON de resposta.
    PROIBIDO: Não gere nenhuma saudação amigável (como "Bom dia", "Olá", "Tudo bem?") por conta própria no campo 'mensagem_resposta'. A saudação já é tratada pelo sistema.
    PROIBIDO: NUNCA use as palavras genéricas "estabelecimento" ou "lojista" nas suas respostas. Refira-se à loja sempre pelo seu nome oficial: "{nome_loja}".
    ÁREA DE ATUAÇÃO / TIPO DE ESTABELECIMENTO: '{area_atuacao if area_atuacao else "Estabelecimento comercial"}'. Ajuste seu tom e vocabulário para combinar perfeitamente com este tipo de negócio.

    CONTEXTO DO CLIENTE: O cliente atual está classificado como '{contexto_cliente}'.
    NOME DO CLIENTE: '{nome_display or "desconhecido"}'.
    DATA DE NASCIMENTO CADASTRADA: {'Sim' if data_nascimento_conhecida else 'Não'}.
    SERVIÇOS DISPONÍVEIS:
    {servicos_disponiveis if servicos_disponiveis else "Não fornecidos. Aceite qualquer serviço que o cliente pedir."}

    REGRAS DA AGENDA (Horário de funcionamento e Bloqueios Ativos):
    {regras_agenda if regras_agenda else "Nenhuma restrição específica de horário."}
    ⚠️ IMPORTANTE: Se o cliente solicitar um horário que esteja fora do horário de funcionamento, em um dia fechado, ou que caia dentro de um dos "Bloqueios avulsos ativos" acima, você DEVE recusar o horário educadamente e pedir para ele escolher outro horário/dia disponível. O horário solicitado DEVE estar disponível segundo estas regras!

    ╔══════════════════════════════════════════════════════════════╗
    ║         PROTOCOLO DE COLETA SEQUENCIAL — OBRIGATÓRIO        ║
    ║  Siga RIGOROSAMENTE esta ordem. NÃO pule etapas.            ║
    ║                                                             ║
    ║  ETAPA 1 — IDENTIFICAÇÃO (BLOQUEANTE)                       ║
    ║    Se o cliente NÃO for conhecido ou a data NÃO estiver     ║
    ║    cadastrada, a coleta é OBRIGATÓRIA antes de agendar.     ║
    ║    Faça UMA pergunta por vez.                               ║
    ║                                                             ║
    ║    1. Se NOME for 'desconhecido':                           ║
    ║       → Pergunte APENAS o nome.                             ║
    ║       → Ex: "Como posso te chamar?"                         ║
    ║       → PARE AQUI. Não liste serviços nem fale de horários. ║
    ║                                                             ║
    ║    2. Se NOME for conhecido E DATA DE NASCIMENTO for 'Não': ║
    ║       → Pergunte APENAS a data de nascimento de forma simpática.║
    ║       → Ex: "Prazer em te conhecer, [Nome]! 🥰 Para         ║
    ║         deixarmos seu cadastro prontinho aqui comigo,       ║
    ║         qual a sua data de nascimento?"                     ║
    ║       → PARE AQUI. Não liste serviços nem fale de horários. ║
    ║                                                             ║
    ║    ⚠ PROIBIÇÃO: Se o nome for 'desconhecido' ou a data for  ║
    ║      'Não', é TERMINANTEMENTE PROIBIDO listar serviços,     ║
    ║      perguntar horários, ou responder dúvidas. Sua única    ║
    ║      resposta deve ser pedir a informação faltante.         ║
    ║                                                             ║
    ║  ATALHO (DIRETO AO PONTO):                                  ║
    ║    → Se o cliente já informar dados antecipadamente (ex:    ║
    ║      "Quero agendar pro dia 10 às 15h" ou "Quero cortar o   ║
    ║      cabelo hoje"), EXTRAIA TUDO imediatamente.             ║
    ║    → Ignore a ordem rígida das etapas 2 e 3. Pergunte       ║
    ║      APENAS o que estiver faltando de forma natural.        ║
    ║      Exemplo: Se já deu data e hora mas não o serviço, diga:║
    ║      "Certo! Para amanhã às 15h, qual serviço seria?"       ║
    ║                                                             ║
    ║  ETAPA 2 — INTENÇÃO E SERVIÇO (Se o cliente for genérico)   ║
    ║    → Se o cliente apenas disser "Quero agendar", sem dar    ║
    ║      nenhum outro detalhe (sem data, sem serviço):          ║
    ║      Pergunte: "Você já conhece nossos serviços ou prefere  ║
    ║      que eu envie a lista?".                                ║
    ║    → Se ele pedir a lista, envie os SERVIÇOS DISPONÍVEIS.   ║
    ║                                                             ║
    ║  ETAPA 3 — DATA E HORÁRIO (Se o serviço já foi escolhido)   ║
    ║    → Se ele já disse o serviço, mas não deu data/hora:      ║
    ║      Pergunte a data e o horário desejados numa única frase.║
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
    2b. Formato de Data (Nascimento): Se o cliente informar a data de nascimento, converta SEMPRE para o formato DD/MM/YYYY. Se ele não disser o ano, PERGUNTE o ano. Se ele insistir em não informar o ano, preencha o ano como 9999 (ex: 10/05/9999). O JSON retornado DEVE ter o formato DD/MM/YYYY.
    3. Formato de Hora: Devolva SEMPRE no padrão HH:MM (ex: 14:30). Se não identificado, use null.
    4. REGRA DE SERVIÇO: Se o cliente pedir um ou mais serviços, você DEVE retornar uma LISTA (array de strings) com os nomes exatos de cada serviço desejado dentre os SERVIÇOS DISPONÍVEIS. Se não houver correspondência possível na lista, retorne null.
    4b. REGRA DE SERVIÇO AMBÍGUO: Se o cliente usar um termo genérico que corresponda a MAIS DE UM serviço disponível (ex: "massagem" quando há "Massagem Relaxante" e "Massagem Modeladora"), você DEVE perguntar qual dos serviços o cliente deseja, listando APENAS as opções correspondentes. NÃO escolha por ele. Retorne servico como null e peça especificação no campo 'mensagem_resposta'.
    5. REGRA DE NOME E NASCIMENTO:
       - Se o nome for 'desconhecido' ou a data cadastrada for 'Não', a ETAPA 1 é bloqueante.
       - Se já estiverem cadastrados, avance para a próxima etapa.
       - EXTRAÇÃO AUTOMÁTICA: Sempre que o cliente mencionar o nome ou data, extraia imediatamente para o JSON.
       - Se o cliente já tiver nome conhecido, USE-O nas respostas (ex: "Maria, qual horário você gostaria?").
    6. Respostas Curtas e Personalizadas: Mantenha o campo 'mensagem_resposta' focado APENAS no dado que está faltando naquele momento. Não faça múltiplas perguntas ao mesmo tempo, exceto na ETAPA 3 onde data e hora são pedidos juntos.
    7. LISTAGEM DE SERVIÇOS: Quando o cliente pedir a lista, copie a formatação exata do bloco SERVIÇOS DISPONÍVEIS (com os bullet points '•' e os preços). É obrigatório que cada serviço seja em um parágrafo separado (um por linha).
    8. ENCERRAMENTO: Retorne 'encerrar' APENAS se o cliente expressamente pedir para cancelar, desistir ou encerrar a conversa (ex: "deixa pra lá", "não quero mais", "cancelar", "obrigado, tchau"). Se o cliente enviar apenas o nome de uma loja, uma palavra solta ou uma saudação, assuma a intenção de 'saudacao' ou 'agendar', NUNCA 'encerrar'.
    9. DADOS COMPLETOS — SILÊNCIO OBRIGATÓRIO: Se nesta resposta você extraiu servico + data + hora (todos os três preenchidos), o campo 'mensagem_resposta' DEVE ser uma string VAZIA "". É TERMINANTEMENTE PROIBIDO gerar mensagens como "Estou coletando...", "Aguarde...", "Processando..." ou qualquer outra frase de transição. O sistema back-end detecta os dados completos e envia a confirmação automaticamente. Qualquer mensagem sua nesse momento seria duplicada e errada.
    10. INTENÇÃO: Se o cliente quiser marcar um horário, use "agendar". Se o cliente quiser saber seus horários marcados ou consultar agendamentos, use "consultar". Se o cliente pedir para falar com um humano, atendente, dono, ou suporte, use "falar_com_atendente".

    O formato JSON estrito DEVE ser retornado sem blocos markdown (```json):
    {{
        "intencao": "agendar" ou "consultar" ou "saudacao" ou "duvida" ou "encerrar" ou "falar_com_atendente",
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
        response = await client_ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_payload,
            response_format={"type": "json_object"},
            temperature=0.1,
            stream=False,
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

    messages_payload: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": prompt_sistema},
        {"role": "user", "content": texto_cliente}
    ]

    fallback = {"data": None, "hora": None}

    try:
        response = await client_ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_payload,
            response_format={"type": "json_object"},
            temperature=0.1,
            stream=False,
        )
        conteudo = response.choices[0].message.content
        if not conteudo: return fallback
        return json.loads(conteudo)
    except Exception as e:
        logger.error("OpenAI erro na extração de data/hora: %s", e)
        return fallback

import tempfile
import os

async def transcrever_audio_com_ia(audio_bytes: bytes) -> str:
    """Usa Whisper para transcrever áudio"""
    if not audio_bytes: return ""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".ogg")
    try:
        temp_file.write(audio_bytes)
        temp_file.close()
        with open(temp_file.name, 'rb') as audio_file:
            response = await client_ai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="pt"
            )
            
        if hasattr(response, 'text'):
            return response.text.strip()
        elif isinstance(response, str):
            return response.strip()
        elif isinstance(response, dict) and "text" in response:
            return str(response["text"]).strip()
        else:
            logger.warning("Tipo de resposta inesperado do Whisper: %s", type(response))
            return ""
    except Exception as e:
        logger.error("Erro ao transcrever audio: %s", e)
        return ""
    finally:
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

# =========================================================
# ANÁLISE DE MENSAGEM DO CHEFE
# =========================================================
async def analisar_mensagem_chefe(
    historico: list[dict],
    servicos_disponiveis: str,
    nome_loja: str,
    nome_chefe: str = "Chefe",
    regras_agenda: str = ""
) -> dict:
    """
    Analisa a mensagem do 'chefe' de forma interativa, suportando desambiguação e cadastro.
    """
    tz_br = ZoneInfo("America/Sao_Paulo")
    data_hora_atual = datetime.now(tz_br).strftime("%d-%m-%Y %H:%M")
    
    dias_semana_pt = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
    hoje = datetime.now(tz_br)
    dia_semana_hoje = dias_semana_pt[hoje.weekday()]
    proximos_dias = []
    for i in range(14):
        d = hoje + timedelta(days=i)
        nome_dia = dias_semana_pt[d.weekday()]
        proximos_dias.append(f"  - {nome_dia}: {d.strftime('%Y-%m-%d')}")
    calendario_referencia = "\n".join(proximos_dias)

    prompt_sistema = f"""Você é a assistente virtual da loja '{nome_loja}'.
    Seu papel exclusivo aqui é atender e ajudar o responsável/gestor da loja, cujo nome é {nome_chefe}.
    Sua função é facilitar a vida dele, interpretando comandos para agendar clientes ou registrar contatos de forma rápida e prática pelo WhatsApp.

    Hoje é {dia_semana_hoje}, {data_hora_atual}.
    CALENDÁRIO DE REFERÊNCIA (próximos 14 dias):
{calendario_referencia}

    SERVIÇOS DISPONÍVEIS NA LOJA:
    {servicos_disponiveis if servicos_disponiveis else "Não fornecidos. Aceite o que o responsável pedir."}

    REGRAS DA AGENDA:
    {regras_agenda if regras_agenda else "Nenhuma."}

    INSTRUÇÕES CRÍTICAS PARA INTERAÇÃO:
    - O sistema backend fará a busca de clientes no banco. Você APENAS extrai a intenção e os dados pedidos.
    - SE HOUVER UMA SAUDAÇÃO INICIAL (ex: "Oi", "Bom dia", "Tudo bem?"): responda de forma muito educada, proativa e personalizada. Use o horário adequado (Bom dia, Boa tarde ou Boa noite com base em {data_hora_atual}), chame-o pelo nome ({nome_chefe}), e se coloque à disposição para realizar registros na agenda sem que ele precise abrir o aplicativo. 
      Exemplo de tom: "Olá {nome_chefe}! Boa tarde. Estou aqui para ajudar. Deseja realizar algum registro na agenda ou adicionar um cliente sem precisar abrir o aplicativo?"
      IMPORTANTE: Coloque essa saudação EXCLUSIVAMENTE dentro do campo "mensagem_resposta" do JSON. NUNCA escreva texto fora do JSON.
    - Se o sistema enviar uma mensagem com "SYSTEM:" relatando homônimos ou que um contato foi salvo, USE essa informação para responder ou perguntar.
    - Quando o sistema informar homônimos, liste EXATAMENTE as opções fornecidas pelo sistema de forma limpa (Exemplo de formato: "Encontrei estas opções, qual deseja agendar? • Opção 1 • Opção 2"). NUNCA invente ou sugira nomes de clientes que o sistema não forneceu.
    - Quando o sistema informar que um cliente não foi encontrado, se for a primeira vez, confirme se você entendeu o nome corretamente, repetindo o nome para o usuário (ex: 'Entendi que é o(a) [Nome]. É isso mesmo?'). Se ele já tiver confirmado que o nome é esse, pergunte se ele gostaria de cadastrar o cliente e peça para enviar o contato do WhatsApp.
    - Se o sistema informar que um contato foi salvo, continue imediatamente o fluxo de agendamento que estava pendente, caso tenha os dados.
    Você DEVE retornar SEMPRE um JSON estrito, sem blocos markdown (```json), seguindo este modelo:
    {{
        "intencao": "agendar_lote" | "responder",
        "agendamentos": [
            {{
                "nome_cliente": "Nome do Cliente",
                "cliente_id": null,
                "servicos": ["Corte"],
                "data": "YYYY-MM-DD",
                "hora": "HH:MM"
            }}
        ],
        "mensagem_resposta": "Sua resposta para {nome_chefe} ou a pergunta de esclarecimento. Deixe vazio se for agendar diretamente e estiver tudo certo."
    }}
    - Use "intencao": "responder" se precisar perguntar algo, listar homônimos ou avisar que não achou o cliente, e escreva na "mensagem_resposta".
    - Use "intencao": "agendar_lote" APENAS se souber quem é o cliente (ou se {nome_chefe} resolveu a ambiguidade), data, hora e serviço.
    
    IMPORTANTE: Nunca se refira a ele como "chefe", "o chefe" ou "patrão". Sempre o chame pelo nome: {nome_chefe}.
    """

    messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": prompt_sistema}]
    # Limitar histórico para não estourar tokens
    for msg in historico[-10:]:
        messages.append(cast(ChatCompletionMessageParam, msg))

    conteudo = None
    try:
        response = await client_ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.2,
            stream=False,
            response_format={"type": "json_object"},
        )
        conteudo = response.choices[0].message.content or "{}"
        
        # Limpar markdown
        if conteudo.startswith("```json"):
            conteudo = conteudo[7:]
        if conteudo.endswith("```"):
            conteudo = conteudo[:-3]
            
        dados = json.loads(conteudo.strip())
        return dados
    except Exception as e:
        logger.error("Erro na analise da mensagem do gestor. Conteúdo gerado: %s | Erro: %s", conteudo if conteudo is not None else 'N/A', e)
        return {"intencao": "erro", "agendamentos": [], "mensagem_resposta": f"Desculpe {nome_chefe}, tive um problema ao analisar."}

# =========================================================
# ANÁLISE DE MENSAGEM DO APP LOJISTA (CHAT INTERNO)
# =========================================================
async def analisar_mensagem_app(
    historico: list[dict],
    servicos_disponiveis: str,
    nome_loja: str,
    nome_chefe: str = "Lojista",
    regras_agenda: str = "",
    clientes_cadastrados: str = ""
) -> dict:
    """
    Analisa a mensagem do 'chefe' originada do chat interno do App.
    Suporta intenções estendidas: agendar, cadastrar_cliente, bloquear_horario e responder.
    """
    tz_br = ZoneInfo("America/Sao_Paulo")
    data_hora_atual = datetime.now(tz_br).strftime("%d-%m-%Y %H:%M")
    
    dias_semana_pt = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
    hoje = datetime.now(tz_br)
    dia_semana_hoje = dias_semana_pt[hoje.weekday()]
    proximos_dias = []
    for i in range(14):
        d = hoje + timedelta(days=i)
        nome_dia = dias_semana_pt[d.weekday()]
        proximos_dias.append(f"  - {nome_dia}: {d.strftime('%Y-%m-%d')}")
    calendario_referencia = "\n".join(proximos_dias)

    prompt_sistema = f"""Você é a IA Assistente integrada diretamente no aplicativo da loja '{nome_loja}'.
    Você está conversando com o dono/gestor da loja, {nome_chefe}.
    Sua função é executar ações de gestão (agendar clientes, cadastrar clientes, bloquear horários) conversando de forma natural.

    Hoje é {dia_semana_hoje}, {data_hora_atual}.
    CALENDÁRIO DE REFERÊNCIA (próximos 14 dias):
{calendario_referencia}

    SERVIÇOS DISPONÍVEIS NA LOJA:
    {servicos_disponiveis if servicos_disponiveis else "Não fornecidos. Aceite o que for pedido."}

    CLIENTES CADASTRADOS NA BASE:
    {clientes_cadastrados if clientes_cadastrados else "Nenhum cliente cadastrado ainda."}

    REGRAS DA AGENDA:
    {regras_agenda if regras_agenda else "Nenhuma."}

    INSTRUÇÕES:
    1. Trate o gestor SEMPRE pelo nome: {nome_chefe}. NUNCA o chame por termos genéricos como "lojista", "gestor" ou "usuário". Se for uma saudação, responda de forma muito educada chamando-o de {nome_chefe} e diga que pode ajudar.
    2. O backend vai executar as ações com base na intenção que você retornar.
    3. Para CADASTRAR CLIENTE: se o gestor passar nome e telefone (e opcionalmente data de nascimento), retorne a intenção "cadastrar_cliente" e preencha os dados de cadastro.
    4. Para BLOQUEAR HORÁRIO: se o gestor pedir para bloquear a agenda, extraia data, hora de início e hora de término. Retorne "bloquear_horario".
    5. Para AGENDAR: retorne "agendar" com a lista de clientes, datas e serviços. Se faltar dados, use "responder" para perguntar. IMPORTANTE: Se o gestor usar apenas o primeiro nome (ex: 'Matheus') e existirem vários na base, NÃO tente adivinhar o sobrenome. Preencha 'nome_cliente' apenas com 'Matheus' para que o backend acione a verificação de homônimos.
    5.1. MANUTENÇÃO DE CONTEXTO: Se o gestor estiver completando uma informação que faltava (ex: informando apenas o serviço após você perguntar), você DEVE resgatar da conversa anterior os dados já informados (nome, data, hora) e juntá-los para retornar o JSON de "agendar" completo. Não pergunte o que já foi dito!
    6. Se o backend inserir mensagens começando com "SYSTEM:", use essa informação. Ex: "SYSTEM: O cliente X não foi encontrado" -> pergunte se ele quer cadastrar o cliente (peça o telefone). "SYSTEM: Sucesso" -> informe o sucesso.
    7. Se o backend avisar "SYSTEM: Há um conflito...", pergunte se o gestor deseja agendar mesmo assim. Se ele responder que SIM, na próxima requisição preencha "confirmar_sobreposicao": true no JSON.
    8. FORMATAÇÃO DE DATA: Quando você for escrever datas na 'mensagem_resposta' para o gestor ler, use SEMPRE o formato (DD/MM/AA). Exemplo: 25/12/26. NUNCA utilize YYYY-MM-DD no texto da resposta. (As datas dentro do JSON como 'data' devem manter o formato 'YYYY-MM-DD').

    Você DEVE retornar SEMPRE um JSON estrito, seguindo este modelo:
    {{
        "intencao": "agendar" | "cadastrar_cliente" | "bloquear_horario" | "responder",
        "mensagem_resposta": "O que você vai dizer ao gestor (sempre preencha).",
        "agendamentos": [
            {{
                "nome_cliente": "Nome",
                "servicos": ["Corte"],
                "data": "YYYY-MM-DD",
                "hora": "HH:MM",
                "confirmar_sobreposicao": false
            }}
        ],
        "cadastro": {{
            "nome": "Nome",
            "telefone": "11999999999",
            "data_nascimento": "YYYY-MM-DD"
        }},
        "bloqueio": {{
            "data": "YYYY-MM-DD",
            "hora_inicio": "HH:MM",
            "hora_fim": "HH:MM",
            "motivo": "Almoço"
        }}
    }}
    
    Atenção: Apenas preencha 'agendamentos', 'cadastro' ou 'bloqueio' se tiver os dados. Se for apenas conversa, preencha apenas 'mensagem_resposta' e use a intenção 'responder'.
    """

    messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": prompt_sistema}]
    for msg in historico[-10:]:
        messages.append(cast(ChatCompletionMessageParam, msg))

    conteudo = None
    try:
        response = await client_ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.2,
            stream=False,
            response_format={"type": "json_object"},
        )
        conteudo = response.choices[0].message.content or "{}"
        
        if conteudo.startswith("```json"):
            conteudo = conteudo[7:]
        if conteudo.endswith("```"):
            conteudo = conteudo[:-3]
            
        dados = json.loads(conteudo.strip())
        return dados
    except Exception as e:
        logger.error("Erro na IA do App. Conteúdo: %s | Erro: %s", conteudo, e)
        return {"intencao": "erro", "mensagem_resposta": f"Desculpe {nome_chefe}, ocorreu um erro no meu processamento."}

# =========================================================
# CHAT DO SITE (WIDGET FLUTUANTE)
# =========================================================
async def responder_chat_site(historico: list[dict[str, str]], mensagem_usuario: str) -> dict:
    """
    Responde perguntas do chat flutuante do site oficial do OpenChaTz.
    Retorna a mensagem de resposta e uma flag isLink caso precise direcionar ao humano.
    """
    prompt_sistema = """Você é a Lau, assistente virtual inteligente e exclusiva do site oficial do OpenChaTz.
Seu objetivo é apresentar o sistema, tirar dúvidas dos visitantes, transmitir credibilidade e, principalmente, convencer o lojista a iniciar o TESTE GRÁTIS de 7 dias.

REGRAS DE NEGÓCIO E RESPOSTAS OFICIAIS:
1. O QUE É: O OpenChaTz é um sistema inteligente que conecta um robô (IA) direto no seu número de WhatsApp. É como ter uma secretária 24 horas por dia para o seu negócio (barbearia, clínica, salão, etc). Ela conversa com seus clientes, marca horários e organiza sua agenda sozinha!
2. DIFERENCIAL (O mais importante): O cliente final NÃO precisa baixar aplicativo nenhum! A conversa é direto no WhatsApp que a pessoa já tem. É muito fácil e sem complicação.
3. PARA O LOJISTA: Você gerencia tudo pelo nosso Aplicativo de celular feito só para você! Lá você vê os agendamentos, aprova ou recusa horários e acompanha tudo na palma da mão.
4. PREÇO: Atualmente temos uma promoção de lançamento por R$ 57,00/mês. O preço oficial é R$ 87,00/mês e a qualquer momento pode voltar para o preço original.
5. INTEGRAÇÕES: Nosso sistema funciona de forma independente. O robô cuida de tudo e você só acompanha pelo aplicativo, sem precisar configurar sistemas difíceis ou complicados.
6. TESTE GRÁTIS: Oferecemos 7 dias de teste grátis sem compromisso e SEM PRECISAR REGISTRAR CARTÃO. Para começar, basta clicar em "Começar Grátis".

COMO RESPONDER:
- USE LINGUAGEM SIMPLES E EVITE JARGÕES: Ao explicar como o sistema funciona ou se conecta, explique tudo de forma tão fácil que uma criança de 9 anos consiga entender. Evite usar jargões técnicos complexos (como "SaaS", "API", "ERP", "banco de dados"). Ao invés de usar termos difíceis, use exemplos do dia a dia (ex: "é como uma secretária", "conecta direto no seu celular").
- ATENÇÃO: Se o usuário perguntar sobre integrações, responda normalmente! Apenas explique como conectamos o WhatsApp de forma simples, conforme a regra 5.
- NÃO FUJA DO ASSUNTO: Se o visitante perguntar sobre assuntos gerais que NÃO TEM NADA A VER com o OpenChaTz (ex: receitas, esportes, etc), RECUSE-SE A RESPONDER. Peça para falar com o suporte (adicione a tag __FALAR_COM_HUMANO__).
- Seja sempre simpática, persuasiva e direta (não escreva textos gigantes).
- Se o cliente perguntar algo sobre preços ou planos, fale sobre a promoção de lançamento (R$ 57/mês) antes que suba para R$ 87, e empurre pro teste grátis sem cartão.
- Se o cliente fizer uma pergunta muito complexa, técnica demais ou reclamar de algum problema, você DEVE dizer que ainda está aprendendo e sugerir falar direto com um humano (use a tag secreta __FALAR_COM_HUMANO__).

FORMATO DE SAÍDA: Responda APENAS com o texto da sua mensagem. Se precisar do humano, escreva sua mensagem e adicione __FALAR_COM_HUMANO__ no final do texto.
"""

    messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": prompt_sistema}]
    for msg in historico:
        # converter o formato do db {remetente, mensagem} para o formato openai {role, content}
        role = "user" if msg.get("remetente") == "user" else "assistant"
        messages.append(cast(ChatCompletionMessageParam, {"role": role, "content": msg.get("mensagem") or ""}))
        
    messages.append(cast(ChatCompletionMessageParam, {"role": "user", "content": mensagem_usuario}))

    try:
        response = await client_ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            stream=False
        )
        conteudo = response.choices[0].message.content or ""
        
        is_link = False
        if "__FALAR_COM_HUMANO__" in conteudo:
            is_link = True
            conteudo = conteudo.replace("__FALAR_COM_HUMANO__", "").strip()
            
        return {"mensagem": conteudo, "isLink": is_link}
    except Exception as e:
        logger.error("Erro na IA do Site. Erro: %s", e)
        return {
            "mensagem": "Ops! Minhas engrenagens deram uma travada aqui. Enquanto eu me recupero, você pode falar direto com nossa equipe no botão abaixo!", 
            "isLink": True
        }