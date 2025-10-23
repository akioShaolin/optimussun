#inv_vs_mod_gui.py

import sqlite3
import tkinter as tk
import math
from tkinter import ttk

from calculos import compensacao_termica

fab_inversor = {}
fab_modulo = {}
inv_selec = {}
mod_selec = {}

# Conectar ao banco de dados

def criar_label(texto, linha, coluna):
    return ttk.Label(root, text=texto).grid(row=linha, column=coluna, sticky='w', padx=5, pady=5)

def carregar_fabricante():
    global fab_inversor, fab_modulo

    conexao = sqlite3.connect('optimus_sun.db')
    cursor = conexao.cursor()
    
    # Carregar fabricantes dos inversores
    cursor.execute("SELECT ID, NAME FROM manufacturer WHERE CATEGORY IN (0, 2)")
    fab_inversor = {row[1]: row[0] for row in cursor.fetchall()} # {Nome : ID}
    
    # Carregar fabricantes dos módulos
    cursor.execute("SELECT ID, NAME FROM manufacturer WHERE CATEGORY IN (1, 2)")
    fab_modulo = {row[1]: row[0] for row in cursor.fetchall()} # {Nome : ID}
    
    conexao.close()

# Busca modelos com base no fabricante selecionado
def carregar_modelo(fab_nome, equipamento):
    global inversores, modulos

    conexao = sqlite3.connect('optimus_sun.db')
    cursor = conexao.cursor()
    
    limpar_saidas()

    if equipamento == "inversor":
        fab_id = fab_inversor.get(fab_nome)
        cursor.execute("SELECT ID, MODEL FROM inverter WHERE MANUFACTURER_ID = ?",(fab_id, ))
        inversores = {row[1]: row[0] for row in cursor.fetchall()}
        inversor_cb["values"] = list(inversores.keys())
        inversor_cb.set("")

    elif equipamento == "modulo": 
        fab_id = fab_modulo.get(fab_nome)
        cursor.execute("SELECT ID, MODEL FROM module WHERE MANUFACTURER_ID = ?", (fab_id, ))
        modulos = {row[1]: row[0] for row in cursor.fetchall()}
        modulo_cb["values"] = list(modulos.keys())
        modulo_cb.set("")
    
    conexao.close()

