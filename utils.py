from itsdangerous import URLSafeTimedSerializer
from flask import current_app
import mercadopago
import os

def gerar_token(email):
    """Gera um token seguro com base no e-mail do usuário."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='recuperar-senha')

def validar_token(token, tempo_expiracao=3600):
    """Valida o token e retorna o e-mail se for válido e não expirado."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        return serializer.loads(token, salt='recuperar-senha', max_age=tempo_expiracao)
    except Exception:
        return None

def gerar_qr_code_pix(payment_id, valor, sdk):
    """Gera QR Code e chave Pix usando a API do Mercado Pago."""
    payment_data = {
        "transaction_amount": float(valor),
        "description": "Pagamento via PIX",
        "payment_method_id": "pix",
        "external_reference": payment_id,
        "payer": {
            "email": "rafaelbraragao@gmail.com",
            "first_name": "Rafael",
            "last_name": "Teste",
            "identification": {
                "type": "CPF",
                "number": "19119119100"
            }
        }
    }

    response = sdk.payment().create(payment_data)
    payment = response.get("response", {})
    status = response.get("status")

    if status != 201 or "point_of_interaction" not in payment:
        raise Exception("Erro ao gerar QR Code Pix")

    dados = payment["point_of_interaction"]["transaction_data"]
    chave_pix = dados["qr_code"]
    qr_code_base64 = dados["qr_code_base64"]

    return chave_pix, qr_code_base64