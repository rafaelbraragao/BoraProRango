from models import db, Oferta
from app import app  # ou run, dependendo do seu arquivo principal

def verificar_sincronizacao(modelo):
    nome_tabela = modelo.__tablename__
    campos_modelo = set(modelo.__table__.columns.keys())

    inspetor = db.inspect(db.engine)
    campos_banco = set([col['name'] for col in inspetor.get_columns(nome_tabela)])

    faltando_no_banco = campos_modelo - campos_banco
    extras_no_banco = campos_banco - campos_modelo

    print(f"\n🔍 Verificando tabela '{nome_tabela}':")
    if not faltando_no_banco and not extras_no_banco:
        print("✅ Banco está sincronizado com o modelo.")
    else:
        if faltando_no_banco:
            print(f"⚠️ Campos no modelo mas ausentes no banco: {faltando_no_banco}")
        if extras_no_banco:
            print(f"⚠️ Campos no banco mas não no modelo: {extras_no_banco}")

with app.app_context():
    verificar_sincronizacao(Oferta)