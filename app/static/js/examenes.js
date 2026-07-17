/******************************************************************************
 * LABSYS DIALIZAR
 * app/static/js/examenes.js
 ******************************************************************************/

let examenesTodosCache = [];

function alertaExam(id, mensaje, tipo = "danger") {
    document.getElementById(id).innerHTML = `<div class="alert alert-${tipo} py-2">${mensaje}</div>`;
}

function formatoPrecio(v) {
    return new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 }).format(v || 0);
}

async function cargarExamenes() {
    try {
        const resp = await fetch("/examenes/");
        examenesTodosCache = resp.ok ? await resp.json() : [];
        renderTablaExamenes(examenesTodosCache);
    } catch (error) {
        alertaExam("alertaExamenes", "No se pudo cargar el catálogo de exámenes.");
    }
}

function renderTablaExamenes(lista) {
    const tbody = document.getElementById("tablaExamenes");
    if (!lista.length) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-muted small">No hay exámenes en el catálogo todavía.</td></tr>';
        return;
    }

    tbody.innerHTML = lista.map(e => `
        <tr>
            <td>${e.codigo}</td>
            <td>${e.nombre}</td>
            <td>${e.categoria || '-'}</td>
            <td>${formatoPrecio(e.precio)}</td>
            <td>${e.activo ? '<span class="badge bg-success">Activo</span>' : '<span class="badge bg-secondary">Inactivo</span>'}</td>
            <td>
                <button class="btn btn-sm btn-outline-secondary" onclick="editarExamen(${e.id})">
                    <i class="bi bi-pencil"></i> Editar
                </button>
            </td>
        </tr>
    `).join("");
}

function limpiarFormularioExamen() {
    document.getElementById("alertaModalExamen").innerHTML = "";
    document.getElementById("examenId").value = "";
    document.getElementById("examenCodigo").value = "";
    document.getElementById("examenCodigo").disabled = false;
    document.getElementById("examenNombre").value = "";
    document.getElementById("examenCategoria").value = "";
    document.getElementById("examenPrecio").value = "0";
    document.getElementById("examenActivo").checked = true;
    document.getElementById("grupoActivoExamen").style.display = "none";
}

function editarExamen(id) {
    const e = examenesTodosCache.find(x => x.id === id);
    if (!e) return;

    limpiarFormularioExamen();
    document.getElementById("tituloModalExamen").textContent = "Editar examen";
    document.getElementById("examenId").value = e.id;
    document.getElementById("examenCodigo").value = e.codigo;
    document.getElementById("examenCodigo").disabled = true;
    document.getElementById("examenNombre").value = e.nombre;
    document.getElementById("examenCategoria").value = e.categoria || "";
    document.getElementById("examenPrecio").value = e.precio;
    document.getElementById("examenActivo").checked = e.activo;
    document.getElementById("grupoActivoExamen").style.display = "block";

    new bootstrap.Modal(document.getElementById("modalExamen")).show();
}

async function guardarExamen() {
    const id = document.getElementById("examenId").value;
    const esEdicion = !!id;

    const nombre = document.getElementById("examenNombre").value;
    const categoria = document.getElementById("examenCategoria").value || null;
    const precio = parseFloat(document.getElementById("examenPrecio").value || 0);

    if (!nombre) {
        alertaExam("alertaModalExamen", "El nombre del examen es obligatorio.");
        return;
    }

    let url, metodo, payload;

    if (esEdicion) {
        url = `/examenes/${id}`;
        metodo = "PUT";
        payload = { nombre, categoria, precio, activo: document.getElementById("examenActivo").checked };
    } else {
        const codigo = document.getElementById("examenCodigo").value;
        if (!codigo) {
            alertaExam("alertaModalExamen", "El código es obligatorio.");
            return;
        }
        url = "/examenes/";
        metodo = "POST";
        payload = { codigo, nombre, categoria, precio };
    }

    try {
        const resp = await fetch(url, {
            method: metodo,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!resp.ok) {
            alertaExam("alertaModalExamen", await extraerMensajeError(resp, "No se pudo guardar el examen."));
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById("modalExamen")).hide();
        await cargarExamenes();
    } catch (error) {
        alertaExam("alertaModalExamen", "Error de conexión al guardar.");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    cargarExamenes();

    document.getElementById("btnNuevoExamen").addEventListener("click", () => {
        limpiarFormularioExamen();
        document.getElementById("tituloModalExamen").textContent = "Nuevo examen";
        new bootstrap.Modal(document.getElementById("modalExamen")).show();
    });

    document.getElementById("btnGuardarExamen").addEventListener("click", guardarExamen);

    document.getElementById("buscarExamen").addEventListener("input", (e) => {
        const texto = e.target.value.toLowerCase();
        const filtrados = examenesTodosCache.filter(ex =>
            `${ex.nombre} ${ex.codigo}`.toLowerCase().includes(texto)
        );
        renderTablaExamenes(filtrados);
    });
});
