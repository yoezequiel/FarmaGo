from flask import abort, render_template
from flask import Flask

app = Flask(__name__)
from src.helpers.helpers import get_db, get_farmacia_info


def ver_detalle_producto(id_producto):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM productos WHERE id=?", (id_producto,))
        producto = cursor.fetchone()
        farmacia_info = get_farmacia_info(producto[7])
        id_farmacia = producto[7]
        cursor.execute("SELECT nombre FROM categorias WHERE id=?", (producto[6],))
        categoria_nombre = cursor.fetchone()[0]
    if producto and farmacia_info:
        return render_template(
            "detalle_producto.html",
            producto=producto,
            farmacia_info=farmacia_info,
            id_farmacia=id_farmacia,
            categoria_nombre=categoria_nombre,
        )
    else:
        abort(404)
