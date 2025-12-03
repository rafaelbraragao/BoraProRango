import sqlite3

# Conecta ao banco de dados
conn = sqlite3.connect('ofertas.db')
cursor = conn.cursor()

# Executa o comando para listar as colunas da tabela 'usuarios'
cursor.execute("PRAGMA table_info(usuarios)")
colunas = cursor.fetchall()

# Exibe os nomes das colunas
print("Colunas da tabela 'usuarios':")
for coluna in colunas:
    print(f"- {coluna[1]}")

# Fecha a conexão
conn.close()