import os
import json
import mercadopago
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Recupera o token de sandbox
access_token = os.getenv("MP_ACCESS_TOKEN_SANDBOX")

if not access_token or not access_token.startswith("TEST-"):
    raise RuntimeError("Access token inválido ou ausente. Verifique seu .env.")

# Inicializa o SDK
sdk = mercadopago.SDK(access_token)

# Dados do pagamento de teste
payment_data = {
    "transaction_amount": 10.00,
    "description": "Teste de pagamento PIX",
    "payment_method_id": "pix",
    "payer": {
        "email": "teste@email.com",
        "first_name": "Rafael"
    }
}

# Cria o pagamento
payment_response = sdk.payment().create(payment_data)

# Exibe a resposta formatada
print("\n=== RESPOSTA DA API ===")
print(json.dumps(payment_response, indent=2, ensure_ascii=False))

# Verifica se o QR Code foi gerado
payment = payment_response.get("response", {})
poi = payment.get("point_of_interaction", {})
tx_data = poi.get("transaction_data", {})

if tx_data.get("qr_code_base64"):
    print("\n✅ QR Code gerado com sucesso!")
    print("ID do pagamento:", payment.get("id"))
    print("Chave PIX:", tx_data.get("qr_code"))
else:
    print("\n❌ Não foi possível gerar o QR Code.")