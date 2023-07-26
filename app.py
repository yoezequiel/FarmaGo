# Aquí van las importaciones necesarias
import sqlite3
from flask import Flask, g, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import session
app = Flask(__name__)
app.secret_key = "yesy"

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Definición de la clase Usuario
class Usuario(UserMixin):
    def __init__(self, id):
        self.id = id

class Farmacia(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return Usuario(user_id)

# Función para obtener la conexión a la base de datos
def get_db_connection():
    conn = sqlite3.connect('FarmaGo.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
        # Crear la tabla 'usuarios'
    conn.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, apellido TEXT, direccion TEXT, numero_telefono TEXT, provincia TEXT, localidad TEXT, correo_electronico TEXT, nombre_usuario TEXT UNIQUE, contraseña TEXT)')
        # Crear la tabla 'farmacias'
    conn.execute('CREATE TABLE IF NOT EXISTS farmacias (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, apellido TEXT, DNI TEXT, direccion TEXT, numero_telefono TEXT, provincia TEXT, localidad TEXT, nombre_usuario TEXT UNIQUE, correo_electronico TEXT, contraseña TEXT)')
        # Crear las demás tablas con claves foráneas después de las tablas principales
    conn.execute('CREATE TABLE IF NOT EXISTS productos (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, imagen TEXT, descripcion TEXT, cantidad INTEGER, id_farmacia INTEGER, precio_unitario REAL,id_categoria INTEGER, FOREIGN KEY(id_farmacia) REFERENCES farmacias(id), FOREIGN KEY(id_categoria) REFERENCES categorias(id))')
    conn.execute('CREATE TABLE IF NOT EXISTS carritos (id INTEGER PRIMARY KEY AUTOINCREMENT, id_usuario INTEGER, fecha TEXT, estado TEXT, id_producto, FOREIGN KEY(id_usuario) REFERENCES usuarios(id))')
    conn.execute('CREATE TABLE IF NOT EXISTS detalles_pedido (id INTEGER PRIMARY KEY AUTOINCREMENT, id_pedido INTEGER, id_producto INTEGER, cantidad INTEGER, precio_unitario REAL, FOREIGN KEY(id_pedido) REFERENCES pedidos(id), FOREIGN KEY(id_producto) REFERENCES productos(id))')
    conn.execute('CREATE TABLE IF NOT EXISTS categorias (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS valoraciones (id INTEGER PRIMARY KEY AUTOINCREMENT, id_usuario INTEGER, id_producto INTEGER, puntuacion INTEGER, comentario TEXT, FOREIGN KEY(id_usuario) REFERENCES usuarios(id), FOREIGN KEY(id_producto) REFERENCES productos(id))')
    conn.execute('CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY AUTOINCREMENT, id_usuario INTEGER, fecha TEXT, estado TEXT, total REAL, FOREIGN KEY(id_usuario) REFERENCES usuarios(id))')
    conn.commit()
    conn.close()
        
# Llamada a la función create_tables() para crear la base de datos si no existe
create_tables()

# Ruta para la página de inicio
@app.route('/')
def index():
    return render_template('index.html')


# Ruta para el registro de usuarios
@app.route('/registro_usuario', methods=['GET', 'POST'])
def registro_usuario():
    if request.method == 'POST':
        # Obtener los datos del formulario de registro
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        direccion = request.form['direccion']
        numero_telefono = request.form['numero_telefono']
        provincia = request.form['provincia']
        localidad = request.form['localidad']
        correo_electronico = request.form['correo_electronico']
        nombre_usuario = request.form['nombre_usuario']
        contraseña = request.form['contraseña']
        
        conn = get_db_connection()
        
        user = conn.execute('SELECT id FROM usuarios WHERE nombre_usuario = ?', (nombre_usuario,)).fetchone()
        if user is not None:
            conn.close()
            return render_template('registro_usuario.html', error='El nombre de usuario ya está en uso. Por favor, elije otro.')
        else:
            conn.execute('INSERT INTO usuarios (nombre, apellido, direccion, numero_telefono, provincia, localidad, correo_electronico, nombre_usuario, contraseña) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                        (nombre, apellido, direccion, numero_telefono, provincia, localidad, correo_electronico, nombre_usuario, contraseña))
            conn.commit()
            # Fetch the newly created user to get their id
            new_user = conn.execute('SELECT id FROM usuarios WHERE nombre_usuario = ?', (nombre_usuario,)).fetchone()
            session['user_id'] = new_user['id']
            return render_template('iniciar_sesion.html')
        conn.close()
        
        
    
    return render_template('registro_usuario.html')



# Ruta para el registro de farmacias
@app.route('/registro_farmacia', methods=['GET', 'POST'])
def registro_farmacia():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # Obtener los datos del formulario de registro
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        DNI = request.form['DNI']
        direccion = request.form['direccion']
        numero_telefono = request.form['numero_telefono']
        provincia = request.form['provincia']
        localidad = request.form['localidad']
        correo_electronico = request.form['correo_electronico']
        nombre_usuario = request.form['nombre_usuario']
        contraseña = request.form['contraseña']

        # Verificar que el nombre de usuario no esté duplicado
        cursor.execute('SELECT id FROM farmacias WHERE nombre_usuario = ?', (nombre_usuario,))
        existing_pharmacy = cursor.fetchone()

        if existing_pharmacy:
            conn.close()
            return render_template('registro_farmacia.html', error='El nombre de usuario ya está en uso. Por favor, elige otro.')
        else:
            # Crear una nueva farmacia en la base de datos
            cursor.execute('INSERT INTO farmacias (nombre, apellido, DNI, direccion, numero_telefono, provincia, localidad, correo_electronico, nombre_usuario, contraseña) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                    (nombre, apellido, DNI, direccion, numero_telefono, provincia, localidad, correo_electronico, nombre_usuario, contraseña))
            conn.commit()
            conn.close()

            # Redirect to the login page after successful registration
            return redirect(url_for('iniciar_sesion'))
    
    conn.close()
    return render_template('registro_farmacia.html')



# Ruta para iniciar sesión
@app.route('/iniciar_sesion', methods=['GET', 'POST'])
def iniciar_sesion():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        contraseña = request.form['contraseña']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Consultar la tabla de usuarios
        user = cursor.execute('SELECT id, contraseña FROM usuarios WHERE nombre_usuario = ?', (nombre_usuario,)).fetchone()

        # Consultar la tabla de farmacias
        pharmacy = cursor.execute('SELECT id, contraseña FROM farmacias WHERE nombre_usuario = ?', (nombre_usuario,)).fetchone()

        conn.close()

        if user and user['contraseña'] == contraseña:
            user_obj = Usuario(user['id'])
            login_user(user_obj)
            return redirect(url_for('perfil_usuario'))
        elif pharmacy and pharmacy['contraseña'] == contraseña:
            farmacia_obj = Farmacia(pharmacy['id'])
            login_user(farmacia_obj)
            return redirect(url_for('perfil_farmacia'))
        else:
            flash('Credenciales inválidas. Por favor, intenta de nuevo.', 'error')

    return render_template('iniciar_sesion.html')

@app.route('/perfil_farmacia')
@login_required
def perfil_farmacia():
    # Get the current user's farmacia details from the database based on their ID
    conn = get_db_connection()
    cursor = conn.cursor()

    farmacia_id = current_user.id

    cursor.execute('SELECT * FROM farmacias WHERE id = ?', (farmacia_id,))
    farmacia = cursor.fetchone()

    conn.close()

    if farmacia is not None:
        return render_template('perfil_farmacia.html', farmacia=farmacia)
    else:
        flash('Farmacia no encontrada.', 'error')
        return redirect(url_for('iniciar_sesion'))  # Redirect to a relevant page if farmacia is not found


# Ruta para que las farmacias agreguen productos
@app.route('/agregar_producto', methods=['GET', 'POST'])
@login_required  # Esta ruta solo será accesible para usuarios autenticados (farmacias)
def agregar_producto():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # Obtener los datos del formulario de agregación de productos
        nombre_producto = request.form['nombre_producto']
        imagen_producto = request.form['imagen_producto']
        descripcion_producto = request.form['descripcion_producto']
        cantidad_producto = int(request.form['cantidad_producto'])
        precio_producto = float(request.form['precio_producto'])

        # Obtener el ID de la farmacia actualmente autenticada
        id_farmacia = current_user.id

        # Insertar el nuevo producto en la tabla 'productos'
        cursor.execute('INSERT INTO productos (nombre, imagen, descripcion, cantidad, precio_unitario, id_farmacia) VALUES (?, ?, ?, ?, ?, ?)',
                    (nombre_producto, imagen_producto, descripcion_producto, cantidad_producto, precio_producto, id_farmacia))

        # Commit the changes to the database
        conn.commit()

        # Close the database connection
        conn.close()

        flash('Producto agregado exitosamente.', 'success')

    # If the request method is 'GET', simply render the template for adding products
    return render_template('agregar_producto.html')


# Ruta para la visualización de productos de diferentes farmacias
@app.route('/productos')
def productos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM productos')
    productos = cursor.fetchall()

    # Close the database connection
    conn.close()

    return render_template('productos.html', productos=productos)


# Ruta para visualizar productos de una categoría específica
@app.route('/categorias/<int:categoria_id>/productos')
def productos_categoria(categoria_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener información de la categoría específica
    cursor.execute('SELECT * FROM categorias WHERE id = ?', (categoria_id,))
    categoria = cursor.fetchone()

    if categoria is None:
        flash('Categoría no encontrada.', 'error')
        conn.close()
        return redirect(url_for('productos'))

    # Obtener los productos de la categoría específica
    cursor.execute('SELECT * FROM productos WHERE id_categoria = ?', (categoria_id,))
    productos_categoria = cursor.fetchall()

    conn.close()
    return render_template('productos_categoria.html', categoria=categoria, productos_categoria=productos_categoria)



# Ruta para agregar productos al carrito
@app.route('/agregar_al_carrito/<int:producto_id>')
@login_required
def agregar_al_carrito(producto_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Obtener el producto seleccionado por su ID
    cursor.execute('SELECT * FROM productos WHERE id = ?', (producto_id,))
    producto = cursor.fetchone()

    if producto is not None:
        # Agregar el producto al carrito del usuario
        # Aquí puedes usar una tabla "carritos" para almacenar los productos del carrito por usuario
        # Por ejemplo, puedes tener una tabla con campos como "id_usuario", "id_producto", "cantidad", etc.
        # Puedes agregar el producto al carrito aquí y redirigir al usuario a la página del carrito o productos.

        # Ejemplo de cómo agregar el producto a la tabla carritos (simplificado):
        user_id = current_user.id  # ID del usuario autenticado actual
        cantidad = 1  # Puedes permitir que el usuario seleccione la cantidad desde la interfaz

        # Verificar si el producto ya está en el carrito del usuario
        cursor.execute('SELECT * FROM carritos WHERE id_usuario = ? AND id_producto = ?', (user_id, producto_id))
        item_carrito = cursor.fetchone()

        if item_carrito is not None:
            # Si el producto ya está en el carrito, aumenta la cantidad
            nueva_cantidad = item_carrito['cantidad'] + cantidad
            cursor.execute('UPDATE carritos SET cantidad = ? WHERE id = ?', (nueva_cantidad, item_carrito['id']))
        else:
            # Si el producto no está en el carrito, agrégalo
            cursor.execute('INSERT INTO carritos (id_usuario, id_producto, cantidad) VALUES (?, ?, ?)', (user_id, producto_id, cantidad))

        
        flash('Producto agregado al carrito correctamente.', 'success')
    else:
        flash('Producto no encontrado.', 'error')
    conn.commit()
    
    conn.close()
    return redirect(url_for('productos'))


# Ruta para ver el contenido del carrito del usuario
@app.route('/carrito')
@login_required
def carrito():
    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = current_user.id  # ID del usuario autenticado actual

    # Obtener los productos del carrito del usuario
    cursor.execute('SELECT p.* FROM carritos c INNER JOIN productos p ON c.id_producto = p.id WHERE c.id_usuario = ?', (user_id,))
    productos_carrito = cursor.fetchall()

    return render_template('carrito.html', productos_carrito=productos_carrito)

# Ruta para realizar el pedido desde el carrito
@app.route('/realizar_pedido')
@login_required
def realizar_pedido():
    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = current_user.id  # ID del usuario autenticado actual

    # Obtener los productos del carrito del usuario
    cursor.execute('SELECT p.*, c.cantidad FROM carritos c INNER JOIN productos p ON c.id_producto = p.id WHERE c.id_usuario = ?', (user_id,))
    productos_carrito = cursor.fetchall()

    # Verificar que el carrito no esté vacío
    if not productos_carrito:
        flash('El carrito está vacío. Agrega productos antes de realizar un pedido.', 'error')
        return redirect(url_for('carrito'))

    # Lógica para crear el pedido y sincronizar con la tabla centralizada
    # Por ejemplo, puedes tener una tabla "pedidos" para almacenar los pedidos de los usuarios
    # y otra tabla "detalles_pedido" para almacenar los detalles de cada pedido

    # Ejemplo de cómo crear un pedido y sus detalles (simplificado):
    total_pedido = sum(producto['cantidad'] * producto['precio_unitario'] for producto in productos_carrito)

    # Crear el pedido en la tabla pedidos
    cursor.execute('INSERT INTO pedidos (id_usuario, fecha, estado, total) VALUES (?, ?, ?, ?)', (user_id, '2023-07-25', 'pendiente', total_pedido))
    pedido_id = cursor.lastrowid

    # Agregar los detalles del pedido en la tabla detalles_pedido
    for producto in productos_carrito:
        cursor.execute('INSERT INTO detalles_pedido (id_pedido, id_producto, cantidad, precio_unitario) VALUES (?, ?, ?, ?)',
                (pedido_id, producto['id'], producto['cantidad'], producto['precio_unitario']))

    # Limpiar el carrito eliminando los productos agregados
    cursor.execute('DELETE FROM carritos WHERE id_usuario = ?', (user_id,))

    
    flash('Pedido realizado con éxito.', 'success')
    conn.commit()
    
    conn.close()
    return redirect(url_for('carrito'))

# Ruta para la visualización de productos de una farmacia específica
@app.route('/farmacia/<int:farmacia_id>/productos')
def productos_farmacia(farmacia_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener información de la farmacia específica
    cursor.execute('SELECT * FROM farmacias WHERE id = ?', (farmacia_id,))
    farmacia = cursor.fetchone()

    if farmacia is None:
        flash('Farmacia no encontrada.', 'error')
        return redirect(url_for('productos'))

    # Obtener los productos de la farmacia específica
    cursor.execute('SELECT * FROM productos WHERE id_farmacia = ?', (farmacia_id,))
    productos_farmacia = cursor.fetchall()
    conn.commit()
    
    conn.close()
    return render_template('productos_farmacia.html', farmacia=farmacia, productos_farmacia=productos_farmacia)


if __name__ == '__main__':
    app.run()
