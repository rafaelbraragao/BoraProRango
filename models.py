from extensoes import db  # ✅ importa do novo módulo
from datetime import datetime
from pytz import timezone

# ... suas classes Usuario, Oferta, Pagamento continuam iguais
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)
    

class Oferta(db.Model):
    __tablename__ = 'ofertas'

    id = db.Column(db.Integer, primary_key=True)
    preco = db.Column(db.String(10), nullable=False)
    endereco = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    imagem = db.Column(db.String(255))  # pode ser mantido se quiser usar futuramente
    cidade = db.Column(db.String(100))
    rango = db.Column(db.String(100))  # ✅ novo campo para armazenar o prato selecionado
    ativa = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    status_pagamento = db.Column(db.String(20), default="pendente")
    payment_id = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<Oferta {self.rango}>'
    
class Pagamento(db.Model):
    __tablename__ = 'pagamentos'

    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.String(100), unique=True, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone("America/Sao_Paulo")))
    atualizado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone("America/Sao_Paulo")), onupdate=lambda: datetime.now(timezone("America/Sao_Paulo")))

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    oferta_id = db.Column(db.Integer, db.ForeignKey('ofertas.id'), nullable=False)

    def __repr__(self):
        return f'<Pagamento {self.payment_id} - {self.status}>'