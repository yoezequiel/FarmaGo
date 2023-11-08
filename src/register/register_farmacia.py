from flask import redirect, render_template, request, url_for

from src.helpers.helpers import register_user


def register_farmacia():
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        direccion = request.form["direccion"]
        numero_telefono = request.form["numero_telefono"]
        provincia = request.form["provincia"]
        localidad = request.form["localidad"]
        correo_electronico = request.form["correo_electronico"]
        nombre_usuario = request.form["nombre_usuario"]
        contraseña = request.form["contraseña"]
        role = "farmacia"
        logo_url = request.form.get("logo_url")
        error_message = register_user(
            nombre_usuario,
            contraseña,
            role,
            nombre,
            apellido,
            direccion,
            numero_telefono,
            provincia,
            localidad,
            correo_electronico,
            logo_url=logo_url,
        )
        if error_message:
            return render_template("register.html", error=error_message)
        return redirect(url_for("login"))
    else:
        return render_template("register.html")
