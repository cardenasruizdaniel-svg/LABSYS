/******************************************************************************
 * LABSYS DIALIZAR
 * app/static/js/muestras.js
 ******************************************************************************/

let ordenesCacheMuestras = [];

function alertaMuestras(id, mensaje, tipo = "danger") {
    document.getElementById(id).innerHTML = `<div class="alert alert-${tipo} py-2">${mensaje}</div>`;
}

function numeroOrdenDe(id) {
    const o = ordenesCacheMuestras.find(x => x.id === id);
    return o ? o.numero_orden : `#${id}`;
}

async function cargarCatalogosMuestra() {
    const [ordenesR, enfermerasR] = await Promise.all([
        fetch("/ordenes/"),
        fetch("/medicos/?tipo=ENFERMERO"),
    ]);

    ordenesCacheMuestras = ordenesR.ok ? await ordenesR.json() : [];
    const enfermeras = enfermerasR.ok ? await enfermerasR.json() : [];

    document.getElementById("muestraOrden").innerHTML = '<option value="">Seleccione...</option>' +
        ordenesCacheMuestras.map(o => `<option value="${o.id}">${o.numero_orden}</option>`).join("");

    document.getElementById("muestraEnfermera").innerHTML = '<option value="">Sin especificar</option>' +
        enfermeras.map(e => `<option value="${e.nombres} ${e.apellidos}">${e.nombres} ${e.apellidos}</option>`).join("");

    if (!enfermeras.length) {
        document.getElementById("muestraEnfermera").innerHTML +=
            '<option value="" disabled>(No hay enfermeras registradas — agréguelas en Médicos y Enfermeras)</option>';
    }
}

async function cargarMuestras() {
    try {
        const resp = await fetch("/muestras/");
        const muestras = resp.ok ? await resp.json() : [];

        const tbody = document.getElementById("tablaMuestras");
        if (!muestras.length) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-muted small">No hay muestras registradas todavía.</td></tr>';
            return;
        }

        const coloresEstado = { PENDIENTE: "secondary", EN_PROCESO: "primary", PROCESADA: "success", RECHAZADA: "danger" };

        tbody.innerHTML = muestras.map(m => `
            <tr>
                <td>${m.codigo_barras}</td>
                <td>${numeroOrdenDe(m.orden_id)}</td>
                <td>${m.tipo_muestra}</td>
                <td>${m.responsable_toma || '-'}</td>
                <td><span class="badge bg-${coloresEstado[m.estado] || 'secondary'}">${m.estado}</span></td>
                <td class="small">${new Date(m.fecha_toma).toLocaleString("es-CO")}</td>
            </tr>
        `).join("");
    } catch (error) {
        alertaMuestras("alertaMuestras", "No se pudieron cargar las muestras.");
    }
}

function generarCodigoBarras() {
    const ahora = new Date();
    return `M${ahora.getFullYear()}${String(ahora.getMonth() + 1).padStart(2, "0")}${String(ahora.getDate()).padStart(2, "0")}${Math.floor(Math.random() * 90000 + 10000)}`;
}

async function guardarMuestra() {
    const orden_id = document.getElementById("muestraOrden").value;
    const codigo_barras = document.getElementById("muestraCodigoBarras").value.trim() || generarCodigoBarras();
    const tipo_muestra = document.getElementById("muestraTipo").value;
    const recipiente = document.getElementById("muestraRecipiente").value || null;
    const responsable_toma = document.getElementById("muestraEnfermera").value || null;

    if (!orden_id) {
        alertaMuestras("alertaModalMuestra", "Seleccione la orden a la que pertenece la muestra.");
        return;
    }

    try {
        const resp = await fetch("/muestras/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                orden_id: parseInt(orden_id, 10),
                codigo_barras,
                tipo_muestra,
                recipiente,
                responsable_toma,
            }),
        });

        if (!resp.ok) {
                        alertaMuestras("alertaModalMuestra", await extraerMensajeError(resp, "No se pudo registrar la muestra."));
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById("modalNuevaMuestra")).hide();
        await cargarMuestras();
    } catch (error) {
        alertaMuestras("alertaModalMuestra", "Error de conexión al registrar la muestra.");
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    await cargarCatalogosMuestra();
    await cargarMuestras();

    document.getElementById("btnNuevaMuestra").addEventListener("click", () => {
        document.getElementById("alertaModalMuestra").innerHTML = "";
        document.getElementById("muestraOrden").value = "";
        document.getElementById("muestraCodigoBarras").value = "";
        document.getElementById("muestraRecipiente").value = "";
        document.getElementById("muestraEnfermera").value = "";
        new bootstrap.Modal(document.getElementById("modalNuevaMuestra")).show();
    });

    document.getElementById("btnGuardarMuestra").addEventListener("click", guardarMuestra);
});
