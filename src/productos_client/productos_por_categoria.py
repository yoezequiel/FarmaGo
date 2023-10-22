from flask import render_template
from flask import Flask

app = Flask(__name__)
from src.helpers.helpers import get_db


def productos_por_categoria(id_categoria):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM productos WHERE id_categoria = ?", (id_categoria,)
        )
        productos = cursor.fetchall()
        cursor.execute("SELECT nombre FROM categorias WHERE id = ?", (id_categoria,))
        categoria_nombre = cursor.fetchone()[0]
    return render_template(
        "productos_por_categoria.html",
        productos=productos,
        categoria_nombre=categoria_nombre,
    )
