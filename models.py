from extensoes import db
from datetime import datetime
from pytz import timezone

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)

    # Relacionamentos
    ofertas = db.relationship('Oferta', backref='usuario', lazy=True)
    pagamentos = db.relationship('Pagamento', backref='usuario', lazy=True)

    def __repr__(self):
        return f'<Usuario {self.nome}>'

class Oferta(db.Model):
    __tablename__ = 'ofertas'

    id = db.Column(db.Integer, primary_key=True)
    preco = db.Column(db.String(10), nullable=False)
    endereco = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    imagem = db.Column(db.String(255))
    cidade = db.Column(db.String(100))
    rango = db.Column(db.String(100))
    ativa = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    status_pagamento = db.Column(db.String(20), default="pendente")
    payment_id = db.Column(db.String(100), nullable=True)

    # Relacionamento com usuário
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    # Relacionamento com pagamentos
    pagamentos = db.relationship('Pagamento', backref='oferta', lazy=True)

    def __repr__(self):
        return f'<Oferta {self.rango}>'

class Pagamento(db.Model):
    __tablename__ = 'pagamentos'

    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.String(100), unique=True, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    ticket_url = db.Column(db.String(255))
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone("America/Sao_Paulo")))
    atualizado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone("America/Sao_Paulo")), onupdate=lambda: datetime.now(timezone("America/Sao_Paulo")))

    # Relacionamentos
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    oferta_id = db.Column(db.Integer, db.ForeignKey('ofertas.id'), nullable=False)

    def __repr__(self):
        return f'<Pagamento {self.payment_id} - {self.status}>'