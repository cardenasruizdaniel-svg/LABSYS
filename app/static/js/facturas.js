/******************************************************************************
 * LABSYS DIALIZAR
 * app/static/js/facturas.js
 ******************************************************************************/

function alertaCaja(id, mensaje, tipo = "danger") {
    document.getElementById(id).innerHTML = `<div class="alert alert-${tipo} py-2">${mensaje}</div>`;
}

async function cargarEstadoCaja() {
    try {
        const resp = await fetch("/caja/estado");
        const estado = resp.ok ? await resp.json() : { hay_caja_abierta: false };

        const panel = document.getElementById("panelCaja");
        const botones = document.getElementById("botonesCaja");

        if (!estado.hay_caja_abierta) {
            panel.innerHTML = '<p class="text-muted mb-0">No hay una caja abierta en este momento.</p>';
            botones.innerHTML = `
                <button class="btn btn-sm btn-success" id="btnAbrirCaja"><i class="bi bi-unlock"></i> Abrir caja</button>
                <button class="btn btn-sm btn-outline-secondary" id="btnVerHistorialCaja"><i class="bi bi-clock-history"></i> Historial</button>
            `;
        } else {
            const ing = estado.total_ingresos_manuales || 0;
            panel.innerHTML = `
                <div class="row text-center">
                    <div class="col"><div class="text-muted small">Monto inicial</div><div class="fw-bold">${formatoMoneda(estado.monto_inicial)}</div></div>
                    <div class="col"><div class="text-muted small">Copagos cobrados</div><div class="fw-bold text-success">${formatoMoneda(estado.total_copagos_cobrados)}</div></div>
                    <div class="col"><div class="text-muted small">Ingresos manuales</div><div class="fw-bold text-info">${formatoMoneda(ing)}</div></div>
                    <div class="col"><div class="text-muted small">Compras inventario</div><div class="fw-bold text-danger">-${formatoMoneda(estado.total_compras_inventario)}</div></div>
                    <div class="col"><div class="text-muted small">Gastos</div><div class="fw-bold text-danger">-${formatoMoneda(estado.total_gastos || 0)}</div></div>
                    <div class="col"><div class="text-muted small">Debería haber ahora</div><div class="fw-bold text-primary">${formatoMoneda(estado.monto_esperado_ahora)}</div></div>
                </div>
                <div class="text-muted small mt-2">Caja abierta desde: ${new Date(estado.fecha_apertura).toLocaleString("es-CO")}</div>
            `;
            botones.innerHTML = `
                <button class="btn btn-sm btn-info" id="btnIngresoCaja"><i class="bi bi-plus-circle"></i> Ingreso</button>
                <button class="btn btn-sm btn-danger" id="btnCerrarCaja"><i class="bi bi-lock"></i> Cerrar caja</button>
                <button class="btn btn-sm btn-outline-secondary" id="btnVerHistorialCaja"><i class="bi bi-clock-history"></i> Historial</button>
            `;
        }

        document.getElementById("btnVerHistorialCaja").addEventListener("click", abrirHistorialCaja);
        const btnAbrir = document.getElementById("btnAbrirCaja");
        if (btnAbrir) btnAbrir.addEventListener("click", () => {
            document.getElementById("alertaModalAbrirCaja").innerHTML = "";
            document.getElementById("cajaMontoInicial").value = "0";
            document.getElementById("cajaObservacionesApertura").value = "";
            new bootstrap.Modal(document.getElementById("modalAbrirCaja")).show();
        });
        const btnIngreso = document.getElementById("btnIngresoCaja");
        if (btnIngreso) btnIngreso.addEventListener("click", () => {
            document.getElementById("alertaModalIngreso").innerHTML = "";
            document.getElementById("ingresoOrigen").value = "";
            document.getElementById("ingresoValor").value = "";
            document.getElementById("ingresoDescripcion").value = "";
            new bootstrap.Modal(document.getElementById("modalIngresoCaja")).show();
        });
        const btnCerrar = document.getElementById("btnCerrarCaja");
        if (btnCerrar) btnCerrar.addEventListener("click", () => {
            document.getElementById("alertaModalCerrarCaja").innerHTML = "";
            document.getElementById("cajaObservacionesCierre").value = "";
            document.getElementById("resumenCierreCaja").innerHTML = `
                <div class="alert alert-secondary py-2 mb-0">
                    Monto esperado en caja ahora mismo: <strong>${formatoMoneda(estado.monto_esperado_ahora)}</strong>
                </div>`;
            construirDenominaciones();
            new bootstrap.Modal(document.getElementById("modalCerrarCaja")).show();
        });
    } catch (error) {
        document.getElementById("panelCaja").innerHTML = '<p class="text-danger mb-0">No se pudo cargar el estado de caja.</p>';
    }
}

async function confirmarAbrirCaja() {
    const monto_inicial = parseFloat(document.getElementById("cajaMontoInicial").value || 0);
    const observaciones = document.getElementById("cajaObservacionesApertura").value || null;

    try {
        const resp = await fetch("/caja/abrir", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ monto_inicial, observaciones }),
        });

        if (!resp.ok) {
            alertaCaja("alertaModalAbrirCaja", await extraerMensajeError(resp, "No se pudo abrir la caja."));
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById("modalAbrirCaja")).hide();
        await cargarEstadoCaja();
    } catch (error) {
        alertaCaja("alertaModalAbrirCaja", "Error de conexión al abrir la caja.");
    }
}

