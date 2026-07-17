/******************************************************************************
 * LABSYS DIALIZAR
 * app/static/js/roles.js
 ******************************************************************************/

let rolesTodos = [];
let permisosTodos = [];
let rolPermisosTodos = [];
let rolSeleccionadoId = null;

function alertaRol(id, mensaje, tipo = "danger") {
    document.getElementById(id).innerHTML = `<div class="alert alert-${tipo} py-2">${mensaje}</div>`;
}

async function cargarTodo() {
    try {
        const [rolesR, permisosR, rolPermisosR] = await Promise.all([
            fetch("/roles/"),
            fetch("/permisos/"),
            fetch("/rol-permisos/"),
        ]);

        rolesTodos = rolesR.ok ? await rolesR.json() : [];
        permisosTodos = permisosR.ok ? await permisosR.json() : [];
        rolPermisosTodos = rolPermisosR.ok ? await rolPermisosR.json() : [];

        renderListaRoles();
        if (rolSeleccionadoId) renderPanelPermisos();
    } catch (error) {
        alertaRol("alertaRoles", "No se pudieron cargar los roles.");
    }
}

function renderListaRoles() {
    const cont = document.getElementById("listaRoles");
    if (!rolesTodos.length) {
        cont.innerHTML = '<div class="list-group-item text-muted small">No hay roles creados todavía.</div>';
        return;
    }

    cont.innerHTML = rolesTodos.map(r => `
        <a href="#" class="list-group-item list-group-item-action ${r.id === rolSeleccionadoId ? 'active' : ''}" onclick="seleccionarRol(event, ${r.id})">
            <strong>${r.nombre}</strong>
            ${r.descripcion ? `<br><small class="${r.id === rolSeleccionadoId ? '' : 'text-muted'}">${r.descripcion}</small>` : ""}
        </a>
    `).join("");
}

function seleccionarRol(event, rolId) {
    event.preventDefault();
    rolSeleccionadoId = rolId;
    renderListaRoles();
    renderPanelPermisos();
}

function renderPanelPermisos() {
    const rol = rolesTodos.find(r => r.id === rolSeleccionadoId);
    document.getElementById("tituloPermisosRol").textContent = `Permisos de: ${rol ? rol.nombre : ''}`;

    const idsAsignados = new Set(
        rolPermisosTodos.filter(rp => rp.rol_id === rolSeleccionadoId).map(rp => rp.permiso_id)
    );

    const panel = document.getElementById("panelPermisosRol");

    if (!permisosTodos.length) {
        panel.innerHTML = `
            <p class="text-muted small">Todavía no hay permisos en el catálogo.</p>
            <button class="btn btn-sm btn-outline-primary" onclick="new bootstrap.Modal(document.getElementById('modalNuevoPermiso')).show()">
                <i class="bi bi-plus"></i> Crear el primer permiso
            </button>
        `;
        return;
    }

    // Agrupar por módulo para que sea más fácil de leer
    const porModulo = {};
    for (const p of permisosTodos) {
        if (!porModulo[p.modulo]) porModulo[p.modulo] = [];
        porModulo[p.modulo].push(p);
    }

    panel.innerHTML = Object.entries(porModulo).map(([modulo, permisos]) => `
        <h6 class="mt-2">${modulo}</h6>
        <div class="row mb-2">
            ${permisos.map(p => `
                <div class="col-md-6">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox"
                               ${idsAsignados.has(p.id) ? "checked" : ""}
                               onchange="togglePermiso(${p.id}, this.checked)">
                        <label class="form-check-label">${p.nombre}</label>
                    </div>
                </div>
            `).join("")}
        </div>
    `).join("") + `
        <hr>
        <button class="btn btn-sm btn-outline-secondary" onclick="new bootstrap.Modal(document.getElementById('modalNuevoPermiso')).show()">
            <i class="bi bi-plus"></i> Nuevo permiso
        </button>
    `;
}

async function togglePermiso(permisoId, marcado) {
    try {
        if (marcado) {
            const resp = await fetch("/rol-permisos/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ rol_id: rolSeleccionadoId, permiso_id: permisoId }),
            });
            if (!resp.ok) {
                alert(await extraerMensajeError(resp, "No se pudo asignar el permiso."));
            }
        } else {
            await fetch(`/rol-permisos/${rolSeleccionadoId}/${permisoId}`, { method: "DELETE" });
        }
        await cargarTodo();
    } catch (error) {
        alert("Error de conexión.");
    }
}

async function guardarRol() {
    const nombre = document.getElementById("rolNombre").value;
    const descripcion = document.getElementById("rolDescripcion").value || null;

    if (!nombre) {
        alertaRol("alertaModalRol", "El nombre del rol es obligatorio.");
        return;
    }

    try {
        const resp = await fetch("/roles/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nombre, descripcion }),
        });

        if (!resp.ok) {
            alertaRol("alertaModalRol", await extraerMensajeError(resp, "No se pudo crear el rol."));
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById("modalNuevoRol")).hide();
        await cargarTodo();
    } catch (error) {
        alertaRol("alertaModalRol", "Error de conexión.");
    }
}

async function guardarPermiso() {
    const codigo = document.getElementById("permisoCodigo").value;
    const nombre = document.getElementById("permisoNombre").value;
    const modulo = document.getElementById("permisoModulo").value;

    if (!codigo || !nombre || !modulo) {
        alertaRol("alertaModalPermiso", "Código, nombre y módulo son obligatorios.");
        return;
    }

    try {
        const resp = await fetch("/permisos/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ codigo, nombre, modulo }),
        });

        if (!resp.ok) {
            alertaRol("alertaModalPermiso", await extraerMensajeError(resp, "No se pudo crear el permiso."));
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById("modalNuevoPermiso")).hide();
        document.getElementById("permisoCodigo").value = "";
        document.getElementById("permisoNombre").value = "";
        document.getElementById("permisoModulo").value = "";
        await cargarTodo();
    } catch (error) {
        alertaRol("alertaModalPermiso", "Error de conexión.");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    cargarTodo();

    document.getElementById("btnNuevoRol").addEventListener("click", () => {
        document.getElementById("alertaModalRol").innerHTML = "";
        document.getElementById("rolNombre").value = "";
        document.getElementById("rolDescripcion").value = "";
        new bootstrap.Modal(document.getElementById("modalNuevoRol")).show();
    });

    document.getElementById("btnGuardarRol").addEventListener("click", guardarRol);
    document.getElementById("btnGuardarPermiso").addEventListener("click", guardarPermiso);
});
