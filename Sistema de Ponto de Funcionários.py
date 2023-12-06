import sqlite3
from customtkinter import *
from datetime import datetime
from tkinter import StringVar, messagebox






set_appearance_mode('dark')
set_default_color_theme('dark-blue')

# Conexão ao banco de dados SQLite
conn = sqlite3.connect('registros.db')
cursor = conn.cursor()

# Criar a tabela para os registros (se não existir)
cursor.execute('''CREATE TABLE IF NOT EXISTS registros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    tipo TEXT,
                    data_hora DATETIME
                )''')

# Variável para rastrear se já carregamos os registros
registros_carregados = False

# Função para carregar registros da base de dados
def carregar_registros():
    registros_textbox.delete(1.0, 'end')  # Remove todo o texto da caixa
    cursor.execute("SELECT nome, tipo, data_hora FROM registros")
    registros_db = cursor.fetchall()
    for registro in registros_db:
        nome, tipo, data_hora = registro
        registros_textbox.insert('end', f"{nome} - {tipo} - {data_hora}\n")

# Função para gerar um relatório com os registros do dia
def gerar_relatorio():
    hoje = datetime.now().strftime('%d/%m/%Y')
    cursor.execute("SELECT nome, tipo, data_hora FROM registros WHERE data_hora LIKE ?", (f'%{hoje}%',))
    registros_do_dia = cursor.fetchall()

    if registros_do_dia:
        relatorio_text = "Relatório dos Registros do Dia:\n"
        for registro in registros_do_dia:
            nome, tipo, data_hora = registro
            relatorio_text += f"{nome} - {tipo} - {data_hora}\n"
        messagebox.showinfo("Relatório", relatorio_text)
    else:
        messagebox.showinfo("Relatório", "Nenhum registro encontrado para o dia de hoje.")

# Função para verificar se o funcionário já registrou entrada hoje
def funcionario_registrou_entrada(nome):
    hoje = datetime.now().strftime('%d/%m/%Y')
    cursor.execute("SELECT COUNT(*) FROM registros WHERE nome = ? AND tipo = 'Entrada' AND data_hora LIKE ?", (nome, f'%{hoje}%'))
    return cursor.fetchone()[0] > 0

# Função para verificar se o funcionário já registrou saída hoje
def funcionario_registrou_saida(nome):
    hoje = datetime.now().strftime('%d/%m/%Y')
    cursor.execute("SELECT COUNT(*) FROM registros WHERE nome = ? AND tipo = 'Saída' AND data_hora LIKE ?", (nome, f'%{hoje}%'))
    return cursor.fetchone()[0] > 0

# Função para registrar entrada/saída no banco de dados
def registrar_evento(tipo):
    nome = nome_entry.get()
    if nome:
        agora = datetime.now()
        agora_formatado = agora.strftime('%d/%m/%Y %H:%M:%S')
        
        if tipo == 'Entrada':
            if funcionario_registrou_entrada(nome):
                mensagem.set("Ops! Você já registrou sua entrada hoje. Verifique no setor responsável.")
                return
        elif tipo == 'Saída':
            if funcionario_registrou_saida(nome):
                mensagem.set("Erro! Saída já registrada hoje.")
                return
        
        cursor.execute("INSERT INTO registros (nome, tipo, data_hora) VALUES (?, ?, ?)", (nome, tipo, agora_formatado))
        conn.commit()
        
        # Carrega e exibe apenas o registro atual
        cursor.execute("SELECT nome, tipo, data_hora FROM registros WHERE nome = ? AND tipo = ? AND data_hora = ?", (nome, tipo, agora_formatado))
        registro_atual = cursor.fetchone()
        nome, tipo, data_hora = registro_atual
        registros_textbox.insert('end', f"{nome} - {tipo} - {data_hora}\n")
    
        mensagem.set("")  # Limpa a mensagem de erro
    else:
        mensagem.set("Erro! Nome do funcionário não especificado.")

# Criando a janela principal
janela = CTk()
janela.geometry('600x550')
janela.title('Sistema de Ponto de Funcionários')

# Título
titulo = CTkLabel(janela, text='Sistema de Ponto')
titulo.pack(pady=10)

# Entrada do nome
nome_label = CTkLabel(janela, text="Nome do funcionário:")
nome_label.pack()

nome_entry = CTkEntry(janela, placeholder_text='Digite o nome completo', width=220)
nome_entry.pack()

# Botões para registrar entrada e saída
registrar_entrada_button = CTkButton(janela, text="Registrar Entrada", command=lambda: registrar_evento('Entrada'))
registrar_entrada_button.pack(pady=5)

registrar_saida_button = CTkButton(janela, text="Registrar Saída", command=lambda: registrar_evento('Saída'))
registrar_saida_button.pack(pady=5)

# Caixa de texto para exibir os registros
registros_textbox = CTkTextbox(janela, width=450, height=250)
registros_textbox.pack(pady=10)

# Mensagem de erro
mensagem = StringVar()
erro_label = CTkLabel(janela, textvariable=mensagem)
erro_label.pack()

# Botão para gerar relatório
gerar_relatorio_button = CTkButton(janela, text="Gerar Relatório", command=gerar_relatorio)
gerar_relatorio_button.pack(pady=5)

# Marque que os registros já foram carregados na inicialização
registros_carregados = True

# Inicie o loop da janela
janela.mainloop()