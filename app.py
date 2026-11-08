from flask import Flask, render_template, request
import sqlite3
import re
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "usuarios.db")
EVENTOS_LOG = os.path.join(BASE_DIR, "eventos.log")

def init_db():
    with sqlite3.connect(DB) as conexion:
        columnas = [f[1] for f in conexion.execute("PRAGMA table_info(usuarios)")]
        if columnas and "correo" not in columnas:
            conexion.execute("DROP TABLE usuarios")
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL UNIQUE,
                correo TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        """)

def validar_usuario(usuario):
    return re.fullmatch(r"[A-Za-z0-9_]{4,20}", usuario) is not None

def validar_correo(correo):
    return re.fullmatch(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", correo) is not None

def validar_password(password):
    return len(password) >= 8

def registrar_evento(tipo, usuario):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    usuario_seguro = str(usuario).replace("\n", "").replace("\r", "").replace(",", "_")
    print(f"--> GUARDANDO EVENTO EN: {EVENTOS_LOG}") 
    with open(EVENTOS_LOG, "a", encoding="utf-8") as archivo:
        archivo.write(f"{fecha},{tipo},{usuario_seguro}\n")

@app.route("/")
def inicio():
    return "Laboratorio de Ciberseguridad"

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        correo = request.form.get("correo", "").strip()
        password = request.form.get("password", "")

        if not validar_usuario(usuario) or not validar_correo(correo) or not validar_password(password):
            return "Datos inválidos"

        conexion = sqlite3.connect(DB)
        cursor = conexion.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE usuario = ? OR correo = ?", (usuario, correo))
        if cursor.fetchone():
            conexion.close()
            return "El usuario o correo ya está registrado"

        password_hash = generate_password_hash(password)
        cursor.execute("INSERT INTO usuarios (usuario, correo, password) VALUES (?, ?, ?)", (usuario, correo, password_hash))
        conexion.commit()
        conexion.close()
        return "Usuario registrado"
    return render_template("registro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    print("\n--- NUEVA PETICIÓN A /login ---")
    if request.method == "POST":
        print("--- ES UN POST ---")
        usuario = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")

        if not validar_usuario(usuario) or not validar_password(password):
            print("--- FORMATO INVÁLIDO, GUARDANDO LOGIN_FALLIDO ---")
            registrar_evento("LOGIN_FALLIDO", usuario)
            return "Credenciales incorrectas"

        conexion = sqlite3.connect(DB)
        cursor = conexion.cursor()
        cursor.execute("SELECT id, usuario, correo, password FROM usuarios WHERE usuario = ?", (usuario,))
        resultado = cursor.fetchone()
        conexion.close()

        if resultado and check_password_hash(resultado[3], password):
            print("--- LOGIN CORRECTO ---")
            registrar_evento("LOGIN_CORRECTO", usuario)
            return "Inicio de sesión correcto"
        else:
            print("--- LOGIN FALLIDO, GUARDANDO LOGIN_FALLIDO ---")
            registrar_evento("LOGIN_FALLIDO", usuario)
            return "Credenciales incorrectas"

    return render_template("login.html")

init_db()

if __name__ == "__main__":
    app.run(debug=True)