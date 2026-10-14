import sqlite3
import hashlib
from datetime import datetime

DB_NAME = "farmacovigilancia.db"

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode('utf-8')).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reportes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_registro TEXT,
            notificador_nombre TEXT,
            notificador_tipo TEXT,
            notificador_contacto TEXT,
            paciente_nombre TEXT,
            paciente_edad TEXT,
            paciente_sexo TEXT,
            medicamento TEXT,
            dosis_via TEXT,
            lote TEXT,
            reaccion TEXT,
            gravedad TEXT,
            desenlace TEXT,
            estado TEXT DEFAULT 'Pendiente'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracion (
            clave TEXT PRIMARY KEY,
            valor TEXT
        )
    ''')
    # Clave inicial por defecto si no existe
    cursor.execute("SELECT valor FROM configuracion WHERE clave = 'admin_password_hash'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO configuracion (clave, valor) VALUES (?, ?)", 
                       ('admin_password_hash', hash_pw('FarmaciaSegura2026*')))
    conn.commit()
    conn.close()

def verificar_password(password: str) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT valor FROM configuracion WHERE clave = 'admin_password_hash'")
    row = cursor.fetchone()
    conn.close()
    if row and row[0] == hash_pw(password):
        return True
    return False

def actualizar_password(nueva_password: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE configuracion SET valor = ? WHERE clave = 'admin_password_hash'", (hash_pw(nueva_password),))
    conn.commit()
    conn.close()

def guardar_reporte(data: dict):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reportes (
            fecha_registro, notificador_nombre, notificador_tipo, notificador_contacto,
            paciente_nombre, paciente_edad, paciente_sexo, medicamento, dosis_via,
            lote, reaccion, gravedad, desenlace
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data.get("notificador_nombre", ""),
        data.get("notificador_tipo", ""),
        data.get("notificador_contacto", ""),
        data.get("paciente_nombre", ""),
        data.get("paciente_edad", ""),
        data.get("paciente_sexo", ""),
        data.get("medicamento", ""),
        data.get("dosis_via", ""),
        data.get("lote", ""),
        data.get("reaccion", ""),
        data.get("gravedad", ""),
        data.get("desenlace", "")
    ))
    conn.commit()
    reporte_id = cursor.lastrowid
    conn.close()
    return reporte_id

def obtener_reportes():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reportes ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
