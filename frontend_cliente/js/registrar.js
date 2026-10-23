function fechaLocal() {
  const d = new Date();
  return [
    d.getFullYear(),
    String(d.getMonth() + 1).padStart(2, "0"),
    String(d.getDate()).padStart(2, "0"),
  ].join("-");
}
if (document.querySelector("#registro")) {
  (async () => {
    try {
      const u = await api("/auth/me/");
      if (u.rol !== "usuario") location.href = "login.html";
    } catch {}
    const f = document.querySelector("#fecha");
    f.value = fechaLocal();
    f.max = fechaLocal();
    document.querySelector("#intensidad").oninput = (e) =>
      (document.querySelector("#numero").textContent = e.target.value);
    document.querySelector("textarea").oninput = (e) =>
      (document.querySelector("#contador").textContent =
        `${e.target.value.length}/200`);
    document.querySelector("#registro").onsubmit = async (e) => {
      e.preventDefault();
      const d = Object.fromEntries(new FormData(e.currentTarget));
      d.intensidad = Number(d.intensidad);
      try {
        const r = await api("/registros/", {
          method: "POST",
          body: JSON.stringify(d),
        });
        document.querySelector("#resultado").textContent =
          r.analisis_texto.mensaje;
        if (r.urgente) {
          document.querySelector("#recursos").click();
        }
        await actualizarAlerta();
        await cargarHistorial();
        await cargarStats();
      } catch (x) {
        document.querySelector("#resultado").textContent = x.message;
      }
    };
    try {
      const x = await api("/racha/");
      document.querySelector("#racha").textContent =
        `Racha: ${x.racha} días · semana ${x.semana.map((v) => (v ? "●" : "○")).join(" ")}`;
    } catch {}
    await actualizarAlerta();
  })();
}

if (document.querySelector("#categorias")) {
  document.querySelectorAll("#categorias .chip").forEach(
    (b) =>
      (b.onclick = () => {
        document.querySelector("#categorias input[name=categoria]").value =
          b.dataset.cat;
        document
          .querySelectorAll("#categorias .chip")
          .forEach((x) => x.classList.toggle("activo", x === b));
      }),
  );
}
