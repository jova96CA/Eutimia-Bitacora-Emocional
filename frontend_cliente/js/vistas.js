/* Vistas dinámicas (una sola página), usuario, foto de perfil y salida.
   Solo se ejecuta en app.html. */
(() => {
  const menu = document.querySelector("#menu");
  if (!menu) return;

  /* ---------- 1. Cambio de vista (sin scroll) ---------- */
  const VISTAS = ["registrar", "historial", "estadisticas"];

  function mostrarVista(nombre) {
    if (!VISTAS.includes(nombre)) nombre = VISTAS[0];
    VISTAS.forEach((v) => {
      const seccion = document.getElementById(v);
      if (seccion) seccion.hidden = v !== nombre;
    });
    menu.querySelectorAll("a").forEach((enlace) => {
      if (enlace.dataset.vista === nombre) {
        enlace.setAttribute("aria-current", "page");
      } else {
        enlace.removeAttribute("aria-current");
      }
    });
    history.replaceState(null, "", "#" + nombre);
    window.scrollTo(0, 0);
  }

  menu.addEventListener("click", (e) => {
    const enlace = e.target.closest("a[data-vista]");
    if (!enlace) return;
    e.preventDefault();
    mostrarVista(enlace.dataset.vista);
  });
  mostrarVista(location.hash.slice(1));

  /* ---------- 2. Fechas del encabezado y del cuaderno ---------- */
  const fechaLarga = new Date().toLocaleDateString("es-MX", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });
  const fechaTitulo = document.querySelector("#fecha-larga");
  const fechaCuaderno = document.querySelector("#fecha-cuaderno");
  if (fechaTitulo) fechaTitulo.textContent = fechaLarga;
  if (fechaCuaderno) fechaCuaderno.textContent = fechaLarga;

  /* ---------- 3. Menú de usuario ---------- */
  const botonAvatar = document.querySelector("#avatar-btn");
  const menuUsuario = document.querySelector("#menu-usuario");
  const imagen = document.querySelector("#avatar-img");
  const icono = document.querySelector("#avatar-icono");
  const quitar = document.querySelector("#quitar-foto");
  const archivo = document.querySelector("#archivo-foto");
  let usuario = null;

  function abrirMenu(abrir) {
    menuUsuario.hidden = !abrir;
    botonAvatar.setAttribute("aria-expanded", String(abrir));
  }
  botonAvatar.addEventListener("click", (e) => {
    e.stopPropagation();
    abrirMenu(menuUsuario.hidden);
  });
  document.addEventListener("click", (e) => {
    if (!menuUsuario.hidden && !menuUsuario.contains(e.target))
      abrirMenu(false);
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !menuUsuario.hidden) {
      abrirMenu(false);
      botonAvatar.focus();
    }
  });

  /* ---------- 4. Foto de perfil (se guarda en este navegador) ---------- */
  const claveFoto = () => (usuario ? `eutimia-foto-${usuario.id}` : null);

  function pintarFoto(url) {
    imagen.classList.toggle("oculto", !url);
    icono.classList.toggle("oculto", Boolean(url));
    quitar.classList.toggle("oculto", !url);
    if (url) imagen.src = url;
    else imagen.removeAttribute("src");
  }

  function leerFoto() {
    try {
      return localStorage.getItem(claveFoto());
    } catch {
      return null;
    }
  }

  function reducirImagen(file, lado = 128) {
    return new Promise((resolver, rechazar) => {
      const url = URL.createObjectURL(file);
      const img = new Image();
      img.onload = () => {
        const lienzo = document.createElement("canvas");
        lienzo.width = lienzo.height = lado;
        const m = Math.min(img.width, img.height);
        lienzo
          .getContext("2d")
          .drawImage(
            img,
            (img.width - m) / 2,
            (img.height - m) / 2,
            m,
            m,
            0,
            0,
            lado,
            lado,
          );
        URL.revokeObjectURL(url);
        resolver(lienzo.toDataURL("image/jpeg", 0.85));
      };
      img.onerror = () => {
        URL.revokeObjectURL(url);
        rechazar(new Error("No se pudo leer la imagen."));
      };
      img.src = url;
    });
  }

  document.querySelector("#cambiar-foto").onclick = () => archivo.click();
  archivo.onchange = async () => {
    const elegido = archivo.files[0];
    archivo.value = "";
    if (!elegido || !claveFoto()) return;
    if (!elegido.type.startsWith("image/") || elegido.size > 8 * 1024 * 1024) {
      alert("Elige una imagen de menos de 8 MB.");
      return;
    }
    try {
      const url = await reducirImagen(elegido);
      localStorage.setItem(claveFoto(), url);
      pintarFoto(url);
      abrirMenu(false);
    } catch (x) {
      alert(x.message || "No se pudo guardar la foto.");
    }
  };
  quitar.onclick = () => {
    try {
      localStorage.removeItem(claveFoto());
    } catch {}
    pintarFoto(null);
    abrirMenu(false);
  };

  /* ---------- 5. Cerrar sesión ---------- */
  document.querySelector("#salir").onclick = async () => {
    try {
      await api("/auth/logout/", { method: "POST" });
    } finally {
      location.href = "login.html";
    }
  };

  /* ---------- 6. Nombre del usuario ---------- */
  (async () => {
    try {
      usuario = await api("/auth/me/");
      const nombre = (usuario.nombre || usuario.email || "").trim();
      document.querySelector("#nombre-usuario").textContent =
        nombre.split(" ")[0];
      pintarFoto(leerFoto());
    } catch {}
  })();
})();