async function confirmarCerrarCaja() {
    const denominaciones = {};
    let totalContado = 0;

    document.querySelectorAll("#tablaBilletes tbody tr, #tablaMonedas tbody tr").forEach(row => {
        const denom = parseInt(row.dataset.denom, 10);
        const cantidad = parseInt(row.querySelector("input").value || 0, 10);
        const subtotal = denom * cantidad;
        denominaciones[denom] = cantidad;
        totalContado += subtotal;
    });

    const observaciones = document.getElementById("cajaObservacionesCierre").value || null;

    try {
        const resp = await fetch("/caja/cerrar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                monto_contado: totalContado,
                denominaciones,
                observaciones,
            }),
        });

        if (!resp.ok) {
            alertaCaja("alertaModalCerrarCaja", await extraerMensajeError(resp, "No se pudo cerrar la caja."));
            return;
        }

        const cierre = await resp.json();
        bootstrap.Modal.getInstance(document.getElementById("modalCerrarCaja")).hide();

        const diferencia = Number(cierre.diferencia);
        const mensaje = diferencia === 0
            ? "Caja cerrada correctamente, sin diferencias."
            : `Caja cerrada. Diferencia: ${formatoMoneda(diferencia)} ${diferencia > 0 ? "(sobra)" : "(falta)"}`;
        alertaCaja("alertaFacturas", mensaje, diferencia === 0 ? "success" : "warning");

        await cargarEstadoCaja();
    } catch (error) {
        alertaCaja("alertaModalCerrarCaja", "Error de conexión al cerrar la caja.");
    }
}

function construirDenominaciones() {
    const fmt = v => new Intl.NumberFormat("es-CO").format(v);

    function buildTabla(selector, lista) {
        const tbody = document.querySelector(`${selector} tbody`);
        tbody.innerHTML = lista.map(d => `
            <tr data-denom="${d}">
                <td class="fw-bold">$${fmt(d)}</td>
                <td><input type="number" min="0" value="0" class="form-control form-control-sm denom-input" style="width:70px"></td>
                <td class="text-end subtotal-cell">$0</td>
            </tr>
        `).join("");

        tbody.querySelectorAll(".denom-input").forEach(input => {
            input.addEventListener("input", () => {
                const tr = input.closest("tr");
                const denom = parseInt(tr.dataset.denom, 10);
                const cantidad = parseInt(input.value || 0, 10);
                tr.querySelector(".subtotal-cell").textContent = `$${fmt(denom * cantidad)}`;
                calcularTotalDenominaciones();
            });
        });
    }

    buildTabla("#tablaBilletes", DENOMINACIONES.billetes);
    buildTabla("#tablaMonedas", DENOMINACIONES.monedas);
    calcularTotalDenominaciones();
}

function calcularTotalDenominaciones() {
    let total = 0;
    document.querySelectorAll(".denom-input").forEach(input => {
        const tr = input.closest("tr");
        const denom = parseInt(tr.dataset.denom, 10);
        const cantidad = parseInt(input.value || 0, 10);
        total += denom * cantidad;
    });
    document.getElementById("totalDenominaciones").textContent = formatoMoneda(total);
}

async function abrirHistorialCaja() {
    const modal = new bootstrap.Modal(document.getElementById("modalHistorialCaja"));
    modal.show();

    try {
        const resp = await fetch("/caja/cierres");
        const cierres = resp.ok ? await resp.json() : [];

        const tbody = document.getElementById("tablaHistorialCaja");
        if (!cierres.length) {
            tbody.innerHTML = '<tr><td colspan="10" class="text-muted small">No hay cuadres de caja registrados todavía.</td></tr>';
            return;
        }

        tbody.innerHTML = cierres.map(c => {
            const dif = Number(c.diferencia);
            const difColor = dif === 0 ? '' : (dif > 0 ? 'text-success' : 'text-danger');
            const fecha = new Date(c.fecha_cierre).toLocaleDateString("es-CO");
            return `
            <tr>
                <td class="small">${fecha}</td>
                <td>${formatoMoneda(c.monto_esperado - c.total_copagos_cobrados - (c.total_ingresos_manuales || 0) + c.total_compras_inventario + c.total_gastos)}</td>
                <td>${formatoMoneda(c.total_ingresos_manuales || 0)}</td>
                <td>${formatoMoneda(c.total_copagos_cobrados)}</td>
                <td>${formatoMoneda(c.total_facturado)}</td>
                <td>${formatoMoneda(c.total_gastos)}</td>
                <td>${formatoMoneda(c.total_compras_inventario)}</td>
                <td>${formatoMoneda(c.monto_esperado)}</td>
                <td>${formatoMoneda(c.monto_contado)}</td>
                <td class="${difColor} fw-bold">${formatoMoneda(dif)}</td>
            </tr>`;
        }).join("");
    } catch (error) {
        document.getElementById("tablaHistorialCaja").innerHTML = '<tr><td colspan="10" class="text-danger small">Error al cargar el historial.</td></tr>';
    }
}

async function confirmarIngreso() {
    const valor = parseFloat(document.getElementById("ingresoValor").value || 0);
    const origen = document.getElementById("ingresoOrigen").value.trim();
    const descripcion = document.getElementById("ingresoDescripcion").value.trim() || null;

    if (!valor || valor <= 0) {
        document.getElementById("alertaModalIngreso").innerHTML = '<div class="alert alert-danger py-2">Ingrese un valor mayor a cero.</div>';
        return;
    }
    if (!origen) {
        document.getElementById("alertaModalIngreso").innerHTML = '<div class="alert alert-danger py-2">Debe indicar el origen del dinero.</div>';
        return;
    }

    try {
        const resp = await fetch("/caja/ingresos", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ valor, origen, descripcion }),
        });

        if (!resp.ok) {
            document.getElementById("alertaModalIngreso").innerHTML =
                `<div class="alert alert-danger py-2">${await extraerMensajeError(resp, "No se pudo registrar el ingreso.")}</div>`;
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById("modalIngresoCaja")).hide();
        await cargarEstadoCaja();
    } catch (e) {
        document.getElementById("alertaModalIngreso").innerHTML = '<div class="alert alert-danger py-2">Error de conexión.</div>';
    }
}

