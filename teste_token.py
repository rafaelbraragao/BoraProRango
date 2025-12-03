from flask import Flask
from utils import gerar_token, validar_token

def criar_app_teste():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'chave-de-teste-super-secreta'
    return app

def testar_token():
    app = criar_app_teste()

    with app.app_context():
        email_original = 'rafael@exemplo.com'

        # Gera o token
        token = gerar_token(email_original)
        print(f'\n🔐 Token gerado: {token}')

        # Valida o token
        email_validado = validar_token(token)
        print(f'✅ Token validado: {email_validado}')

        # Verifica se o e-mail recuperado é o mesmo
        assert email_validado == email_original, "❌ O e-mail validado não corresponde ao original."

        # Teste de expiração (opcional)
        import time
        token_curto = gerar_token(email_original)
        time.sleep(2)
        expirado = validar_token(token_curto, tempo_expiracao=1)
        assert expirado is None, "❌ O token deveria ter expirado, mas ainda é válido."
        print("⏱️ Token expirado corretamente após o tempo limite.")

if __name__ == '__main__':
    testar_token()