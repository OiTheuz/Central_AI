from app.services.schema_service import criar_novo_estabelecimento
import traceback

schema_nome = "Jessiely_Moura"
tabelas = [
    "agendamentos",
    "appointment",
    "appointments",
    "business_hours",
    "client",
    "customers",
    "services",
]

try:
    criar_novo_estabelecimento(schema_nome, tabelas)
    print(f"Schema '{schema_nome}' criado com sucesso.")
except Exception as e:
    print("Erro ao criar schema:")
    traceback.print_exc()
