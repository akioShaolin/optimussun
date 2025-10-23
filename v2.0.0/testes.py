#testes

import sqlite3

DB_PATH = 'optimus_sun.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

#cursor.execute('DELETE FROM module')
#cursor.execute("DELETE FROM sqlite_sequence WHERE name='module'")
cursor.execute('SELECT * FROM module')

resultados = cursor.fetchall()
for linha in resultados:
    print (f"\n{linha}")

conn.commit()
conn.close()