/* ======================================================================
   REPORTES DE CAJA
   ====================================================================== */

let reporteCajaActual = "cuadre";

function cambiarReporteCaja(tipo) {
    reporteCajaActual = tipo;
    document.querySelectorAll(".btn-group .btn").forEach(b => b.classList.remove("active"));
    const btnId = tipo === "rango" ? "btnRptRango" : "btnRpt" + tipo.charAt(0).toUpperCase() + tipo.slice(1);
    const btn = document.getElementById(btnId);
    if (btn) btn.classList.add("active");
    cargarReporteCaja();
}

async function cargarReporteCaja() {
    const panel = document.getElementById("panelReporteCaja");
    panel.innerHTML = '<div class="text-muted small">Cargando...</div>';
    try {
        if (reporteCajaActual === "cuadre") {
            await renderCuadreDia(panel);
        } else if (reporteCajaActual === "rango") {
            await renderResumenRango(panel);
        } else {
            await renderResumenPeriodo(panel, reporteCajaActual);
        }
    } catch (error) {
        panel.innerHTML = '<div class="alert alert-danger py-2">Error al cargar el reporte.</div>';
    }
}

async function renderResumenRango(panel) {
    const desde = document.getElementById("rptFechaDesde").value;
    const hasta = document.getElementById("rptFechaHasta").value;
    if (!desde || !hasta) {
        panel.innerHTML = '<div class="text-muted">Seleccione un rango de fechas.</div>';
        return;
    }
    const resp = await fetch(`/caja/resumen-rango?desde=${desde}&hasta=${hasta}`);
    if (!resp.ok) throw new Error("HTTP " + resp.status);
    const datos = await resp.json();
    const d = datos[0];
    if (!d) {
        panel.innerHTML = '<div class="text-muted">Sin datos para este período.</div>';
        return;
    }

    let html = `
    <h6 class="fw-bold mb-3">Reporte: ${d.periodo}</h6>
    <div class="row g-3 mb-3">
        <div class="col-md-3 col-6">
            <div class="card border-start border-4 border-primary h-100">
                <div class="card-body py-2">
                    <div class="text-muted small">Facturado</div>
                    <div class="fs-5 fw-bold text-primary">${formatoMoneda(d.facturado)}</div>
                    <div class="text-muted small">${d.cantidad_facturas} factura(s)</div>
                </div>
            </div>
        </div>
        <div class="col-md-3 col-6">
            <div class="card border-start border-4 border-success h-100">
                <div class="card-body py-2">
                    <div class="text-muted small">Copagos cobrados</div>
                    <div class="fs-5 fw-bold text-success">${formatoMoneda(d.copagos_cobrados)}</div>
                </div>
            </div>
        </div>
        <div class="col-md-3 col-6">
            <div class="card border-start border-4 border-danger h-100">
                <div class="card-body py-2">
                    <div class="text-muted small">Gastos</div>
                    <div class="fs-5 fw-bold text-danger">${formatoMoneda(d.gastos)}</div>
                    <div class="text-muted small">${d.cantidad_gastos} gasto(s)</div>
                </div>
            </div>
        </div>
        <div class="col-md-3 col-6">
            <div class="card border-start border-4 border-warning h-100">
                <div class="card-body py-2">
                    <div class="text-muted small">Compras inventario</div>
                    <div class="fs-5 fw-bold text-warning">${formatoMoneda(d.compras_inventario)}</div>
                </div>
            </div>
        </div>
    </div>`;

    if (d.gastos_por_categoria && d.gastos_por_categoria.length) {
        html += `<h6 class="fw-bold mt-3">Desglose de gastos</h6>
        <table class="table table-sm mb-0"><thead><tr><th>Categoría</th><th class="text-end">Total</th></tr></thead><tbody>`;
        d.gastos_por_categoria.forEach(gc => {
            html += `<tr><td>${gc.categoria}</td><td class="text-end">${formatoMoneda(gc.total)}</td></tr>`;
        });
        html += `<tr class="table-active fw-bold"><td>Total</td><td class="text-end">${formatoMoneda(d.gastos)}</td></tr></tbody></table>`;
    }

    panel.innerHTML = html;
}

