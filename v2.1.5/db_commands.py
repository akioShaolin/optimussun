#import sqlite3 

#Inicio

# Conectar ao banco de dados

#op_db = sqlite3.connect("optimus_sun.db")
#cursor = op_db.cursor()
#print("Banco de dados SQLite conectado com sucesso")

#Criar a tabela de inversores

#fabricantes = [('ASTRONERGY', 1),
#('BYD', 1),
#('HUASUN', 1),
#('JA SOLAR', 1),
#('JINKO', 1),
#('LONGI', 1),
#('RISEN', 1),
#('SUNOVA', 1),
#('TALESUN', 1),
#('TRINA SOLAR', 1)
#]

#cursor.execute("INSERT INTO inverter (MODEL, MANUFACTURER_ID, DIM_WIDTH, DIM_HEIGHT, DIM_DEPTH, DIM_WEIGHT, MAX_OPERATING_TEMPERATURE, MIN_OPERATING_TEMPERATURE, COOLING_MODE, PROTECTION_DEGREE, TOPOLOGY, RATED_ACTIVE_POWER, MAX_ACTIVE_POWER, RATED_OUTPUT_VOLTAGE, RATED_OUTPUT_CURRENT, MAX_OUTPUT_CURRENT, OVERLOAD, NUMBER_OF_TRACKERS, NUMBER_OF_INPUTS, ACTIVE) VALUES ('SUN2000L-2KTL', 2, 149.5, 375, 375, 11.6, 60, -30, 'CONVECÇÃO NATURAL', 'IP65', 'TRANSFORMLESS', 2000, 2200, 220, 10, 10, 50, 2, 2, 1)")
#cursor.execute("INSERT INTO mppt (INVERTER_ID, NUMBER_OF_INPUTS, MAX_INPUT_VOLTAGE, MIN_STARTUP_VOLTAGE, MAX_OPERATING_VOLTAGE, MIN_OPERATING_VOLTAGE, MAX_FULL_LOAD_VOLTAGE, MIN_FULL_LOAD_VOLTAGE, RATED_INPUT_VOLTAGE, MAX_SHORT_CIRCUIT_CURRENT, MAX_OPERATING_CURRENT) VALUES (1, 1, 600, 120, 500, 90, 500, 90, 380, 15, 11)")
#cursor.execute("INSERT INTO inverter_system(INVERTER_ID, SYSTEM_TYPE) VALUES (1, 'ON-GRID')")
#cursor.execute("INSERT INTO inverter_communication(INVERTER_ID, COMMUNICATION_TYPE) VALUES (1, 'RS485')")
#cursor.execute("INSERT INTO inverter_communication(INVERTER_ID, COMMUNICATION_TYPE) VALUES (1, 'WIFI')")
#cursor.execute("INSERT INTO inverter_communication(INVERTER_ID, COMMUNICATION_TYPE) VALUES (1, 'LED')")
#cursor.execute("INSERT INTO inverter_output_mode(INVERTER_ID, OUTPUT_MODE) VALUES (1, 'SINGLE_PHASE')")
#cursor.execute("INSERT INTO module(MODEL, MANUFACTURER_ID, DIM_WIDTH, DIM_HEIGHT, DIM_DEPTH, DIM_WEIGHT, WP, VMPP, IMPP, VOC, ISC, SOLAR_CELLS, CELL_TYPE, SURFACE_TYPE, COEF_PMAX, COEF_VOC, COEF_ISC, ACTIVE) VALUES ('CHSM72M-HC-405', 6, 2018, 1002, 35, 22.6, 405, 41.59, 9.74, 49.53, 10.31, 'POLICRISTALINO', 'HALF CELL', 'MONOFACIAL', -0.35, -0.28, 0.035, 1)")

