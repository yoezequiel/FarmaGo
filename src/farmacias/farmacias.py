from flask import render_template, request
from flask import Flask

app = Flask(__name__)
from src.helpers.helpers import get_db


def todas_farmacias():
    if request.method == "POST":
        search_query = request.form.get("search_query", "").strip()
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            if search_query:
                cursor.execute(
                    'SELECT * FROM usuarios WHERE role="farmacia" AND nombre LIKE ?',
                    ("%" + search_query + "%",),
                )
            else:
                cursor.execute('SELECT * FROM usuarios WHERE role="farmacia"')
            farmacias = cursor.fetchall()
    else:
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE role="farmacia"')
            farmacias = cursor.fetchall()
    return render_template("todas_farmacias.html", farmacias=farmacias)
