from app import app
from models import db, Usuario, Oferta
from werkzeug.security import generate_password_hash

with app.app_context():
    # Cria as tabelas (caso ainda não existam)
    db.create_all()

    # Cria um usuário de teste
    usuario = Usuario(
        nome='Rafael Teste',
        email='rafael@teste.com',
        senha=generate_password_hash('123456'),
        avatar='avatar_padrao.png'
    )
    db.session.add(usuario)
    db.session.commit()

    # Cria algumas ofertas de exemplo
    ofertas = [
        Oferta(
            titulo='Desconto em Pizza',
            preco='29.90',
            endereco='Rua das Flores, 123',
            validade='2025-12-31',
            imagem='pizza.jpg',
            cidade='Macapá',
            usuario_id=usuario.id
        ),
        Oferta(
            titulo='Promoção de Sorvete',
            preco='9.90',
            endereco='Av. Central, 456',
            validade='2025-12-15',
            imagem='sorvete.jpg',
            cidade='Macapá',
            usuario_id=usuario.id
        )
    ]

    db.session.add_all(ofertas)
    db.session.commit()

    print('Banco populado com sucesso!')



    # Como rodar
 # No terminal, com o ambiente ativado:

 # python popular_banco.py
