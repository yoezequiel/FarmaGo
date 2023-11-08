from flask import redirect, session, url_for


def logout():
    session.clear()
    return redirect(url_for("login"))
