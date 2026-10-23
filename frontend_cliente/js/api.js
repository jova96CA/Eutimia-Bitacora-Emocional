const API = "/api/v1";
async function api(path, options = {}) {
  const method = (options.method || "GET").toUpperCase();
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    await fetch(API + "/auth/csrf/", { credentials: "same-origin" });
    const m = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    if (m) headers["X-CSRFToken"] = decodeURIComponent(m[1]);
  }
  const r = await fetch(API + path, {
    ...options,
    method,
    headers,
    credentials: "same-origin",
  });
  let data = {};
  try {
    data = await r.json();
  } catch {}
  if (!r.ok) {
    if (
      [401, 403].includes(r.status) &&
      !path.includes("/auth/login") &&
      !path.includes("/auth/registro")
    )
      location.href = "login.html";
    throw new Error(data.detail || "No se pudo completar la solicitud");
  }
  return data;
}
