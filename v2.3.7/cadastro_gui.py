import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

def conectar_bd():
    return sqlite3.connect('seu_banco_de_dados.db')

def cadastrar_inversor():
    conexao = conectar_bd()
    cursor = conexao.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO inverter (
                MODEL, MANUFACTURER_ID, DIM_WIDTH, DIM_HEIGHT, DIM_DEPTH, DIM_WEIGHT,
                MAX_OPERATING_TEMPERATURE, MIN_OPERATING_TEMPERATURE, COOLING_MODE,
                PROTECTION_DEGREE, TOPOLOGY, RATED_ACTIVE_POWER, MAX_ACTIVE_POWER,
                RATED_OUTPUT_VOLTAGE, RATED_OUTPUT_CURRENT, MAX_OUTPUT_CURRENT,
                OVERLOAD, NUMBER_OF_TRACKERS, NUMBER_OF_INPUTS, ACTIVE
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            model_var.get(), int(manufacturer_var.get()), float(dim_width_var.get()),
            float(dim_height_var.get()), float(dim_depth_var.get()), float(dim_weight_var.get()),
            int(max_temp_var.get()), int(min_temp_var.get()), cooling_mode_var.get(),
            protection_degree_var.get(), topology_var.get(), int(rated_power_var.get()),
            int(max_power_var.get()), float(rated_voltage_var.get()), float(rated_current_var.get()),
            float(max_current_var.get()), int(overload_var.get()), int(trackers_var.get()),
            int(inputs_var.get()), int(active_var.get())
        ))
        conexao.commit()
        messagebox.showinfo("Sucesso", "Inversor cadastrado com sucesso!")
        limpar_campos()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao cadastrar inversor: {e}")
    finally:
        conexao.close()

def limpar_campos():
    for var in todas_variaveis:
        var.set('')

# Criando a janela principal
root = tk.Tk()
root.title("Cadastro de Inversores")
root.geometry("500x600")

# Labels e campos de entrada
campos = [
    ("Modelo:", "model_var"),
    ("ID do Fabricante:", "manufacturer_var"),
    ("Largura (cm):", "dim_width_var"),
    ("Altura (cm):", "dim_height_var"),
    ("Profundidade (cm):", "dim_depth_var"),
    ("Peso (kg):", "dim_weight_var"),
    ("Temp. Máx (°C):", "max_temp_var"),
    ("Temp. Mín (°C):", "min_temp_var"),
    ("Modo de Resfriamento:", "cooling_mode_var"),
    ("Grau de Proteção:", "protection_degree_var"),
    ("Topologia:", "topology_var"),
    ("Potência Nominal (W):", "rated_power_var"),
    ("Potência Máx (W):", "max_power_var"),
    ("Tensão Nominal (V):", "rated_voltage_var"),
    ("Corrente Nominal (A):", "rated_current_var"),
    ("Corrente Máx (A):", "max_current_var"),
    ("Sobrecarga (%):", "overload_var"),
    ("Número de MPPTs:", "trackers_var"),
    ("Número de Entradas:", "inputs_var"),
    ("Ativo (0 ou 1):", "active_var")
]

todas_variaveis = []
for i, (label, var_name) in enumerate(campos):
    ttk.Label(root, text=label).grid(row=i, column=0, padx=10, pady=5, sticky='w')
    var = tk.StringVar()
    todas_variaveis.append(var)
    globals()[var_name] = var  # Cria variáveis globais dinamicamente
    ttk.Entry(root, textvariable=var).grid(row=i, column=1, padx=10, pady=5)

# Botão de cadastro
btn_cadastrar = ttk.Button(root, text="Cadastrar", command=cadastrar_inversor)
btn_cadastrar.grid(row=len(campos), column=0, columnspan=2, pady=20)

# Rodar a interface gráfica
root.mainloop()
