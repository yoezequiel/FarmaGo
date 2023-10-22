from flask import abort, redirect, render_template, request, session, url_for
from flask import Flask

app = Flask(__name__)
from src.helpers.helpers import get_db


def editar_producto(id_producto):
    user_role = session.get("user_role")
    if user_role == "farmacia":
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "SELECT id_usuario FROM farmacia_productos WHERE id_producto = ?",
                (id_producto,),
            )
            product_owner = cursor.fetchone()
            if not product_owner or product_owner[0] != session.get("user_id"):
                abort(403)
        if request.method == "POST":
            nombre = request.form["nombre"]
            imagen = request.form["imagen"]
            descripcion = request.form["descripcion"]
            precio_unitario = float(request.form["precio_unitario"])
            cantidad = int(request.form["cantidad"])
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute(
                    "UPDATE productos SET nombre=?, imagen=?,descripcion=?, precio_unitario=?, cantidad=? WHERE id=?",
                    (
                        nombre,
                        imagen,
                        descripcion,
                        precio_unitario,
                        cantidad,
                        id_producto,
                    ),
                )
                db.commit()
            return redirect(url_for("dashboard"))
        else:
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute(
                    "SELECT nombre, imagen,descripcion, precio_unitario, cantidad FROM productos WHERE id=?",
                    (id_producto,),
                )
                producto = cursor.fetchone()
            if producto:
                return render_template("editar_producto.html", producto=producto)
            else:
                abort(404)
    else:
        abort(403)
