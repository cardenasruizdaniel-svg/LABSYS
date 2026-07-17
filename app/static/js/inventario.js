/******************************************************************************
 * LABSYS DIALIZAR
 * app/static/js/inventario.js
 ******************************************************************************/

let itemsCache = [];

function alerta(id, mensaje, tipo = "danger") {
    document.getElementById(id).innerHTML = `<div class="alert alert-${tipo} py-2">${mensaje}</div>`;
}

function badgeCategoria(cat) {
    const colores = { REACTIVO: "info", INSUMO: "primary", EQUIPO: "secondary", OTRO: "dark" };
    return `<span class="badge bg-${colores[cat] || "secondary"}">${cat}</span>`;
}

async function cargarItems() {
    try {
        const resp = await fetch("/inventario/items");
        itemsCache = resp.ok ? await resp.json() : [];

        const tbody = document.getElementById("tablaItems");
        if (!itemsCache.length) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-muted small">No hay ítems registrados todavía.</td></tr>';
        } else {
            tbody.innerHTML = itemsCache.map(item => {
                const bajo = parseFloat(item.stock_actual) <= parseFloat(item.stock_minimo);
                return `
                    <tr class="${bajo ? 'table-warning' : ''}">
                        <td>${item.codigo}</td>
                        <td>${item.nombre}</td>
                        <td>${badgeCategoria(item.categoria)}</td>
                        <td>${item.stock_actual} ${item.unidad_medida} ${bajo ? '<i class="bi bi-exclamation-triangle-fill text-warning" title="Stock bajo"></i>' : ''}</td>
                        <td>${item.stock_minimo}</td>
                        <td>${item.fecha_vencimiento || '-'}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-secondary" onclick="verMovimientos(${item.id})">
                                <i class="bi bi-clock-history"></i>
                            </button>
                        </td>
                    </tr>`;
            }).join("");
        }

        const selectMov = document.getElementById("movItem");
        selectMov.innerHTML = itemsCache.map(i => `<option value="${i.id}">${i.nombre} (${i.codigo})</option>`).join("");

        await cargarStockBajo();
    } catch (error) {
        alerta("alertaInventario", "No se pudieron cargar los ítems de inventario.");
    }
}

async function cargarStockBajo() {
    try {
        const resp = await fetch("/inventario/items/stock-bajo");
        const bajos = resp.ok ? await resp.json() : [];

        if (bajos.length) {
            const nombres = bajos.map(i => i.nombre).join(", ");
            alerta("alertaStockBajo", `<i class="bi bi-exclamation-triangle-fill"></i> Stock bajo en: ${nombres}`, "warning");
        } else {
            document.getElementById("alertaStockBajo").innerHTML = "";
        }
    } catch (error) {
        // silencioso
    }
}

function verMovimientos(itemId) {
    window.open(`/inventario/movimientos?item_id=${itemId}`, "_blank");
}

async function guardarItem() {
    const payload = {
        codigo: document.getElementById("itemCodigo").value,
        nombre: document.getElementById("itemNombre").value,
        categoria: document.getElementById("itemCategoria").value,
        unidad_medida: document.getElementById("itemUnidad").value,
        stock_inicial: parseFloat(document.getElementById("itemStockInicial").value || 0),
        stock_minimo: parseFloat(document.getElementById("itemStockMinimo").value || 0),
        proveedor: document.getElementById("itemProveedor").value || null,
        fecha_vencimiento: document.getElementById("itemVencimiento").value || null,
    };

    if (!payload.codigo || !payload.nombre || !payload.unidad_medida) {
        alerta("alertaModalItem", "Código, nombre y unidad de medida son obligatorios.");
        return;
    }

    try {
        const resp = await fetch("/inventario/items", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!resp.ok) {
                        alerta("alertaModalItem", await extraerMensajeError(resp, "No se pudo crear el ítem."));
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById("modalNuevoItem")).hide();
        await cargarItems();
    } catch (error) {
        alerta("alertaModalItem", "Error de conexión al crear el ítem.");
    }
}

