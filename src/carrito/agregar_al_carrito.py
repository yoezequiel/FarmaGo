import datetime
from flask import abort, redirect, request, session, url_for
from flask import Flask

app = Flask(__name__)
from src.helpers.helpers import get_db


def agregar_al_carrito(id_producto):
    user_id = session.get("user_id")
    if user_id:
        cantidad = int(request.form["cantidad"])
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM productos WHERE id=?", (id_producto,))
            producto = cursor.fetchone()
            if producto:
                cursor.execute(
                    'SELECT * FROM carritos WHERE id_usuario=? AND estado="abierto"',
                    (user_id,),
                )
                carrito = cursor.fetchone()
                if not carrito:
                    cursor.execute(
                        "INSERT INTO carritos (id_usuario, fecha, estado, total) VALUES (?, ?, ?, ?)",
                        (
                            user_id,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "abierto",
                            0,
                        ),
                    )
                    db.commit()
                    carrito = cursor.execute(
                        'SELECT * FROM carritos WHERE id_usuario=? AND estado="abierto"',
                        (user_id,),
                    ).fetchone()
                    carrito_id = carrito[0]
                else:
                    carrito_id = carrito[0]
                new_total = carrito[4] + (producto[5] * cantidad)
                cursor.execute(
                    "UPDATE carritos SET total=? WHERE id=?", (new_total, carrito_id)
                )
                db.commit()
                cursor.execute(
                    "INSERT OR REPLACE INTO detalles_carrito (id_carrito, id_producto, cantidad, precio_unitario) VALUES (?, ?, ?, ?)",
                    (carrito_id, id_producto, cantidad, producto[5]),
                )
                db.commit()
                return redirect(
                    url_for("ver_detalle_producto", id_producto=id_producto)
                )
            else:
                abort(404)
    else:
        abort(403)
