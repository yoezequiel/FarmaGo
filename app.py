from flask import Flask, g, session, request, abort, redirect, url_for, render_template
import sqlite3

DATABASE = 'database.db'
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Cambia esto por una clave secreta segura en un entorno real

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
                role TEXT,
                apellido TEXT,
                direccion TEXT,
                numero_telefono TEXT,
                provincia TEXT,
                localidad TEXT,
                correo_electronico TEXT,
                nombre_usuario TEXT UNIQUE,
                contraseña TEXT
            );


            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                imagen TEXT,
                descripcion TEXT,
                cantidad INTEGER,
                precio_unitario REAL,
                id_categoria INTEGER,
                FOREIGN KEY(id_categoria) REFERENCES categorias(id)
            );

            CREATE TABLE IF NOT EXISTS carritos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER,
                fecha TEXT,
                estado TEXT,
                id_producto INTEGER,
                FOREIGN KEY(id_usuario) REFERENCES usuarios(id)
            );

            CREATE TABLE IF NOT EXISTS detalles_pedido (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_pedido INTEGER,
                id_producto INTEGER,
                cantidad INTEGER,
                precio_unitario REAL,
                FOREIGN KEY(id_pedido) REFERENCES pedidos(id),
                FOREIGN KEY(id_producto) REFERENCES productos(id)
            );

            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT
            );

            CREATE TABLE IF NOT EXISTS valoraciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER,
                id_producto INTEGER,
                puntuacion INTEGER,
                comentario TEXT,
                FOREIGN KEY(id_usuario) REFERENCES usuarios(id),
                FOREIGN KEY(id_producto) REFERENCES productos(id)
            );

            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER,
                fecha TEXT,
                estado TEXT,
                total REAL,
                FOREIGN KEY(id_usuario) REFERENCES usuarios(id)
            );
            CREATE TABLE IF NOT EXISTS farmacia_productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER,
                id_producto INTEGER,
                FOREIGN KEY(id_usuario) REFERENCES usuarios(id),
                FOREIGN KEY(id_producto) REFERENCES productos(id)
                
            );
            -- Insertar algunas categorías predefinidas
            INSERT INTO categorias (nombre) VALUES ('Medicamentos');
            INSERT INTO categorias (nombre) VALUES ('Perfumes');
            INSERT INTO categorias (nombre) VALUES ('Cremas');
            INSERT INTO categorias (nombre) VALUES ('Maquillaje');
            
        ''')
        db.commit()

@app.route('/')
def index():
    return render_template('index.html')

# Función para obtener el rol del usuario desde la base de datos.
def get_user_role(nombre_usuario):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT role FROM usuarios WHERE nombre_usuario = ?', (nombre_usuario,))
        result = cursor.fetchone()
        return result[0] if result else None

# Función para autenticar al usuario y verificar su contraseña.
def authenticate_user(nombre_usuario, contraseña):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT contraseña FROM usuarios WHERE nombre_usuario = ?', (nombre_usuario,))
        result = cursor.fetchone()
        if result and (contraseña, result[0]):
            return get_user_role(nombre_usuario)
        return None


# Función para registrar un nuevo usuario en la base de datos.
def register_user(nombre_usuario, contraseña, role, nombre, apellido, direccion, numero_telefono, provincia, localidad, correo_electronico):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        # Check if the username already exists
        cursor.execute('SELECT id FROM usuarios WHERE nombre_usuario = ?', (nombre_usuario,))
        existing_user = cursor.fetchone()
        if existing_user:
            # Handle the case where the username already exists (e.g., show an error message)
            return "El nombre de usuario ya está en uso. Por favor, elige otro."

        # If the username is unique, insert the new user
        cursor.execute('INSERT INTO usuarios (nombre_usuario, contraseña, role, nombre, apellido, direccion, numero_telefono, provincia, localidad, correo_electronico) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (nombre_usuario, contraseña, role, nombre, apellido, direccion, numero_telefono, provincia, localidad, correo_electronico))
        db.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user_role = authenticate_user(username, password)

        if user_role:
            session['user_role'] = user_role
            return redirect(url_for('dashboard'))
        else:
            return "Credenciales inválidas. Por favor, inténtalo nuevamente."
    else:
        return render_template('login.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
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
        role = request.form.get('role')  # Se asume que en el formulario tienes un campo para seleccionar el rol.

        register_user(nombre_usuario, contraseña, role, nombre, apellido, direccion, numero_telefono, provincia, localidad, correo_electronico)
        return redirect(url_for('login'))
    else:
        return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    user_role = session.get('user_role')
    if user_role == 'farmacia':
        return render_template('panel.html')
    elif user_role == 'cliente':
            return redirect(url_for('listar_productos'))  # Redirigir al dashboard después de guardar los cambios

    else:
        abort(403)  # Acceso prohibido (Forbidden) para usuarios no autenticados o con roles desconocidos.


# ...

# Función para obtener la información actual de la farmacia desde la base de datos
def get_farmacia_info(id_usuario):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT nombre, direccion, provincia, localidad, numero_telefono, correo_electronico FROM usuarios WHERE id = ?', (id_usuario,))
        result = cursor.fetchone()
        return result if result else None


# ...

@app.route('/editar_farmacia', methods=['GET', 'POST'])
def editar_farmacia():
    user_role = session.get('user_role')
    if user_role == 'farmacia':
        id_usuario = session.get('user_id')
        farmacia_info = get_farmacia_info(id_usuario)
        if request.method == 'POST':
            # Obtener los datos del formulario para editar la información de la farmacia
            nombre = request.form['nombre']
            direccion = request.form['direccion']
            provincia = request.form['provincia']
            localidad = request.form['localidad']
            telefono = request.form['telefono']
            correo = request.form['correo']

            # Actualizar la información de la farmacia en la base de datos (puedes implementar esta lógica según tus necesidades)
            # ...

            return redirect(url_for('dashboard'))  # Redirigir al dashboard después de guardar los cambios
        else:
            if farmacia_info:
                farmacia_nombre, farmacia_direccion, farmacia_provincia, farmacia_localidad, farmacia_telefono, farmacia_correo = farmacia_info
            else:
                # Si no se encuentra la información de la farmacia en la base de datos, se pueden proporcionar valores predeterminados o mostrar mensajes de error
                farmacia_nombre, farmacia_direccion, farmacia_provincia, farmacia_localidad, farmacia_telefono, farmacia_correo = "", "", "", "", "", ""

            return render_template('editar_farmacia.html', farmacia_nombre=farmacia_nombre, farmacia_direccion=farmacia_direccion, farmacia_provincia=farmacia_provincia, farmacia_localidad=farmacia_localidad, farmacia_telefono=farmacia_telefono, farmacia_correo=farmacia_correo)
    else:
        abort(403)


# Función para obtener los productos de la farmacia actual
def get_farmacia_productos():
    # Verificar si el usuario tiene el rol de "farmacia" y está autenticado
    if 'user_role' in session and session['user_role'] == 'farmacia':
        # Obtener el ID del usuario (farmacia) actual desde la sesión
        user_id = session.get('user_id')

        with app.app_context():
            db = get_db()
            cursor = db.cursor()

            # Consulta SQL para obtener los productos asociados a la farmacia actual
            cursor.execute('''
                SELECT p.id, p.nombre, p.imagen, p.descripcion, p.cantidad, p.precio_unitario, c.nombre AS categoria
                FROM productos AS p
                INNER JOIN farmacia_productos AS fp ON p.id = fp.id_producto
                INNER JOIN categorias AS c ON p.id_categoria = c.id
                WHERE fp.id_usuario = ?;
            ''', (user_id,))

            productos = cursor.fetchall()

        return render_template('lista_productos.html', productos=productos)
    else:
        abort(403)  # Acceso prohibido (Forbidden) para usuarios no autenticados o con roles desconocidos


# Rutas para el CRUD de productos (solo para farmacias)
@app.route('/productos', methods=['GET'])
def listar_productos():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM productos')
        productos = cursor.fetchall()

    return render_template('listar_productos.html', productos=productos)



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

            # Insertar el producto en la tabla "productos"
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute('INSERT INTO productos (nombre, imagen, descripcion, cantidad, precio_unitario) VALUES (?, ?, ?, ?, ?)', (nombre, imagen, descripcion, cantidad, precio_unitario,))

                product_id = cursor.lastrowid
                db.commit()

                # Asociar el producto a la farmacia actual en la tabla "farmacia_productos"
                cursor.execute('INSERT INTO farmacia_productos (id_usuario, id_producto) VALUES (?, ?)', (session.get('user_id'), product_id))
                db.commit()

            return redirect(url_for('listar_productos'))
        else:
            # Obtener las categorías existentes para mostrarlas en el formulario
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
        # Obtener el producto de la base de datos
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM productos WHERE id = ?', (id_producto,))
            producto = cursor.fetchone()

            # Verificar que el producto pertenece a la farmacia actual
            cursor.execute('SELECT id_usuario FROM farmacia_productos WHERE id_producto = ?', (id_producto,))
            product_owner = cursor.fetchone()
            if not product_owner or product_owner[0] != session.get('user_id'):
                abort(403)

        if request.method == 'POST':
            # Actualizar el producto en la base de datos
            nombre = request.form['nombre']
            imagen = request.form['imagen']
            descripcion = request.form['descripcion']
            cantidad = int(request.form['cantidad'])
            precio_unitario = float(request.form['precio_unitario'])
            id_categoria = int(request.form['id_categoria'])

            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute('UPDATE productos SET nombre=?, imagen=?, descripcion=?, cantidad=?, precio_unitario=?, id_categoria=? WHERE id=?', (nombre, imagen, descripcion, cantidad, precio_unitario, id_categoria, id_producto))
                db.commit()

            return redirect(url_for('listar_productos'))
        else:
            # Obtener las categorías existentes para mostrarlas en el formulario
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute('SELECT id, nombre FROM categorias')
                categorias = cursor.fetchall()
            return render_template('editar_producto.html', producto=producto, categorias=categorias)
    else:
        abort(403)

@app.route('/productos/eliminar/<int:id_producto>', methods=['POST'])
def eliminar_producto(id_producto):
    user_role = session.get('user_role')
    if user_role == 'farmacia':
        # Verificar que el producto pertenece a la farmacia actual
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT id_usuario FROM farmacia_productos WHERE id_producto = ?', (id_producto,))
            product_owner = cursor.fetchone()
            if not product_owner or product_owner[0] != session.get('user_id'):
                abort(403)

        # Eliminar el producto de la base de datos
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('DELETE FROM productos WHERE id=?', (id_producto,))
            db.commit()

        return redirect(url_for('listar_productos'))
    else:
        abort(403)

# ...

if __name__ == '__main__':
    create_tables()
    app.run()


