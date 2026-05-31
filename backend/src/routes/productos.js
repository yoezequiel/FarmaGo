import { Router } from "express";
import { db } from "../db/client.js";
import { requireAuth, requireRole } from "../middleware/auth.js";

const router = Router();

router.get("/", async (req, res) => {
  const { pagina = 1, categoria_id, search_query } = req.query;
  const limit = 9;
  const offset = (Number(pagina) - 1) * limit;

  let countSql = "SELECT COUNT(*) as total FROM productos";
  let listSql = "SELECT * FROM productos";
  const args = [];

  if (categoria_id) {
    countSql += " WHERE id_categoria = ?";
    listSql += " WHERE id_categoria = ?";
    args.push(Number(categoria_id));
  } else if (search_query) {
    countSql += " WHERE nombre LIKE ?";
    listSql += " WHERE nombre LIKE ?";
    args.push(`%${search_query}%`);
  }

  listSql += " LIMIT ? OFFSET ?";

  const [countResult, listResult, catsResult] = await Promise.all([
    db.execute({ sql: countSql, args }),
    db.execute({ sql: listSql, args: [...args, limit, offset] }),
    db.execute("SELECT id, nombre FROM categorias"),
  ]);

  const total = Number(countResult.rows[0].total);
  res.json({
    productos: listResult.rows,
    total,
    paginas: Math.ceil(total / limit),
    categorias: catsResult.rows,
  });
});

router.get("/categorias", async (req, res) => {
  const result = await db.execute("SELECT id, nombre FROM categorias");
  res.json(result.rows);
});

router.get("/categoria/:id", async (req, res) => {
  const [prods, cat] = await Promise.all([
    db.execute({
      sql: "SELECT * FROM productos WHERE id_categoria = ?",
      args: [req.params.id],
    }),
    db.execute({
      sql: "SELECT nombre FROM categorias WHERE id = ?",
      args: [req.params.id],
    }),
  ]);
  if (!cat.rows[0]) return res.status(404).json({ error: "Categoría no encontrada" });
  res.json({ productos: prods.rows, categoria: cat.rows[0] });
});

router.get("/farmacia/:id", async (req, res) => {
  const [prods, farmacia] = await Promise.all([
    db.execute({
      sql: "SELECT * FROM productos WHERE id_farmacia = ?",
      args: [req.params.id],
    }),
    db.execute({
      sql: "SELECT nombre, apellido, direccion, provincia, localidad, numero_telefono, correo_electronico, nombre_usuario, logo_url FROM usuarios WHERE id = ?",
      args: [req.params.id],
    }),
  ]);
  res.json({ productos: prods.rows, farmacia: farmacia.rows[0] });
});

router.get("/:id", async (req, res) => {
  const result = await db.execute({
    sql: "SELECT * FROM productos WHERE id = ?",
    args: [req.params.id],
  });
  const producto = result.rows[0];
  if (!producto) return res.status(404).json({ error: "Producto no encontrado" });

  const [farmacia, categoria] = await Promise.all([
    db.execute({
      sql: "SELECT nombre, apellido, direccion, provincia, localidad, numero_telefono, correo_electronico, nombre_usuario, logo_url FROM usuarios WHERE id = ?",
      args: [producto.id_farmacia],
    }),
    db.execute({
      sql: "SELECT nombre FROM categorias WHERE id = ?",
      args: [producto.id_categoria],
    }),
  ]);

  res.json({
    producto,
    farmacia: farmacia.rows[0],
    categoria_nombre: categoria.rows[0]?.nombre,
  });
});

router.post("/", requireAuth, requireRole("farmacia"), async (req, res) => {
  const { nombre, imagen, descripcion, cantidad, precio_unitario, id_categoria } = req.body;
  const id_farmacia = req.user.id;

  const result = await db.execute({
    sql: "INSERT INTO productos (nombre, imagen, descripcion, cantidad, precio_unitario, id_categoria, id_farmacia) VALUES (?, ?, ?, ?, ?, ?, ?)",
    args: [nombre, imagen, descripcion, Number(cantidad), Number(precio_unitario), Number(id_categoria), id_farmacia],
  });
  const productId = Number(result.lastInsertRowid);

  await db.execute({
    sql: "INSERT INTO farmacia_productos (id_usuario, id_producto) VALUES (?, ?)",
    args: [id_farmacia, productId],
  });

  res.status(201).json({ ok: true, id: productId });
});

router.put("/:id", requireAuth, requireRole("farmacia"), async (req, res) => {
  const owner = await db.execute({
    sql: "SELECT id_usuario FROM farmacia_productos WHERE id_producto = ?",
    args: [req.params.id],
  });
  if (!owner.rows[0] || Number(owner.rows[0].id_usuario) !== req.user.id) {
    return res.status(403).json({ error: "Acceso prohibido" });
  }

  const { nombre, imagen, descripcion, precio_unitario, cantidad } = req.body;
  await db.execute({
    sql: "UPDATE productos SET nombre=?, imagen=?, descripcion=?, precio_unitario=?, cantidad=? WHERE id=?",
    args: [nombre, imagen, descripcion, Number(precio_unitario), Number(cantidad), req.params.id],
  });
  res.json({ ok: true });
});

router.delete("/:id", requireAuth, requireRole("farmacia"), async (req, res) => {
  const owner = await db.execute({
    sql: "SELECT id_usuario FROM farmacia_productos WHERE id_producto = ?",
    args: [req.params.id],
  });
  if (!owner.rows[0] || Number(owner.rows[0].id_usuario) !== req.user.id) {
    return res.status(403).json({ error: "Acceso prohibido" });
  }

  await db.execute({ sql: "DELETE FROM productos WHERE id=?", args: [req.params.id] });
  await db.execute({ sql: "DELETE FROM farmacia_productos WHERE id_producto=?", args: [req.params.id] });
  res.json({ ok: true });
});

export default router;
