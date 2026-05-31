import "dotenv/config";
import express from "express";
import cookieParser from "cookie-parser";
import cors from "cors";
import helmet from "helmet";
import morgan from "morgan";
import rateLimit from "express-rate-limit";

import { createTables } from "./db/schema.js";
import authRoutes from "./routes/auth.js";
import userRoutes from "./routes/user.js";
import productosRoutes from "./routes/productos.js";
import farmaciasRoutes from "./routes/farmacias.js";
import inventarioRoutes from "./routes/inventario.js";
import carritoRoutes from "./routes/carrito.js";
import pagosRoutes from "./routes/pagos.js";
import ventasRoutes from "./routes/ventas.js";

const app = express();
const PORT = process.env.PORT || 3001;
const FRONTEND_URL = process.env.FRONTEND_URL || "http://localhost:4321";

app.use(helmet({ crossOriginResourcePolicy: { policy: "cross-origin" } }));
app.use(cors({ origin: FRONTEND_URL, credentials: true }));
app.use(morgan("dev"));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 20,
  message: { error: "Demasiados intentos. Intenta de nuevo en 15 minutos." },
  standardHeaders: true,
  legacyHeaders: false,
});

app.get("/api/health", (req, res) => res.json({ ok: true }));

app.use("/api/auth", authLimiter, authRoutes);
app.use("/api/user", userRoutes);
app.use("/api/productos", productosRoutes);
app.use("/api/farmacias", farmaciasRoutes);
app.use("/api/inventario", inventarioRoutes);
app.use("/api/carrito", carritoRoutes);
app.use("/api/pagos", pagosRoutes);
app.use("/api/ventas", ventasRoutes);

app.use((err, req, res, _next) => {
  console.error(err.stack);
  res.status(500).json({ error: "Error interno del servidor" });
});

await createTables();
app.listen(PORT, () => console.log(`Backend corriendo en http://localhost:${PORT}`));
