import asyncio
from app.services.openai_service import analisar_mensagem_com_ia

async def run_test():
    historico = [
        {"role": "user", "content": "Moura"},
        {"role": "assistant", "content": "Qual o seu nome?"},
        {"role": "user", "content": "Matheus"}
    ]
    res = await analisar_mensagem_com_ia(historico, "cliente_novo", None)
    print(res)

if __name__ == "__main__":
    asyncio.run(run_test())
