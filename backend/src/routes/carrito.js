import { Router } from "express";
import { db } from "../db/client.js";
import { requireAuth } from "../middleware/auth.js";

const router = Router();

router.use(requireAuth);

router.get("/", async (req, res) => {
  const carrito = await getCarritoAbierto(req.user.id);
  if (!carrito) return res.json({ carrito: [], total: 0 });

  const detalles = await db.execute({
    sql: `SELECT dc.id, p.id as id_producto, p.nombre, p.precio_unitario, dc.cantidad
          FROM detalles_carrito dc
          JOIN productos p ON dc.id_producto = p.id
          JOIN carritos c ON dc.id_carrito = c.id
          WHERE c.id_usuario = ? AND c.estado = 'abierto'`,
    args: [req.user.id],
  });

  const total = detalles.rows.reduce(
    (acc, d) => acc + Number(d.precio_unitario) * Number(d.cantidad),
    0
  );
  res.json({ carrito: detalles.rows, total });
});

router.post("/:id_producto", async (req, res) => {
  const { cantidad = 1 } = req.body;
  const id_producto = Number(req.params.id_producto);
  const qty = Number(cantidad);

  const prodResult = await db.execute({
    sql: "SELECT * FROM productos WHERE id = ?",
    args: [id_producto],
  });
  const producto = prodResult.rows[0];
  if (!producto) return res.status(404).json({ error: "Producto no encontrado" });

  if (Number(producto.cantidad) < qty) {
    return res.status(400).json({ error: `Stock insuficiente. Disponible: ${producto.cantidad}` });
  }

  let carrito = await getCarritoAbierto(req.user.id);
  if (!carrito) {
    await db.execute({
      sql: "INSERT INTO carritos (id_usuario, fecha, estado, total) VALUES (?, ?, 'abierto', 0)",
      args: [req.user.id, new Date().toISOString()],
    });
    carrito = await getCarritoAbierto(req.user.id);
  }

  await db.execute({
    sql: "INSERT OR REPLACE INTO detalles_carrito (id_carrito, id_producto, cantidad, precio_unitario) VALUES (?, ?, ?, ?)",
    args: [carrito.id, id_producto, qty, producto.precio_unitario],
  });

  await recalcularTotal(carrito.id);
  res.json({ ok: true });
});

router.delete("/:id_detalle", async (req, res) => {
  const carritoResult = await db.execute({
    sql: "SELECT id FROM carritos WHERE id_usuario = ? AND estado = 'abierto'",
    args: [req.user.id],
  });
  const carrito = carritoResult.rows[0];
  if (!carrito) return res.status(404).json({ error: "Carrito no encontrado" });

  await db.execute({
    sql: "DELETE FROM detalles_carrito WHERE id = ? AND id_carrito = ?",
    args: [req.params.id_detalle, carrito.id],
  });

  await recalcularTotal(carrito.id);
  res.json({ ok: true });
});

async function getCarritoAbierto(userId) {
  const result = await db.execute({
    sql: "SELECT * FROM carritos WHERE id_usuario = ? AND estado = 'abierto'",
    args: [userId],
  });
  return result.rows[0] || null;
}

async function recalcularTotal(carritoId) {
  const result = await db.execute({
    sql: "SELECT SUM(precio_unitario * cantidad) as total FROM detalles_carrito WHERE id_carrito = ?",
    args: [carritoId],
  });
  const total = Number(result.rows[0]?.total || 0);
  await db.execute({
    sql: "UPDATE carritos SET total = ? WHERE id = ?",
    args: [total, carritoId],
  });
}

export default router;
