import os
import sqlite3
from flask import Flask, g

app = Flask(__name__)

# Configuración de la base de datos
DATABASE = 'farmacia.db'
SCHEMA_FILE = 'schema.sql'

# Función para conectarse a la base de datos
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

# Función para cerrar la conexión con la base de datos al final de cada solicitud
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Función para inicializar la base de datos
def init_db():
    if not os.path.exists(DATABASE):
        with app.app_context():
            db = get_db()
            with app.open_resource(SCHEMA_FILE, mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()

# Definición de las tablas
def create_tables():
    db = get_db()
    db.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, apellido TEXT, direccion TEXT, numero_telefono TEXT, provincia TEXT, localidad TEXT, correo_electronico TEXT, nombre_usuario TEXT UNIQUE, contraseña TEXT)')
    db.execute('CREATE TABLE IF NOT EXISTS farmacias (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, apellido TEXT, DNI TEXT, direccion TEXT, numero_telefono TEXT, provincia TEXT, localidad TEXT, nombre_usuario TEXT UNIQUE, correo_electronico TEXT, contraseña TEXT)')
    db.execute('CREATE TABLE IF NOT EXISTS productos (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, imagen TEXT, descripcion TEXT, cantidad INTEGER, id_farmacia INTEGER, id_categoria INTEGER, FOREIGN KEY(id_farmacia) REFERENCES farmacias(id), FOREIGN KEY(id_categoria) REFERENCES categorias(id))')
    db.execute('CREATE TABLE IF NOT EXISTS carritos (id INTEGER PRIMARY KEY AUTOINCREMENT, id_usuario INTEGER, fecha TEXT, estado TEXT, FOREIGN KEY(id_usuario) REFERENCES usuarios(id))')
    db.execute('CREATE TABLE IF NOT EXISTS detalles_pedido (id INTEGER PRIMARY KEY AUTOINCREMENT, id_pedido INTEGER, id_producto INTEGER, cantidad INTEGER, precio_unitario REAL, FOREIGN KEY(id_pedido) REFERENCES pedidos(id), FOREIGN KEY(id_producto) REFERENCES productos(id))')
    db.execute('CREATE TABLE IF NOT EXISTS categorias (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT)')
    db.execute('CREATE TABLE IF NOT EXISTS valoraciones (id INTEGER PRIMARY KEY AUTOINCREMENT, id_usuario INTEGER, id_producto INTEGER, puntuacion INTEGER, comentario TEXT, FOREIGN KEY(id_usuario) REFERENCES usuarios(id), FOREIGN KEY(id_producto) REFERENCES productos(id))')
    db.execute('CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY AUTOINCREMENT, id_usuario INTEGER, fecha TEXT, estado TEXT, total REAL, FOREIGN KEY(id_usuario) REFERENCES usuarios(id))')
    db.commit()

if __name__ == '__main__':
    init_db()  # Se ejecutará solo si el archivo de la base de datos no existe
    create_tables()
    app.run()
