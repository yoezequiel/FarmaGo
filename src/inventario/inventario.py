from flask import abort, render_template, request, session
from flask import Flask

app = Flask(__name__)
from src.helpers.helpers import get_db


def farmacia_inventario():
    user_role = session.get("user_role")
    if user_role == "farmacia":
        if request.method == "POST":
            inventario = request.form.getlist("inventario")
            farmacia_id = session.get("user_id")
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute(
                    "DELETE FROM inventario WHERE id_farmacia = ?", (farmacia_id,)
                )
                for id_producto, cantidad in enumerate(inventario, start=1):
                    if cantidad.isdigit() and int(cantidad) >= 0:
                        cursor.execute(
                            "INSERT INTO inventario (id_farmacia, id_producto, cantidad_disponible) VALUES (?, ?, ?)",
                            (farmacia_id, id_producto, cantidad),
                        )
                db.commit()
        else:
            farmacia_id = session.get("user_id")
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute(
                    "SELECT p.id, p.nombre, COALESCE(i.cantidad_disponible, 0) as cantidad_disponible, p.cantidad, p.precio_unitario FROM productos p LEFT JOIN inventario i ON p.id = i.id_producto AND i.id_farmacia = ? WHERE p.id_farmacia = ?",
                    (farmacia_id, farmacia_id),
                )
                inventario = cursor.fetchall()
        return render_template("farmacia_inventario.html", inventario=inventario)
    else:
        abort(403)
