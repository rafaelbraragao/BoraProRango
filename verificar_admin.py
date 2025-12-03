from app import app
from extensoes import db
from models import Usuario

def listar_admins(nome_filtro=None, email_filtro=None):
    with app.app_context():
        query = Usuario.query.filter_by(is_admin=True)

        if nome_filtro:
            query = query.filter(Usuario.nome.ilike(f"%{nome_filtro}%"))
        if email_filtro:
            query = query.filter(Usuario.email.ilike(f"%{email_filtro}%"))

        admins = query.all()

        if admins:
            print(f"\n✅ {len(admins)} administrador(es) encontrado(s):\n")
            for admin in admins:
                print(f" - {admin.nome} ({admin.email})")
        else:
            print("\n❌ Nenhum administrador encontrado com os filtros aplicados.")

if __name__ == "__main__":
    print("🔍 Filtro de administradores (pressione Enter para ignorar):")
    nome = input("Filtrar por nome: ").strip()
    email = input("Filtrar por e-mail: ").strip()

    listar_admins(nome_filtro=nome or None, email_filtro=email or None)