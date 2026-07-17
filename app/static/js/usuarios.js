/******************************************************************************
 * LABSYS DIALIZAR
 * app/static/js/usuarios.js
 ******************************************************************************/

let rolesCacheUsr = [];
let usuarioRolesCacheUsr = [];

function alertaUsr(id, mensaje, tipo = "danger") {
    document.getElementById(id).innerHTML = `<div class="alert alert-${tipo} py-2">${mensaje}</div>`;
}

function rolesDeUsuario(usuarioId) {
    const ids = usuarioRolesCacheUsr.filter(ur => ur.usuario_id === usuarioId).map(ur => ur.rol_id);
    return rolesCacheUsr.filter(r => ids.includes(r.id)).map(r => r.nombre);
}

async function cargarCatalogoRoles() {
    const resp = await fetch("/roles/");
    rolesCacheUsr = resp.ok ? await resp.json() : [];

    document.getElementById("listaRolesCheckbox").innerHTML = rolesCacheUsr.length
        ? rolesCacheUsr.map(r => `
            <div class="col-md-6 mb-2">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" value="${r.id}" id="rolChk${r.id}">
                    <label class="form-check-label" for="rolChk${r.id}">${r.nombre}</label>
                </div>
            </div>
        `).join("")
        : '<div class="text-muted small">No hay roles creados todavía. Ve a "Roles" para crear el primero.</div>';
}

async function cargarUsuarios() {
    try {
        const [usuariosR, usuarioRolesR] = await Promise.all([
            fetch("/usuarios/"),
            fetch("/usuario-roles/"),
        ]);

        const usuarios = usuariosR.ok ? await usuariosR.json() : [];
        usuarioRolesCacheUsr = usuarioRolesR.ok ? await usuarioRolesR.json() : [];

        const tbody = document.getElementById("tablaUsuarios");
        if (!usuarios.length) {
            tbody.innerHTML = '<tr><td colspan="8" class="text-muted small">No hay usuarios registrados.</td></tr>';
            return;
        }

        tbody.innerHTML = usuarios.map(u => {
            const roles = rolesDeUsuario(u.id);
            return `
            <tr>
                <td>${u.usuario}</td>
                <td>${u.nombres} ${u.apellidos}</td>
                <td>${u.cargo}</td>
                <td>${u.correo}</td>
                <td>${roles.length ? roles.map(r => `<span class="badge bg-info me-1">${r}</span>`).join("") : '<span class="text-muted small">Sin roles</span>'}</td>
                <td>${u.acceso_movil ? '<span class="badge bg-success"><i class="bi bi-phone"></i> Sí</span>' : '<span class="badge bg-secondary">No</span>'}</td>
                <td>${u.activo ? '<span class="badge bg-success">Activo</span>' : '<span class="badge bg-secondary">Inactivo</span>'}</td>
                <td>
                    <button class="btn btn-sm btn-outline-warning" onclick="abrirModalReset(${u.id})">
                        <i class="bi bi-key"></i> Contraseña
                    </button>
                </td>
            </tr>`;
        }).join("");
    } catch (error) {
        alertaUsr("alertaUsuarios", "No se pudo cargar el listado de usuarios.");
    }
}

async function guardarUsuario() {
    const payload = {
        tipo_documento: document.getElementById("usrTipoDocumento").value,
        documento: document.getElementById("usrDocumento").value,
        nombres: document.getElementById("usrNombres").value,
        apellidos: document.getElementById("usrApellidos").value,
        correo: document.getElementById("usrCorreo").value,
        celular: document.getElementById("usrCelular").value || null,
        cargo: document.getElementById("usrCargo").value,
        usuario: document.getElementById("usrUsuario").value,
        password: document.getElementById("usrPassword").value,
        acceso_movil: document.getElementById("usrAccesoMovil").checked,
    };

    if (!payload.documento || !payload.nombres || !payload.apellidos || !payload.usuario || !payload.password) {
        alertaUsr("alertaModalUsuario", "Documento, nombres, apellidos, usuario y contraseña son obligatorios.");
        return;
    }

    try {
        const resp = await fetch("/usuarios/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!resp.ok) {
            alertaUsr("alertaModalUsuario", await extraerMensajeError(resp, "No se pudo crear el usuario."));
            return;
        }

        const usuarioCreado = await resp.json();

        const rolesSeleccionados = Array.from(document.querySelectorAll("#listaRolesCheckbox input:checked"))
            .map(cb => parseInt(cb.value, 10));

        for (const rolId of rolesSeleccionados) {
            await fetch("/usuario-roles/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ usuario_id: usuarioCreado.id, rol_id: rolId }),
            });
        }

        bootstrap.Modal.getInstance(document.getElementById("modalNuevoUsuario")).hide();
        await cargarUsuarios();
    } catch (error) {
        alertaUsr("alertaModalUsuario", "Error de conexión al crear el usuario.");
    }
}

function abrirModalReset(usuarioId) {
    document.getElementById("alertaModalReset").innerHTML = "";
    document.getElementById("resetUsuarioId").value = usuarioId;
    document.getElementById("resetPasswordNueva").value = "";
    new bootstrap.Modal(document.getElementById("modalResetPassword")).show();
}

async function confirmarReset() {
    const id = document.getElementById("resetUsuarioId").value;
    const password = document.getElementById("resetPasswordNueva").value;

    if (!password || password.length < 6) {
        alertaUsr("alertaModalReset", "La contraseña debe tener al menos 6 caracteres.");
        return;
    }

    try {
        const resp = await fetch(`/usuarios/${id}/resetear-password`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ password }),
        });

        if (!resp.ok) {
            alertaUsr("alertaModalReset", await extraerMensajeError(resp, "No se pudo restablecer la contraseña."));
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById("modalResetPassword")).hide();
        alertaUsr("alertaUsuarios", "Contraseña restablecida correctamente.", "success");
    } catch (error) {
        alertaUsr("alertaModalReset", "Error de conexión.");
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    await cargarCatalogoRoles();
    await cargarUsuarios();

    document.getElementById("btnNuevoUsuario").addEventListener("click", () => {
        document.getElementById("alertaModalUsuario").innerHTML = "";
        document.querySelectorAll("#modalNuevoUsuario input").forEach(i => {
            if (i.type === "checkbox") i.checked = false;
            else i.value = "";
        });
        document.querySelectorAll("#listaRolesCheckbox input").forEach(cb => cb.checked = false);
        new bootstrap.Modal(document.getElementById("modalNuevoUsuario")).show();
    });

    document.getElementById("btnGuardarUsuario").addEventListener("click", guardarUsuario);
    document.getElementById("btnConfirmarReset").addEventListener("click", confirmarReset);
});