async function guardarMovimiento() {
    const payload = {
        item_id: parseInt(document.getElementById("movItem").value, 10),
        tipo_movimiento: document.getElementById("movTipo").value,
        cantidad: parseFloat(document.getElementById("movCantidad").value || 0),
        motivo: document.getElementById("movMotivo").value,
        responsable: document.getElementById("movResponsable").value || null,
    };

    const costoInput = document.getElementById("movCosto").value;
    if (payload.tipo_movimiento === "ENTRADA" && costoInput) {
        payload.costo_total = parseFloat(costoInput);
    }

    if (!payload.item_id || !payload.motivo || payload.cantidad === undefined) {
        alerta("alertaModalMovimiento", "Ítem, cantidad y motivo son obligatorios.");
        return;
    }

    try {
        const resp = await fetch("/inventario/movimientos", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!resp.ok) {
                        alerta("alertaModalMovimiento", await extraerMensajeError(resp, "No se pudo registrar el movimiento."));
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById("modalMovimiento")).hide();
        await cargarItems();
    } catch (error) {
        alerta("alertaModalMovimiento", "Error de conexión al registrar el movimiento.");
    }
}

async function cargarCierres() {
    try {
        const resp = await fetch("/inventario/cierres");
        const cierres = resp.ok ? await resp.json() : [];

        const tbody = document.getElementById("tablaCierres");
        if (!cierres.length) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-muted small">Todavía no se ha ejecutado ningún cierre.</td></tr>';
            return;
        }

        tbody.innerHTML = cierres.map(c => `
            <tr>
                <td>${c.nombre_archivo}</td>
                <td class="small">${new Date(c.fecha_generado).toLocaleString("es-CO")}</td>
                <td class="small">${c.tamano_kb} KB</td>
                <td>
                    <a class="btn btn-sm btn-outline-secondary" href="/inventario/cierres/${c.nombre_archivo}/descargar">
                        <i class="bi bi-download"></i>
                    </a>
                </td>
            </tr>
        `).join("");
    } catch (error) {
        // silencioso
    }
}

async function ejecutarCierreMes() {
    if (!confirm("¿Ejecutar el cierre de mes ahora? Esto archiva y borra los movimientos de inventario de meses anteriores. Esta acción no se puede deshacer.")) return;

    try {
        const resp = await fetch("/inventario/cierre-mes", { method: "POST" });

        if (!resp.ok) {
            alerta("alertaCierreMes", await extraerMensajeError(resp, "No se pudo ejecutar el cierre de mes."));
            return;
        }

        const resultado = await resp.json();
        alerta("alertaCierreMes", resultado.mensaje, resultado.archivado > 0 ? "success" : "secondary");
        await cargarCierres();
    } catch (error) {
        alerta("alertaCierreMes", "Error de conexión al ejecutar el cierre.");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    cargarItems();

    document.getElementById("btnNuevoItem").addEventListener("click", () => {
        document.getElementById("alertaModalItem").innerHTML = "";
        ["itemCodigo","itemNombre","itemUnidad","itemProveedor","itemVencimiento"].forEach(id => document.getElementById(id).value = "");
        document.getElementById("itemStockInicial").value = 0;
        document.getElementById("itemStockMinimo").value = 0;
        new bootstrap.Modal(document.getElementById("modalNuevoItem")).show();
    });

    document.getElementById("btnNuevoMovimiento").addEventListener("click", () => {
        document.getElementById("alertaModalMovimiento").innerHTML = "";
        document.getElementById("movCantidad").value = "";
        document.getElementById("movMotivo").value = "";
        document.getElementById("movResponsable").value = "";
        document.getElementById("movCosto").value = "";
        document.getElementById("grupoCostoMovimiento").style.display =
            document.getElementById("movTipo").value === "ENTRADA" ? "block" : "none";
        new bootstrap.Modal(document.getElementById("modalMovimiento")).show();
    });

    document.getElementById("movTipo").addEventListener("change", (e) => {
        document.getElementById("labelCantidad").textContent =
            e.target.value === "AJUSTE" ? "Nuevo stock (conteo físico)" : "Cantidad";
        document.getElementById("grupoCostoMovimiento").style.display =
            e.target.value === "ENTRADA" ? "block" : "none";
    });

    document.getElementById("btnGuardarItem").addEventListener("click", guardarItem);
    document.getElementById("btnGuardarMovimiento").addEventListener("click", guardarMovimiento);

    document.getElementById("btnCierreMes").addEventListener("click", () => {
        document.getElementById("alertaCierreMes").innerHTML = "";
        cargarCierres();
        new bootstrap.Modal(document.getElementById("modalCierreMes")).show();
    });

    document.getElementById("btnConfirmarCierreMes").addEventListener("click", ejecutarCierreMes);
});