async function renderCuadreDia(panel) {
    const resp = await fetch("/caja/cuadre-dia");
    if (!resp.ok) throw new Error("HTTP " + resp.status);
    const d = await resp.json();

    const f = d.facturacion || {};
    const c = d.copagos || {};
    const g = d.gastos || {};
    const ci = d.compras_inventario || {};
    const ing = d.ingresos_manuales || {};
    const cu = d.cuadre;

    let html = `
    <h6 class="fw-bold mb-3">Cuadre del día ${d.fecha}</h6>
    <div class="row g-3 mb-3">
        <div class="col-md-2 col-4">
            <div class="card border-start border-4 border-secondary h-100">
                <div class="card-body py-2">
                    <div class="text-muted small">M. Inicial</div>
                    <div class="fs-5 fw-bold">${formatoMoneda(d.monto_inicial)}</div>
                </div>
            </div>
        </div>
        <div class="col-md-2 col-4">
            <div class="card border-start border-4 border-primary h-100">
                <div class="card-body py-2">
                    <div class="text-muted small">Facturado</div>
                    <div class="fs-5 fw-bold text-primary">${formatoMoneda(f.total_facturado)}</div>
                    <div class="text-muted small">${f.cantidad_facturas} factura(s)</div>
                </div>
            </div>
        </div>
        <div class="col-md-2 col-4">
            <div class="card border-start border-4 border-success h-100">
                <div class="card-body py-2">
                    <div class="text-muted small">Copagos</div>
                    <div class="fs-5 fw-bold text-success">${formatoMoneda(c.total_cobrado)}</div>
                </div>
            </div>
        </div>
        <div class="col-md-2 col-4">
            <div class="card border-start border-4 border-info h-100">
                <div class="card-body py-2">
                    <div class="text-muted small">Ingresos</div>
                    <div class="fs-5 fw-bold text-info">${formatoMoneda(ing.total)}</div>
                    <div class="text-muted small">${ing.cantidad || 0} ingreso(s)</div>
                </div>
            </div>
        </div>
        <div class="col-md-2 col-4">
            <div class="card border-start border-4 border-danger h-100">
                <div class="card-body py-2">
                    <div class="text-muted small">Gastos</div>
                    <div class="fs-5 fw-bold text-danger">${formatoMoneda(g.total)}</div>
                    <div class="text-muted small">${g.cantidad} gasto(s)</div>
                </div>
            </div>
        </div>
        <div class="col-md-2 col-4">
            <div class="card border-start border-4 border-warning h-100">
                <div class="card-body py-2">
                    <div class="text-muted small">Compras</div>
                    <div class="fs-5 fw-bold text-warning">${formatoMoneda(ci.total)}</div>
                    <div class="text-muted small">${ci.cantidad} compra(s)</div>
                </div>
            </div>
        </div>
    </div>`;

    if (f.detalle && f.detalle.length) {
        html += `<h6 class="fw-bold mt-3">Facturas del día</h6>
        <div style="max-height:160px;overflow-y:auto" class="mb-3">
        <table class="table table-sm table-hover mb-0 small"><thead class="sticky-top bg-white"><tr><th>N.°</th><th>Estado</th><th class="text-end">Copago</th><th class="text-end">Total</th></tr></thead><tbody>`;
        f.detalle.forEach(fact => {
            html += `<tr><td>${fact.numero}</td><td><span class="badge bg-${fact.estado === 'PAGADO' ? 'success' : 'warning text-dark'}">${fact.estado}</span></td><td class="text-end">${formatoMoneda(fact.valor_copago)}</td><td class="text-end">${formatoMoneda(fact.total)}</td></tr>`;
        });
        html += `<tr class="table-active fw-bold"><td colspan="3">Total</td><td class="text-end">${formatoMoneda(f.total_facturado)}</td></tr></tbody></table></div>`;
    }

    if (ing.detalle && ing.detalle.length) {
        html += `<h6 class="fw-bold">Ingresos manuales</h6>
        <div style="max-height:120px;overflow-y:auto" class="mb-3">
        <table class="table table-sm table-hover mb-0 small"><thead class="sticky-top bg-white"><tr><th>Origen</th><th>Descripción</th><th class="text-right">Valor</th></tr></thead><tbody>`;
        ing.detalle.forEach(ingr => {
            html += `<tr><td>${ingr.origen}</td><td>${ingr.descripcion || "—"}</td><td class="text-end">${formatoMoneda(ingr.valor)}</td></tr>`;
        });
        html += `<tr class="table-active fw-bold"><td colspan="2">Total</td><td class="text-end">${formatoMoneda(ing.total)}</td></tr></tbody></table></div>`;
    }

    if (g.detalle && g.detalle.length) {
        html += `<h6 class="fw-bold">Gastos del día</h6>
        <div style="max-height:120px;overflow-y:auto" class="mb-3">
        <table class="table table-sm table-hover mb-0 small"><thead class="sticky-top bg-white"><tr><th>Categoría</th><th>Descripción</th><th>Proveedor</th><th class="text-end">Valor</th></tr></thead><tbody>`;
        g.detalle.forEach(gas => {
            html += `<tr><td>${gas.categoria}</td><td>${gas.descripcion}</td><td>${gas.proveedor || "—"}</td><td class="text-end">${formatoMoneda(gas.valor)}</td></tr>`;
        });
        html += `<tr class="table-active fw-bold"><td colspan="3">Total</td><td class="text-end">${formatoMoneda(g.total)}</td></tr></tbody></table></div>`;
    }

    if (ci.detalle && ci.detalle.length) {
        html += `<h6 class="fw-bold">Compras de inventario</h6>
        <div style="max-height:120px;overflow-y:auto" class="mb-3">
        <table class="table table-sm table-hover mb-0 small"><thead class="sticky-top bg-white"><tr><th>Descripción</th><th class="text-end">Costo</th></tr></thead><tbody>`;
        ci.detalle.forEach(comp => {
            html += `<tr><td>${comp.descripcion}</td><td class="text-end">${formatoMoneda(comp.costo_total)}</td></tr>`;
        });
        html += `<tr class="table-active fw-bold"><td>Total</td><td class="text-end">${formatoMoneda(ci.total)}</td></tr></tbody></table></div>`;
    }

    html += `
    <div class="card bg-light mt-2">
        <div class="card-body py-2">
            <div class="row text-center">
                <div class="col"><div class="text-muted small">M. Inicial</div><div class="fw-bold">${formatoMoneda(d.monto_inicial)}</div></div>
                <div class="col"><div class="text-muted small">(+) Copagos</div><div class="fw-bold text-success">${formatoMoneda(c.total_cobrado)}</div></div>
                <div class="col"><div class="text-muted small">(+) Ingresos</div><div class="fw-bold text-info">${formatoMoneda(ing.total)}</div></div>
                <div class="col"><div class="text-muted small">(-) Compras</div><div class="fw-bold text-danger">-${formatoMoneda(ci.total)}</div></div>
                <div class="col"><div class="text-muted small">(-) Gastos</div><div class="fw-bold text-danger">-${formatoMoneda(g.total)}</div></div>
                <div class="col"><div class="text-muted small">Debe haber</div><div class="fw-bold text-primary">${formatoMoneda(d.monto_esperado_calculado)}</div></div>
            </div>
        </div>
    </div>`;

    if (cu) {
        const dif = cu.diferencia || 0;
        const difColor = dif === 0 ? "success" : (dif > 0 ? "primary" : "danger");
        html += `
        <div class="card bg-light mt-2">
            <div class="card-body py-2">
                <div class="row text-center">
                    <div class="col"><div class="text-muted small">M. Esperado (sistema)</div><div class="fw-bold">${formatoMoneda(cu.monto_esperado)}</div></div>
                    <div class="col"><div class="text-muted small">M. Contado (físico)</div><div class="fw-bold">${formatoMoneda(cu.monto_contado)}</div></div>
                    <div class="col"><div class="text-muted small">Diferencia</div><div class="fw-bold text-${difColor}">${formatoMoneda(dif)}</div></div>
                </div>
            </div>
        </div>`;
    } else {
        html += '<div class="alert alert-secondary py-2 mb-0 mt-2">No hay cuadre de caja registrado para este día.</div>';
    }

    panel.innerHTML = html;
}

