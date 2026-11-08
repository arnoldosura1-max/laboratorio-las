import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "usuarios.db")

conexion = sqlite3.connect(DB)
cursor = conexion.cursor()

# Si existe una tabla vieja sin la columna 'correo', se elimina para recrearla bien
columnas = [f[1] for f in cursor.execute("PRAGMA table_info(usuarios)")]
if columnas and "correo" not in columnas:
    cursor.execute("DROP TABLE usuarios")

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL UNIQUE,
    correo TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);
""")

conexion.commit()
conexion.close()

print("Base de datos y tabla creadas correctamente.")