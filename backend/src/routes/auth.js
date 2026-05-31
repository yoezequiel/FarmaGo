import { Router } from "express";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import { db } from "../db/client.js";

const router = Router();

router.post("/login", async (req, res) => {
  const { correo_electronico, contrasena } = req.body;
  if (!correo_electronico || !contrasena) {
    return res.status(400).json({ error: "Datos requeridos" });
  }
  const result = await db.execute({
    sql: "SELECT id, role, contrasena FROM usuarios WHERE correo_electronico = ?",
    args: [correo_electronico],
  });
  const user = result.rows[0];
  if (!user) return res.status(401).json({ error: "Credenciales inválidas" });

  const valid = await bcrypt.compare(contrasena, user.contrasena);
  if (!valid) return res.status(401).json({ error: "Credenciales inválidas" });

  const token = jwt.sign(
    { id: user.id, role: user.role },
    process.env.JWT_SECRET,
    { expiresIn: "7d" }
  );
  res
    .cookie("token", token, {
      httpOnly: true,
      sameSite: "lax",
      maxAge: 7 * 24 * 60 * 60 * 1000,
    })
    .json({ ok: true, role: user.role });
});

router.post("/register/cliente", async (req, res) => {
  await registerUser(req, res, "cliente");
});

router.post("/register/farmacia", async (req, res) => {
  await registerUser(req, res, "farmacia");
});

router.post("/logout", (req, res) => {
  res.clearCookie("token", { path: "/" }).json({ ok: true });
});

router.get("/me", (req, res) => {
  const token = req.cookies?.token;
  if (!token) return res.status(401).json({ user: null });
  try {
    const user = jwt.verify(token, process.env.JWT_SECRET);
    res.json({ user: { id: user.id, role: user.role } });
  } catch {
    res.status(401).json({ user: null });
  }
});

async function registerUser(req, res, role) {
  const {
    nombre,
    apellido,
    direccion,
    numero_telefono,
    provincia,
    localidad,
    correo_electronico,
    nombre_usuario,
    contrasena,
    logo_url,
  } = req.body;

  const existing = await db.execute({
    sql: "SELECT id FROM usuarios WHERE nombre_usuario = ? OR correo_electronico = ?",
    args: [nombre_usuario, correo_electronico],
  });
  if (existing.rows.length > 0) {
    return res.status(409).json({ error: "El usuario o correo ya está en uso" });
  }

  const hash = await bcrypt.hash(contrasena, 10);
  const result = await db.execute({
    sql: "INSERT INTO usuarios (nombre, apellido, direccion, numero_telefono, provincia, localidad, correo_electronico, nombre_usuario, contrasena, role, logo_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
    args: [
      nombre,
      apellido,
      direccion,
      numero_telefono,
      provincia,
      localidad,
      correo_electronico,
      nombre_usuario,
      hash,
      role,
      logo_url || null,
    ],
  });

  if (role === "farmacia") {
    const farmaciaId = Number(result.lastInsertRowid);
    const productos = await db.execute("SELECT id FROM productos");
    for (const p of productos.rows) {
      await db.execute({
        sql: "INSERT INTO inventario (id_farmacia, id_producto, cantidad_disponible) VALUES (?, ?, 0)",
        args: [farmaciaId, p.id],
      });
    }
  }

  res.status(201).json({ ok: true });
}

export default router;
