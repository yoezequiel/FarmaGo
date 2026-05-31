import type { APIRoute } from "astro";

export const POST: APIRoute = async ({ cookies, redirect }) => {
  const API_URL = import.meta.env.PUBLIC_API_URL || "http://localhost:3001";
  const token = cookies.get("token")?.value;
  await fetch(`${API_URL}/api/user/cuenta`, {
    method: "DELETE",
    headers: { Cookie: `token=${token}` },
  });
  cookies.delete("token", { path: "/" });
  return redirect("/login");
};
