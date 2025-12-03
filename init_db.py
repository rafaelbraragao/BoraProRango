from app import app
from models import db, Usuario, Oferta
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    print("Banco de dados criado com sucesso!")

    admin_existente = Usuario.query.filter_by(email='admin@exemplo.com').first()
    print("Verificando se admin já existe...")
    if not admin_existente:
        admin = Usuario(
         nome='Admin',
         email='admin@exemplo.com',
         senha='123456',
         is_admin=True  # <-- ESSA LINHA É ESSENCIAL
)
        db.session.add(admin)
        db.session.commit()
        print("Usuário admin criado.")

        oferta1 = Oferta(
            titulo='Pizza Gigante',
            preco='29.90',
            endereco='Rua das Ofertas, 123',
            validade='2025-12-31',
            imagem='pizza.jpg',
            cidade='Macapá',
            usuario_id=admin.id
        )

        oferta2 = Oferta(
            titulo='Sorvete 2L',
            preco='14.90',
            endereco='Av. Gelada, 456',
            validade='2025-12-25',
            imagem='sorvete.jpg',
            cidade='Santana',
            usuario_id=admin.id
        )

        db.session.add_all([oferta1, oferta2])
        db.session.commit()
        print("Ofertas de exemplo criadas.")
    else:
        print("Usuário admin já existe. Nenhuma alteração feita.")