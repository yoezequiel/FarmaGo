import sqlite3
from flask import g
import mercadopago
from config import access_token
from flask import Flask

app = Flask(__name__)

DATABASE = "FarmaGo.db"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def create_tables():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                apellido TEXT,
                direccion TEXT,
                numero_telefono TEXT,
                provincia TEXT,
                localidad TEXT,
                correo_electronico TEXT UNIQUE,
                nombre_usuario TEXT UNIQUE,
                contraseña TEXT,
                role TEXT,
                logo_url TEXT
            );
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                imagen TEXT,
                descripcion TEXT,
                cantidad INTEGER,
                precio_unitario REAL,
                id_categoria INTEGER,
                id_farmacia INTEGER, 
                FOREIGN KEY(id_categoria) REFERENCES categorias(id),
                FOREIGN KEY(id_farmacia) REFERENCES usuarios(id)
            );
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT
            );
            CREATE TABLE IF NOT EXISTS farmacia_productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER,
                id_producto INTEGER,
                FOREIGN KEY(id_usuario) REFERENCES usuarios(id),
                FOREIGN KEY(id_producto) REFERENCES productos(id)
            );
            CREATE TABLE IF NOT EXISTS inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_farmacia INTEGER,
                id_producto INTEGER,
                cantidad_disponible INTEGER,
                FOREIGN KEY(id_farmacia) REFERENCES usuarios(id),
                FOREIGN KEY(id_producto) REFERENCES productos(id)
            );
            CREATE TABLE IF NOT EXISTS carritos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER,
                fecha TEXT,
                estado TEXT,
                total REAL,
                FOREIGN KEY(id_usuario) REFERENCES usuarios(id)
            );
            CREATE TABLE IF NOT EXISTS detalles_carrito (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_carrito INTEGER,
                id_producto INTEGER,
                cantidad INTEGER,
                precio_unitario REAL,
                FOREIGN KEY(id_carrito) REFERENCES carritos(id),
                FOREIGN KEY(id_producto) REFERENCES productos(id)
            );
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_vendedor INTEGER,
                id_comprador INTEGER,
                fecha TEXT,
                total REAL,
                FOREIGN KEY(id_vendedor) REFERENCES usuarios(id),
                FOREIGN KEY(id_comprador) REFERENCES usuarios(id)
            );
            CREATE TABLE IF NOT EXISTS detalles_venta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_venta INTEGER,
                id_producto INTEGER,
                cantidad INTEGER,
                precio_unitario REAL,
                FOREIGN KEY(id_venta) REFERENCES ventas(id),
                FOREIGN KEY(id_producto) REFERENCES productos(id)
            );
        """
        )
        db.commit()


def get_user_id(correo_electronico):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT id FROM usuarios WHERE correo_electronico = ?",
            (correo_electronico,),
        )
        result = cursor.fetchone()
        return result[0] if result else None


def get_farmacia_info(id_usuario):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT nombre, apellido, direccion, provincia, localidad, numero_telefono, correo_electronico, nombre_usuario, contraseña, logo_url FROM usuarios WHERE id = ?",
            (id_usuario,),
        )
        result = cursor.fetchone()
        return result if result else None


def get_user_info(id_usuario):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT nombre, apellido, direccion, provincia, localidad, numero_telefono, correo_electronico, nombre_usuario, contraseña, logo_url FROM usuarios WHERE id = ?",
            (id_usuario,),
        )
        result = cursor.fetchone()
        return result if result else None


def get_user_role(nombre_usuario):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT role FROM usuarios WHERE nombre_usuario = ?", (nombre_usuario,)
        )
        result = cursor.fetchone()
        return result[0] if result else None


def authenticate_user(correo_electronico, contraseña):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, role FROM usuarios WHERE correo_electronico = ? AND contraseña = ?",
            (correo_electronico, contraseña),
        )
        result = cursor.fetchone()
        if result:
            return result[0], result[1]
        return None, None


def register_user(
    nombre_usuario,
    contraseña,
    role,
    nombre,
    apellido,
    direccion,
    numero_telefono,
    provincia,
    localidad,
    correo_electronico,
    logo_url=None,
):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT id FROM usuarios WHERE nombre_usuario = ?", (nombre_usuario,)
        )
        existing_username = cursor.fetchone()
        if existing_username:
            return "El nombre de usuario ya está en uso. Por favor, elige otro."
        cursor.execute(
            "SELECT id FROM usuarios WHERE correo_electronico = ?",
            (correo_electronico,),
        )
        existing_user = cursor.fetchone()
        if existing_user:
            return "El correo electrónico ya está en uso. Por favor, elige otro."
        if role == "farmacia":
            cursor.execute(
                "INSERT INTO usuarios (nombre_usuario, contraseña, role, nombre, apellido, direccion, numero_telefono, provincia, localidad, correo_electronico, logo_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    nombre_usuario,
                    contraseña,
                    role,
                    nombre,
                    apellido,
                    direccion,
                    numero_telefono,
                    provincia,
                    localidad,
                    correo_electronico,
                    logo_url,
                ),
            )
            farmacia_id = cursor.lastrowid
            db.commit()
            cursor.execute("SELECT id FROM productos")
            productos = cursor.fetchall()
            for producto in productos:
                cursor.execute(
                    "INSERT INTO inventario (id_farmacia, id_producto, cantidad_disponible) VALUES (?, ?, ?)",
                    (farmacia_id, producto[0], 0),
                )
            db.commit()
        else:
            cursor.execute(
                "INSERT INTO usuarios (nombre_usuario, contraseña, role, nombre, apellido, direccion, numero_telefono, provincia, localidad, correo_electronico, logo_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    nombre_usuario,
                    contraseña,
                    role,
                    nombre,
                    apellido,
                    direccion,
                    numero_telefono,
                    provincia,
                    localidad,
                    correo_electronico,
                    logo_url,
                ),
            )
        db.commit()


def crear_enlace_de_pago(producto, precio, moneda="ARS", cantidad=1, descripcion=""):
    mp = mercadopago.SDK(access_token)
    preference_data = {
        "items": [
            {
                "title": producto,
                "quantity": cantidad,
                "currency_id": moneda,
                "unit_price": precio,
            }
        ],
        "back_urls": {
            "success": "192.168.0.106:5000/pago_exitoso",
            "failure": "192.168.0.106:5000/pago_fallido",
            "pending": "192.168.0.106:5000/pago_pendiente",
        },
        "auto_return": "approved",
    }
    preference = mp.preference().create(preference_data)
    return preference["response"]["init_point"]
