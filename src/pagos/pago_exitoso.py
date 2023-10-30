import datetime
from flask import render_template, request, session
from flask import Flask

app = Flask(__name__)
from src.helpers.helpers import get_db


def pago_exitoso():
    payment_status = request.args.get("status")
    collection_status = request.args.get("collection_status")
    preference_id = request.args.get("preference_id")
    site_id = request.args.get("site_id")
    external_reference = request.args.get("external_reference")
    merchant_order_id = request.args.get("merchant_order_id")
    collection_id = request.args.get("collection_id")
    payment_id = request.args.get("payment_id")
    payment_type = request.args.get("payment_type")
    processing_mode = request.args.get("processing_mode")
    if payment_status == "approved" and collection_status == "approved":
        user_id = session.get("user_id")
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM carritos WHERE id_usuario = ?", (user_id,))
            carrito = cursor.fetchone()
            if carrito:
                cursor.execute(
                    "SELECT * FROM detalles_carrito WHERE id_carrito = ?", (carrito[0],)
                )
                detalles_carrito = cursor.fetchall()
                if detalles_carrito:
                    total = sum(detalle[3] * detalle[4] for detalle in detalles_carrito)
                    cursor.execute(
                        "SELECT id_usuario FROM farmacia_productos WHERE id_producto = ?",
                        (detalles_carrito[0][2],),
                    )
                    id_vendedor = cursor.fetchone()[0]
                    cursor.execute(
                        "INSERT INTO ventas (id_vendedor, id_comprador, fecha, total) VALUES (?, ?, ?, ?)",
                        (
                            id_vendedor,
                            user_id,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            total,
                        ),
                    )
                    venta_id = cursor.lastrowid
                    for detalle in detalles_carrito:
                        cursor.execute(
                            "INSERT INTO detalles_venta (id_venta, id_producto, cantidad, precio_unitario) VALUES (?, ?, ?, ?)",
                            (venta_id, detalle[2], detalle[3], detalle[4]),
                        )
                        cursor.execute(
                            "UPDATE productos SET cantidad = cantidad - ? WHERE id = ?",
                            (detalle[3], detalle[2]),
                        )
                    cursor.execute(
                        "DELETE FROM detalles_carrito WHERE id_carrito = ?",
                        (carrito[0],),
                    )
                    cursor.execute("DELETE FROM carritos WHERE id = ?", (carrito[0],))
                    db.commit()
                    success = "Pago exitoso. Gracias por tu compra."
                    return render_template("carrito.html", success=success)
    else:
        error = "Pago fallido o pendiente. Por favor, intenta nuevamente."
        return render_template("carrito.html", error=error)
    error = "Error en la respuesta de pago."
    return render_template("carrito.html", error=error)
