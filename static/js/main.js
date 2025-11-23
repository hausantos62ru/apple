// Pequeñas interacciones: confirm delete
function confirmDelete(id) {
    if (confirm("¿Eliminar producto?")) {
        window.location.href = `/admin/delete/${id}`;
    }
}
