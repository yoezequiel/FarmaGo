from flask import abort, redirect, render_template, session, url_for
from flask import Flask

app = Flask(__name__)

from src.helpers.helpers import get_db


def ver_carrito():
    user_id = session.get("user_id")
    if user_id:
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                'SELECT * FROM carritos WHERE id_usuario=? AND estado="abierto"',
                (user_id,),
            )
            carrito = cursor.fetchone()
        if carrito:
            cursor.execute(
                'SELECT dc.id, p.id, p.nombre, p.precio_unitario, dc.cantidad FROM detalles_carrito dc JOIN productos p ON dc.id_producto = p.id JOIN carritos c ON dc.id_carrito = c.id WHERE c.id_usuario = ? AND c.estado = "abierto"',
                (user_id,),
            )
            carrito = cursor.fetchall()
            total_carrito = 0
            total_carrito = sum(detalle[3] * detalle[4] for detalle in carrito)
            return render_template(
                "carrito.html", carrito=carrito, total_carrito=total_carrito
            )
        else:
            return redirect(url_for("listar_productos"))
    else:
        abort(403)
