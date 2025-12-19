#import numpy as np
#import pandas as pd
#import matplotlib.pyplot as plt
#import openpyxl
#import json

#print("Bibliotecas instaladas com sucesso!")

#Carregar dados do Excel

#optimus_Sun = "Optimus Sun v0.1.5.xlsx"
#df_inversores = pd.read_excel(optimus_Sun, sheet_name="Dados dos Inversores")
#df_modulos = pd.read_excel(optimus_Sun, sheet_name="Dados dos Modulos")

#print("Inversores: ")
#print(df_inversores.head())

#print("\nMódulos Fotovoltaicos: ")
#print(df_modulos.head())


#Carregar dados de .json

#Nome do arquivo json
#optimus_sun = "inversores.json"

#with open(optimus_sun, "r", encoding="utf-8") as file:
#    dados = json.load(file)

    #print(dados)

#print("Modelo: ", dados[0]["fabricante"])

import json

# Nome do arquivo JSON onde os dados serão armazenados
ARQUIVO_JSON = "inversores.json"

# Função para carregar os dados existentes do JSON
def carregar_dados():
    try:
        with open(ARQUIVO_JSON, "r", encoding="utf-8") as file:
            return json.load(file)  # Carrega os dados existentes
    except (FileNotFoundError, json.JSONDecodeError):
        return []  # Retorna uma lista vazia se o arquivo não existir ou estiver corrompido

# Função para salvar os dados no JSON
def salvar_dados(dados):
    with open(ARQUIVO_JSON, "w", encoding="utf-8") as file:
        json.dump(dados, file, indent=4, ensure_ascii=False)
    print("\n✅ Dados salvos com sucesso!\n")

# Função para cadastrar um novo inversor
def cadastrar_inversor():
    print("\n🔹 Cadastro de Novo Inversor 🔹")

    modelo = input("Modelo: ")
    fabricante = input("Fabricante: ")
    ef_max = input("Eficiência Máxima (%): ")

    sistema = input("Sistema (separado por vírgula, ex: ongrid, offgrid): ").split(",")

    quant_MPPT = int(input("Quantidade de MPPTs: "))
    MPPT = []

    for i in range(quant_MPPT):
        print(f"\n➡ Dados do MPPT {i + 1}")
        quant_str = input("Quantidade de Strings: ")
        tensao_max_part = input("Tensão Máxima de Partida (V): ")
        tensao_min_part = input("Tensão Mínima de Partida (V): ")
        tensao_max_op = input("Tensão Máxima de Operação (V): ")
        tensao_min_op = input("Tensão Mínima de Operação (V): ")
        corrente_max_op = input("Corrente Máxima de Operação (A): ")

        MPPT.append({
            "quant_str": quant_str,
            "tensao_max_part": tensao_max_part,
            "tensao_min_part": tensao_min_part,
            "tensao_max_op": tensao_max_op,
            "tensao_min_op": tensao_min_op,
            "corrente_max_op": corrente_max_op
        })

    novo_inversor = {
        "modelo": modelo,
        "fabricante": fabricante,
        "ef_max": ef_max,
        "sistema": [s.strip() for s in sistema],
        "entrada": {
            "quant_MPPT": quant_MPPT,
            "MPPT": MPPT
        }
    }

    # Carregar os dados atuais e adicionar o novo inversor
    dados = carregar_dados()
    dados.append(novo_inversor)

    # Salvar os dados atualizados no JSON
    salvar_dados(dados)

# Função para listar os inversores cadastrados
def listar_inversores():
    dados = carregar_dados()

    if not dados:
        print("\n⚠ Nenhum inversor cadastrado!\n")
        return

    print("\n Lista de Inversores Cadastrados:\n")
    for i, inversor in enumerate(dados, start=1):
        print(f"{i}. Modelo: {inversor['modelo']} | Fabricante: {inversor['fabricante']} | Eficiência: {inversor['ef_max']}%")
    print()

# Menu principal
def menu():
    while True:
        print("\n MENU PRINCIPAL ")
        print("1️ Cadastrar novo inversor")
        print("2️ Listar inversores cadastrados")
        print("3️ Sair")
        
        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            cadastrar_inversor()
        elif opcao == "2":
            listar_inversores()
        elif opcao == "3":
            print("\n Saindo... Até mais!\n")
            break
        else:
            print("\n Opção inválida! Tente novamente.\n")

# Iniciar o programa
if __name__ == "__main__":
    menu()
