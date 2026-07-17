/******************************************************************************
 * LABSYS DIALIZAR
 * app/static/js/reportes.js
 ******************************************************************************/

function tarjeta(titulo, valor) {
    return `
        <div class="col-md-3 col-6">
            <div class="card dashboard-card shadow-sm h-100">
                <div class="card-body">
                    <div class="text-muted small">${titulo}</div>
                    <div class="fs-3 fw-bold">${valor}</div>
                </div>
            </div>
        </div>`;
}

function formatoMonedaRep(v) {
    return new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 }).format(v || 0);
}

async function cargarReportes() {
    try {
        const [indicadoresR, produccionR, financieroR, ordenesEstadoR] = await Promise.all([
            fetch("/reportes/indicadores"),
            fetch("/reportes/produccion"),
            fetch("/reportes/financiero"),
            fetch("/reportes/ordenes-estado"),
        ]);

        const indicadores = indicadoresR.ok ? await indicadoresR.json() : {};
        const produccion = produccionR.ok ? await produccionR.json() : {};
        const financiero = financieroR.ok ? await financieroR.json() : {};
        const ordenesEstado = ordenesEstadoR.ok ? await ordenesEstadoR.json() : [];

        document.getElementById("tarjetasIndicadores").innerHTML =
            tarjeta("Pacientes", indicadores.pacientes ?? 0) +
            tarjeta("Órdenes", indicadores.ordenes ?? 0) +
            tarjeta("Muestras", indicadores.muestras ?? 0) +
            tarjeta("Facturas", indicadores.facturas ?? 0);

        document.getElementById("tarjetasProduccion").innerHTML = `
            <p class="mb-2">Muestras pendientes: <strong>${produccion.muestras_pendientes ?? 0}</strong></p>
            <p class="mb-2">Muestras procesadas: <strong>${produccion.muestras_procesadas ?? 0}</strong></p>
            <p class="mb-0">Resultados emitidos: <strong>${produccion.resultados_emitidos ?? 0}</strong></p>
        `;

        document.getElementById("tarjetasFinanciero").innerHTML = `
            <p class="mb-2">Facturación total: <strong>${formatoMonedaRep(financiero.facturacion)}</strong></p>
            <p class="mb-2">Facturas con copago pagado: <strong class="text-success">${financiero.facturas_con_copago_pagado ?? 0}</strong></p>
            <p class="mb-0">Facturas con copago pendiente: <strong class="text-warning">${financiero.facturas_con_copago_pendiente ?? 0}</strong></p>
        `;

        const tabla = document.getElementById("tablaOrdenesEstado");
        if (!ordenesEstado.length) {
            tabla.innerHTML = '<tr><td class="text-muted small">Sin datos.</td></tr>';
        } else {
            tabla.innerHTML = `<thead><tr><th>Estado</th><th>Cantidad</th></tr></thead><tbody>` +
                ordenesEstado.map(([estado, cantidad]) => `<tr><td>${estado}</td><td>${cantidad}</td></tr>`).join("") +
                `</tbody>`;
        }
    } catch (error) {
        document.getElementById("alertaReportes").innerHTML =
            '<div class="alert alert-danger py-2">No se pudieron cargar los reportes.</div>';
    }
}

document.addEventListener("DOMContentLoaded", cargarReportes);
