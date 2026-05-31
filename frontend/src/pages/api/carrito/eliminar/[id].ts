import type { APIRoute } from "astro";

export const POST: APIRoute = async ({ params, cookies, redirect }) => {
  const API_URL = import.meta.env.PUBLIC_API_URL || "http://localhost:3001";
  const token = cookies.get("token")?.value;
  await fetch(`${API_URL}/api/carrito/${params.id}`, {
    method: "DELETE",
    headers: { Cookie: `token=${token}` },
  });
  return redirect("/carrito");
};