#cursor.execute("INSERT INTO inverter (MODEL, MANUFACTURER_ID, DIM_WIDTH, DIM_HEIGHT, DIM_DEPTH, DIM_WEIGHT, MAX_OPERATING_TEMPERATURE, MIN_OPERATING_TEMPERATURE, COOLING_MODE, PROTECTION_DEGREE, TOPOLOGY, RATED_ACTIVE_POWER, MAX_ACTIVE_POWER, RATED_OUTPUT_VOLTAGE, RATED_OUTPUT_CURRENT, MAX_OUTPUT_CURRENT, OVERLOAD, NUMBER_OF_TRACKERS, NUMBER_OF_INPUTS, ACTIVE) VALUES ('R75', 3, 360, 975, 630, 90, 60, -30, 'VENTILAÇÃO FORÇADA', 'IP66', 'TRANSFORMLESS', 75000, 75000, 380, 113.7, 113.7, 50, 9, 18, 1)")
#cursor.execute("INSERT INTO mppt (INVERTER_ID, NUMBER_OF_INPUTS, MAX_INPUT_VOLTAGE, MIN_STARTUP_VOLTAGE, MAX_OPERATING_VOLTAGE, MIN_OPERATING_VOLTAGE, MAX_FULL_LOAD_VOLTAGE, MIN_FULL_LOAD_VOLTAGE, RATED_INPUT_VOLTAGE, MAX_SHORT_CIRCUIT_CURRENT, MAX_OPERATING_CURRENT) VALUES (2, 2, 1100, 250, 1000, 200, 850, 550, 600, 40, 26)")
#cursor.execute("INSERT INTO inverter_system(INVERTER_ID, SYSTEM_TYPE) VALUES (2, 'ON-GRID')")
#cursor.execute("INSERT INTO inverter_communication(INVERTER_ID, COMMUNICATION_TYPE) VALUES (2, 'RS485')")
#cursor.execute("INSERT INTO inverter_communication(INVERTER_ID, COMMUNICATION_TYPE) VALUES (2, 'WIFI')")
#cursor.execute("INSERT INTO inverter_communication(INVERTER_ID, COMMUNICATION_TYPE) VALUES (2, 'LED')")
#cursor.execute("INSERT INTO inverter_communication(INVERTER_ID, COMMUNICATION_TYPE) VALUES (2, 'USB')")
#cursor.execute("INSERT INTO inverter_communication(INVERTER_ID, COMMUNICATION_TYPE) VALUES (2, '4G')")
#cursor.execute("INSERT INTO inverter_output_mode(INVERTER_ID, OUTPUT_MODE) VALUES (2, 'THREE_PHASE_FOUR_WIRE')")

#cursor.execute("INSERT INTO module(MODEL, MANUFACTURER_ID, DIM_WIDTH, DIM_HEIGHT, DIM_DEPTH, DIM_WEIGHT, WP, VMPP, IMPP, VOC, ISC, SOLAR_CELLS, CELL_TYPE, SURFACE_TYPE, COEF_PMAX, COEF_VOC, COEF_ISC, ACTIVE) VALUES ('WPV 550 HMM3', 1, 2278, 1134, 30, 27.3, 550, 41.96, 13.11, 49.9, 14, 'MONOCRISTALINO', 'HALF CELL', 'MONOFACIAL', -0.35, -0.275, 0.045, 1)")

#cursor.executescript("""
#                     UPDATE manufacturer
#                     SET CATEGORY = 2
#                     WHERE ID = 1
#                     """)

#cursor.execute("DELETE FROM inverter_system WHERE ID = 2")

#cursor.execute('SELECT * FROM manufacturer')

#resultados = cursor.fetchall()
#print(resultados)
#for linha in resultados:
#    print (linha)


#Fechar conexão

#op_db.commit()
#op_db.close()

import sqlite3

# Caminho para seu banco de dados
DB_PATH = 'optimus_sun.db'

def inserir_fabricantes(conn, fabricantes):
    cursor = conn.cursor()
    for nome, categoria in fabricantes:
        cursor.execute("INSERT INTO manufacturer (NAME, CATEGORY) VALUES (?, ?)", (nome, categoria))
    conn.commit()

def inserir_inversores(conn, inversores):
    cursor = conn.cursor()

    sql = "INSERT INTO inverter (MODEL, MANUFACTURER_ID, DIM_WIDTH, DIM_HEIGHT, DIM_DEPTH, DIM_WEIGHT, MAX_OPERATING_TEMPERATURE, MIN_OPERATING_TEMPERATURE, COOLING_MODE, PROTECTION_DEGREE, TOPOLOGY, RATED_ACTIVE_POWER, MAX_ACTIVE_POWER, RATED_OUTPUT_VOLTAGE, RATED_OUTPUT_CURRENT, MAX_OUTPUT_CURRENT, OVERLOAD, NUMBER_OF_TRACKERS, NUMBER_OF_INPUTS, ACTIVE) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    for inversor in inversores:
            cursor.execute(sql, inversor)
    conn.commit()

