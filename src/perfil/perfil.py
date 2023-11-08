from flask import abort, render_template, session


def perfil():
    user_role = session.get("user_role")
    if user_role == "farmacia" or user_role == "cliente":
        return render_template("perfil.html")
    else:
        abort(403)
