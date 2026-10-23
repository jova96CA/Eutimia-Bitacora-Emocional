async function cargarUsuarios() {
  const q = encodeURIComponent(document.querySelector("#buscar").value);
  const us = await api(`/admin/usuarios/?q=${q}`),
    box = document.querySelector("#lista-usuarios");
  if (!box) return;
  box.replaceChildren();
  const table = document.createElement("table"),
    head = document.createElement("tr");
  for (const t of [
    "Nombre",
    "Correo",
    "Rol",
    "Activo",
    "Alta",
    "Registros",
    "Acciones",
  ]) {
    const th = document.createElement("th");
    th.textContent = t;
    head.append(th);
  }
  table.append(head);
  for (const u of us) {
    const tr = document.createElement("tr");
    for (const v of [
      u.nombre,
      u.email,
      u.rol,
      u.is_active ? "Sí" : "No",
      new Date(u.date_joined).toLocaleDateString(),
      String(u.num_registros),
    ]) {
      const td = document.createElement("td");
      td.textContent = v;
      tr.append(td);
    }
    const td = document.createElement("td"),
      toggle = document.createElement("button");
    toggle.textContent = u.is_active ? "Desactivar" : "Activar";
    toggle.onclick = async () => {
      try {
        await api(`/admin/usuarios/${u.id}/`, {
          method: "PATCH",
          body: JSON.stringify({ is_active: !u.is_active }),
        });
        cargarUsuarios();
      } catch (e) {
        alert(e.message);
      }
    };
    td.append(toggle);
    if (u.rol === "usuario") {
      const role = document.createElement("button");
      role.textContent = "Hacer administrador";
      role.onclick = async () => {
        if (confirm(`¿Asignar rol administrador a ${u.email}?`)) {
          await api(`/admin/usuarios/${u.id}/asignar-rol/`, {
            method: "POST",
            body: JSON.stringify({ rol: "administrador" }),
          });
          cargarUsuarios();
        }
      };
      td.append(role);
    }
    const del = document.createElement("button");
    del.textContent = "Eliminar";
    del.onclick = async () => {
      if (confirm(`¿Eliminar definitivamente a ${u.email} y sus registros?`)) {
        if (prompt("Escribe ELIMINAR para confirmar") === "ELIMINAR") {
          await api(`/admin/usuarios/${u.id}/`, { method: "DELETE" });
          cargarUsuarios();
        }
      }
    };
    td.append(del);
    tr.append(td);
    table.append(tr);
  }
  box.append(table);
}
if (document.querySelector("#lista-usuarios")) {
  cargarUsuarios();
  document.querySelector("#buscar").oninput = cargarUsuarios;
  document.querySelector("#crear").onclick = async () => {
    const nombre = prompt("Nombre"),
      email = prompt("Correo"),
      password = prompt("Contraseña");
    if (nombre && email && password) {
      try {
        await api("/admin/usuarios/", {
          method: "POST",
          body: JSON.stringify({ nombre, email, password }),
        });
        cargarUsuarios();
      } catch (e) {
        alert(e.message);
      }
    }
  };
}
