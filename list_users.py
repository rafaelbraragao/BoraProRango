# list_users.py

# Importa o objeto 'app' e o modelo 'Usuario'
from app import app
from models import Usuario

def list_all_users():
    """Busca e lista todos os usuários cadastrados no banco de dados."""
    
    # O contexto da aplicação é obrigatório para acessar o banco de dados
    with app.app_context():
        try:
            # 1. Faz a consulta de todos os usuários
            usuarios = Usuario.query.all()
            
            print("-" * 50)
            if not usuarios:
                print("❌ Não há usuários cadastrados no banco de dados.")
                print("-" * 50)
                return

            print("Lista de Usuários:")
            print(f"{'ID':<4} | {'Nome':<25} | {'Email':<25} | {'Admin':<5}")
            print("-" * 50)
            
            # 2. Itera sobre os usuários e imprime os dados
            for user in usuarios:
                admin_status = "✅" if user.is_admin else "❌"
                print(f"{user.id:<4} | {user.nome:<25} | {user.email:<25} | {admin_status:<5}")
            
            print("-" * 50)
            print(f"Total de Usuários: {len(usuarios)}")
            
        except Exception as e:
            print(f"❌ Ocorreu um erro ao acessar o banco de dados: {e}")
            print("Verifique a configuração do banco e se o arquivo 'instance/ofertas.db' está acessível.")

if __name__ == '__main__':
    list_all_users()