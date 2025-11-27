// Pequeñas interacciones: confirm delete
function confirmDelete(id) {
    if (confirm("¿Eliminar producto?")) {
        window.location.href = `/admin/delete/${id}`;
    }
}

document.addEventListener("DOMContentLoaded", () => {

  const userBtn = document.getElementById("userBtn");
  const userMenu = document.getElementById("userMenu");

  if (userBtn && userMenu) {
    userBtn.addEventListener("click", () => {
      userMenu.style.display =
        userMenu.style.display === "block" ? "none" : "block";
    });

    // Cerrar si haces click fuera
    document.addEventListener("click", (e) => {
      if (!userMenu.contains(e.target) && !userBtn.contains(e.target)) {
        userMenu.style.display = "none";
      }
    });
  }
});
