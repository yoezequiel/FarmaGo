import { defineMiddleware } from "astro:middleware";
import jwt from "jsonwebtoken";

export const onRequest = defineMiddleware((context, next) => {
  const token = context.cookies.get("token")?.value;
  context.locals.user = null;

  if (token) {
    try {
      const secret = import.meta.env.JWT_SECRET;
      const payload = jwt.verify(token, secret) as { id: number; role: string };
      context.locals.user = { id: payload.id, role: payload.role };
    } catch {
      context.cookies.delete("token", { path: "/" });
    }
  }

  return next();
});
