from flask import abort, redirect, render_template, session, url_for


def dashboard():
    user_role = session.get("user_role")
    if user_role == "farmacia":
        return render_template("panel.html")
    elif user_role == "cliente":
        return redirect(url_for("listar_productos"))
    else:
        abort(403)
