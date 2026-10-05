import sqlite3 as lite

# Criando conexão
con = lite.connect('dados.db')

# Criando tabelas (apenas se ainda não existirem)
with con:
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Categoria(
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Receitas(
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria    TEXT NOT NULL,
            adicionado_em DATE NOT NULL,
            valor        REAL NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Gastos(
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria    TEXT NOT NULL,
            retirado_em  DATE NOT NULL,
            valor        REAL NOT NULL
        )
    """)

print("Banco de dados criado com sucesso.")
