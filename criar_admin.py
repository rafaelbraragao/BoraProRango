from app import app, db
from models import Usuario
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = Usuario.query.filter_by(nome='admin').first()
    
    if admin:
        print(f"✅ Usuário admin já existe: {admin.email}")
    else:
        novo_admin = Usuario(
            nome='admin',
            email='admin@exemplo.com',
            senha=generate_password_hash('admin123'),  # você pode trocar a senha
            is_admin=True
        )
        db.session.add(novo_admin)
        db.session.commit()
        print("✅ Usuário admin criado com sucesso!")