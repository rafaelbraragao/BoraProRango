from itsdangerous import URLSafeTimedSerializer
from flask import current_app

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