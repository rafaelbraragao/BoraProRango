# count_offers.py

# Importa o objeto 'app' e os modelos do seu arquivo principal da aplicação
from app import app
from models import Oferta

# O contexto da aplicação é necessário para que o Flask
# saiba qual banco de dados usar e inicialize o SQLAlchemy.
with app.app_context():
    try:
        # 1. Faz a consulta de contagem
        total_ofertas = Oferta.query.count()
        
        # 2. Imprime o resultado
        print("-" * 30)
        print(f"✅ Total de Ofertas no Banco de Dados: {total_ofertas}")
        print("-" * 30)

    except Exception as e:
        print(f"❌ Ocorreu um erro ao acessar o banco de dados: {e}")
        print("Certifique-se de que o arquivo 'instance/ofertas.db' existe e que a aplicação está configurada corretamente.")