from flask import abort, render_template, session
from flask import Flask

app = Flask(__name__)
from src.helpers.helpers import get_db


def ventas():
    user_role = session.get("user_role")
    if user_role == "farmacia":
        farmacia_id = session.get("user_id")
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "SELECT v.id, v.fecha, v.total, u.nombre AS comprador_nombre, u.correo_electronico AS comprador_correo FROM ventas v INNER JOIN usuarios u ON v.id_comprador = u.id WHERE v.id_vendedor = ?",
                (farmacia_id,),
            )
            ventas = cursor.fetchall()
        return render_template("ventas.html", ventas=ventas)
    else:
        abort(403)
