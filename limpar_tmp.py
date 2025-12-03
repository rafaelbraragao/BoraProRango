import sqlite3

# Caminho correto com base no app.py
caminho_banco = 'ofertas.db'

conn = sqlite3.connect(caminho_banco)
cursor = conn.cursor()

try:
    cursor.execute("DROP TABLE IF EXISTS _alembic_tmp_ofertas")
    conn.commit()
    print("Tabela temporária _alembic_tmp_ofertas removida com sucesso.")
except Exception as e:
    print(f"Erro ao remover tabela temporária: {e}")
finally:
    conn.close()