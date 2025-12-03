from app import app, db
from models import Usuario
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = Usuario.query.filter_by(nome='admin').first()
    if admin:
        admin.senha = generate_password_hash('admin123')  # nova senha segura
        db.session.commit()
        print("Senha do admin redefinida com sucesso.")
    else:
        print("Usuário admin não encontrado.")