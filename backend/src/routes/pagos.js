import { Router } from "express";
import { db } from "../db/client.js";
import { requireAuth } from "../middleware/auth.js";

const router = Router();

router.get("/pago_exitoso", requireAuth, async (req, res) => {
  const { status, collection_status } = req.query;

  if (status !== "approved" || collection_status !== "approved") {
    return res.json({ ok: false, error: "Pago fallido o pendiente" });
  }

  const carritoResult = await db.execute({
    sql: "SELECT * FROM carritos WHERE id_usuario = ? AND estado = 'abierto'",
    args: [req.user.id],
  });
  const carrito = carritoResult.rows[0];
  if (!carrito) return res.json({ ok: false, error: "Carrito no encontrado" });

  const detallesResult = await db.execute({
    sql: "SELECT * FROM detalles_carrito WHERE id_carrito = ?",
    args: [carrito.id],
  });
  const detalles = detallesResult.rows;
  if (!detalles.length) return res.json({ ok: false, error: "Carrito vacío" });

  const total = detalles.reduce((acc, d) => acc + Number(d.precio_unitario) * Number(d.cantidad), 0);

  const vendedorResult = await db.execute({
    sql: "SELECT id_usuario FROM farmacia_productos WHERE id_producto = ?",
    args: [detalles[0].id_producto],
  });
  const id_vendedor = vendedorResult.rows[0]?.id_usuario;

  const ventaResult = await db.execute({
    sql: "INSERT INTO ventas (id_vendedor, id_comprador, fecha, total) VALUES (?, ?, ?, ?)",
    args: [id_vendedor, req.user.id, new Date().toISOString(), total],
  });
  const ventaId = Number(ventaResult.lastInsertRowid);

  for (const detalle of detalles) {
    await db.execute({
      sql: "INSERT INTO detalles_venta (id_venta, id_producto, cantidad, precio_unitario) VALUES (?, ?, ?, ?)",
      args: [ventaId, detalle.id_producto, detalle.cantidad, detalle.precio_unitario],
    });
    await db.execute({
      sql: "UPDATE productos SET cantidad = cantidad - ? WHERE id = ?",
      args: [detalle.cantidad, detalle.id_producto],
    });
  }

  await db.execute({ sql: "DELETE FROM detalles_carrito WHERE id_carrito = ?", args: [carrito.id] });
  await db.execute({ sql: "DELETE FROM carritos WHERE id = ?", args: [carrito.id] });

  res.json({ ok: true });
});

router.post("/checkout", requireAuth, async (req, res) => {
  const MERCADOPAGO_ACCESS_TOKEN = process.env.MERCADOPAGO_ACCESS_TOKEN;
  if (!MERCADOPAGO_ACCESS_TOKEN) {
    return res.status(500).json({ error: "MercadoPago no configurado" });
  }

  const carritoResult = await db.execute({
    sql: "SELECT * FROM carritos WHERE id_usuario = ? AND estado = 'abierto'",
    args: [req.user.id],
  });
  const carrito = carritoResult.rows[0];
  if (!carrito) return res.status(400).json({ error: "Carrito vacío" });

  const detallesResult = await db.execute({
    sql: `SELECT dc.cantidad, dc.precio_unitario, p.nombre
          FROM detalles_carrito dc
          INNER JOIN productos p ON dc.id_producto = p.id
          WHERE dc.id_carrito = ?`,
    args: [carrito.id],
  });
  const detalles = detallesResult.rows;
  if (!detalles.length) return res.status(400).json({ error: "Carrito vacío" });

  const total = detalles.reduce((acc, d) => acc + Number(d.precio_unitario) * Number(d.cantidad), 0);
  const frontendUrl = process.env.FRONTEND_URL || "http://localhost:4321";

  const preference = {
    items: detalles.map((d) => ({
      title: d.nombre,
      quantity: Number(d.cantidad),
      currency_id: "ARS",
      unit_price: Number(d.precio_unitario),
    })),
    back_urls: {
      success: `${frontendUrl}/pago-exitoso`,
      failure: `${frontendUrl}/carrito`,
      pending: `${frontendUrl}/carrito`,
    },
    auto_return: "approved",
  };

  const mpRes = await fetch("https://api.mercadopago.com/checkout/preferences", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${MERCADOPAGO_ACCESS_TOKEN}`,
    },
    body: JSON.stringify(preference),
  });

  if (!mpRes.ok) {
    return res.status(500).json({ error: "Error al crear preferencia de pago" });
  }

  const data = await mpRes.json();
  res.json({ init_point: data.init_point });
});

export default router;
