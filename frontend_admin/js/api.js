const API = "/api/v1";
async function api(path, options = {}) {
  const method = (options.method || "GET").toUpperCase(),
    headers = {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    };
  if (["POST", "PATCH", "PUT", "DELETE"].includes(method)) {
    await fetch(API + "/auth/csrf/", { credentials: "same-origin" });
    const c = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    if (c) headers["X-CSRFToken"] = decodeURIComponent(c[1]);
  }
  const r = await fetch(API + path, {
    ...options,
    method,
    headers,
    credentials: "same-origin",
  });
  let d = {};
  try {
    d = await r.json();
  } catch {}
  if (!r.ok) throw new Error(d.detail || "No se pudo completar");
  return d;
}