async function renderResumenPeriodo(panel, agrupacion) {
    const resp = await fetch(`/caja/resumen?agrupacion=${agrupacion}`);
    if (!resp.ok) throw new Error("HTTP " + resp.status);
    const datos = await resp.json();

    if (!datos.length) {
        panel.innerHTML = '<div class="text-muted">Sin datos para este período.</div>';
        return;
    }

    const colores = ["primary", "success", "danger", "warning"];
    const colLabels = { dia: "Fecha", semana: "Semana", mes: "Mes", anio: "Año" };
    const labelCol = colLabels[agrupacion] || "Período";

    let html = `
    <h6 class="fw-bold mb-3">Resumen por ${agrupacion}</h6>
    <div style="overflow-x: auto;">
        <table class="table table-hover table-sm align-middle mb-0">
            <thead>
                <tr>
                    <th>${labelCol}</th>
                    <th class="text-end">Facturado</th>
                    <th class="text-end">Copagos</th>
                    <th class="text-end">Gastos</th>
                    <th class="text-end">Compras</th>
                    <th class="text-end"># Facturas</th>
                </tr>
            </thead>
            <tbody>`;

    let totales = { facturado: 0, copagos: 0, gastos: 0, compras: 0, facturas: 0 };
    datos.forEach(d => {
        totales.facturado += d.facturado;
        totales.copagos += d.copagos_cobrados;
        totales.gastos += d.gastos;
        totales.compras += d.compras_inventario;
        totales.facturas += d.cantidad_facturas;
        html += `
            <tr>
                <td class="fw-semibold">${d.periodo}</td>
                <td class="text-end">${formatoMoneda(d.facturado)}</td>
                <td class="text-end">${formatoMoneda(d.copagos_cobrados)}</td>
                <td class="text-end">${formatoMoneda(d.gastos)}</td>
                <td class="text-end">${formatoMoneda(d.compras_inventario)}</td>
                <td class="text-end">${d.cantidad_facturas}</td>
            </tr>`;
    });

    html += `
                <tr class="table-active fw-bold">
                    <td>TOTAL</td>
                    <td class="text-end">${formatoMoneda(totales.facturado)}</td>
                    <td class="text-end">${formatoMoneda(totales.copagos)}</td>
                    <td class="text-end">${formatoMoneda(totales.gastos)}</td>
                    <td class="text-end">${formatoMoneda(totales.compras)}</td>
                    <td class="text-end">${totales.facturas}</td>
                </tr>
            </tbody>
        </table>
    </div>`;

    panel.innerHTML = html;
}

/* ======================================================================
   IMPRESIÓN DE REPORTES
   ====================================================================== */

function imprimirResumen() {
    if (reporteCajaActual === "cuadre") {
        imprimirCuadreDia();
    } else {
        imprimirResumenPeriodo();
    }
}

function abrirVentanaImpresionReporte(titulo, contenidoHtml) {
    const win = window.open("", "_blank");
    win.document.write(`<!DOCTYPE html>
<html><head><title>${titulo}</title>
<style>
    @page { size: letter; margin: 15mm; }
    @media print { body { margin: 0; padding: 0; } }
    * { box-sizing: border-box; }
    body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 11px; color: #222; }
    h2 { font-size: 16px; margin: 0 0 4px; }
    h4 { font-size: 13px; margin: 0 0 8px; color: #555; }
    .header { text-align: center; margin-bottom: 12px; border-bottom: 2px solid #333; padding-bottom: 8px; }
    .header .lab-name { font-size: 18px; font-weight: bold; }
    .header .sub { font-size: 11px; color: #555; }
    table { width: 100%; border-collapse: collapse; margin-top: 8px; }
    th, td { border: 1px solid #ccc; padding: 4px 6px; text-align: left; }
    th { background: #f0f0f0; font-weight: 600; }
    .text-right { text-align: right; }
    .total-row { font-weight: bold; background: #e8e8e8; }
    .cards { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }
    .card-print { flex: 1; min-width: 140px; border: 1px solid #ccc; border-radius: 4px; padding: 8px; text-align: center; }
    .card-print .label { font-size: 10px; color: #666; }
    .card-print .value { font-size: 15px; font-weight: bold; }
    .footer { margin-top: 16px; font-size: 9px; color: #888; text-align: center; border-top: 1px solid #ccc; padding-top: 6px; }
</style>
</head><body>
${contenidoHtml}
<script>window.onload = function() { window.print(); };<\/script>
</body></html>`);
    win.document.close();
}

