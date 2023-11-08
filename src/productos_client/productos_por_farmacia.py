from flask import render_template
from flask import Flask

app = Flask(__name__)
from src.helpers.helpers import get_db, get_farmacia_info


def productos_por_farmacia(id_usuario):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM productos WHERE id_farmacia=?", (id_usuario,))
        productos = cursor.fetchall()
        farmacia_info = get_farmacia_info(id_usuario)
    return render_template(
        "productos_farmacia.html", productos=productos, farmacia_info=farmacia_info
    )
