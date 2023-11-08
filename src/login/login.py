from flask import redirect, render_template, request, session, url_for

from src.helpers.helpers import authenticate_user


def login():
    if request.method == "POST":
        correo_electronico = request.form.get("correo_electronico")
        password = request.form.get("password")
        user_id, user_role = authenticate_user(correo_electronico, password)
        if user_id and user_role:
            session["user_id"] = user_id
            session["user_role"] = user_role
            return redirect(url_for("dashboard"))
        else:
            error = "Credenciales inválidas. Por favor, inténtalo nuevamente."
            return render_template("login.html", error=error)
    else:
        return render_template("login.html")
