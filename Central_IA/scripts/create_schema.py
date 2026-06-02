import sys
import os

# Adiciona o diretório raiz do projeto ao PYTHONPATH para permitir importação do pacote "app"
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.services.schema_service import criar_novo_estabelecimento

# Nome do novo estabelecimento (schema)
schema_nome = "Jessiely_Moura"
# Tabelas a replicar (conforme solicitado)
tabelas = [
    "agendamentos",
    "appointment",
    "appointments",
    "business_hours",
    "client",
    "customers",
    "services",
]

criar_novo_estabelecimento(schema_nome, tabelas)
print(f"Schema '{schema_nome}' criado com {len(tabelas)} tabelas.")
