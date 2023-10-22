from flask import abort, redirect, session, url_for
from flask import Flask

app = Flask(__name__)
from src.helpers.helpers import get_db


def eliminar_producto(id_producto):
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
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("DELETE FROM productos WHERE id=?", (id_producto,))
            cursor.execute(
                "DELETE FROM farmacia_productos WHERE id_producto=?", (id_producto,)
            )
            db.commit()
        return redirect(url_for("farmacia_inventario"))
    else:
        abort(403)
