# Mapeamento de Serviços Padrão por Nicho

NICHE_TEMPLATES = {
    "petshop": [
        {"nome": "Banho", "preco": 50.00, "duracao_minutos": 60, "lembrete_ativo": True, "lembrete_valor": 15, "lembrete_tipo": "dias"},
        {"nome": "Tosa", "preco": 70.00, "duracao_minutos": 60, "lembrete_ativo": True, "lembrete_valor": 30, "lembrete_tipo": "dias"},
        {"nome": "Banho e Tosa", "preco": 100.00, "duracao_minutos": 120, "lembrete_ativo": True, "lembrete_valor": 30, "lembrete_tipo": "dias"},
        {"nome": "Hidratação", "preco": 40.00, "duracao_minutos": 30, "lembrete_ativo": False, "lembrete_valor": 30, "lembrete_tipo": "dias"},
        {"nome": "Corte de Unhas", "preco": 20.00, "duracao_minutos": 15, "lembrete_ativo": False, "lembrete_valor": 15, "lembrete_tipo": "dias"}
    ],
    "barbearia": [
        {"nome": "Corte de Cabelo", "preco": 40.00, "duracao_minutos": 30, "lembrete_ativo": True, "lembrete_valor": 20, "lembrete_tipo": "dias"},
        {"nome": "Barba", "preco": 30.00, "duracao_minutos": 30, "lembrete_ativo": True, "lembrete_valor": 15, "lembrete_tipo": "dias"},
        {"nome": "Corte e Barba", "preco": 60.00, "duracao_minutos": 60, "lembrete_ativo": True, "lembrete_valor": 20, "lembrete_tipo": "dias"},
        {"nome": "Sobrancelha", "preco": 15.00, "duracao_minutos": 15, "lembrete_ativo": False, "lembrete_valor": 20, "lembrete_tipo": "dias"}
    ],
    "estetica": [
        {"nome": "Limpeza de Pele", "preco": 120.00, "duracao_minutos": 60, "lembrete_ativo": True, "lembrete_valor": 30, "lembrete_tipo": "dias"},
        {"nome": "Massagem Relaxante", "preco": 90.00, "duracao_minutos": 60, "lembrete_ativo": True, "lembrete_valor": 15, "lembrete_tipo": "dias"},
        {"nome": "Drenagem Linfática", "preco": 100.00, "duracao_minutos": 60, "lembrete_ativo": True, "lembrete_valor": 7, "lembrete_tipo": "dias"},
        {"nome": "Design de Sobrancelha", "preco": 40.00, "duracao_minutos": 30, "lembrete_ativo": True, "lembrete_valor": 20, "lembrete_tipo": "dias"}
    ],
    "outros": [
        {"nome": "Atendimento", "preco": 50.00, "duracao_minutos": 60, "lembrete_ativo": False, "lembrete_valor": 30, "lembrete_tipo": "dias"},
        {"nome": "Consulta", "preco": 100.00, "duracao_minutos": 60, "lembrete_ativo": False, "lembrete_valor": 30, "lembrete_tipo": "dias"},
        {"nome": "Serviço Especial", "preco": 80.00, "duracao_minutos": 90, "lembrete_ativo": False, "lembrete_valor": 30, "lembrete_tipo": "dias"},
        {"nome": "Avaliação", "preco": 0.00, "duracao_minutos": 30, "lembrete_ativo": False, "lembrete_valor": 30, "lembrete_tipo": "dias"}
    ]
}

def get_services_for_niche(niche: str) -> list:
    """Retorna os serviços padrões de um nicho. Fallback para 'outros' se não encontrar."""
    if not niche:
        return NICHE_TEMPLATES["outros"]
        
    # Normaliza a string do nicho (ex: "Clínica de Estética" -> "estetica")
    niche_lower = niche.lower()
    
    if "pet" in niche_lower:
        return NICHE_TEMPLATES["petshop"]
    elif "barb" in niche_lower:
        return NICHE_TEMPLATES["barbearia"]
    elif "est" in niche_lower or "beleza" in niche_lower:
        return NICHE_TEMPLATES["estetica"]
    elif "odont" in niche_lower or "dent" in niche_lower:
        # Apenas reusando "estetica" provisório ou definindo novo se tivéssemos odontologia
        return [
            {"nome": "Avaliação Odontológica", "preco": 0.00, "duracao_minutos": 30, "lembrete_ativo": True, "lembrete_valor": 6, "lembrete_tipo": "meses"},
            {"nome": "Limpeza (Profilaxia)", "preco": 150.00, "duracao_minutos": 60, "lembrete_ativo": True, "lembrete_valor": 6, "lembrete_tipo": "meses"},
            {"nome": "Clareamento", "preco": 400.00, "duracao_minutos": 60, "lembrete_ativo": False, "lembrete_valor": 1, "lembrete_tipo": "anos"}
        ]
        
    return NICHE_TEMPLATES["outros"]
