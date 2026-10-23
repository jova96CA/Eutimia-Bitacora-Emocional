const f = document.querySelector("#form");
if (f)
  f.addEventListener("submit", async (e) => {
    e.preventDefault();
    const d = Object.fromEntries(new FormData(f));
    try {
      if (location.pathname.endsWith("registro.html")) {
        delete d.rol;
        await api("/auth/registro/", {
          method: "POST",
          body: JSON.stringify(d),
        });
        location.href = "login.html";
      } else {
        await api("/auth/login/", { method: "POST", body: JSON.stringify(d) });
        location.href = "app.html";
      }
    } catch (x) {
      document.querySelector("#error").textContent = x.message;
    }
  });
const exit = document.querySelector("#salir");
if (exit)
  exit.onclick = async () => {
    try {
      await api("/auth/logout/", { method: "POST" });
    } finally {
      location.href = "login.html";
    }
  };
