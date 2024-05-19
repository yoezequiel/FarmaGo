from flask import render_template
from config import SECRET_KEY
from src.helpers.helpers import create_tables

from flask import Flask

app = Flask(__name__)

app.secret_key = SECRET_KEY


@app.route("/")
def index():
    return render_template("index.html")


from src.perfil.perfil import perfil
from src.inventario.inventario import farmacia_inventario
from src.productos_client.listar_productos import listar_productos
from src.productos_client.ver_detalle_producto import ver_detalle_producto
from src.productos_client.productos_por_categoria import productos_por_categoria
from src.productos_client.productos_por_farmacia import productos_por_farmacia
from src.farmacias.farmacias import todas_farmacias
from src.register.register_farmacia import register_farmacia
from src.register.register_cliente import register_cliente
from src.dashboard.dashboard import dashboard
from src.login.login import login
from src.perfil.editar_perfil import editar_perfil
from src.eliminar_cuenta.eliminar_cuenta import eliminar_cuenta
from src.productos_farmacia.agregar_producto import agregar_producto
from src.productos_farmacia.editar_producto import editar_producto
from src.productos_farmacia.eliminar_producto import eliminar_producto
from src.carrito.agregar_al_carrito import agregar_al_carrito
from src.carrito.eliminar_del_carrito import eliminar_del_carrito
from src.carrito.ver_carrito import ver_carrito
from src.carrito.comprar_carrito import comprar_carrito
from src.pagos.pago_exitoso import pago_exitoso
from src.ventas.ventas import ventas
from src.logout.logout import logout
from src.errors.not_found import page_not_found
from src.errors.forbidden import forbidden_error

app.route("/perfil")(perfil)

app.route("/farmacia/inventario", methods=["GET", "POST"])(farmacia_inventario)

app.route("/productos", methods=["GET"])(listar_productos)

app.route("/productos/<int:id_producto>", methods=["GET"])(ver_detalle_producto)

app.route("/productos/categoria/<int:id_categoria>", methods=["GET"])(
    productos_por_categoria
)

app.route("/productos/farmacia/<int:id_usuario>", methods=["GET"])(
    productos_por_farmacia
)

app.route("/todas_farmacias", methods=["GET", "POST"])(todas_farmacias)

app.route("/login", methods=["GET", "POST"])(login)

app.route("/register/cliente", methods=["GET", "POST"])(register_cliente)

app.route("/register/farmacia", methods=["GET", "POST"])(register_farmacia)

app.route("/dashboard")(dashboard)

app.route("/editar_perfil", methods=["GET", "POST"])(editar_perfil)

app.route("/eliminar_cuenta", methods=["POST"])(eliminar_cuenta)

app.route("/productos/agregar", methods=["GET", "POST"])(agregar_producto)

app.route("/productos/editar/<int:id_producto>", methods=["GET", "POST"])(
    editar_producto
)

app.route("/productos/eliminar/<int:id_producto>", methods=["POST"])(eliminar_producto)

app.route("/agregar_al_carrito/<int:id_producto>", methods=["POST"])(agregar_al_carrito)
app.route("/eliminar_del_carrito/<int:id_detalle_carrito>", methods=["POST"])(
    eliminar_del_carrito
)

app.route("/carrito", methods=["GET"])(ver_carrito)

app.route("/carrito/comprar", methods=["POST"])(comprar_carrito)

app.route("/pago_exitoso", methods=["GET"])(pago_exitoso)

app.route("/ventas")(ventas)

app.route("/logout")(logout)

app.errorhandler(403)(forbidden_error)

app.errorhandler(404)(page_not_found)

import os

if __name__ == "__main__":
    create_tables()
    app.run(host="0.0.0.0", port=os.environ.get("PORT", 5000))
