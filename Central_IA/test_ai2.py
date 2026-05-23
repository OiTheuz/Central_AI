import asyncio
from app.services.openai_service import analisar_mensagem_com_ia

async def run_test():
    historico = [
        {"role": "user", "content": "Moura"},
        {"role": "assistant", "content": "Matheus, você gostaria de agendar um serviço no Estabelecimento Moura? Qual serviço você precisa?"},
        {"role": "user", "content": "Cortar o cabelo"},
        {"role": "assistant", "content": "Matheus, para qual dia você gostaria de agendar o corte de cabelo?"},
        {"role": "user", "content": "dia 24 as 12:00"}
    ]
    res = await analisar_mensagem_com_ia(historico, "cliente_antigo", "Matheus")
    print(res)

if __name__ == "__main__":
    asyncio.run(run_test())
