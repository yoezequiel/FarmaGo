import { Router } from "express";
import { db } from "../db/client.js";
import { requireAuth, requireRole } from "../middleware/auth.js";

const router = Router();

router.use(requireAuth, requireRole("farmacia"));

router.get("/", async (req, res) => {
  const result = await db.execute({
    sql: `SELECT p.id, p.nombre, COALESCE(i.cantidad_disponible, 0) as cantidad_disponible, p.cantidad, p.precio_unitario
          FROM productos p
          LEFT JOIN inventario i ON p.id = i.id_producto AND i.id_farmacia = ?
          WHERE p.id_farmacia = ?`,
    args: [req.user.id, req.user.id],
  });
  res.json(result.rows);
});

router.post("/", async (req, res) => {
  const { inventario } = req.body;
  const farmaciaId = req.user.id;

  await db.execute({
    sql: "DELETE FROM inventario WHERE id_farmacia = ?",
    args: [farmaciaId],
  });

  for (const item of inventario) {
    if (Number(item.cantidad) >= 0) {
      await db.execute({
        sql: "INSERT INTO inventario (id_farmacia, id_producto, cantidad_disponible) VALUES (?, ?, ?)",
        args: [farmaciaId, item.id_producto, Number(item.cantidad)],
      });
    }
  }

  res.json({ ok: true });
});

export default router;
