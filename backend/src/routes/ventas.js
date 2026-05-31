import { Router } from "express";
import { db } from "../db/client.js";
import { requireAuth, requireRole } from "../middleware/auth.js";

const router = Router();

router.get("/", requireAuth, requireRole("farmacia"), async (req, res) => {
  const result = await db.execute({
    sql: `SELECT v.id, v.fecha, v.total, u.nombre AS comprador_nombre, u.correo_electronico AS comprador_correo
          FROM ventas v
          INNER JOIN usuarios u ON v.id_comprador = u.id
          WHERE v.id_vendedor = ?`,
    args: [req.user.id],
  });
  res.json(result.rows);
});

export default router;
