from app import app, db
from models import Oferta, Usuario
from sqlalchemy import select

with app.app_context():
    usuarios_validos = select(Usuario.id)

    ofertas_orfas = db.session.query(Oferta).filter(
        ~Oferta.usuario_id.in_(usuarios_validos)
    )

    total_apagadas = ofertas_orfas.delete(synchronize_session=False)
    db.session.commit()

    print(f"{total_apagadas} ofertas órfãs apagadas com sucesso.")