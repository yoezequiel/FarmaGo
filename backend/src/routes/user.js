import { Router } from "express";
import bcrypt from "bcryptjs";
import { db } from "../db/client.js";
import { requireAuth } from "../middleware/auth.js";

const router = Router();

router.use(requireAuth);

router.get("/perfil", async (req, res) => {
  const result = await db.execute({
    sql: "SELECT id, nombre, apellido, direccion, provincia, localidad, numero_telefono, correo_electronico, nombre_usuario, logo_url, role FROM usuarios WHERE id = ?",
    args: [req.user.id],
  });
  if (!result.rows[0]) return res.status(404).json({ error: "Usuario no encontrado" });
  res.json(result.rows[0]);
});

router.put("/perfil", async (req, res) => {
  const {
    nombre,
    apellido,
    direccion,
    provincia,
    localidad,
    numero_telefono,
    correo_electronico,
    nombre_usuario,
    contrasena,
    logo_url,
  } = req.body;

  let hash;
  if (contrasena) {
    hash = await bcrypt.hash(contrasena, 10);
  } else {
    const cur = await db.execute({
      sql: "SELECT contrasena FROM usuarios WHERE id = ?",
      args: [req.user.id],
    });
    hash = cur.rows[0].contrasena;
  }

  await db.execute({
    sql: "UPDATE usuarios SET nombre=?, apellido=?, direccion=?, provincia=?, localidad=?, numero_telefono=?, correo_electronico=?, nombre_usuario=?, contrasena=?, logo_url=? WHERE id=?",
    args: [
      nombre, apellido, direccion, provincia, localidad, numero_telefono,
      correo_electronico, nombre_usuario, hash, logo_url || null, req.user.id,
    ],
  });
  res.json({ ok: true });
});

router.delete("/cuenta", async (req, res) => {
  await db.execute({ sql: "DELETE FROM usuarios WHERE id=?", args: [req.user.id] });
  res.clearCookie("token", { path: "/" }).json({ ok: true });
});

router.get("/pedidos", async (req, res) => {
  const ventas = await db.execute({
    sql: `SELECT v.id, v.fecha, v.total,
            u.nombre AS vendedor_nombre, u.nombre_usuario AS vendedor_usuario
          FROM ventas v
          INNER JOIN usuarios u ON v.id_vendedor = u.id
          WHERE v.id_comprador = ?
          ORDER BY v.fecha DESC`,
    args: [req.user.id],
  });

  const pedidos = await Promise.all(
    ventas.rows.map(async (v) => {
      const items = await db.execute({
        sql: `SELECT dv.cantidad, dv.precio_unitario, p.nombre, p.imagen
              FROM detalles_venta dv
              JOIN productos p ON dv.id_producto = p.id
              WHERE dv.id_venta = ?`,
        args: [v.id],
      });
      return { ...v, items: items.rows };
    })
  );

  res.json(pedidos);
});

export default router;
