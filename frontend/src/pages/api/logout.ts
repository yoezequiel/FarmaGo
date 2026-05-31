import type { APIRoute } from "astro";

export const POST: APIRoute = async ({ cookies, redirect }) => {
  cookies.delete("token", { path: "/" });
  return redirect("/login");
};
