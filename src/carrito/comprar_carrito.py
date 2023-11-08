from flask import redirect, render_template, session, url_for
from flask import Flask

app = Flask(__name__)
from src.helpers.helpers import crear_enlace_de_pago, get_db


def comprar_carrito():
    user_id = session.get("user_id")
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM carritos WHERE id_usuario = ?", (user_id,))
        carrito = cursor.fetchone()
        if carrito:
            cursor.execute(
                "SELECT dc.id, p.nombre, dc.precio_unitario, dc.cantidad FROM detalles_carrito dc INNER JOIN productos p ON dc.id_producto = p.id WHERE dc.id_carrito = ?",
                (carrito[0],),
            )
            detalles_carrito = cursor.fetchall()
            if detalles_carrito:
                total = sum(detalle[2] * detalle[3] for detalle in detalles_carrito)
                descripcion_productos = "\n".join(
                    f"{detalle[1]} (Precio unitario: ${detalle[2]:.2f}, Cantidad: {detalle[3]}) | "
                    for detalle in detalles_carrito
                )
                link_pago = crear_enlace_de_pago(descripcion_productos, total)
                db.commit()
                return render_template("carrito_pago.html", link_pago=link_pago)
    return redirect(url_for("ver_carrito"))