def carregar_dados(modelo, equipamento):
   
    global mod_selec, inv_selec

    conexao = sqlite3.connect('optimus_sun.db')
    cursor = conexao.cursor()

    if (equipamento == "inversor"):
        inv_id = inversores.get(modelo)
        cursor.execute("SELECT NUMBER_OF_TRACKERS, NUMBER_OF_INPUTS FROM inverter WHERE ID = ?", (inv_id,))
        colunas = [col[0] for col in cursor.description]
        valores = cursor.fetchone()
        inv_selec = dict(zip(colunas, valores)) if valores else {}

        cursor.execute("SELECT MPPT_INDEX, NUMBER_OF_INPUTS, MAX_INPUT_VOLTAGE, MIN_STARTUP_VOLTAGE, MAX_OPERATING_VOLTAGE, MIN_OPERATING_VOLTAGE, MAX_FULL_LOAD_VOLTAGE, MIN_FULL_LOAD_VOLTAGE, RATED_INPUT_VOLTAGE, MAX_SHORT_CIRCUIT_CURRENT, MAX_OPERATING_CURRENT FROM mppt WHERE INVERTER_ID = ?", (inv_id,))
        colunas_mppt = [col[0] for col in cursor.description]
        mppt_data = cursor.fetchall()
        mppt_list = [dict(zip(colunas_mppt, linha)) for linha in mppt_data]

        inv_selec["MPPT"] = mppt_list

    elif (equipamento == "modulo"):
        mod_id = modulos.get(modelo)
        cursor.execute("SELECT WP, VMPP, IMPP, VOC, ISC, COEF_VOC, COEF_ISC FROM module WHERE ID = ?", (mod_id, ))
        linha = cursor.fetchone()

        if linha:
            colunas = [col[0] for col in cursor.description]
            mod_selec = dict(zip(colunas, linha))

    conexao.close()

    n_in_mppt = inv_selec["MPPT"][0]["NUMBER_OF_INPUTS"]
    max_i_v = inv_selec["MPPT"][0]["MAX_INPUT_VOLTAGE"]
    min_i_v = inv_selec["MPPT"][0]["MIN_STARTUP_VOLTAGE"]
    max_o_v = inv_selec["MPPT"][0]["MAX_OPERATING_VOLTAGE"]
    min_o_v = inv_selec["MPPT"][0]["MIN_OPERATING_VOLTAGE"]
    max_fl_v = inv_selec["MPPT"][0]["MAX_FULL_LOAD_VOLTAGE"]
    min_fl_v = inv_selec["MPPT"][0]["MIN_FULL_LOAD_VOLTAGE"]
    max_sc_i = inv_selec["MPPT"][0]["MAX_SHORT_CIRCUIT_CURRENT"]
    max_o_i = inv_selec["MPPT"][0]["MAX_OPERATING_CURRENT"]

    vmpp_min, vmpp_max = compensacao_termica(mod_selec["COEF_VOC"], 10, 50, mod_selec["VMPP"])
    voc_min, voc_max = compensacao_termica(mod_selec["COEF_VOC"], 10, 50, mod_selec["VOC"])
    isc_min, isc_max = compensacao_termica(mod_selec["COEF_ISC"], 10, 50, mod_selec["ISC"])
    impp_min, impp_max = compensacao_termica(mod_selec["COEF_ISC"], 10, 50, mod_selec["IMPP"]) 
        
    print(f"\nVmpp Max: {vmpp_max:.2f},\nVmpp Min: {vmpp_min:.2f},\nVoc Max: {voc_max:.2f},\nVoc Min {voc_min:.2f},\nIsc Max: {isc_max:.2f},\nIsc Min: {isc_min:.2f},\nImpp Max: {impp_max:.2f},\nImpp Min: {impp_min:.2f}")
    print(f"\nInput Voltage Range: {min_i_v:.2f}, {max_i_v:.2f},\nOperating Voltage Range: {min_o_v:.2f}, {max_o_v:.2f},\nFull Load Voltage Range: {min_fl_v:.2f}, {max_fl_v:.2f},\nMax Short Circuit Current: {max_sc_i:.2f},\nMax Operating Current:  {max_o_i:.2f}")
    
    # 10% de tolerância na corrente de entrada
    
    q_s_mppt = math.trunc(min(n_in_mppt, max_sc_i/isc_max, max_o_i * 1.1/impp_max))

    if (q_s_mppt > 0):
        q_min_in = math.ceil(max(min_i_v/voc_min, min_o_v/vmpp_min))
        q_max_in = math.trunc(min(max_i_v/voc_max, max_o_v/vmpp_max))
        q_min_fl = math.ceil(max(min_fl_v/vmpp_min, q_min_in))
        q_max_fl = math.trunc(min(max_fl_v/vmpp_max, q_max_in))
    else:
        q_min_in = 0
        q_max_in = 0
        q_min_fl = 0
        q_max_fl = 0

    print(f"\nQuantidade máxima de séries por MPPT: {q_s_mppt}\nQuantidade mínima de módulos por string: {q_min_in}\nQuantidade máxima de módulos por string: {q_max_in}\nQuantidade mínima de módulos em Carga máxima: {q_min_fl}\nQuantidade máxima de módulos em Carga máxima: {q_max_fl}")

    q_max_s_mppt_e.config(state='normal')
    q_max_s_mppt_e.delete(0, tk.END)
    q_max_s_mppt_e.insert(0, str(q_s_mppt))
    q_max_s_mppt_e.config(state='readonly')

    q_min_mod_str_e.config(state='normal')
    q_min_mod_str_e.delete(0, tk.END)
    q_min_mod_str_e.insert(0, str(q_min_in))
    q_min_mod_str_e.config(state="readonly")

    q_max_mod_str_e.config(state='normal')
    q_max_mod_str_e.delete(0, tk.END)
    q_max_mod_str_e.insert(0, str(q_max_in))
    q_max_mod_str_e.config(state="readonly")

    q_min_mod_fl_e.config(state='normal')
    q_min_mod_fl_e.delete(0, tk.END)
    q_min_mod_fl_e.insert(0, str(q_min_fl))
    q_min_mod_fl_e.config(state="readonly")

    q_max_mod_fl_e.config(state='normal')
    q_max_mod_fl_e.delete(0, tk.END)
    q_max_mod_fl_e.insert(0, str(q_max_fl))
    q_max_mod_fl_e.config(state="readonly")

def limpar_saidas():

    q_max_s_mppt_e.config(state='normal')
    q_max_s_mppt_e.delete(0, tk.END)
    q_max_s_mppt_e.insert(0, 0)
    q_max_s_mppt_e.config(state='readonly')

    q_min_mod_str_e.config(state='normal')
    q_min_mod_str_e.delete(0, tk.END)
    q_min_mod_str_e.insert(0, 0)
    q_min_mod_str_e.config(state="readonly")

    q_max_mod_str_e.config(state='normal')
    q_max_mod_str_e.delete(0, tk.END)
    q_max_mod_str_e.insert(0, 0)
    q_max_mod_str_e.config(state="readonly")

    q_min_mod_fl_e.config(state='normal')
    q_min_mod_fl_e.delete(0, tk.END)
    q_min_mod_fl_e.insert(0, 0)
    q_min_mod_fl_e.config(state="readonly")

    q_max_mod_fl_e.config(state='normal')
    q_max_mod_fl_e.delete(0, tk.END)
    q_max_mod_fl_e.insert(0, 0)
    q_max_mod_fl_e.config(state="readonly")


