from flask import abort, redirect, session, url_for
from flask import Flask

app = Flask(__name__)
from src.helpers.helpers import get_db


def eliminar_cuenta():
    user_id = session.get("user_id")
    if user_id:
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id=?", (user_id,))
            db.commit()
        session.clear()
        return redirect(url_for("login"))
    else:
        abort(403)
