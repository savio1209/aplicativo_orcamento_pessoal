from tkinter import *
from tkinter import ttk, messagebox
from tkinter.ttk import Progressbar

from PIL import Image, ImageTk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from tkcalendar import DateEntry

from view import (
    pie_valores, bar_valores, percentagem_valor,
    inserir_categoria, ver_categoria,
    inserir_gastos, inserir_receitas,
    tabela, deletar_gastos, deletar_receitas, deletar_categoria
)

# Cores -------------------------------------------------
co0 = "#2e2d2b"
co1 = "#feffff"
co2 = "#4fa882"
co3 = "#38576b"
co4 = "#403d3d"
co5 = "#e06636"
co6 = "#038cfc"
co7 = "#3fbfb9"
co8 = "#263238"
co9 = "#e9edf5"

colors = ['#5588bb', '#66bbbb', '#99bb55', '#ee9944', '#444466', '#bb5555']

# Criando janela ----------------------------------------
janela = Tk()
janela.title("Controle de Gastos Pessoal")
janela.geometry('900x700')
janela.configure(background=co9)
janela.resizable(width=FALSE, height=FALSE)

style = ttk.Style(janela)
style.theme_use("clam")

# Frames principais -------------------------------------
frameCima = Frame(janela, width=1043, height=50, bg=co1, relief="flat")
frameCima.grid(row=0, column=0)

frameMeio = Frame(janela, width=1043, height=361, bg=co1, pady=20, relief="raised")
frameMeio.grid(row=1, column=0, pady=1, padx=0, sticky=NSEW)

frameBaixo = Frame(janela, width=1043, height=300, bg=co1, relief="flat")
frameBaixo.grid(row=2, column=0, pady=0, padx=10, sticky=NSEW)

frame_gra_pie = Frame(frameMeio, width=500, height=250, bg=co2)
frame_gra_pie.place(x=415, y=5)

# Logo --------------------------------------------------
app_img = Image.open('icons8-money-box-50.png')
app_img = app_img.resize((45, 45))
app_img = ImageTk.PhotoImage(app_img)

app_logo = Label(frameCima, image=app_img, text=" Controle de Gastos Pessoal",
                 width=900, compound=LEFT, padx=5, relief=RAISED, anchor=NW,
                 font=('Verdana 20 bold'), bg=co1, fg=co4)
app_logo.place(x=0, y=0)

# Variável global da treeview
tree = None

# Funções de UI -----------------------------------------

def inserir_categoria_b():
    nome = e_categoria.get()
    if nome == '':
        messagebox.showerror('Erro', 'Preencha o campo de categoria.')
        return

    inserir_categoria([nome])
    messagebox.showinfo('Sucesso', 'Categoria inserida com sucesso.')
    e_categoria.delete(0, 'end')
    atualizar_combobox()


def deletar_categoria_b():
    nome = combo_categoria_despesas.get()
    if nome == '':
        messagebox.showerror('Erro', 'Selecione uma categoria no combobox para deletar.')
        return

    confirmar = messagebox.askyesno(
        'Confirmar', f'Deseja deletar a categoria "{nome}"?\nIsso não apaga as despesas associadas a ela.'
    )
    if not confirmar:
        return

    # Busca o id da categoria pelo nome
    categorias = ver_categoria()
    for cat in categorias:
        if cat[1] == nome:
            deletar_categoria([cat[0]])
            break

    messagebox.showinfo('Sucesso', f'Categoria "{nome}" deletada.')
    combo_categoria_despesas.set('')
    atualizar_combobox()


def atualizar_combobox():
    """Recarrega as categorias no combobox sem duplicatas."""
    categorias = ver_categoria()
    combo_categoria_despesas['values'] = [i[1] for i in categorias]


def inserir_receitas_b():
    nome = 'Receita'
    data = e_cal_receitas.get()
    quantia = e_valor_receitas.get()

    if data == '' or quantia == '':
        messagebox.showerror('Erro', 'Preencha todos os campos.')
        return

    inserir_receitas([nome, data, quantia])
    messagebox.showinfo('Sucesso', 'Receita inserida com sucesso.')

    e_cal_receitas.delete(0, 'end')
    e_valor_receitas.delete(0, 'end')

    atualizar_tudo()


