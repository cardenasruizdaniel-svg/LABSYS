/******************************************************************************
 * LABSYS DIALIZAR
 * app/static/js/convenios.js
 ******************************************************************************/

let epsCacheConv = [];
let conveniosTodosCache = [];

function alertaConv(id, mensaje, tipo = "danger") {
    document.getElementById(id).innerHTML = `<div class="alert alert-${tipo} py-2">${mensaje}</div>`;
}

function nombreEpsDe(id) {
    const e = epsCacheConv.find(x => x.id === id);
    return e ? e.nombre : `#${id}`;
}

function descripcionCopago(c) {
    if (c.tipo_copago === "NINGUNO") return '<span class="badge bg-success">Sin copago</span>';
    if (c.tipo_copago === "FIJO") return `<span class="badge bg-warning text-dark">Fijo: $${Number(c.valor_copago).toLocaleString("es-CO")}</span>`;
    return `<span class="badge bg-info text-dark">${c.valor_copago}% del total</span>`;
}

async function cargarCatalogoEpsConvenio() {
    const resp = await fetch("/eps/");
    epsCacheConv = resp.ok ? await resp.json() : [];
    document.getElementById("convenioEps").innerHTML = '<option value="">Seleccione...</option>' +
        epsCacheConv.map(e => `<option value="${e.id}">${e.nombre}</option>`).join("");
}

async function cargarConvenios() {
    try {
        const resp = await fetch("/convenios/");
        conveniosTodosCache = resp.ok ? await resp.json() : [];

        const tbody = document.getElementById("tablaConvenios");
        if (!conveniosTodosCache.length) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-muted small">No hay convenios registrados todavía.</td></tr>';
            return;
        }

        tbody.innerHTML = conveniosTodosCache.map(c => `
            <tr>
                <td>${c.codigo}</td>
                <td>${c.nombre}</td>
                <td>${nombreEpsDe(c.eps_id)}</td>
                <td>${descripcionCopago(c)}</td>
                <td class="small">${c.fecha_inicio}${c.fecha_fin ? ' a ' + c.fecha_fin : ' (indefinido)'}</td>
                <td>
                    <button class="btn btn-sm btn-outline-secondary" onclick="editarConvenio(${c.id})">
                        <i class="bi bi-pencil"></i> Editar
                    </button>
                </td>
            </tr>
        `).join("");
    } catch (error) {
        alertaConv("alertaConvenios", "No se pudo cargar el listado de convenios.");
    }
}

function limpiarFormularioConvenio() {
    document.getElementById("alertaModalConvenio").innerHTML = "";
    document.getElementById("convenioId").value = "";
    document.getElementById("convenioEps").value = "";
    document.getElementById("convenioCodigo").value = "";
    document.getElementById("convenioCodigo").disabled = false;
    document.getElementById("convenioNombre").value = "";
    document.getElementById("convenioFechaInicio").value = (() => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")}`; })();
    document.getElementById("convenioFechaFin").value = "";
    document.getElementById("convenioTipoCopago").value = "NINGUNO";
    document.getElementById("convenioValorCopago").value = "0";
    document.getElementById("convenioObservaciones").value = "";
}

function editarConvenio(id) {
    const c = conveniosTodosCache.find(x => x.id === id);
    if (!c) return;

    limpiarFormularioConvenio();
    document.getElementById("tituloModalConvenio").textContent = "Editar convenio";
    document.getElementById("convenioId").value = c.id;
    document.getElementById("convenioEps").value = c.eps_id;
    document.getElementById("convenioCodigo").value = c.codigo;
    document.getElementById("convenioCodigo").disabled = true;
    document.getElementById("convenioNombre").value = c.nombre;
    document.getElementById("convenioFechaInicio").value = c.fecha_inicio;
    document.getElementById("convenioFechaFin").value = c.fecha_fin || "";
    document.getElementById("convenioTipoCopago").value = c.tipo_copago;
    document.getElementById("convenioValorCopago").value = c.valor_copago;
    document.getElementById("convenioObservaciones").value = c.observaciones || "";

    new bootstrap.Modal(document.getElementById("modalConvenio")).show();
}

async function guardarConvenio() {
    const id = document.getElementById("convenioId").value;
    const esEdicion = !!id;

    const payload = {
        eps_id: parseInt(document.getElementById("convenioEps").value, 10),
        codigo: document.getElementById("convenioCodigo").value,
        nombre: document.getElementById("convenioNombre").value,
        fecha_inicio: document.getElementById("convenioFechaInicio").value,
        fecha_fin: document.getElementById("convenioFechaFin").value || null,
        tipo_copago: document.getElementById("convenioTipoCopago").value,
        valor_copago: parseFloat(document.getElementById("convenioValorCopago").value || 0),
        observaciones: document.getElementById("convenioObservaciones").value || null,
    };

    if (!payload.eps_id || !payload.codigo || !payload.nombre || !payload.fecha_inicio) {
        alertaConv("alertaModalConvenio", "EPS, código, nombre y fecha de inicio son obligatorios.");
        return;
    }

    if (esEdicion) payload.activo = true;

    try {
        const resp = await fetch(esEdicion ? `/convenios/${id}` : "/convenios/", {
            method: esEdicion ? "PUT" : "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!resp.ok) {
            alertaConv("alertaModalConvenio", await extraerMensajeError(resp, "No se pudo guardar el convenio."));
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById("modalConvenio")).hide();
        await cargarConvenios();
    } catch (error) {
        alertaConv("alertaModalConvenio", "Error de conexión al guardar.");
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    await cargarCatalogoEpsConvenio();
    await cargarConvenios();

    document.getElementById("btnNuevoConvenio").addEventListener("click", () => {
        limpiarFormularioConvenio();
        document.getElementById("tituloModalConvenio").textContent = "Nuevo convenio";
        new bootstrap.Modal(document.getElementById("modalConvenio")).show();
    });

    document.getElementById("btnGuardarConvenio").addEventListener("click", guardarConvenio);

    document.getElementById("convenioTipoCopago").addEventListener("change", (e) => {
        document.getElementById("labelValorCopago").textContent =
            e.target.value === "PORCENTAJE" ? "Porcentaje (0-100)" : "Valor en pesos";
    });
});
