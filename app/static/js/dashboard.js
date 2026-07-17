/******************************************************************************
 * LABSYS DIALIZAR
 * app/static/js/dashboard.js
 * Dashboard Ejecutivo completo con analytics
 ******************************************************************************/

const charts = {};

function formatearMoneda(valor) {
    return new Intl.NumberFormat("es-CO", {
        style: "currency", currency: "COP", maximumFractionDigits: 0,
    }).format(valor || 0);
}

function formatearFecha(fechaStr) {
    if (!fechaStr) return "-";
    const f = new Date(fechaStr);
    if (isNaN(f)) return fechaStr;
    return f.toLocaleString("es-CO", { dateStyle: "short", timeStyle: "short" });
}

function crearChart(id, config) {
    const ctx = document.getElementById(id);
    if (!ctx || typeof Chart === "undefined") return null;
    if (charts[id]) { charts[id].destroy(); }
    charts[id] = new Chart(ctx, config);
    return charts[id];
}

const COLORES = ["#0B5ED7", "#198754", "#ffc107", "#dc3545", "#0dcaf0", "#6f42c1", "#fd7e14", "#20c997", "#d63384", "#6c757d"];

async function cargarDashboard() {
    try {
        const resp = await fetch("/api/dashboard/");
        if (!resp.ok) throw new Error("HTTP " + resp.status);
        const data = await resp.json();
        renderKPIs(data.indicadores || {});
        renderFinanzas(data.finanzas || {});
        renderCaja(data.finanzas?.caja || {});
        renderOperaciones(data.operaciones || {});
        renderPacientes(data.pacientes || {});
        renderInventario(data.inventario || {});
        renderAlertas(data.alertas || []);
        renderActividad(data.actividad || []);
    } catch (error) {
        console.error("Dashboard error:", error);
        document.getElementById("listaAlertas").innerHTML =
            '<div class="alert alert-danger py-2">No se pudo cargar el dashboard.</div>';
    }
}

/* ================================================================
   1. KPIs PRINCIPALES
   ================================================================ */
function renderKPIs(ind) {
    document.getElementById("kpiPacientes").textContent = ind.pacientes ?? 0;
    document.getElementById("kpiOrdenesHoy").textContent = ind.ordenes_hoy ?? 0;
    document.getElementById("kpiOrdenesMes").textContent = ind.ordenes_mes ?? 0;
    document.getElementById("kpiFacturadoHoy").textContent = formatearMoneda(ind.facturado_hoy);
    document.getElementById("kpiFacturadoMes").textContent = formatearMoneda(ind.facturado_mes);
    document.getElementById("kpiCopagosPendientes").textContent = formatearMoneda(ind.copagos_pendientes);
    document.getElementById("kpiInventarioBajo").textContent = ind.inventario_bajo ?? 0;
}

/* ================================================================
   2. INGRESOS Y FINANZAS
   ================================================================ */
function renderFinanzas(fin) {
    const ig = fin.ingresos_gastos || {};
    const gc = fin.gastos_categoria || {};

    crearChart("chartIngresosGastos", {
        type: "bar",
        data: {
            labels: (ig.fechas || []).map(f => {
                const p = f.split("-");
                return p[2] + "/" + p[1];
            }),
            datasets: [
                {
                    label: "Ingresos",
                    data: ig.ingresos || [],
                    backgroundColor: "rgba(11, 94, 215, 0.7)",
                    borderRadius: 4,
                },
                {
                    label: "Gastos",
                    data: ig.gastos || [],
                    backgroundColor: "rgba(220, 53, 69, 0.7)",
                    borderRadius: 4,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: "top" } },
            scales: { y: { beginAtZero: true, ticks: { callback: v => "$" + (v / 1000).toFixed(0) + "k" } } },
        },
    });

    if (gc.categorias && gc.categorias.length) {
        crearChart("chartGastosCategoria", {
            type: "doughnut",
            data: {
                labels: gc.categorias,
                datasets: [{ data: gc.valores, backgroundColor: COLORES }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "right", labels: { boxWidth: 12, font: { size: 11 } } },
                    tooltip: { callbacks: { label: ctx => ctx.label + ": " + formatearMoneda(ctx.raw) } },
                },
            },
        });
    }
}