def inserir_despesas_b():
    nome = combo_categoria_despesas.get()
    data = e_cal_despesas.get()
    quantia = e_valor_despesas.get()

    if nome == '' or data == '' or quantia == '':
        messagebox.showerror('Erro', 'Preencha todos os campos.')
        return

    inserir_gastos([nome, data, quantia])
    messagebox.showinfo('Sucesso', 'Despesa inserida com sucesso.')

    combo_categoria_despesas.set('')
    e_cal_despesas.delete(0, 'end')
    e_valor_despesas.delete(0, 'end')

    atualizar_tudo()


def deletar_dados():
    try:
        treev_dados = tree.focus()
        treev_lista = tree.item(treev_dados)['values']
        valor_id = treev_lista[0]
        nome = treev_lista[1]

        if nome == 'Receita':
            deletar_receitas([valor_id])
        else:
            deletar_gastos([valor_id])

        messagebox.showinfo('Sucesso', 'Registro deletado com sucesso.')
        atualizar_tudo()

    except IndexError:
        messagebox.showerror('Erro', 'Selecione um registro da tabela.')


def atualizar_tudo():
    """Atualiza todos os elementos visuais de uma vez."""
    mostrar_renda()
    percentagem()
    grafico_bar()
    resumo()
    grafico_pie()


def percentagem():
    style = ttk.Style()
    style.theme_use('default')
    style.configure("black.Horizontal.TProgressbar", background='#daed6b')
    style.configure("TProgressbar", thickness=25)

    valor = percentagem_valor()[0]

    Label(frameMeio, text='Porcentagem da Receita Restante', height=1,
          anchor=NW, font=('Verdana 12'), bg=co1, fg=co4).place(x=7, y=5)

    bar = Progressbar(frameMeio, length=180, style='black.Horizontal.TProgressbar')
    bar.place(x=10, y=35)
    bar['value'] = valor

    # StringVar evita o problema de %% duplicado no Label
    pct_var = StringVar(value='{:.2f}%'.format(valor))
    Label(frameMeio, textvariable=pct_var,
          anchor=NW, font=('Verdana 12'), bg=co1, fg=co4).place(x=200, y=35)

