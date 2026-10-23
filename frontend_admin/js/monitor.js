function dibujarTabla(box, rows, cols) {
  box.replaceChildren();
  if (!rows.length) {
    box.textContent = "Sin eventos";
    return;
  }
  const t = document.createElement("table"),
    h = document.createElement("tr");
  cols.forEach((c) => {
    const th = document.createElement("th");
    th.textContent = c[0];
    h.append(th);
  });
  t.append(h);
  rows.forEach((r) => {
    const tr = document.createElement("tr");
    cols.forEach((c) => {
      const td = document.createElement("td"),
        v = r[c[1]];
      td.textContent =
        typeof v === "object" && v !== null
          ? JSON.stringify(v)
          : String(v ?? "—");
      tr.append(td);
    });
    t.append(tr);
  });
  box.append(t);
}
async function cargarMonitor() {
  try {
    const sesiones = await api("/admin/auditoria/?categoria=sesion");
    dibujarTabla(document.querySelector("#lista-sesiones"), sesiones, [
      ["Fecha", "creado_en"],
      ["Acción", "accion"],
      ["Resultado", "resultado"],
      ["Actor", "actor"],
      ["Referencia", "referencia"],
    ]);
    const logs = await api("/admin/monitor/analizador/");
    dibujarTabla(document.querySelector("#lista-analizador"), logs, [
      ["Fecha", "creado_en"],
      ["Válido", "valido"],
      ["Tokens léxicos", "num_tokens"],
      ["Conteo por tipo", "tipos_token"],
      ["Campos", "estructura"],
      ["Códigos", "codigos_error"],
    ]);
    const ia = await api("/admin/monitor/ia/"),
      summary = document.createElement("p"),
      box = document.querySelector("#lista-ia");
    summary.textContent =
      `Total: ${ia.resumen.total} · Fallidas: ${ia.resumen.fallidas} · ` +
      `Tiempo promedio: ${ia.resumen.tiempo_promedio_ms ?? "—"} ms`;
    const rows = ia.solicitudes.map((x) => ({
      ...x,
      esquema_valido:
        x.esquema_valido === null ? "No aplica" : x.esquema_valido,
    }));
    dibujarTabla(box, rows, [
      ["Fecha", "creado_en"],
      ["Estado", "estado"],
      ["Tiempo ms", "tiempo_ms"],
      ["Esquema válido", "esquema_valido"],
      ["Tipo de error", "error_tipo"],
    ]);
    box.prepend(summary);
  } catch (e) {
    for (const id of ["#lista-sesiones", "#lista-analizador", "#lista-ia"])
      document.querySelector(id).textContent = e.message;
  }
}
if (document.querySelector("#lista-sesiones")) cargarMonitor();