function imprimirCuadreDia() {
    fetch("/caja/cuadre-dia")
        .then(r => r.json())
        .then(d => {
            const f = d.facturacion || {};
            const c = d.copagos || {};
            const g = d.gastos || {};
            const ci = d.compras_inventario || {};
            const ing = d.ingresos_manuales || {};
            const cu = d.cuadre;

            let html = `
            <div class="header">
                <div class="lab-name">LABSYS DIALIZAR</div>
                <div class="sub">Cuadre de Caja del día ${d.fecha}</div>
            </div>
            <div class="cards">
                <div class="card-print"><div class="label">Monto inicial</div><div class="value">${formatoMoneda(d.monto_inicial)}</div></div>
                <div class="card-print"><div class="label">Facturado</div><div class="value">${formatoMoneda(f.total_facturado)}</div><div class="label">${f.cantidad_facturas} factura(s)</div></div>
                <div class="card-print"><div class="label">Copagos cobrados</div><div class="value">${formatoMoneda(c.total_cobrado)}</div></div>
                <div class="card-print"><div class="label">Ingresos manuales</div><div class="value">${formatoMoneda(ing.total)}</div><div class="label">${ing.cantidad || 0} ingreso(s)</div></div>
                <div class="card-print"><div class="label">Gastos</div><div class="value">${formatoMoneda(g.total)}</div><div class="label">${g.cantidad} gasto(s)</div></div>
                <div class="card-print"><div class="label">Compras inventario</div><div class="value">${formatoMoneda(ci.total)}</div><div class="label">${ci.cantidad} compra(s)</div></div>
            </div>`;

            if (f.detalle && f.detalle.length) {
                html += `<h4>Listado de Facturas (${f.cantidad_facturas})</h4>
                <table><thead><tr><th>N.° Factura</th><th>Estado</th><th class="text-right">Copago</th><th class="text-right">Total</th></tr></thead><tbody>`;
                f.detalle.forEach(fact => {
                    html += `<tr><td>${fact.numero}</td><td>${fact.estado}</td><td class="text-right">${formatoMoneda(fact.valor_copago)}</td><td class="text-right">${formatoMoneda(fact.total)}</td></tr>`;
                });
                html += `<tr class="total-row"><td colspan="3">Total facturado</td><td class="text-right">${formatoMoneda(f.total_facturado)}</td></tr></tbody></table>`;
            }

            if (ing.detalle && ing.detalle.length) {
                html += `<h4>Ingresos Manuales (${ing.cantidad})</h4>
                <table><thead><tr><th>Origen</th><th>Descripción</th><th class="text-right">Valor</th></tr></thead><tbody>`;
                ing.detalle.forEach(ingr => {
                    html += `<tr><td>${ingr.origen}</td><td>${ingr.descripcion || "—"}</td><td class="text-right">${formatoMoneda(ingr.valor)}</td></tr>`;
                });
                html += `<tr class="total-row"><td colspan="2">Total ingresos</td><td class="text-right">${formatoMoneda(ing.total)}</td></tr></tbody></table>`;
            }

            if (g.detalle && g.detalle.length) {
                html += `<h4>Listado de Gastos (${g.cantidad})</h4>
                <table><thead><tr><th>Categoría</th><th>Descripción</th><th>Proveedor</th><th class="text-right">Valor</th></tr></thead><tbody>`;
                g.detalle.forEach(gas => {
                    html += `<tr><td>${gas.categoria}</td><td>${gas.descripcion}</td><td>${gas.proveedor || "—"}</td><td class="text-right">${formatoMoneda(gas.valor)}</td></tr>`;
                });
                html += `<tr class="total-row"><td colspan="3">Total gastos</td><td class="text-right">${formatoMoneda(g.total)}</td></tr></tbody></table>`;
            }

            if (ci.detalle && ci.detalle.length) {
                html += `<h4>Listado de Compras de Inventario (${ci.cantidad})</h4>
                <table><thead><tr><th>Descripción</th><th class="text-right">Costo</th></tr></thead><tbody>`;
                ci.detalle.forEach(comp => {
                    html += `<tr><td>${comp.descripcion}</td><td class="text-right">${formatoMoneda(comp.costo_total)}</td></tr>`;
                });
                html += `<tr class="total-row"><td>Total compras</td><td class="text-right">${formatoMoneda(ci.total)}</td></tr></tbody></table>`;
            }

            html += `
            <h4>Cuadre de Caja</h4>
            <table>
                <tr><td>Monto inicial</td><td class="text-right">${formatoMoneda(d.monto_inicial)}</td></tr>
                <tr><td>(+) Copagos cobrados</td><td class="text-right">${formatoMoneda(c.total_cobrado)}</td></tr>
                <tr><td>(+) Ingresos manuales</td><td class="text-right">${formatoMoneda(ing.total)}</td></tr>
                <tr><td>(-) Compras inventario</td><td class="text-right">-${formatoMoneda(ci.total)}</td></tr>
                <tr><td>(-) Gastos</td><td class="text-right">-${formatoMoneda(g.total)}</td></tr>
                <tr class="total-row"><td>Total que debe haber en caja</td><td class="text-right">${formatoMoneda(d.monto_esperado_calculado)}</td></tr>
            </table>`;

            if (cu) {
                const dif = cu.diferencia || 0;
                const difColor = dif === 0 ? '' : (dif > 0 ? 'color:#198754' : 'color:#dc3545');
                html += `
                <table style="margin-top:8px">
                    <tr><td>Monto contado (físico)</td><td class="text-right">${formatoMoneda(cu.monto_contado)}</td></tr>
                    <tr class="total-row"><td>Diferencia</td><td class="text-right" style="${difColor}">${formatoMoneda(dif)}</td></tr>
                </table>`;
                if (cu.observaciones) {
                    html += `<p style="margin-top:8px"><strong>Observaciones:</strong> ${cu.observaciones}</p>`;
                }
            }

            html += `<div class="footer">Impreso el ${new Date().toLocaleString("es-CO")}</div>`;
            abrirVentanaImpresionReporte("Cuadre de Caja " + d.fecha, html);
        });
}