def grafico_bar():
    lista_categorias = ['Renda', 'Despesas', 'Saldo']
    receitas, gastos, saldo = bar_valores()
    lista_valores = [receitas, gastos, saldo]

    figura = plt.Figure(figsize=(4, 3.45), dpi=60)
    ax = figura.add_subplot(111)

    ax.bar(lista_categorias, lista_valores, color=colors, width=0.9)

    for idx, patch in enumerate(ax.patches):
        ax.text(patch.get_x() - .001, patch.get_height() + .5,
                "{:,.0f}".format(lista_valores[idx]),
                fontsize=17, fontstyle='italic',
                verticalalignment='bottom', color='dimgrey')

    ax.set_xticklabels(lista_categorias, fontsize=16)
    ax.patch.set_facecolor('#ffffff')
    for spine in ['bottom', 'left']:
        ax.spines[spine].set_color('#CCCCCC')
        ax.spines[spine].set_linewidth(1)
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    ax.tick_params(bottom=False, left=False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(False)
    ax.xaxis.grid(False)

    canva = FigureCanvasTkAgg(figura, frameMeio)
    canva.get_tk_widget().place(x=10, y=70)


def resumo():
    receitas, gastos, saldo = bar_valores()

    # (titulo, valor, y_titulo, y_linha, y_valor)
    dados = [
        ("Renda Mensal",     receitas, 35,  60,  75),
        ("Despesas Mensais", gastos,   120, 145, 160),
        ("Saldo Total",      saldo,    205, 230, 245),
    ]

    for titulo, valor, y_titulo, y_linha, y_valor in dados:
        Label(frameMeio, text=titulo.upper(), anchor=NW,
              font=('Verdana 12'), bg=co1, fg='#83a9e6').place(x=309, y=y_titulo)
        Label(frameMeio, text="", width=215, height=1,
              font=('arial 1'), bg='#545454').place(x=309, y=y_linha)
        Label(frameMeio, text="R$ {:,.2f}".format(valor), anchor=NW,
              font=('arial 17'), bg=co1, fg='#545454').place(x=309, y=y_valor)


def grafico_pie():
    figura = plt.Figure(figsize=(5, 3), dpi=90)
    ax = figura.add_subplot(111)

    lista_categorias, lista_valores = pie_valores()  # corrigido: [0] e [1]

    if not lista_valores:
        return

    explode = [0.05] * len(lista_categorias)

    ax.pie(lista_valores, explode=explode, wedgeprops=dict(width=0.2),
           autopct='%1.1f%%', colors=colors, shadow=True, startangle=90)
    ax.legend(lista_categorias, loc="center right", bbox_to_anchor=(1.55, 0.50))

    canva_categoria = FigureCanvasTkAgg(figura, frame_gra_pie)
    canva_categoria.get_tk_widget().grid(row=0, column=0)


def mostrar_renda():
    global tree

    tabela_head = ['#Id', 'Categoria', 'Data', 'Quantia']
    lista_itens = tabela()

    tree = ttk.Treeview(frame_renda, selectmode="extended",
                        columns=tabela_head, show="headings")
    vsb = ttk.Scrollbar(frame_renda, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame_renda, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tree.grid(column=0, row=0, sticky='nsew')
    vsb.grid(column=1, row=0, sticky='ns')
    hsb.grid(column=0, row=1, sticky='ew')

    larguras = [30, 100, 100, 100]
    for idx, col in enumerate(tabela_head):
        tree.heading(col, text=col.title(), anchor=CENTER)
        tree.column(col, width=larguras[idx], anchor="center")

    for item in lista_itens:
        tree.insert('', 'end', values=item)


# Render inicial ----------------------------------------
percentagem()
grafico_bar()
resumo()
grafico_pie()

# Frames internos do frameBaixo -------------------------
frame_renda = Frame(frameBaixo, width=300, height=250, bg=co1)
frame_renda.grid(row=0, column=0)

frame_operacoes = Frame(frameBaixo, width=220, height=250, bg=co1)
frame_operacoes.grid(row=0, column=1, padx=5)

frame_configuracao = Frame(frameBaixo, width=220, height=250, bg=co1)
frame_configuracao.grid(row=0, column=2, padx=5)

Label(frameMeio, text=" Tabela de Receitas e Despesas", anchor=NW,
      font=('Verdana 12'), bg=co1, fg=co4).place(x=5, y=309)

mostrar_renda()

# Seção: Despesas ---------------------------------------
Label(frame_operacoes, text='Insira novas despesas:', height=1, anchor=NW,
      font=('Verdana 10 bold'), bg=co1, fg=co4).place(x=10, y=10)

Label(frame_operacoes, text='Categoria', height=1, anchor=NW,
      font=('Ivy 10'), bg=co1, fg=co4).place(x=10, y=40)

categoria_funcao = ver_categoria()
combo_categoria_despesas = ttk.Combobox(frame_operacoes, width=10, font=('Ivy 10'), state='readonly')
combo_categoria_despesas['values'] = [i[1] for i in categoria_funcao]
combo_categoria_despesas.place(x=110, y=41)

Label(frame_operacoes, text='Data', height=1, anchor=NW,
      font=('Ivy 10'), bg=co1, fg=co4).place(x=10, y=70)
e_cal_despesas = DateEntry(frame_operacoes, width=12, background='darkblue',
                           foreground='white', borderwidth=2)
e_cal_despesas.place(x=110, y=71)

Label(frame_operacoes, text='Quantia Total', height=1, anchor=NW,
      font=('Ivy 10'), bg=co1, fg=co4).place(x=10, y=100)
e_valor_despesas = Entry(frame_operacoes, width=14, justify='left', relief='solid')
e_valor_despesas.place(x=110, y=101)

img_add_despesas = Image.open('icons8-plus-50.png')
img_add_despesas = img_add_despesas.resize((17, 17))
img_add_despesas = ImageTk.PhotoImage(img_add_despesas)

Button(frame_operacoes, command=inserir_despesas_b, image=img_add_despesas,
       text=" Adicionar".upper(), width=80, compound=LEFT, anchor=NW,
       font=('Ivy 7 bold'), bg=co1, fg=co0, overrelief=RIDGE).place(x=110, y=131)

Label(frame_operacoes, text='Excluir ação', height=1, anchor=NW,
      font=('Ivy 10 bold'), bg=co1, fg=co4).place(x=10, y=190)

img_deletar = Image.open('icons8-delete-50.png')
img_deletar = img_deletar.resize((17, 17))
img_deletar = ImageTk.PhotoImage(img_deletar)

Button(frame_operacoes, command=deletar_dados, image=img_deletar,
       text=" Deletar".upper(), width=80, compound=LEFT, anchor=NW,
       font=('Ivy 7 bold'), bg=co1, fg=co0, overrelief=RIDGE).place(x=110, y=190)

# Seção: Receitas ---------------------------------------
Label(frame_configuracao, text='Insira novas receitas:', height=1, anchor=NW,
      font=('Verdana 10 bold'), bg=co1, fg=co4).place(x=10, y=10)

Label(frame_configuracao, text='Data', height=1, anchor=NW,
      font=('Ivy 10'), bg=co1, fg=co4).place(x=10, y=40)
e_cal_receitas = DateEntry(frame_configuracao, width=12, background='darkblue',
                           foreground='white', borderwidth=2)
e_cal_receitas.place(x=110, y=41)

Label(frame_configuracao, text='Quantia Total', height=1, anchor=NW,
      font=('Ivy 10'), bg=co1, fg=co4).place(x=10, y=70)
e_valor_receitas = Entry(frame_configuracao, width=14, justify='left', relief='solid')
e_valor_receitas.place(x=110, y=71)

img_add_receitas = Image.open('icons8-plus-50.png')
img_add_receitas = img_add_receitas.resize((17, 17))
img_add_receitas = ImageTk.PhotoImage(img_add_receitas)

Button(frame_configuracao, command=inserir_receitas_b, image=img_add_receitas,
       text=" Adicionar".upper(), width=80, compound=LEFT, anchor=NW,
       font=('Ivy 7 bold'), bg=co1, fg=co0, overrelief=RIDGE).place(x=110, y=111)

# Seção: Nova Categoria ---------------------------------
Label(frame_configuracao, text='Categoria:', height=1, anchor=NW,
      font=('Ivy 10 bold'), bg=co1, fg=co4).place(x=10, y=160)

e_categoria = Entry(frame_configuracao, width=14, justify='left', relief='solid')
e_categoria.place(x=110, y=160)

img_add_categoria = Image.open('icons8-plus-50.png')
img_add_categoria = img_add_categoria.resize((17, 17))
img_add_categoria = ImageTk.PhotoImage(img_add_categoria)

Button(frame_configuracao, command=inserir_categoria_b, image=img_add_categoria,
       text=" Adicionar".upper(), width=80, compound=LEFT, anchor=NW,
       font=('Ivy 7 bold'), bg=co1, fg=co0, overrelief=RIDGE).place(x=110, y=190)

# Botão deletar categoria
img_del_categoria = Image.open('icons8-delete-50.png')
img_del_categoria = img_del_categoria.resize((17, 17))
img_del_categoria = ImageTk.PhotoImage(img_del_categoria)

Label(frame_configuracao, text='Deletar\ncategoria:', height=2, anchor=NW,
      font=('Ivy 10 bold'), bg=co1, fg=co4).place(x=10, y=215)

Button(frame_configuracao, command=deletar_categoria_b, image=img_del_categoria,
       text=" Deletar".upper(), width=80, compound=LEFT, anchor=NW,
       font=('Ivy 7 bold'), bg=co1, fg=co0, overrelief=RIDGE).place(x=110, y=222)

janela.mainloop()
