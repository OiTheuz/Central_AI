import os
import requests
import json
from datetime import datetime, timedelta

ASAAS_API_KEY = os.getenv("ASAAS_API_KEY", "")
# TODO: Alternar entre sandbox e produção dependendo da escolha do usuário
ASAAS_BASE_URL = "https://api.asaas.com/v3" # Produção

def get_headers():
    return {
        "accept": "application/json",
        "content-type": "application/json",
        "access_token": ASAAS_API_KEY
    }

def criar_cliente(nome: str, email: str, telefone: str = None, cpfCnpj: str = None) -> str:
    """
    Cria um cliente no Asaas e retorna o customer_id.
    """
    url = f"{ASAAS_BASE_URL}/customers"
    
    payload = {
        "name": nome,
        "email": email,
    }
    if telefone:
        payload["mobilePhone"] = telefone
    if cpfCnpj:
        payload["cpfCnpj"] = cpfCnpj

    response = requests.post(url, json=payload, headers=get_headers())
    
    if response.status_code in [200, 201]:
        data = response.json()
        return data.get("id")
    else:
        raise Exception(f"Erro ao criar cliente no Asaas: {response.text}")

def criar_assinatura_pix(customer_id: str, valor: float = 57.00):
    """
    Cria uma assinatura mensal no PIX e retorna os dados do QRCode da primeira fatura.
    """
    url_sub = f"{ASAAS_BASE_URL}/subscriptions"
    
    hoje = datetime.now()
    vencimento_hoje = hoje.strftime("%Y-%m-%d") # Primeira cobrança para hoje

    payload_sub = {
        "customer": customer_id,
        "billingType": "PIX",
        "value": valor,
        "nextDueDate": vencimento_hoje,
        "cycle": "MONTHLY",
        "description": "Mensalidade SaaS OpenChatz"
    }

    res_sub = requests.post(url_sub, json=payload_sub, headers=get_headers())
    
    if res_sub.status_code not in [200, 201]:
        raise Exception(f"Erro ao criar assinatura: {res_sub.text}")
        
    sub_data = res_sub.json()
    subscription_id = sub_data.get("id")
    
    # 2. Como a cobrança é para hoje, o Asaas já gerou o primeiro 'Payment' (fatura).
    # Precisamos pegar o ID desse payment para gerar o QR Code.
    url_payments = f"{ASAAS_BASE_URL}/payments?subscription={subscription_id}"
    res_pay = requests.get(url_payments, headers=get_headers())
    pay_data = res_pay.json()
    
    if not pay_data.get("data"):
        raise Exception("Nenhum pagamento gerado para esta assinatura.")
        
    primeiro_pagamento_id = pay_data["data"][0]["id"]
    
    # 3. Gerar o payload do PIX (QR Code e Linha Digitável)
    url_pix = f"{ASAAS_BASE_URL}/payments/{primeiro_pagamento_id}/pixQrCode"
    res_pix = requests.get(url_pix, headers=get_headers())
    
    if res_pix.status_code not in [200, 201]:
        raise Exception(f"Erro ao gerar QR Code: {res_pix.text}")
        
    pix_data = res_pix.json()
    
    return {
        "subscription_id": subscription_id,
        "payment_id": primeiro_pagamento_id,
        "pix_payload": pix_data.get("payload"), # Copia e cola
        "pix_qrcode_image": pix_data.get("encodedImage") # Base64 da imagem
    }

def recuperar_qrcode_pix(subscription_id: str):
    """
    Recupera o QR Code da primeira fatura pendente de uma assinatura existente.
    """
    # 1. Pegar o pagamento (fatura)
    url_payments = f"{ASAAS_BASE_URL}/payments?subscription={subscription_id}"
    res_pay = requests.get(url_payments, headers=get_headers())
    pay_data = res_pay.json()
    
    if not pay_data.get("data"):
        raise Exception("Nenhum pagamento gerado para esta assinatura.")
        
    primeiro_pagamento_id = pay_data["data"][0]["id"]
    status_pagamento = pay_data["data"][0]["status"]
    
    if status_pagamento in ["RECEIVED", "CONFIRMED"]:
        return {"status": "pago"}
    
    # 2. Gerar o payload do PIX (QR Code e Linha Digitável)
    url_pix = f"{ASAAS_BASE_URL}/payments/{primeiro_pagamento_id}/pixQrCode"
    res_pix = requests.get(url_pix, headers=get_headers())
    
    if res_pix.status_code not in [200, 201]:
        raise Exception(f"Erro ao gerar QR Code: {res_pix.text}")
        
    pix_data = res_pix.json()
    
    return {
        "status": "pendente",
        "pix_payload": pix_data.get("payload"),
        "pix_qrcode_image": pix_data.get("encodedImage")
    }
