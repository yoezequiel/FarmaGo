import { db } from "./client.js";

export async function createTables() {
  await db.executeMultiple(`
    CREATE TABLE IF NOT EXISTS usuarios (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      nombre TEXT,
      apellido TEXT,
      direccion TEXT,
      numero_telefono TEXT,
      provincia TEXT,
      localidad TEXT,
      correo_electronico TEXT UNIQUE,
      nombre_usuario TEXT UNIQUE,
      contrasena TEXT,
      role TEXT,
      logo_url TEXT
    );
    CREATE TABLE IF NOT EXISTS categorias (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      nombre TEXT
    );
    CREATE TABLE IF NOT EXISTS productos (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      nombre TEXT,
      imagen TEXT,
      descripcion TEXT,
      cantidad INTEGER,
      precio_unitario REAL,
      id_categoria INTEGER,
      id_farmacia INTEGER,
      FOREIGN KEY(id_categoria) REFERENCES categorias(id),
      FOREIGN KEY(id_farmacia) REFERENCES usuarios(id)
    );
    CREATE TABLE IF NOT EXISTS farmacia_productos (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      id_usuario INTEGER,
      id_producto INTEGER,
      FOREIGN KEY(id_usuario) REFERENCES usuarios(id),
      FOREIGN KEY(id_producto) REFERENCES productos(id)
    );
    CREATE TABLE IF NOT EXISTS inventario (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      id_farmacia INTEGER,
      id_producto INTEGER,
      cantidad_disponible INTEGER,
      FOREIGN KEY(id_farmacia) REFERENCES usuarios(id),
      FOREIGN KEY(id_producto) REFERENCES productos(id)
    );
    CREATE TABLE IF NOT EXISTS carritos (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      id_usuario INTEGER,
      fecha TEXT,
      estado TEXT,
      total REAL,
      FOREIGN KEY(id_usuario) REFERENCES usuarios(id)
    );
    CREATE TABLE IF NOT EXISTS detalles_carrito (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      id_carrito INTEGER,
      id_producto INTEGER,
      cantidad INTEGER,
      precio_unitario REAL,
      FOREIGN KEY(id_carrito) REFERENCES carritos(id),
      FOREIGN KEY(id_producto) REFERENCES productos(id)
    );
    CREATE TABLE IF NOT EXISTS ventas (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      id_vendedor INTEGER,
      id_comprador INTEGER,
      fecha TEXT,
      total REAL,
      FOREIGN KEY(id_vendedor) REFERENCES usuarios(id),
      FOREIGN KEY(id_comprador) REFERENCES usuarios(id)
    );
    CREATE TABLE IF NOT EXISTS detalles_venta (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      id_venta INTEGER,
      id_producto INTEGER,
      cantidad INTEGER,
      precio_unitario REAL,
      FOREIGN KEY(id_venta) REFERENCES ventas(id),
      FOREIGN KEY(id_producto) REFERENCES productos(id)
    );
  `);

  const cats = await db.execute("SELECT COUNT(*) as cnt FROM categorias");
  if (cats.rows[0].cnt === 0) {
    await db.executeMultiple(`
      INSERT INTO categorias (nombre) VALUES ('Analgésicos');
      INSERT INTO categorias (nombre) VALUES ('Antibióticos');
      INSERT INTO categorias (nombre) VALUES ('Vitaminas');
      INSERT INTO categorias (nombre) VALUES ('Antiinflamatorios');
      INSERT INTO categorias (nombre) VALUES ('Dermatología');
      INSERT INTO categorias (nombre) VALUES ('Higiene');
    `);
  }

  console.log("Database tables ready");
}
