import requests

url = "http://localhost:8000/api/mobile/agendamentos/manual"
headers = {
    "Content-Type": "application/json",
    # Just need an auth token or maybe auth is disabled for this test?
    # Wait, the endpoint uses Depends(get_lojista_atual) so I need a token.
}
data = {
    "clienteNome": "Teste",
    "clienteTelefone": "11999999999",
    "servicoId": 1,
    "data": "2026-05-30",
    "hora": "14:00"
}
try:
    response = requests.post(url, headers=headers, json=data)
    print(response.status_code)
    print(response.text)
except Exception as e:
    print(e)
