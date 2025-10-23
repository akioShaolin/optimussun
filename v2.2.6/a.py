import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# Inicializa variáveis globais
fab_inversor = {}
fab_modulo = {}

# Função para conectar e carregar fabricantes
def carregar_fabricante():
    global fab_inversor, fab_modulo
    try:
        conexao = sqlite3.connect('optimus_sun.db')
        cursor = conexao.cursor()

        cursor.execute("SELECT ID, NAME FROM manufacturer WHERE CATEGORY IN (0, 2)")
        fab_inversor = {row[1]: row[0] for row in cursor.fetchall()}

        cursor.execute("SELECT ID, NAME FROM manufacturer WHERE CATEGORY IN (1, 2)")
        fab_modulo = {row[1]: row[0] for row in cursor.fetchall()}
    except sqlite3.Error as e:
        messagebox.showerror("Erro ao conectar", f"Erro: {e}")
    finally:
        conexao.close()

# Busca modelos baseado no fabricante
def carregar_modelo(fab_nome, equipamento):
    global inversores, modulos
    try:
        conexao = sqlite3.connect('optimus_sun.db')
        cursor = conexao.cursor()
        if equipamento == "inversor":
            fab_id = fab_inversor.get(fab_nome)
            cursor.execute("SELECT ID, MODEL FROM inverter WHERE MANUFACTURER_ID = ?", (fab_id,))
            inversores = {row[1]: row[0] for row in cursor.fetchall()}
            inversor_cb["values"] = list(inversores.keys())
            inversor_cb.set("")
        elif equipamento == "modulo":
            fab_id = fab_modulo.get(fab_nome)
            cursor.execute("SELECT ID, MODEL FROM module WHERE MANUFACTURER_ID = ?", (fab_id,))
            modulos = {row[1]: row[0] for row in cursor.fetchall()}
            modulo_cb["values"] = list(modulos.keys())
            modulo_cb.set("")
    except sqlite3.Error as e:
        messagebox.showerror("Erro ao buscar modelos", f"Erro: {e}")
    finally:
        conexao.close()

# Exibe dados do inversor
def mostrar_dados_inversor():
    modelo = inversor_cb.get()
    if not modelo:
        messagebox.showinfo("Aviso", "Selecione um inversor.")
        return
    try:
        conexao = sqlite3.connect('optimus_sun.db')
        cursor = conexao.cursor()
        inversor_id = inversores.get(modelo)
        cursor.execute("SELECT * FROM inverter WHERE ID = ?", (inversor_id,))
        dados = cursor.fetchone()
        if dados:
            messagebox.showinfo("Dados do Inversor", f"{dados}")
    except sqlite3.Error as e:
        messagebox.showerror("Erro", f"Erro: {e}")
    finally:
        conexao.close()

# Exibe dados do módulo
def mostrar_dados_modulo():
    modelo = modulo_cb.get()
    if not modelo:
        messagebox.showinfo("Aviso", "Selecione um módulo.")
        return
    try:
        conexao = sqlite3.connect('optimus_sun.db')
        cursor = conexao.cursor()
        modulo_id = modulos.get(modelo)
        cursor.execute("SELECT * FROM module WHERE ID = ?", (modulo_id,))
        dados = cursor.fetchone()
        if dados:
            messagebox.showinfo("Dados do Módulo", f"{dados}")
    except sqlite3.Error as e:
        messagebox.showerror("Erro", f"Erro: {e}")
    finally:
        conexao.close()

# Inicia a interface Tkinter
root = tk.Tk()
root.title("Optimus Sun - Dimensionamento Individual")
root.configure(bg="#e6f2ff")
root.geometry("900x560")

carregar_fabricante()

style = ttk.Style()
style.configure("TLabel", padding=5, background="#e6f2ff", font=("Arial", 10))
style.configure("TCombobox", padding=5, font=("Arial", 10))
style.configure("TEntry", padding=5, font=("Arial", 10))

frame = ttk.Frame(root, padding=20)
frame.grid(row=0, column=0, padx=10, pady=10)

def criar_label(texto, linha, coluna):
    return ttk.Label(frame, text=texto).grid(row=linha, column=coluna, sticky='w', padx=10, pady=5)

criar_label("Fabricante do inversor:", 0, 0)
fab_inversor_cb = ttk.Combobox(frame, values=list(fab_inversor.keys()))
fab_inversor_cb.grid(row=0, column=1, padx=5, pady=5)
fab_inversor_cb.bind("<<ComboboxSelected>>", lambda e: carregar_modelo(fab_inversor_cb.get(), "inversor"))

criar_label("Fabricante do módulo:", 0, 2)
fab_modulo_cb = ttk.Combobox(frame, values=list(fab_modulo.keys()))
fab_modulo_cb.grid(row=0, column=3, padx=5, pady=5)
fab_modulo_cb.bind("<<ComboboxSelected>>", lambda e: carregar_modelo(fab_modulo_cb.get(), "modulo"))

criar_label("Inversor:", 1, 0)
inversor_cb = ttk.Combobox(frame)
inversor_cb.grid(row=1, column=1, padx=5, pady=5)
btn_inversor = ttk.Button(frame, text="Ver dados do inversor", command=mostrar_dados_inversor)
btn_inversor.grid(row=2, column=1, padx=5, pady=(0, 10))

criar_label("Selecione o Módulo:", 1, 2)
modulo_cb = ttk.Combobox(frame)
modulo_cb.grid(row=1, column=3, padx=5, pady=5)
btn_modulo = ttk.Button(frame, text="Ver dados do módulo", command=mostrar_dados_modulo)
btn_modulo.grid(row=2, column=3, padx=5, pady=(0, 10))

entradas = {}
campo_labels = [
    "Quantidade de módulos", "Temp. Mínima", "Temp. Máxima",
    "Tolerância de Potência (%)", "Tolerância de Corrente de Operação (%)"
]

for i, label in enumerate(campo_labels, start=3):
    criar_label(label + ":", i, 0)
    entradas[label] = ttk.Entry(frame)
    entradas[label].grid(row=i, column=1, padx=5, pady=5)

saidas = {}
saida_labels = [
    "Quant. Máxima de séries por MPPT", "Quantidade mínima de módulos", "Quantidade máxima de módulos",
    "Quantidade mínima de módulos em Carga máxima", "Quantidade máxima de módulos em Carga máxima",
    "Quantidade máxima de módulos em Sobrecarga", "Potência em Sobrecarga"
]

for i, label in enumerate(saida_labels, start=8):
    criar_label(label + ":", i, 0)
    saidas[label] = ttk.Entry(frame, state='readonly')
    saidas[label].grid(row=i, column=1, padx=5, pady=5)
    print(label)

root.mainloop()