# Criar interface Tkinter
root = tk.Tk()
root.iconbitmap("optimus_sun.ico")
root.title("Optimus Sun 2.0.0")
root.configure(background="#e6f2ff")
root.geometry("650x300")
root.resizable(False, False)

# Carregar fabricantes antes de criar os widgets
carregar_fabricante()

# Estilos
style = ttk.Style()
style.configure("Tlabel", padding = 5, background = "#f0f0f0", font=("Arial", 10))
style.configure("TCombobox", padding = 5, font=("Arial", 10))
style.configure("TEntry", padding = 5, font=("Arial", 10))

frame = ttk.Frame(root, padding = 20)
frame.grid(row = 0, column = 0, padx = 5, pady = 10)

# Selecionar fabricante do Inversor
criar_label("Fabricante do inversor:", 0, 0)
fab_inversor_cb = ttk.Combobox(root, values = list(fab_inversor.keys()), state = "readonly")
fab_inversor_cb.grid(row = 0, column = 1, padx = 5, pady = 5)
fab_inversor_cb.bind("<<ComboboxSelected>>", lambda e: carregar_modelo(fab_inversor_cb.get(), "inversor"))

# Selecionar fabricante do Módulo
criar_label("Fabricante do módulo:", 0, 3)
fab_modulo_cb = ttk.Combobox(root, values = list(fab_modulo.keys()), state = "readonly")
fab_modulo_cb.grid(row=0, column=4, padx = 5, pady = 5)
fab_modulo_cb.bind("<<ComboboxSelected>>", lambda e: carregar_modelo(fab_modulo_cb.get(), "modulo"))

# Seleção de inversor por modelo
criar_label("Inversor:", 1, 0)
inversor_cb = ttk.Combobox(root, state = "readonly")
inversor_cb.grid(row=1, column=1, padx=5, pady=5)
inversor_cb.bind("<<ComboboxSelected>>", lambda e: carregar_dados(inversor_cb.get(), "inversor"))

# Seleção de módulo por modelo
criar_label("Selecione o Módulo:", 1, 3)
modulo_cb = ttk.Combobox(root, state = "readonly")
modulo_cb.grid(row=1, column=4, padx=5, pady=5)
modulo_cb.bind("<<ComboboxSelected>>", lambda e: carregar_dados(modulo_cb.get(), "modulo"))

# Campos de entrada
# Temperatura mínima
#criar_label("Temp mínima:", 2, 0)
#temp_min_e = ttk.Entry(root)
#temp_min_e.grid(row=2, column=1, padx=5, pady=5)

#entradas = {}
#campo_labels = [
#    "Temp. Máxima", "Tolerância de Potência (%)", "Tolerância de Corrente de Operação (%)"
#]

#for i, label in enumerate(campo_labels, start=3):
#    criar_label(label+":", i, 0)
#    entradas[label] = tk.Entry(root)
#    entradas[label].grid(row=i, column=1, padx=5, pady=5)

# Campos de saída
criar_label("Strings por MPPT:", 7, 1)
q_max_s_mppt_e = ttk.Entry(root, state='readonly')
q_max_s_mppt_e.grid(row=7, column=3, padx=5, pady=5)

criar_label("Mín. de módulos por string:", 8, 1)
q_min_mod_str_e = ttk.Entry(root, state='readonly')
q_min_mod_str_e.grid(row=8, column=3, padx=5, pady=5)

criar_label("Máx. de módulos por string:", 9, 1)
q_max_mod_str_e = ttk.Entry(root, state='readonly')
q_max_mod_str_e.grid(row=9, column=3, padx=5, pady=5)

criar_label("Mín. de módulos em Carga máxima:", 10, 1)
q_min_mod_fl_e = ttk.Entry(root, state='readonly')
q_min_mod_fl_e.grid(row=10, column=3, padx=5, pady=5)

criar_label("Máx. de módulos em Carga máxima:", 11, 1)
q_max_mod_fl_e = ttk.Entry(root, state='readonly')
q_max_mod_fl_e.grid(row=11, column=3, padx=5, pady=5)

root.mainloop()