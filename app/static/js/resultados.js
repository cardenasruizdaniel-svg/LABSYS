/******************************************************************************
 * LABSYS DIALIZAR
 * app/static/js/resultados.js
 ******************************************************************************/

function alertaResultados(mensaje, tipo = "danger") {
    document.getElementById("alertaResultados").innerHTML = `<div class="alert alert-${tipo} py-2">${mensaje}</div>`;
}

async function cargarResultados() {
    try {
        const [ordenesR, pacientesR, muestrasR, procesamientosR, validacionesR, resultadosR] = await Promise.all([
            fetch("/ordenes/"),
            fetch("/pacientes/"),
            fetch("/muestras/"),
            fetch("/procesamientos/"),
            fetch("/validaciones/"),
            fetch("/resultados/"),
        ]);

        const ordenes = ordenesR.ok ? await ordenesR.json() : [];
        const pacientes = pacientesR.ok ? await pacientesR.json() : [];
        const muestras = muestrasR.ok ? await muestrasR.json() : [];
        const procesamientos = procesamientosR.ok ? await procesamientosR.json() : [];
        const validaciones = validacionesR.ok ? await validacionesR.json() : [];
        const resultados = resultadosR.ok ? await resultadosR.json() : [];

        const validacionPorId = Object.fromEntries(validaciones.map(v => [v.id, v]));
        const procesamientoPorId = Object.fromEntries(procesamientos.map(p => [p.id, p]));
        const muestraPorId = Object.fromEntries(muestras.map(m => [m.id, m]));
        const pacientePorId = Object.fromEntries(pacientes.map(p => [p.id, p]));

        const resultadosPorOrden = {};
        let pendientesSinValidar = 0;

        for (const r of resultados) {
            const val = validacionPorId[r.validacion_id];
            if (!val) continue;

            if (val.estado !== "VALIDADO") {
                pendientesSinValidar++;
                continue;
            }

            const proc = procesamientoPorId[val.procesamiento_id];
            if (!proc) continue;
            const muestra = muestraPorId[proc.muestra_id];
            if (!muestra) continue;

            if (!resultadosPorOrden[muestra.orden_id]) resultadosPorOrden[muestra.orden_id] = [];
            resultadosPorOrden[muestra.orden_id].push(r);
        }

        const avisoDiv = document.getElementById("avisoPendientes");
        if (pendientesSinValidar > 0) {
            avisoDiv.innerHTML = `<div class="alert alert-warning py-2">
                <i class="bi bi-info-circle"></i>
                Hay <strong>${pendientesSinValidar}</strong> resultado(s) cargado(s) que todavía no se han
                <strong>validado</strong>. Por eso no aparecen impresos aquí — ve al módulo
                <a href="/validaciones">Validaciones</a> y usa el botón "Validar" para finalizarlos.
            </div>`;
        } else {
            avisoDiv.innerHTML = "";
        }

        renderOrdenes(ordenes, pacientePorId, resultadosPorOrden);
    } catch (error) {
        alertaResultados("No se pudieron cargar los resultados.");
    }
}

function renderOrdenes(ordenes, pacientePorId, resultadosPorOrden) {
    const cont = document.getElementById("listaOrdenesResultados");
    const ordenesConResultados = ordenes.filter(o => resultadosPorOrden[o.id] && resultadosPorOrden[o.id].length);

    if (!ordenesConResultados.length) {
        cont.innerHTML = '<div class="alert alert-secondary">Todavía no hay resultados validados para mostrar. Una vez se validen resultados en el módulo de Validaciones, aparecerán aquí.</div>';
        return;
    }

    cont.innerHTML = ordenesConResultados.map(o => {
        const paciente = pacientePorId[o.paciente_id];
        const nombrePaciente = paciente ? `${paciente.primer_nombre} ${paciente.primer_apellido}` : `Paciente #${o.paciente_id}`;
        const filas = resultadosPorOrden[o.id];

        return `
        <div class="card shadow-sm mb-3">
            <div class="card-header bg-white d-flex justify-content-between align-items-center">
                <div>
                    <strong>${nombrePaciente}</strong>
                    <span class="text-muted small">— Orden ${o.numero_orden}</span>
                </div>
                <div>
                    <a class="btn btn-sm btn-outline-primary" href="/resultados/orden/${o.id}/pdf" target="_blank">
                        <i class="bi bi-printer"></i> Imprimir
                    </a>
                    <a class="btn btn-sm btn-outline-secondary" href="/resultados/paciente/${o.paciente_id}/historial/pdf" target="_blank">
                        <i class="bi bi-clock-history"></i> Historial del paciente
                    </a>
                </div>
            </div>
            <div class="card-body">
                <table class="table table-sm mb-0">
                    <thead>
                        <tr><th>Examen</th><th>Resultado</th><th>Unidad</th><th>Referencia</th></tr>
                    </thead>
                    <tbody>
                        ${filas.map(r => `
                            <tr class="${r.critico ? 'table-danger' : ''}">
                                <td>${r.examen}</td>
                                <td>${r.resultado ?? (r.valor_numerico ?? '-')} ${r.critico ? '<i class="bi bi-exclamation-triangle-fill text-danger" title="Valor crítico"></i>' : ''}</td>
                                <td>${r.unidad || '-'}</td>
                                <td>${r.valor_referencia || '-'}</td>
                            </tr>
                        `).join("")}
                    </tbody>
                </table>
            </div>
        </div>`;
    }).join("");
}

document.addEventListener("DOMContentLoaded", cargarResultados);
