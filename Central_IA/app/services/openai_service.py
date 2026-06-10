import json
import logging
from datetime import datetime, timedelta
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
    servicos_disponiveis: str = ""
) -> dict:
    """
    Analisa as mensagens e extrai os dados em formato JSON puro.
    contexto_cliente pode ser: 'cliente_novo' ou 'cliente_antigo'
    nome_cliente: nome já conhecido do cliente (ou None se desconhecido)
    servicos_disponiveis: lista de serviços cadastrados no banco para a loja atual

    Retorna um dicionário com os campos extraídos pela IA, ou um fallback
    seguro em caso de erro de API ou JSON inválido.
    """
    data_hora_atual = datetime.now().strftime("%d-%m-%Y %H:%M")
    nome_display = nome_cliente if nome_cliente and nome_cliente != "Cliente" else None

    # Gerar referência dos próximos 14 dias com nomes dos dias da semana em pt-BR
    dias_semana_pt = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
    hoje = datetime.now()
    dia_semana_hoje = dias_semana_pt[hoje.weekday()]
    proximos_dias = []
    for i in range(14):
        d = hoje + timedelta(days=i)
        nome_dia = dias_semana_pt[d.weekday()]
        proximos_dias.append(f"  - {nome_dia}: {d.strftime('%Y-%m-%d')}")
    calendario_referencia = "\n".join(proximos_dias)
    
    prompt_sistema = f"""Você é a inteligência por trás da Lau, uma secretária virtual altamente objetiva, profissional e assertiva de uma Central de Agendamentos.
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

    CONTEXTO DO CLIENTE: O cliente atual está classificado como '{contexto_cliente}'.
    NOME DO CLIENTE: '{nome_display or "desconhecido"}'.
    SERVIÇOS DISPONÍVEIS:
    {servicos_disponiveis if servicos_disponiveis else "Não fornecidos. Aceite qualquer serviço que o cliente pedir."}

    ╔══════════════════════════════════════════════════════════════╗
    ║         PROTOCOLO DE COLETA SEQUENCIAL — OBRIGATÓRIO        ║
    ║  Siga RIGOROSAMENTE esta ordem. NÃO pule etapas.            ║
    ║                                                             ║
    ║  ETAPA 1 — NOME (apenas se cliente_novo e desconhecido)     ║
    ║    → Pergunte o nome do cliente antes de qualquer outra     ║
    ║      coisa. Não passe para a ETAPA 2 sem o nome.            ║
    ║    → Se o cliente já tiver nome conhecido: pule a ETAPA 1.  ║
    ║                                                             ║
    ║  ETAPA 2 — SERVIÇO                                          ║
    ║    → Liste TODOS os serviços disponíveis com os preços      ║
    ║      (sem a duração interna). Peça para o cliente escolher. ║
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
    2. Formato de Data: Devolva SEMPRE no formato ISO YYYY-MM-DD (ex: 2026-05-25) para compatibilidade com o banco de dados. Se não identificado, use null.
    3. Formato de Hora: Devolva SEMPRE no padrão HH:MM (ex: 14:30). Se não identificado, use null.
    4. REGRA DE SERVIÇO: Se o cliente pedir um serviço, você DEVE retornar EXATAMENTE um dos nomes da lista de SERVIÇOS DISPONÍVEIS que melhor corresponda à intenção dele. Se não houver correspondência possível na lista, retorne null.
    5. REGRA DE NOME:
       - Se o contexto for 'cliente_novo' E o nome do cliente for 'desconhecido', peça o nome ANTES de qualquer outra coisa.
       - Se o contexto for 'cliente_antigo' E o nome for 'desconhecido', É PROIBIDO perguntar o nome. Siga o fluxo normalmente.
       - Se o nome do cliente for conhecido, USE-O nas respostas para criar proximidade (ex: "Matheus, qual horário você gostaria de agendar?").
    6. Respostas Curtas e Personalizadas: Mantenha o campo 'mensagem_resposta' focado APENAS no dado que está faltando naquele momento. Não faça múltiplas perguntas ao mesmo tempo, exceto na ETAPA 3 onde data e hora são pedidos juntos.
    7. LISTAGEM DE SERVIÇOS: Quando listar os serviços, copie a formatação exata do bloco SERVIÇOS DISPONÍVEIS (com os bullet points '•' e os preços). É obrigatório que cada serviço seja em um parágrafo separado (um por linha). É ESTRITAMENTE PROIBIDO exibir o bloco "[Duração interna: X]" para o cliente. Apenas informe a duração se o cliente perguntar diretamente.
    8. ENCERRAMENTO: Retorne 'encerrar' APENAS se o cliente expressamente pedir para cancelar, desistir ou encerrar a conversa (ex: "deixa pra lá", "não quero mais", "cancelar", "obrigado, tchau"). Se o cliente enviar apenas o nome de uma loja, uma palavra solta ou uma saudação, assuma a intenção de 'saudacao' ou 'agendamento', NUNCA 'encerrar'.
    9. DADOS COMPLETOS — SILÊNCIO OBRIGATÓRIO: Se nesta resposta você extraiu servico + data + hora (todos os três preenchidos), o campo 'mensagem_resposta' DEVE ser uma string VAZIA "". É TERMINANTEMENTE PROIBIDO gerar mensagens como "Estou coletando...", "Aguarde...", "Processando..." ou qualquer outra frase de transição. O sistema back-end detecta os dados completos e envia a confirmação automaticamente. Qualquer mensagem sua nesse momento seria duplicada e errada.

    O formato JSON estrito DEVE ser retornado sem blocos markdown (```json):
    {{
        "intencao": "agendamento" ou "saudacao" ou "duvida" ou "encerrar",
        "nome_cliente": "nome extraído da pessoa, ou null",
        "servico": "serviço desejado, ou null",
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