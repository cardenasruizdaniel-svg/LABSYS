/******************************************************************************
 * LABSYS DIALIZAR
 * app/static/js/gastos.js
 ******************************************************************************/

let gastosCache = [];
let categoriasCache = [];

function formatoMonedaG(v) {
    return new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 }).format(v || 0);
}

function alertaG(id, msg, tipo = "danger") {
    document.getElementById(id).innerHTML = `<div class="alert alert-${tipo} py-2">${msg}</div>`;
}

function badgeCategoriaG(cat) {
    const colores = {
        "Insumos médicos": "primary", "Reactivos": "info", "Papelería y oficina": "secondary",
        "Aseo y limpieza": "success", "Mantenimiento equipos": "warning",
        "Servicios públicos": "dark", "Arriendo": "danger", "Nómina y prestaciones": "primary",
        "Transporte y logística": "info", "Capacitación": "purple",
        "Imprevistos": "danger", "Otros": "secondary"
    };
    return `<span class="badge bg-${colores[cat] || "secondary"}">${cat}</span>`;
}

async function cargarCategorias() {
    try {
        const resp = await fetch("/gastos/categorias");
        const data = resp.ok ? await resp.json() : { categorias: [] };
        categoriasCache = data.categorias;
        document.getElementById("gastoCategoria").innerHTML =
            '<option value="">Seleccione...</option>' +
            categoriasCache.map(c => `<option value="${c}">${c}</option>`).join("");
    } catch (e) { /* silent */ }
}

async function cargarGastos() {
    try {
        const resp = await fetch("/gastos/");
        gastosCache = resp.ok ? await resp.json() : [];
        renderTabla();
        await cargarResumen();
    } catch (e) {
        alertaG("alertaGastos", "No se pudieron cargar los gastos.");
    }
}

function renderTabla() {
    const tbody = document.getElementById("tablaGastos");
    if (!gastosCache.length) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-muted small">No hay gastos registrados todavía.</td></tr>';
        return;
    }

    tbody.innerHTML = gastosCache.map(g => {
        const fecha = new Date(g.fecha_gasto).toLocaleDateString("es-CO");
        return `
        <tr>
            <td class="small">${fecha}</td>
            <td>${badgeCategoriaG(g.categoria)}</td>
            <td>${g.descripcion}</td>
            <td>${g.proveedor || "—"}</td>
            <td class="fw-bold text-danger">${formatoMonedaG(g.valor)}</td>
            <td>
                <button class="btn btn-sm btn-outline-secondary" onclick="editarGasto(${g.id})" title="Editar">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="eliminarGasto(${g.id})" title="Eliminar">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        </tr>`;
    }).join("");
}

async function cargarResumen() {
    try {
        const resp = await fetch("/gastos/resumen-hoy");
        const data = resp.ok ? await resp.json() : { total_gastos_hoy: 0, por_categoria: [] };
        document.getElementById("totalGastosHoy").textContent = formatoMonedaG(data.total_gastos_hoy);

        const panel = document.getElementById("resumenCategorias");
        if (!data.por_categoria.length) {
            panel.innerHTML = '<div class="text-muted small">Sin gastos registrados.</div>';
            return;
        }

        const maxVal = Math.max(...data.por_categoria.map(c => Number(c.total)));
        panel.innerHTML = data.por_categoria.map(c => {
            const pct = maxVal > 0 ? (Number(c.total) / maxVal * 100) : 0;
            return `
            <div class="d-flex align-items-center mb-2">
                <div style="width:140px" class="small">${badgeCategoriaG(c.categoria)}</div>
                <div class="flex-grow-1 mx-2">
                    <div class="progress" style="height:20px">
                        <div class="progress-bar bg-danger" style="width:${pct}%"></div>
                    </div>
                </div>
                <div class="fw-bold small" style="width:100px;text-align:right">${formatoMonedaG(c.total)}</div>
            </div>`;
        }).join("");
    } catch (e) { /* silent */ }
}

function abrirModalGasto(gasto = null) {
    document.getElementById("alertaModalGasto").innerHTML = "";
    document.getElementById("gastoId").value = "";
    document.getElementById("gastoCategoria").value = "";
    document.getElementById("gastoValor").value = "";
    document.getElementById("gastoDescripcion").value = "";
    document.getElementById("gastoProveedor").value = "";
    document.getElementById("gastoObservaciones").value = "";

    if (gasto) {
        document.getElementById("tituloModalGasto").textContent = "Editar gasto";
        document.getElementById("gastoId").value = gasto.id;
        document.getElementById("gastoCategoria").value = gasto.categoria;
        document.getElementById("gastoValor").value = gasto.valor;
        document.getElementById("gastoDescripcion").value = gasto.descripcion;
        document.getElementById("gastoProveedor").value = gasto.proveedor || "";
        document.getElementById("gastoObservaciones").value = gasto.observaciones || "";
    } else {
        document.getElementById("tituloModalGasto").textContent = "Nuevo gasto";
    }

    new bootstrap.Modal(document.getElementById("modalNuevoGasto")).show();
}

function editarGasto(id) {
    const g = gastosCache.find(x => x.id === id);
    if (g) abrirModalGasto(g);
}

async function guardarGasto() {
    const id = document.getElementById("gastoId").value;
    const payload = {
        categoria: document.getElementById("gastoCategoria").value,
        descripcion: document.getElementById("gastoDescripcion").value.trim(),
        valor: parseFloat(document.getElementById("gastoValor").value || 0),
        proveedor: document.getElementById("gastoProveedor").value.trim() || null,
        observaciones: document.getElementById("gastoObservaciones").value.trim() || null,
    };

    if (!payload.categoria || !payload.descripcion || !payload.valor) {
        alertaG("alertaModalGasto", "Categoría, descripción y valor son obligatorios.");
        return;
    }

    try {
        const esEdicion = !!id;
        const url = esEdicion ? `/gastos/${id}` : "/gastos/";
        const metodo = esEdicion ? "PUT" : "POST";
        const resp = await fetch(url, {
            method: metodo,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!resp.ok) {
            alertaG("alertaModalGasto", await extraerMensajeError(resp, "No se pudo guardar el gasto."));
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById("modalNuevoGasto")).hide();
        await cargarGastos();
    } catch (e) {
        alertaG("alertaModalGasto", "Error de conexión al guardar.");
    }
}

async function eliminarGasto(id) {
    if (!confirm("¿Está seguro de eliminar este gasto?")) return;
    try {
        const resp = await fetch(`/gastos/${id}`, { method: "DELETE" });
        if (!resp.ok) {
            alertaG("alertaGastos", await extraerMensajeError(resp, "No se pudo eliminar."));
            return;
        }
        await cargarGastos();
    } catch (e) {
        alertaG("alertaGastos", "Error de conexión al eliminar.");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    cargarCategorias();
    cargarGastos();

    document.getElementById("btnNuevoGasto").addEventListener("click", () => abrirModalGasto());
    document.getElementById("btnGuardarGasto").addEventListener("click", guardarGasto);
});
