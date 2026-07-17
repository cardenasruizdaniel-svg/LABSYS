/******************************************************************************
 * LABSYS DIALIZAR
 * app/static/js/procesamientos.js
 ******************************************************************************/

let muestrasCacheProc = [];

function alertaProc(id, mensaje, tipo = "danger") {
    document.getElementById(id).innerHTML = `<div class="alert alert-${tipo} py-2">${mensaje}</div>`;
}

function codigoMuestraDe(id) {
    const m = muestrasCacheProc.find(x => x.id === id);
    return m ? m.codigo_barras : `#${id}`;
}

async function cargarDatos() {
    try {
        const [muestrasR, procesamientosR, profesionalesR] = await Promise.all([
            fetch("/muestras/"),
            fetch("/procesamientos/"),
            fetch("/medicos/"),
        ]);

        muestrasCacheProc = muestrasR.ok ? await muestrasR.json() : [];
        const procesamientos = procesamientosR.ok ? await procesamientosR.json() : [];
        const profesionales = profesionalesR.ok ? await profesionalesR.json() : [];

        document.getElementById("procesarProfesional").innerHTML = '<option value="">Sin especificar</option>' +
            profesionales.map(p => `<option value="${p.id}">${p.nombres} ${p.apellidos} (${p.tipo_profesional})</option>`).join("");

        const idsConProcesamiento = new Set(procesamientos.map(p => p.muestra_id));
        const pendientes = muestrasCacheProc.filter(m => !idsConProcesamiento.has(m.id));

        renderPendientes(pendientes);
        renderProcesamientos(procesamientos);
    } catch (error) {
        alertaProc("alertaProcesamientos", "No se pudieron cargar los datos.");
    }
}

function renderPendientes(pendientes) {
    const tbody = document.getElementById("tablaPendientes");
    if (!pendientes.length) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-muted small">No hay muestras pendientes de procesar.</td></tr>';
        return;
    }

    tbody.innerHTML = pendientes.map(m => `
        <tr>
            <td>${m.codigo_barras}</td>
            <td>${m.tipo_muestra}</td>
            <td><span class="badge bg-secondary">${m.estado}</span></td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="abrirModalProcesar(${m.id})">
                    <i class="bi bi-play-circle"></i> Procesar
                </button>
            </td>
        </tr>
    `).join("");
}

function renderProcesamientos(procesamientos) {
    const tbody = document.getElementById("tablaProcesamientos");
    if (!procesamientos.length) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-muted small">Todavía no hay procesamientos registrados.</td></tr>';
        return;
    }

    const coloresEstado = { EN_PROCESO: "primary", COMPLETADO: "success" };

    tbody.innerHTML = procesamientos.map(p => `
        <tr>
            <td>${codigoMuestraDe(p.muestra_id)}</td>
            <td>${p.analizador}</td>
            <td>${p.profesional || '-'}</td>
            <td><span class="badge bg-${coloresEstado[p.estado] || 'secondary'}">${p.estado}</span></td>
            <td class="small">${new Date(p.fecha_inicio).toLocaleString("es-CO")}</td>
            <td>
                ${p.estado === "EN_PROCESO"
                    ? `<button class="btn btn-sm btn-outline-success" onclick="completarProcesamiento(${p.id})">
                        <i class="bi bi-check-circle"></i> Completar
                       </button>`
                    : ""}
            </td>
        </tr>
    `).join("");
}

function abrirModalProcesar(muestraId) {
    document.getElementById("alertaModalProcesar").innerHTML = "";
    document.getElementById("procesarMuestraId").value = muestraId;
    document.getElementById("procesarAnalizador").value = "";
    document.getElementById("procesarProfesional").value = "";
    document.getElementById("procesarObservaciones").value = "";
    new bootstrap.Modal(document.getElementById("modalProcesar")).show();
}

async function guardarProcesar() {
    const muestra_id = parseInt(document.getElementById("procesarMuestraId").value, 10);
    const analizador = document.getElementById("procesarAnalizador").value;
    const profesionalSelect = document.getElementById("procesarProfesional");
    const profesional_id = profesionalSelect.value ? parseInt(profesionalSelect.value, 10) : null;
    const observaciones = document.getElementById("procesarObservaciones").value || null;

    if (!analizador) {
        alertaProc("alertaModalProcesar", "Indique el analizador o equipo usado.");
        return;
    }

    try {
        const resp = await fetch("/procesamientos/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ muestra_id, analizador, profesional_id, observaciones }),
        });

        if (!resp.ok) {
                        alertaProc("alertaModalProcesar", await extraerMensajeError(resp, "No se pudo iniciar el procesamiento."));
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById("modalProcesar")).hide();
        await cargarDatos();
    } catch (error) {
        alertaProc("alertaModalProcesar", "Error de conexión al iniciar el procesamiento.");
    }
}

async function completarProcesamiento(procesamientoId) {
    try {
        const resp = await fetch(`/procesamientos/${procesamientoId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                estado: "COMPLETADO",
                fecha_fin: new Date().toISOString(),
            }),
        });

        if (!resp.ok) {
            alert("No se pudo marcar como completado.");
            return;
        }

        await cargarDatos();
    } catch (error) {
        alert("Error de conexión.");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    cargarDatos();
    document.getElementById("btnGuardarProcesar").addEventListener("click", guardarProcesar);
});
