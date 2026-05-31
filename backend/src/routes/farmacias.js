import { Router } from "express";
import { db } from "../db/client.js";

const router = Router();

router.get("/", async (req, res) => {
  const { search } = req.query;
  let sql = "SELECT id, nombre, apellido, direccion, provincia, localidad, numero_telefono, correo_electronico, nombre_usuario, logo_url FROM usuarios WHERE role = 'farmacia'";
  const args = [];
  if (search) {
    sql += " AND nombre LIKE ?";
    args.push(`%${search}%`);
  }
  const result = await db.execute({ sql, args });
  res.json(result.rows);
});

export default router;
