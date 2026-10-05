import sqlite3 as lite

# Criando conexão
con = lite.connect('dados.db')

# Funções de inserção --------------------------------

def inserir_categoria(i):
    with con:
        cur = con.cursor()
        query = "INSERT INTO Categoria (nome) VALUES (?)"
        cur.execute(query, i)


def inserir_receitas(i):
    with con:
        cur = con.cursor()
        query = "INSERT INTO Receitas (categoria, adicionado_em, valor) VALUES (?,?,?)"
        cur.execute(query, i)


def inserir_gastos(i):
    with con:
        cur = con.cursor()
        query = "INSERT INTO Gastos (categoria, retirado_em, valor) VALUES (?,?,?)"
        cur.execute(query, i)


# Funções para deletar --------------------------------

def deletar_receitas(i):
    with con:
        cur = con.cursor()
        query = "DELETE FROM Receitas WHERE id=?"
        cur.execute(query, i)


def deletar_gastos(i):
    with con:
        cur = con.cursor()
        query = "DELETE FROM Gastos WHERE id=?"
        cur.execute(query, i)


def deletar_categoria(i):
    with con:
        cur = con.cursor()
        query = "DELETE FROM Categoria WHERE id=?"
        cur.execute(query, i)


# Funções para ver dados --------------------------------

def ver_categoria():
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM Categoria")
        return cur.fetchall()


def ver_receitas():
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM Receitas")
        return cur.fetchall()


def ver_gastos():
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM Gastos")
        return cur.fetchall()


def tabela():
    return ver_gastos() + ver_receitas()


# Função para dados do gráfico de barra
def bar_valores():
    with con:
        cur = con.cursor()

        cur.execute("SELECT SUM(valor) FROM Receitas")
        receitas = cur.fetchone()[0] or 0

        cur.execute("SELECT SUM(valor) FROM Gastos")
        gastos = cur.fetchone()[0] or 0

    saldo = receitas - gastos
    return receitas, gastos, saldo


# Função para dados do gráfico de pizza
def pie_valores():
    with con:
        cur = con.cursor()
        cur.execute("SELECT categoria, SUM(valor) FROM Gastos GROUP BY categoria")
        resultado = cur.fetchall()

    categorias = [r[0] for r in resultado]
    valores = [r[1] for r in resultado]

    return categorias, valores


# Função para percentagem do saldo em relação à receita
def percentagem_valor():
    receitas, gastos, _ = bar_valores()

    if receitas == 0:
        return [0.0]

    total = ((receitas - gastos) / receitas) * 100
    return [total]