/* ================================================================
   3. CAJA
   ================================================================ */
function renderCaja(caja) {
    if (!caja.abierta) {
        document.getElementById("kpiCajaEstado").textContent = "Sin caja abierta";
        document.getElementById("kpiCajaEstado").className = "fs-5 fw-bold text-muted";
        document.getElementById("kpiCajaMontoInicial").textContent = "-";
        document.getElementById("kpiCajaCierre").textContent = "-";
        return;
    }
    document.getElementById("kpiCajaEstado").textContent = caja.cerrada ? "Cerrada" : "Abierta";
    document.getElementById("kpiCajaEstado").className = "fs-5 fw-bold " + (caja.cerrada ? "text-success" : "text-warning");
    document.getElementById("kpiCajaMontoInicial").textContent = formatearMoneda(caja.monto_inicial);
    document.getElementById("kpiCajaCierre").textContent = caja.cerrada ? "Realizado" : "Pendiente";
    document.getElementById("kpiCajaCierre").className = "fs-5 fw-bold " + (caja.cerrada ? "text-success" : "text-warning");
}

/* ================================================================
   4. OPERACIONES DEL LABORATORIO
   ================================================================ */
function renderOperaciones(op) {
    const oh = op.ordenes_hoy || {};
    const por = oh.por_estado || {};
    document.getElementById("kpiOrdenesHoyTotal").textContent = oh.total || 0;
    document.getElementById("kpiOrdRegistradas").textContent = por.REGISTRADA || 0;
    document.getElementById("kpiOrdMuestra").textContent = por.EN_MUESTRA || 0;
    document.getElementById("kpiOrdProcesamiento").textContent = por.EN_PROCESAMIENTO || 0;
    document.getElementById("kpiOrdValidadas").textContent = por.VALIDADO || 0;

    const tbody = document.getElementById("tablaOrdenesHoy");
    const ordenes = oh.ordenes || [];
    if (!ordenes.length) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-muted">Sin órdenes hoy.</td></tr>';
    } else {
        const colores = { REGISTRADA: "secondary", EN_MUESTRA: "info", EN_PROCESAMIENTO: "warning", VALIDADO: "success" };
        const prioridadBadge = p => p === "URGENTE" ? "bg-danger" : "bg-light text-dark";
        tbody.innerHTML = ordenes.map((o, i) => `
            <tr>
                <td>${i + 1}</td>
                <td class="fw-semibold">${o.numero_orden}</td>
                <td>${o.paciente}</td>
                <td><span class="badge ${prioridadBadge(o.prioridad)}">${o.prioridad}</span></td>
                <td><span class="badge bg-${colores[o.estado] || "secondary"}">${o.estado}</span></td>
            </tr>
        `).join("");
    }

    const od = op.ordenes_dia || {};
    crearChart("chartOrdenesDia", {
        type: "line",
        data: {
            labels: od.fechas || [],
            datasets: [{
                label: "Órdenes",
                data: od.totales || [],
                borderColor: "#0B5ED7",
                backgroundColor: "rgba(11, 94, 215, 0.1)",
                fill: true,
                tension: 0.3,
                pointRadius: 4,
                pointBackgroundColor: "#0B5ED7",
            }],
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
        },
    });

    const et = op.examenes_top || {};
    if (et.nombres && et.nombres.length) {
        crearChart("chartExamenesTop", {
            type: "bar",
            data: {
                labels: et.nombres,
                datasets: [{
                    label: "Solicitudes",
                    data: et.totales,
                    backgroundColor: COLORES.slice(0, et.nombres.length),
                    borderRadius: 4,
                }],
            },
            options: {
                indexAxis: "y", responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { x: { beginAtZero: true, ticks: { precision: 0 } } },
            },
        });
    }

    const mt = op.medicos_top || {};
    if (mt.nombres && mt.nombres.length) {
        crearChart("chartMedicosTop", {
            type: "bar",
            data: {
                labels: mt.nombres,
                datasets: [{
                    label: "Órdenes",
                    data: mt.totales,
                    backgroundColor: COLORES.slice(0, mt.nombres.length),
                    borderRadius: 4,
                }],
            },
            options: {
                indexAxis: "y", responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { x: { beginAtZero: true, ticks: { precision: 0 } } },
            },
        });
    }
}

