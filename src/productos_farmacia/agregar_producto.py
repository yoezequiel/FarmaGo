from flask import abort, redirect, render_template, request, session, url_for
from flask import Flask

app = Flask(__name__)
from src.helpers.helpers import get_db


def agregar_producto():
    user_role = session.get("user_role")
    if user_role == "farmacia":
        if request.method == "POST":
            nombre = request.form["nombre"]
            imagen = request.form["imagen"]
            descripcion = request.form["descripcion"]
            cantidad = int(request.form["cantidad"])
            precio_unitario = float(request.form["precio_unitario"])
            id_categoria = int(request.form["categoria"])
            id_farmacia = session.get("user_id")
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute(
                    "INSERT INTO productos (nombre, imagen, descripcion, cantidad, precio_unitario, id_categoria, id_farmacia) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        nombre,
                        imagen,
                        descripcion,
                        cantidad,
                        precio_unitario,
                        id_categoria,
                        id_farmacia,
                    ),
                )
                product_id = cursor.lastrowid
                db.commit()
                cursor.execute(
                    "INSERT INTO farmacia_productos (id_usuario, id_producto) VALUES (?, ?)",
                    (id_farmacia, product_id),
                )
                db.commit()
            return redirect(url_for("farmacia_inventario"))
        else:
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute("SELECT id, nombre FROM categorias")
                categorias = cursor.fetchall()
            return render_template("agregar_producto.html", categorias=categorias)
    else:
        abort(403)