def inserir_mppts(conn, mppts):
     
    cursor = conn.cursor()

    sql = "INSERT INTO mppt (INVERTER_ID, MPPT_INDEX, NUMBER_OF_INPUTS, MAX_INPUT_VOLTAGE, MIN_STARTUP_VOLTAGE, MAX_OPERATING_VOLTAGE, MIN_OPERATING_VOLTAGE, MAX_FULL_LOAD_VOLTAGE, MIN_FULL_LOAD_VOLTAGE, RATED_INPUT_VOLTAGE, MAX_SHORT_CIRCUIT_CURRENT, MAX_OPERATING_CURRENT) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    for mppt in mppts:
        cursor.execute(sql, mppt)

    conn.commit()

def inserir_system(conn, systems):
     
    cursor = conn.cursor()

    sql = "INSERT INTO inverter_system (INVERTER_ID, SYSTEM_TYPE) VALUES (?, ?)"

    for system in systems:
          cursor.execute(sql, system)

    conn.commit()

def inserir_comunicacao(conn, comunicacoes):
    cursor = conn.cursor()

    sql = "INSERT INTO inverter_communication (INVERTER_ID, COMMUNICATION_TYPE) VALUES (?, ?)"

    for comunicacao in comunicacoes:
        cursor.execute(sql, comunicacao)

    conn.commit()


def inserir_modos (conn, modos):
     
    cursor = conn.cursor()
          
    sql = "INSERT INTO inverter_output_mode (INVERTER_ID, OUTPUT_MODE) VALUES (?, ?)"

    for modo in modos:
        cursor.execute(sql, modo)     
     
    conn.commit()

def inserir_modulos(conn, modulos):

    cursor = conn.cursor()

    sql = "INSERT INTO module (MODEL, MANUFACTURER_ID, DIM_WIDTH, DIM_HEIGHT, DIM_DEPTH, DIM_WEIGHT, WP, VMPP, IMPP, VOC, ISC, SOLAR_CELLS, CELL_TYPE, SURFACE_TYPE, COEF_PMAX, COEF_VOC, COEF_ISC, ACTIVE) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    for modulo in modulos:
        cursor.execute(sql, modulo)

    conn.commit()

if __name__ == '__main__':
    # Fabricantes: (NOME, CATEGORIA)
 #   fabricantes = [
 #       ("Fabricante X", 0),
 #       ("Fabricante Y", 0)
 #   ]

    # Exemplo: (modelo, id_fabricante, potência nominal, topologia, tensão nominal de entrada, ...)
    inversores = [
('SIW610 T075 W0', 1, 840, 680, 360, 90, 60, -10, 'COOLER', 'IP66', 'TRANSFORMERLESS', 75000, 75000, 380, 114, 114, 0, 6, 12, 1),

    ]

    mppts = [
(230, 0, 2, 1100, 480, 950, 250, 850, 480, 670, 40, 30), 

    ]

    inverter_system = [
(230, 'ON-GRID'),				
	
		

    ]

    comunicacoes = [
(230, 'RS485'),	(230, 'DISPLAY'),	(230, 'LED'),		
	

    ]

    modos = [
	(230, 'THREE_PHASE_FOUR_WIRE'),	


    ]

    modulos = [
('CHSM72M-HC-405', 6, 2018, 1002, 35, 22.6, 405, 41.59, 9.74, 49.53, 10.31, 'MONOCRISTALINO', 'HALF CELL', 'MONOFACIAL', -0.35, -0.28, 0.035, 0),
    ]

    conn = sqlite3.connect(DB_PATH)

    # inserir_fabricantes(conn, fabricantes)
    # inserir_inversores(conn, inversores)
    # inserir_mppts(conn, mppts)
    # inserir_system(conn, inverter_system)
    # inserir_comunicacao(conn, comunicacoes)
    # inserir_modos (conn, modos)
    # inserir_modulos(conn, modulos)

    conn.close()
    print("Cadastro concluído.")

    