function imprimirResumenPeriodo() {
    const url = reporteCajaActual === "rango"
        ? `/caja/resumen-rango?desde=${document.getElementById("rptFechaDesde").value}&hasta=${document.getElementById("rptFechaHasta").value}`
        : `/caja/resumen?agrupacion=${reporteCajaActual}`;

    fetch(url)
        .then(r => r.json())
        .then(datos => {
            const d = Array.isArray(datos) ? datos[0] : datos;
            if (!d) return;

            const titulo = reporteCajaActual === "rango"
                ? `Reporte ${d.periodo}`
                : `Resumen por ${reporteCajaActual}`;

            let html = `
            <div class="header">
                <div class="lab-name">LABSYS DIALIZAR</div>
                <div class="sub">${titulo}</div>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Período</th>
                        <th class="text-right">Facturado</th>
                        <th class="text-right">Copagos</th>
                        <th class="text-right">Gastos</th>
                        <th class="text-right">Compras</th>
                        <th class="text-right"># Facturas</th>
                    </tr>
                </thead>
                <tbody>`;

            let totales = { facturado: 0, copagos: 0, gastos: 0, compras: 0, facturas: 0 };
            const rows = Array.isArray(datos) ? datos : [d];
            rows.forEach(r => {
                totales.facturado += r.facturado;
                totales.copagos += r.copagos_cobrados;
                totales.gastos += r.gastos;
                totales.compras += r.compras_inventario;
                totales.facturas += r.cantidad_facturas;
                html += `
                    <tr>
                        <td>${r.periodo}</td>
                        <td class="text-right">${formatoMoneda(r.facturado)}</td>
                        <td class="text-right">${formatoMoneda(r.copagos_cobrados)}</td>
                        <td class="text-right">${formatoMoneda(r.gastos)}</td>
                        <td class="text-right">${formatoMoneda(r.compras_inventario)}</td>
                        <td class="text-right">${r.cantidad_facturas}</td>
                    </tr>`;
            });

            html += `
                    <tr class="total-row">
                        <td>TOTAL</td>
                        <td class="text-right">${formatoMoneda(totales.facturado)}</td>
                        <td class="text-right">${formatoMoneda(totales.copagos)}</td>
                        <td class="text-right">${formatoMoneda(totales.gastos)}</td>
                        <td class="text-right">${formatoMoneda(totales.compras)}</td>
                        <td class="text-right">${totales.facturas}</td>
                    </tr>
                </tbody>
            </table>`;

            if (d.gastos_por_categoria && d.gastos_por_categoria.length) {
                html += `<h4>Desglose de gastos</h4><table><thead><tr><th>Categoría</th><th class="text-right">Total</th></tr></thead><tbody>`;
                d.gastos_por_categoria.forEach(gc => {
                    html += `<tr><td>${gc.categoria}</td><td class="text-right">${formatoMoneda(gc.total)}</td></tr>`;
                });
                html += `<tr class="total-row"><td>Total gastos</td><td class="text-right">${formatoMoneda(totales.gastos)}</td></tr></tbody></table>`;
            }

            html += `<div class="footer">Impreso el ${new Date().toLocaleString("es-CO")}</div>`;
            abrirVentanaImpresionReporte(titulo, html);
        });
}

function abrirModalRangoFechas() {
    const hoy = new Date();
    const hace7 = new Date(hoy);
    hace7.setDate(hace7.getDate() - 6);
    const fmt = d => `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")}`;
    document.getElementById("rptFechaDesde").value = fmt(hace7);
    document.getElementById("rptFechaHasta").value = fmt(hoy);
    new bootstrap.Modal(document.getElementById("modalRangoFechas")).show();
}


let ordenesCacheFact = [];
let facturasCacheGlobal = [];

const DENOMINACIONES = {
    billetes: [100000, 50000, 20000, 10000, 5000, 2000, 1000],
    monedas: [500, 200, 100, 50],
};

function alertaFact(id, mensaje, tipo = "danger") {
    document.getElementById(id).innerHTML = `<div class="alert alert-${tipo} py-2">${mensaje}</div>`;
}

function formatoMoneda(v) {
    return new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 }).format(v || 0);
}

function numeroOrdenDeFactura(id) {
    const o = ordenesCacheFact.find(x => x.id === id);
    return o ? o.numero_orden : `#${id}`;
}

async function cargarOrdenesParaFactura() {
    const resp = await fetch("/ordenes/");
    ordenesCacheFact = resp.ok ? await resp.json() : [];
}

