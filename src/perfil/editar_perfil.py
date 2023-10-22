from flask import abort, redirect, render_template, request, session, url_for
from flask import Flask

app = Flask(__name__)
from src.helpers.helpers import get_db, get_user_info


def editar_perfil():
    user_role = session.get("user_role")
    if user_role in ("farmacia", "cliente"):
        user_id = session.get("user_id")
        user_info = get_user_info(user_id)
        if request.method == "POST":
            nombre = request.form["nombre"]
            apellido = request.form["apellido"]
            direccion = request.form["direccion"]
            provincia = request.form["provincia"]
            localidad = request.form["localidad"]
            numero_telefono = request.form["numero_telefono"]
            correo_electronico = request.form["correo_electronico"]
            nombre_usuario = request.form["nombre_usuario"]
            contraseña = request.form["contraseña"]
            logo_url = request.form["logo_url"]
            with app.app_context():
                db = get_db()
                cursor = db.cursor()
                cursor.execute(
                    "UPDATE usuarios SET nombre=?, apellido=?, direccion=?, provincia=?, localidad=?, numero_telefono=?, correo_electronico=?, contraseña=?, nombre_usuario=?, logo_url=? WHERE id=?",
                    (
                        nombre,
                        apellido,
                        direccion,
                        provincia,
                        localidad,
                        numero_telefono,
                        correo_electronico,
                        contraseña,
                        nombre_usuario,
                        logo_url,
                        user_id,
                    ),
                )
                db.commit()
            return redirect(url_for("perfil"))
        else:
            if user_info:
                (
                    nombre,
                    apellido,
                    direccion,
                    provincia,
                    localidad,
                    numero_telefono,
                    correo_electronico,
                    nombre_usuario,
                    contraseña,
                    logo_url,
                ) = user_info
            else:
                (
                    nombre,
                    apellido,
                    direccion,
                    provincia,
                    localidad,
                    numero_telefono,
                    correo_electronico,
                    nombre_usuario,
                    contraseña,
                    logo_url,
                ) = ("", "", "", "", "", "", "", "", "", "")
            return render_template(
                "editar_perfil.html",
                nombre=nombre,
                apellido=apellido,
                direccion=direccion,
                provincia=provincia,
                localidad=localidad,
                numero_telefono=numero_telefono,
                correo_electronico=correo_electronico,
                nombre_usuario=nombre_usuario,
                contraseña=contraseña,
                logo_url=logo_url,
            )
    else:
        abort(403)
