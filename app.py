from flask import Flask, g, session, request, abort, redirect, url_for, render_template
import sqlite3
from math import ceil
from config import SECRET_KEY

DATABASE = 'FarmaGo.db'
app = Flask(__name__)
app.secret_key = SECRET_KEY

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def create_tables():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.executescript('''
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
                logo_url TEXT,
                pharmacy_uuid TEXT
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
        ''')
        db.commit()

def get_user_id(correo_electronico):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id FROM usuarios WHERE correo_electronico = ?', (correo_electronico,))
        result = cursor.fetchone()
        return result[0] if result else None

def get_farmacia_info(id_usuario):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT nombre, direccion, provincia, localidad, numero_telefono, correo_electronico FROM usuarios WHERE id = ?', (id_usuario,))
        result = cursor.fetchone()
        return result if result else None


def get_user_info(id_usuario):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT nombre, apellido, direccion, provincia, localidad, numero_telefono, correo_electronico, nombre_usuario, contraseña, logo_url FROM usuarios WHERE id = ?', (id_usuario,))
        result = cursor.fetchone()
        return result if result else None

def register_user(nombre_usuario, contraseña, role, nombre, apellido, direccion, numero_telefono, provincia, localidad, correo_electronico, pharmacy_uuid=None,logo_url=None):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id FROM usuarios WHERE correo_electronico = ?', (correo_electronico,))
        existing_user = cursor.fetchone()
        if existing_user:
            return "El correo electrónico ya está en uso. Por favor, elige otro."
        if role == 'farmacia':
            cursor.execute('INSERT INTO usuarios (nombre_usuario, contraseña, role, nombre, apellido, direccion, numero_telefono, provincia, localidad, correo_electronico, pharmacy_uuid, logo_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (nombre_usuario, contraseña, role, nombre, apellido, direccion, numero_telefono, provincia, localidad, correo_electronico, pharmacy_uuid, logo_url))
            farmacia_id = cursor.lastrowid
            db.commit()
            cursor.execute('SELECT id FROM productos')
            productos = cursor.fetchall()
            for producto in productos:
                cursor.execute('INSERT INTO inventario (id_farmacia, id_producto, cantidad_disponible) VALUES (?, ?, ?)', (farmacia_id, producto[0], 0))
            db.commit()
        else:
            cursor.execute('INSERT INTO usuarios (nombre_usuario, contraseña, role, nombre, apellido, direccion, numero_telefono, provincia, localidad, correo_electronico, logo_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (nombre_usuario, contraseña, role, nombre, apellido, direccion, numero_telefono, provincia, localidad, correo_electronico, logo_url))
        db.commit()

@app.route('/perfil')
def perfil():
    user_role = session.get('user_role')
    if user_role == 'farmacia' or user_role == 'cliente':
        return render_template('perfil.html')
    else:
        abort(403)

@app.route('/farmacia/inventario', methods=['GET', 'POST'])
def farmacia_inventario():
    user_role = session.get('user_role')
    if user_role == 'farmacia':
        if request.method == 'POST':
            inventario = request.form.getlist('inventario')
            farmacia_id = session.get('user_id')
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute('DELETE FROM inventario WHERE id_farmacia = ?', (farmacia_id,))
                for id_producto, cantidad in enumerate(inventario, start=1):
                    if cantidad.isdigit() and int(cantidad) >= 0:
                        cursor.execute('INSERT INTO inventario (id_farmacia, id_producto, cantidad_disponible) VALUES (?, ?, ?)', (farmacia_id, id_producto, cantidad))
                db.commit()
        else:
            farmacia_id = session.get('user_id')
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute('SELECT p.id, p.nombre, COALESCE(i.cantidad_disponible, 0) as cantidad_disponible FROM productos p LEFT JOIN inventario i ON p.id = i.id_producto AND i.id_farmacia = ? WHERE p.id_farmacia = ?', (farmacia_id, farmacia_id))
                inventario = cursor.fetchall()
        return render_template('farmacia_inventario.html', inventario=inventario)
    else:
        abort(403)

@app.route('/productos', methods=['GET'])
def listar_productos():
    user_role = session.get('user_role')
    if user_role == 'farmacia' or user_role == 'cliente':
        pagina = request.args.get('pagina', default=1, type=int)
        productos_por_pagina = 9
        search_query = request.args.get('search_query')
        if search_query:
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute('SELECT COUNT(*) FROM productos WHERE nombre LIKE ?', ('%' + search_query + '%',))
                total_productos = cursor.fetchone()[0]
                total_paginas = ceil(total_productos / productos_por_pagina)
                if pagina < 1:
                    pagina = 1
                elif pagina > total_paginas:
                    pagina = total_paginas
                inicio = (pagina - 1) * productos_por_pagina
                cursor.execute('SELECT * FROM productos WHERE nombre LIKE ? LIMIT ? OFFSET ?', ('%' + search_query + '%', productos_por_pagina, inicio))
                productos = cursor.fetchall()
            return render_template('listar_productos.html', productos=productos, pagina=pagina, total_paginas=total_paginas, user_role=user_role, search_query=search_query)
        else: 
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute('SELECT COUNT(*) FROM productos')
                total_productos = cursor.fetchone()[0]
                total_paginas = ceil(total_productos / productos_por_pagina)
                if pagina < 1:
                    pagina = 1
                elif pagina > total_paginas:
                    pagina = total_paginas
                inicio = (pagina - 1) * productos_por_pagina
                cursor.execute('SELECT * FROM productos LIMIT ? OFFSET ?', (productos_por_pagina, inicio))
                productos = cursor.fetchall()
            return render_template('listar_productos.html', productos=productos, pagina=pagina, total_paginas=total_paginas, user_role=user_role)

    else:
        abort(403)


@app.route('/productos/<int:id_producto>', methods=['GET'])
def ver_detalle_producto(id_producto):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM productos WHERE id=?', (id_producto,))
        producto = cursor.fetchone()
        farmacia_info = get_farmacia_info(producto[7])
        id_farmacia = producto[7]
    if producto and farmacia_info:
        return render_template('detalle_producto.html', producto=producto, farmacia_info=farmacia_info, id_farmacia=id_farmacia)
    else:
        abort(404)

@app.route('/todas_farmacias', methods=['GET', 'POST'])
def todas_farmacias():
    if request.method == 'POST':
        search_query = request.form.get('search_query', '').strip()
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            if search_query:
                cursor.execute('SELECT * FROM usuarios WHERE role="farmacia" AND nombre LIKE ?', ('%' + search_query + '%',))
            else:
                cursor.execute('SELECT * FROM usuarios WHERE role="farmacia"')
            farmacias = cursor.fetchall()
    else:
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE role="farmacia"')
            farmacias = cursor.fetchall()
    return render_template('todas_farmacias.html', farmacias=farmacias)



@app.route('/productos/farmacia/<int:id_usuario>', methods=['GET'])
def productos_por_farmacia(id_usuario):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM productos WHERE id_farmacia=?', (id_usuario,))
        productos = cursor.fetchall()
        farmacia_info = get_farmacia_info(id_usuario)
    return render_template('productos_farmacia.html', productos=productos, farmacia_info=farmacia_info)

def get_user_role(nombre_usuario):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT role FROM usuarios WHERE nombre_usuario = ?', (nombre_usuario,))
        result = cursor.fetchone()
        return result[0] if result else None

@app.route('/')
def index():
    return render_template('index.html')

def authenticate_user(correo_electronico, contraseña):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id, role FROM usuarios WHERE correo_electronico = ? AND contraseña = ?', (correo_electronico, contraseña))
        result = cursor.fetchone()
        if result:
            return result[0], result[1]
        return None, None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo_electronico = request.form.get('correo_electronico')
        password = request.form.get('password')
        user_id, user_role = authenticate_user(correo_electronico, password)
        if user_id and user_role:
            session['user_id'] = user_id
            session['user_role'] = user_role
            return redirect(url_for('dashboard'))
        else:
            error="Credenciales inválidas. Por favor, inténtalo nuevamente."
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')

@app.route('/register/cliente', methods=['GET', 'POST'])
def register_cliente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        direccion = request.form['direccion']
        numero_telefono = request.form['numero_telefono']
        provincia = request.form['provincia']
        localidad = request.form['localidad']
        correo_electronico = request.form['correo_electronico']
        nombre_usuario = request.form['nombre_usuario']
        contraseña = request.form['contraseña']
        role = 'cliente'
        logo_url = request.form.get('logo_url')  # Get the logo URL from the form
        error_message = register_user(nombre_usuario, contraseña, role, nombre, apellido, direccion, numero_telefono, provincia, localidad, correo_electronico, logo_url=logo_url)
        if error_message:
            return render_template('register.html', error=error_message)
        return redirect(url_for('login'))
    else:
        return render_template('register.html')

@app.route('/register/farmacia', methods=['GET', 'POST'])
def register_farmacia():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        direccion = request.form['direccion']
        numero_telefono = request.form['numero_telefono']
        provincia = request.form['provincia']
        localidad = request.form['localidad']
        correo_electronico = request.form['correo_electronico']
        nombre_usuario = request.form['nombre_usuario']
        contraseña = request.form['contraseña']
        role = 'farmacia'
        logo_url = request.form.get('logo_url')  # Get the logo URL from the form

        error_message = register_user(nombre_usuario, contraseña, role, nombre, apellido, direccion, numero_telefono, provincia, localidad, correo_electronico,logo_url=logo_url)
        if error_message:
            return render_template('register.html', error=error_message)
        return redirect(url_for('login'))
    else:
        return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    user_role = session.get('user_role')
    if user_role == 'farmacia':
        return render_template('panel.html')
    elif user_role == 'cliente':
        return redirect(url_for('listar_productos'))
    else:
        abort(403)

@app.route('/editar_perfil', methods=['GET', 'POST'])
def editar_perfil():
    user_role = session.get('user_role')
    if user_role in ('farmacia', 'cliente'):
        user_id = session.get('user_id')
        user_info = get_user_info(user_id)
        if request.method == 'POST':
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            direccion = request.form['direccion']
            provincia = request.form['provincia']
            localidad = request.form['localidad']
            numero_telefono = request.form['numero_telefono']
            correo_electronico = request.form['correo_electronico']
            nombre_usuario = request.form['nombre_usuario']
            contraseña = request.form['contraseña']
            logo_url= request.form['logo_url']
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute('UPDATE usuarios SET nombre=?, apellido=?, direccion=?, provincia=?, localidad=?, numero_telefono=?, correo_electronico=?, contraseña=?, nombre_usuario=? logo_url=? WHERE id=?',
                            (nombre, apellido, direccion, provincia, localidad, numero_telefono, correo_electronico, contraseña, nombre_usuario, logo_url, user_id))
                db.commit()
            return redirect(url_for('perfil'))
        else:
            if user_info:
                nombre, apellido, direccion, provincia, localidad, numero_telefono, correo_electronico, nombre_usuario, contraseña, logo_url = user_info
            else:
                nombre, apellido, direccion, provincia, localidad, numero_telefono, correo_electronico, nombre_usuario, contraseña, logo_url = "", "", "", "", "", "", "", "", "", ""
            return render_template('editar_perfil.html', nombre=nombre, apellido=apellido, direccion=direccion, provincia=provincia, localidad=localidad, numero_telefono=numero_telefono, correo_electronico=correo_electronico, nombre_usuario=nombre_usuario, contraseña=contraseña, logo_url=logo_url)
    else:
        abort(403)

@app.route('/eliminar_cuenta', methods=['POST'])
def eliminar_cuenta():
    user_id = session.get('user_id')
    if user_id:
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('DELETE FROM usuarios WHERE id=?', (user_id,))
            db.commit()
        session.clear()
        return redirect(url_for('login'))
    else:
        abort(403)

@app.route('/productos/agregar', methods=['GET', 'POST'])
def agregar_producto():
    user_role = session.get('user_role')
    if user_role == 'farmacia':
        if request.method == 'POST':
            nombre = request.form['nombre']
            imagen = request.form['imagen']
            descripcion = request.form['descripcion']
            cantidad = int(request.form['cantidad'])
            precio_unitario = float(request.form['precio_unitario'])
            id_categoria = int(request.form['categoria'])
            id_farmacia = session.get('user_id')
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute('INSERT INTO productos (nombre, imagen, descripcion, cantidad, precio_unitario, id_categoria, id_farmacia) VALUES (?, ?, ?, ?, ?, ?, ?)', (nombre, imagen, descripcion, cantidad, precio_unitario, id_categoria, id_farmacia))
                product_id = cursor.lastrowid
                db.commit()
                cursor.execute('INSERT INTO farmacia_productos (id_usuario, id_producto) VALUES (?, ?)', (id_farmacia, product_id))
                db.commit()
            return redirect(url_for('farmacia_inventario'))
        else:
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute('SELECT id, nombre FROM categorias')
                categorias = cursor.fetchall()
            return render_template('agregar_producto.html', categorias=categorias)
    else:
        abort(403)

@app.route('/productos/editar/<int:id_producto>', methods=['GET', 'POST'])
def editar_producto(id_producto):
    user_role = session.get('user_role')
    if user_role == 'farmacia':
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT id_usuario FROM farmacia_productos WHERE id_producto = ?', (id_producto,))
            product_owner = cursor.fetchone()
            if not product_owner or product_owner[0] != session.get('user_id'):
                abort(403)
        if request.method == 'POST':
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            precio_unitario = float(request.form['precio_unitario'])
            cantidad = int(request.form['cantidad'])
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute('UPDATE productos SET nombre=?, descripcion=?, precio_unitario=?, cantidad=? WHERE id=?',
                            (nombre, descripcion, precio_unitario, cantidad, id_producto))
                db.commit()
            return redirect(url_for('listar_productos'))
        else:
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute('SELECT nombre, descripcion, precio_unitario, cantidad FROM productos WHERE id=?',
                            (id_producto,))
                producto = cursor.fetchone()
            if producto:
                return render_template('editar_producto.html', producto=producto)
            else:
                abort(404) 
    else:
        abort(403)

@app.route('/productos/eliminar/<int:id_producto>', methods=['POST'])
def eliminar_producto(id_producto):
    user_role = session.get('user_role')
    if user_role == 'farmacia':
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT id_usuario FROM farmacia_productos WHERE id_producto = ?', (id_producto,))
            product_owner = cursor.fetchone()
            if not product_owner or product_owner[0] != session.get('user_id'):
                abort(403)
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('DELETE FROM productos WHERE id=?', (id_producto,))
            cursor.execute('DELETE FROM farmacia_productos WHERE id_producto=?', (id_producto,))
            db.commit()
        return redirect(url_for('farmacia_inventario'))
    else:
        abort(403)

@app.route('/agregar_al_carrito/<int:id_producto>', methods=['POST'])
def agregar_al_carrito(id_producto):
    user_id = session.get('user_id')
    if user_id:
        cantidad = int(request.form['cantidad'])
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM productos WHERE id=?', (id_producto,))
            producto = cursor.fetchone()
            if producto:
                cursor.execute('SELECT * FROM carritos WHERE id_usuario=? AND estado="abierto"', (user_id,))
                carrito = cursor.fetchone()
                if not carrito:
                    cursor.execute('INSERT INTO carritos (id_usuario, fecha, estado, total) VALUES (?, ?, ?, ?)', (user_id, "2023-07-26", "abierto", 0))
                    db.commit()
                    carrito_id = cursor.lastrowid
                else:
                    carrito_id = carrito[0]
                cursor.execute('INSERT OR REPLACE INTO detalles_carrito (id_carrito, id_producto, cantidad, precio_unitario) VALUES (?, ?, ?, ?)', (carrito_id, id_producto, cantidad, producto[5]))
                db.commit()
                return redirect(url_for('ver_detalle_producto', id_producto=id_producto))
            else:
                abort(404)
    else:
        abort(403)

@app.route('/carrito', methods=['GET'])
def ver_carrito():
    user_id = session.get('user_id')
    if user_id:
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM carritos WHERE id_usuario=? AND estado="abierto"', (user_id,))
            carrito = cursor.fetchone()
            if carrito:
                carrito_id = carrito[0]
                cursor.execute('SELECT p.id, p.nombre, p.precio_unitario, dc.cantidad FROM detalles_carrito AS dc INNER JOIN productos AS p ON dc.id_producto = p.id WHERE dc.id_carrito = ?', (carrito_id,))
                productos_carrito = cursor.fetchall()
                total_carrito = sum(producto[2] * producto[3] for producto in productos_carrito)
            else:
                carrito_id = None
                productos_carrito = []
                total_carrito = 0
        return render_template('carrito.html', productos_carrito=productos_carrito, total_carrito=total_carrito)
    else:
        abort(403)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.errorhandler(403)
def page_not_found(error):
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, host="0.0.0.0")