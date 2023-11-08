from flask import abort, redirect, session, url_for
from flask import Flask

app = Flask(__name__)
from src.helpers.helpers import get_db


def eliminar_del_carrito(id_detalle_carrito):
    user_id = session.get("user_id")
    if user_id:
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                'DELETE FROM detalles_carrito WHERE id = ? AND id_carrito IN (SELECT id FROM carritos WHERE id_usuario = ? AND estado = "abierto")',
                (id_detalle_carrito, user_id),
            )
            db.commit()
            return redirect(url_for("ver_carrito"))
    else:
        abort(403)
