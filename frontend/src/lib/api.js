const API_URL = import.meta.env.PUBLIC_API_URL || "http://localhost:3001";

export async function apiFetch(path, options = {}, cookieHeader = "") {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(cookieHeader ? { Cookie: cookieHeader } : {}),
      ...options.headers,
    },
  });
  return res;
}

export async function apiGet(path, cookieHeader = "") {
  const res = await apiFetch(path, { method: "GET" }, cookieHeader);
  if (!res.ok) return null;
  return res.json();
}

export function cookieHeader(cookies) {
  const token = cookies.get("token")?.value;
  return token ? `token=${token}` : "";
}