/* ================================================================
   5. ANÁLISIS DE PACIENTES
   ================================================================ */
function renderPacientes(pac) {
    const nm = pac.nuevos_mes || {};
    crearChart("chartPacientesMes", {
        type: "bar",
        data: {
            labels: nm.labels || [],
            datasets: [{
                label: "Nuevos",
                data: nm.totales || [],
                backgroundColor: "rgba(25, 135, 84, 0.7)",
                borderRadius: 4,
            }],
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
        },
    });

    const pe = pac.por_eps || {};
    if (pe.nombres && pe.nombres.length) {
        crearChart("chartPacientesEPS", {
            type: "doughnut",
            data: {
                labels: pe.nombres,
                datasets: [{ data: pe.totales, backgroundColor: COLORES }],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: {
                    legend: { position: "right", labels: { boxWidth: 12, font: { size: 11 } } },
                },
            },
        });
    }
}

/* ================================================================
   6. INVENTARIO
   ================================================================ */
function renderInventario(inv) {
    const ic = inv.por_categoria || {};
    if (ic.categorias && ic.categorias.length) {
        crearChart("chartInventarioCategoria", {
            type: "bar",
            data: {
                labels: ic.categorias,
                datasets: [{
                    label: "Items",
                    data: ic.items,
                    backgroundColor: COLORES.slice(0, ic.categorias.length),
                    borderRadius: 4,
                }],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
            },
        });
    }

    const sb = inv.stock_bajo || [];
    const tbody = document.getElementById("tablaStockBajo");
    if (!sb.length) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-muted">Sin items con stock bajo.</td></tr>';
    } else {
        tbody.innerHTML = sb.map(i => `
            <tr>
                <td class="fw-semibold">${i.nombre}</td>
                <td><span class="badge bg-secondary">${i.categoria}</span></td>
                <td class="text-danger fw-bold">${i.stock_actual}</td>
                <td>${i.stock_minimo}</td>
                <td>${i.proveedor}</td>
            </tr>
        `).join("");
    }
}

/* ================================================================
   7. ALERTAS Y ACTIVIDAD
   ================================================================ */
function renderAlertas(alertas) {
    const cont = document.getElementById("listaAlertas");
    if (!alertas.length) {
        cont.innerHTML = '<div class="alert alert-success py-2">Sin alertas.</div>';
        return;
    }
    cont.innerHTML = alertas.map(a => `
        <div class="alert alert-${a.tipo || 'info'} py-2 mb-2">
            <strong>${a.titulo}</strong><br>
            <span class="small">${a.mensaje}</span>
        </div>
    `).join("");
}

function renderActividad(actividad) {
    const tbody = document.getElementById("tablaActividad");
    if (!actividad.length) {
        tbody.innerHTML = '<tr><td colspan="3" class="text-muted small">Sin actividad reciente.</td></tr>';
        return;
    }
    const iconos = {
        Orden: "bi-clipboard-data",
        Facturación: "bi-cash-stack",
        Gastos: "bi-dash-circle",
        Inventario: "bi-box-seam",
    };
    const coloresModulo = {
        Orden: "primary",
        Facturación: "success",
        Gastos: "danger",
        Inventario: "warning",
    };
    tbody.innerHTML = actividad.map(item => `
        <tr>
            <td class="small text-nowrap">${formatearFecha(item.fecha)}</td>
            <td><span class="badge bg-${coloresModulo[item.modulo] || "secondary"}"><i class="bi ${iconos[item.modulo] || "bi-circle"}"></i> ${item.modulo}</span></td>
            <td class="small">${item.descripcion}</td>
        </tr>
    `).join("");
}

document.addEventListener("DOMContentLoaded", () => {
    cargarDashboard();
    document.getElementById("btnActualizarDashboard").addEventListener("click", cargarDashboard);
});