async function cargarFacturas() {
    try {
        const resp = await fetch("/facturas/");
        const facturas = resp.ok ? await resp.json() : [];
        facturasCacheGlobal = facturas;

        const tbody = document.getElementById("tablaFacturas");
        if (!facturas.length) {
            tbody.innerHTML = '<tr><td colspan="8" class="text-muted small">No hay facturas registradas todavía.</td></tr>';
            return;
        }

        tbody.innerHTML = facturas.map(f => {
            const esPagado = f.estado === "PAGADO";
            const esParticular = f.es_particular;
            const badgeEstado = esPagado
                ? '<span class="badge bg-success">Pagado</span>'
                : '<span class="badge bg-warning text-dark">Pendiente</span>';
            const badgeCopago = esParticular
                ? '<span class="badge bg-secondary">No aplica</span>'
                : (f.copago_pagado
                    ? '<span class="badge bg-success">Pagado</span>'
                    : '<span class="badge bg-warning text-dark">Pendiente</span>');

            let botones = '';
            if (esParticular) {
                if (!esPagado) {
                    botones += `<button class="btn btn-sm btn-success me-1" onclick="cambiarEstado(${f.id}, 'PAGADO')">
                        <i class="bi bi-check-circle"></i> Ya pagado
                    </button>`;
                } else {
                    botones += `<button class="btn btn-sm btn-outline-warning me-1" onclick="cambiarEstado(${f.id}, 'PENDIENTE')">
                        <i class="bi bi-arrow-counterclockwise"></i> Pendiente
                    </button>`;
                    botones += `<button class="btn btn-sm btn-outline-primary" onclick="modificarFactura(${f.id})">
                        <i class="bi bi-pencil"></i> Modificar
                    </button>`;
                }
            } else {
                if (!esPagado) {
                    botones += `<button class="btn btn-sm btn-success me-1" onclick="cambiarEstado(${f.id}, 'PAGADO')">
                        <i class="bi bi-check-circle"></i> Marcar Pagado
                    </button>`;
                } else {
                    botones += `<button class="btn btn-sm btn-outline-warning me-1" onclick="cambiarEstado(${f.id}, 'PENDIENTE')">
                        <i class="bi bi-arrow-counterclockwise"></i> Pendiente
                    </button>`;
                    botones += `<button class="btn btn-sm btn-outline-primary" onclick="modificarFactura(${f.id})">
                        <i class="bi bi-pencil"></i> Modificar
                    </button>`;
                }
                if (!f.copago_pagado && f.valor_copago > 0) {
                    botones += `<button class="btn btn-sm btn-outline-success ms-1" onclick="pagarCopago(${f.id})">
                        <i class="bi bi-cash"></i> Registrar copago
                    </button>`;
                }
            }

            return `
            <tr>
                <td>${f.numero}</td>
                <td>${numeroOrdenDeFactura(f.orden_id)}</td>
                <td>${badgeEstado}</td>
                <td>${formatoMoneda(f.subtotal)}</td>
                <td>${esParticular ? '<span class="text-muted small">No aplica</span>' : formatoMoneda(f.valor_copago)}</td>
                <td>${formatoMoneda(f.valor_cubierto_convenio)}</td>
                <td>${badgeCopago}</td>
                <td>${botones}</td>
            </tr>`;
        }).join("");
    } catch (error) {
        alertaFact("alertaFacturas", "No se pudieron cargar las facturas.");
    }
}

async function pagarCopago(facturaId) {
    if (!confirm("¿Confirmar que el paciente ya pagó el copago de esta factura?")) return;

    try {
        const resp = await fetch(`/facturas/${facturaId}/pagar-copago`, { method: "PATCH" });
        if (!resp.ok) {
            alert(await extraerMensajeError(resp, "No se pudo registrar el pago."));
            return;
        }
        await cargarFacturas();
    } catch (error) {
        alert("Error de conexión al registrar el pago.");
    }
}

async function cambiarEstado(facturaId, nuevoEstado) {
    const msg = nuevoEstado === "PAGADO"
        ? "¿Marcar esta factura como PAGADO?"
        : "¿Cambiar el estado de esta factura a PENDIENTE?";
    if (!confirm(msg)) return;

    try {
        const resp = await fetch(`/facturas/${facturaId}/estado`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ estado: nuevoEstado }),
        });
        if (!resp.ok) {
            alert(await extraerMensajeError(resp, "No se pudo cambiar el estado."));
            return;
        }
        await cargarFacturas();
    } catch (error) {
        alert("Error de conexión al cambiar estado.");
    }
}

function modificarFactura(facturaId) {
    const f = facturasCacheGlobal.find(x => x.id === facturaId);
    if (!f) return;

    document.getElementById("alertaModalModificar").innerHTML = "";
    document.getElementById("modFacturaId").value = f.id;
    document.getElementById("modFacturaNumero").value = f.numero;
    document.getElementById("modFacturaOrden").value = numeroOrdenDeFactura(f.orden_id);
    document.getElementById("modFacturaSubtotal").value = f.subtotal;
    document.getElementById("modFacturaImpuestos").value = f.impuestos;
    document.getElementById("modFacturaTotal").value = f.total;
    document.getElementById("modFacturaEstado").value = f.estado;

    document.getElementById("modFacturaSubtotal").addEventListener("input", () => {
        const sub = parseFloat(document.getElementById("modFacturaSubtotal").value || 0);
        const imp = parseFloat(document.getElementById("modFacturaImpuestos").value || 0);
        document.getElementById("modFacturaTotal").value = (sub + imp).toFixed(2);
    });
    document.getElementById("modFacturaImpuestos").addEventListener("input", () => {
        const sub = parseFloat(document.getElementById("modFacturaSubtotal").value || 0);
        const imp = parseFloat(document.getElementById("modFacturaImpuestos").value || 0);
        document.getElementById("modFacturaTotal").value = (sub + imp).toFixed(2);
    });

    new bootstrap.Modal(document.getElementById("modalModificarFactura")).show();
}

async function guardarModFactura() {
    const id = document.getElementById("modFacturaId").value;
    const payload = {
        subtotal: parseFloat(document.getElementById("modFacturaSubtotal").value || 0),
        impuestos: parseFloat(document.getElementById("modFacturaImpuestos").value || 0),
        total: parseFloat(document.getElementById("modFacturaTotal").value || 0),
        estado: document.getElementById("modFacturaEstado").value,
    };

    try {
        const resp = await fetch(`/facturas/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!resp.ok) {
            document.getElementById("alertaModalModificar").innerHTML =
                `<div class="alert alert-danger py-2">${await extraerMensajeError(resp, "No se pudo guardar.")}</div>`;
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById("modalModificarFactura")).hide();
        await cargarFacturas();
    } catch (e) {
        document.getElementById("alertaModalModificar").innerHTML =
            '<div class="alert alert-danger py-2">Error de conexión.</div>';
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    await cargarOrdenesParaFactura();
    await cargarFacturas();
    await cargarEstadoCaja();
    cargarReporteCaja();

    document.getElementById("btnConfirmarAbrirCaja").addEventListener("click", confirmarAbrirCaja);
    document.getElementById("btnConfirmarCerrarCaja").addEventListener("click", confirmarCerrarCaja);
    document.getElementById("btnGuardarModFactura").addEventListener("click", guardarModFactura);
    document.getElementById("btnConfirmarIngreso").addEventListener("click", confirmarIngreso);
});
