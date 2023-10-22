from math import ceil
from flask import abort, redirect, render_template, request, session, url_for
from flask import Flask

app = Flask(__name__)
from src.helpers.helpers import get_db


def listar_productos():
    user_role = session.get("user_role")
    if user_role == "farmacia" or user_role == "cliente" or user_role == None:
        pagina = request.args.get("pagina", default=1, type=int)
        productos_por_pagina = 9
        categoria_id = request.args.get("categoria_id", default=None, type=int)
        search_query = request.args.get("search_query")
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT id, nombre FROM categorias")
            categorias = cursor.fetchall()
            if categoria_id is not None:
                cursor.execute(
                    "SELECT COUNT(*) FROM productos WHERE id_categoria = ?",
                    (categoria_id,),
                )
                total_productos = cursor.fetchone()[0]
                total_paginas = ceil(total_productos / productos_por_pagina)
                if pagina < 1:
                    pagina = 1
                elif pagina > total_paginas:
                    pagina = total_paginas
                inicio = (pagina - 1) * productos_por_pagina
                cursor.execute(
                    "SELECT * FROM productos WHERE id_categoria = ? LIMIT ? OFFSET ?",
                    (categoria_id, productos_por_pagina, inicio),
                )
                productos = cursor.fetchall()
            elif search_query:
                with app.app_context():
                    db = get_db()
                    cursor = db.cursor()
                    cursor.execute(
                        "SELECT COUNT(*) FROM productos WHERE nombre LIKE ?",
                        ("%" + search_query + "%",),
                    )
                    total_productos = cursor.fetchone()[0]
                    total_paginas = ceil(total_productos / productos_por_pagina)
                    if pagina < 1:
                        pagina = 1
                    elif pagina > total_paginas:
                        pagina = total_paginas
                    inicio = (pagina - 1) * productos_por_pagina
                    cursor.execute(
                        "SELECT * FROM productos WHERE nombre LIKE ? LIMIT ? OFFSET ?",
                        ("%" + search_query + "%", productos_por_pagina, inicio),
                    )
                    productos = cursor.fetchall()
                return render_template(
                    "listar_productos.html",
                    productos=productos,
                    pagina=pagina,
                    total_paginas=total_paginas,
                    user_role=user_role,
                    search_query=search_query,
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM productos")
                total_productos = cursor.fetchone()[0]
                total_paginas = ceil(total_productos / productos_por_pagina)
                if pagina < 1:
                    pagina = 1
                elif pagina > total_paginas:
                    pagina = total_paginas
                inicio = (pagina - 1) * productos_por_pagina
                cursor.execute(
                    "SELECT * FROM productos LIMIT ? OFFSET ?",
                    (productos_por_pagina, inicio),
                )
                productos = cursor.fetchall()
        return render_template(
            "listar_productos.html",
            productos=productos,
            pagina=pagina,
            total_paginas=total_paginas,
            user_role=user_role,
            categorias=categorias,
            categoria_id=categoria_id,
        )
    else:
        abort(403)
