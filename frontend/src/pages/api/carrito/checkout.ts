import type { APIRoute } from "astro";

export const POST: APIRoute = async ({ cookies, redirect }) => {
  const API_URL = import.meta.env.PUBLIC_API_URL || "http://localhost:3001";
  const token = cookies.get("token")?.value;

  const res = await fetch(`${API_URL}/api/pagos/checkout`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Cookie: `token=${token}` },
  });

  if (!res.ok) return redirect("/carrito");

  const data = await res.json();
  return redirect(data.init_point);
};
