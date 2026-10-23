if (document.querySelector("#lista-auditoria"))
  (async () => {
    const box = document.querySelector("#lista-auditoria");
    try {
      const rows = await api("/admin/auditoria/?categoria=admin");
      box.replaceChildren();
      const t = document.createElement("table"),
        h = document.createElement("tr");
      for (const label of [
        "Fecha",
        "Acción",
        "Resultado",
        "Actor",
        "Objetivo",
      ]) {
        const th = document.createElement("th");
        th.textContent = label;
        h.append(th);
      }
      t.append(h);
      for (const r of rows) {
        const tr = document.createElement("tr");
        for (const value of [
          r.creado_en,
          r.accion,
          r.resultado,
          r.actor,
          r.objetivo_id,
        ]) {
          const td = document.createElement("td");
          td.textContent = value ?? "—";
          tr.append(td);
        }
        t.append(tr);
      }
      box.append(t);
    } catch (e) {
      box.textContent = e.message;
    }
  })();
