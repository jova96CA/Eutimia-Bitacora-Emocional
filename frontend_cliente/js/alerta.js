async function actualizarAlerta() {
  try {
    const a = await api("/alerta/");
    const el = document.querySelector("#alerta");
    el.hidden = !a.activa || sessionStorage.getItem("alerta-cerrada") === "1";
  } catch {}
}
const b = document.querySelector("#alerta");
if (b) {
  document.querySelector("#cerrar-alerta").onclick = () => {
    b.hidden = true;
    sessionStorage.setItem("alerta-cerrada", "1");
  };
  document.querySelector("#recursos").onclick = async () => {
    const m = document.querySelector("#modal"),
      list = document.querySelector("#recursos-lista");
    list.replaceChildren();
    for (const r of await api("/recursos-apoyo/")) {
      const p = document.createElement("p");
      p.textContent = `${r.nombre} ${r.telefono} — ${r.detalle}`;
      list.append(p);
    }
    m.showModal();
  };
  document.querySelector("#cerrar-modal").onclick = () =>
    document.querySelector("#modal").close();
}
