/******************************************************************************
 * LABSYS DIALIZAR
 * app/static/js/eps.js
 ******************************************************************************/

let epsTodasCache = [];

function alertaEps(id, mensaje, tipo = "danger") {
    document.getElementById(id).innerHTML = `<div class="alert alert-${tipo} py-2">${mensaje}</div>`;
}

async function cargarEps() {
    try {
        const resp = await fetch("/eps/");
        epsTodasCache = resp.ok ? await resp.json() : [];

        const tbody = document.getElementById("tablaEps");
        if (!epsTodasCache.length) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-muted small">No hay EPS registradas todavía.</td></tr>';
            return;
        }

        tbody.innerHTML = epsTodasCache.map(e => `
            <tr>
                <td>${e.codigo}</td>
                <td>${e.nombre}</td>
                <td>${e.nit || '-'}</td>
                <td>${e.telefono || '-'}</td>
                <td>${e.correo || '-'}</td>
                <td>
                    <button class="btn btn-sm btn-outline-secondary" onclick="editarEps(${e.id})">
                        <i class="bi bi-pencil"></i> Editar
                    </button>
                </td>
            </tr>
        `).join("");
    } catch (error) {
        alertaEps("alertaEps", "No se pudo cargar el listado de EPS.");
    }
}

function limpiarFormularioEps() {
    document.getElementById("alertaModalEps").innerHTML = "";
    document.getElementById("epsId").value = "";
    document.getElementById("epsCodigo").value = "";
    document.getElementById("epsCodigo").disabled = false;
    document.getElementById("epsNombre").value = "";
    document.getElementById("epsNit").value = "";
    document.getElementById("epsTelefono").value = "";
    document.getElementById("epsCorreo").value = "";
    document.getElementById("epsDireccion").value = "";
}

function editarEps(id) {
    const e = epsTodasCache.find(x => x.id === id);
    if (!e) return;

    limpiarFormularioEps();
    document.getElementById("tituloModalEps").textContent = "Editar EPS";
    document.getElementById("epsId").value = e.id;
    document.getElementById("epsCodigo").value = e.codigo;
    document.getElementById("epsCodigo").disabled = true;
    document.getElementById("epsNombre").value = e.nombre;
    document.getElementById("epsNit").value = e.nit || "";
    document.getElementById("epsTelefono").value = e.telefono || "";
    document.getElementById("epsCorreo").value = e.correo || "";
    document.getElementById("epsDireccion").value = e.direccion || "";

    new bootstrap.Modal(document.getElementById("modalEps")).show();
}

async function guardarEps() {
    const id = document.getElementById("epsId").value;
    const esEdicion = !!id;

    const payload = {
        codigo: document.getElementById("epsCodigo").value,
        nombre: document.getElementById("epsNombre").value,
        nit: document.getElementById("epsNit").value || null,
        telefono: document.getElementById("epsTelefono").value || null,
        correo: document.getElementById("epsCorreo").value || null,
        direccion: document.getElementById("epsDireccion").value || null,
    };

    if (!payload.codigo || !payload.nombre) {
        alertaEps("alertaModalEps", "Código y nombre son obligatorios.");
        return;
    }

    if (esEdicion) payload.activo = true;

    try {
        const resp = await fetch(esEdicion ? `/eps/${id}` : "/eps/", {
            method: esEdicion ? "PUT" : "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!resp.ok) {
            alertaEps("alertaModalEps", await extraerMensajeError(resp, "No se pudo guardar la EPS."));
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById("modalEps")).hide();
        await cargarEps();
    } catch (error) {
        alertaEps("alertaModalEps", "Error de conexión al guardar.");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    cargarEps();

    document.getElementById("btnNuevaEps").addEventListener("click", () => {
        limpiarFormularioEps();
        document.getElementById("tituloModalEps").textContent = "Nueva EPS";
        new bootstrap.Modal(document.getElementById("modalEps")).show();
    });

    document.getElementById("btnGuardarEps").addEventListener("click", guardarEps);
});
