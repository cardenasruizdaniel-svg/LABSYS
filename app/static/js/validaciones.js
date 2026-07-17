/******************************************************************************
 * LABSYS DIALIZAR
 * app/static/js/validaciones.js
 ******************************************************************************/

let muestrasCacheVal = [];
let procesamientosCacheVal = [];
let resultadosCacheVal = [];
let examenesCacheVal = [];

function alertaVal(id, mensaje, tipo = "danger") {
    document.getElementById(id).innerHTML = `<div class="alert alert-${tipo} py-2">${mensaje}</div>`;
}

function muestraDeProcesamiento(procesamientoId) {
    const p = procesamientosCacheVal.find(x => x.id === procesamientoId);
    if (!p) return "-";
    const m = muestrasCacheVal.find(x => x.id === p.muestra_id);
    return m ? `${m.codigo_barras} (${m.tipo_muestra})` : `#${p.muestra_id}`;
}

async function cargarBacteriologos() {
    const select = document.getElementById("validarSelect");
    try {
        const resp = await fetch("/medicos/?tipo=BACTERIOLOGO");

        if (!resp.ok) {
            select.innerHTML = '<option value="">Error al cargar bacteriólogos</option>';
            console.error("No se pudo cargar /medicos/?tipo=BACTERIOLOGO:", resp.status, await resp.text());
            return;
        }

        const bacteriologos = await resp.json();

        if (!bacteriologos.length) {
            select.innerHTML = '<option value="">No hay bacteriólogos/as registrados — créelos en "Profesionales"</option>';
            return;
        }

        select.innerHTML = '<option value="">Seleccione...</option>' +
            bacteriologos.map(b => `<option value="${b.id}">${b.nombres} ${b.apellidos}</option>`).join("");
    } catch (error) {
        select.innerHTML = '<option value="">Error de conexión al cargar bacteriólogos</option>';
        console.error("Error de conexión cargando bacteriólogos:", error);
    }
}

async function cargarTodo() {
    try {
        const [muestrasR, procesamientosR, validacionesR, resultadosR, examenesR] = await Promise.all([
            fetch("/muestras/"),
            fetch("/procesamientos/"),
            fetch("/validaciones/"),
            fetch("/resultados/"),
            fetch("/examenes/"),
        ]);

        muestrasCacheVal = muestrasR.ok ? await muestrasR.json() : [];
        procesamientosCacheVal = procesamientosR.ok ? await procesamientosR.json() : [];
        const validaciones = validacionesR.ok ? await validacionesR.json() : [];
        resultadosCacheVal = resultadosR.ok ? await resultadosR.json() : [];
        examenesCacheVal = examenesR.ok ? await examenesR.json() : [];

        document.getElementById("listaExamenesCatalogo").innerHTML =
            examenesCacheVal.map(e => `<option value="${e.nombre}">`).join("");

        await cargarBacteriologos();

        const idsConValidacion = new Set(validaciones.map(v => v.procesamiento_id));
        const pendientes = procesamientosCacheVal.filter(p => p.estado === "COMPLETADO" && !idsConValidacion.has(p.id));

        renderPendientesValidar(pendientes);
        renderValidaciones(validaciones);
    } catch (error) {
        alertaVal("alertaValidaciones", "No se pudieron cargar los datos.");
    }
}

function renderPendientesValidar(pendientes) {
    const tbody = document.getElementById("tablaPendientesValidar");
    if (!pendientes.length) {
        tbody.innerHTML = '<tr><td colspan="3" class="text-muted small">No hay procesamientos pendientes de validación.</td></tr>';
        return;
    }

    tbody.innerHTML = pendientes.map(p => `
        <tr>
            <td>${muestraDeProcesamiento(p.id)}</td>
            <td>${p.analizador}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="iniciarValidacion(${p.id})">
                    <i class="bi bi-play-circle"></i> Iniciar validación
                </button>
            </td>
        </tr>
    `).join("");
}

function renderValidaciones(validaciones) {
    const tbody = document.getElementById("tablaValidaciones");
    if (!validaciones.length) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-muted small">No hay validaciones registradas.</td></tr>';
        return;
    }

    tbody.innerHTML = validaciones.map(v => {
        const numResultados = resultadosCacheVal.filter(r => r.validacion_id === v.id).length;
        const esPendiente = v.estado === "PENDIENTE";

        return `
        <tr>
            <td>${muestraDeProcesamiento(v.procesamiento_id)}</td>
            <td><span class="badge bg-${esPendiente ? 'secondary' : 'success'}">${v.estado}</span></td>
            <td>${v.validador || '-'}</td>
            <td>${numResultados} resultado(s)</td>
            <td>
                ${esPendiente ? `
                    <button class="btn btn-sm btn-outline-primary" onclick="abrirModalResultado(${v.id})">
                        <i class="bi bi-plus"></i> Resultado
                    </button>
                    <button class="btn btn-sm btn-success" onclick="abrirModalValidar(${v.id})">
                        <i class="bi bi-check2"></i> Validar
                    </button>
                ` : ""}
            </td>
        </tr>`;
    }).join("");
}

async function iniciarValidacion(procesamientoId) {
    try {
        const resp = await fetch("/validaciones/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ procesamiento_id: procesamientoId }),
        });

        if (!resp.ok) {
                        alertaVal("alertaValidaciones", await extraerMensajeError(resp, "No se pudo iniciar la validación."));
            return;
        }

        await cargarTodo();
    } catch (error) {
        alertaVal("alertaValidaciones", "Error de conexión.");
    }
}

function abrirModalResultado(validacionId) {
    document.getElementById("alertaModalResultado").innerHTML = "";
    document.getElementById("resultadoValidacionId").value = validacionId;
    document.getElementById("resultadoExamen").value = "";
    document.getElementById("resultadoTexto").value = "";
    document.getElementById("resultadoValorNumerico").value = "";
    document.getElementById("resultadoUnidad").value = "";
    document.getElementById("resultadoReferencia").value = "";
    document.getElementById("resultadoCritico").checked = false;
    new bootstrap.Modal(document.getElementById("modalResultado")).show();
}

async function guardarResultado() {
    const validacion_id = parseInt(document.getElementById("resultadoValidacionId").value, 10);
    const examen = document.getElementById("resultadoExamen").value;
    const resultado = document.getElementById("resultadoTexto").value || null;
    const valorTexto = document.getElementById("resultadoValorNumerico").value;
    const valor_numerico = valorTexto ? parseFloat(valorTexto) : null;
    const unidad = document.getElementById("resultadoUnidad").value || null;
    const valor_referencia = document.getElementById("resultadoReferencia").value || null;
    const critico = document.getElementById("resultadoCritico").checked;

    if (!examen) {
        alertaVal("alertaModalResultado", "Indique el nombre del examen.");
        return;
    }

    try {
        const resp = await fetch("/resultados/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ validacion_id, examen, resultado, valor_numerico, unidad, valor_referencia, critico }),
        });

        if (!resp.ok) {
                        alertaVal("alertaModalResultado", await extraerMensajeError(resp, "No se pudo agregar el resultado."));
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById("modalResultado")).hide();
        await cargarTodo();
    } catch (error) {
        alertaVal("alertaModalResultado", "Error de conexión.");
    }
}

function abrirModalValidar(validacionId) {
    document.getElementById("alertaModalValidar").innerHTML = "";
    document.getElementById("validarId").value = validacionId;
    document.getElementById("validarSelect").value = "";
    document.getElementById("validarObservaciones").value = "";

    const numResultados = resultadosCacheVal.filter(r => r.validacion_id === validacionId).length;
    if (numResultados === 0) {
        alertaVal("alertaModalValidar", "Esta validación todavía no tiene resultados agregados. Puede validar igual, pero no habrá nada que imprimir.", "warning");
    }

    new bootstrap.Modal(document.getElementById("modalValidar")).show();
}

async function confirmarValidar() {
    const id = document.getElementById("validarId").value;
    const validador_id = document.getElementById("validarSelect").value;
    const observaciones = document.getElementById("validarObservaciones").value || null;

    if (!validador_id) {
        alertaVal("alertaModalValidar", "Seleccione quién está validando.");
        return;
    }

    try {
        const resp = await fetch(`/validaciones/${id}/validar`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ validador_id: parseInt(validador_id, 10), observaciones }),
        });

        if (!resp.ok) {
                        alertaVal("alertaModalValidar", await extraerMensajeError(resp, "No se pudo validar."));
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById("modalValidar")).hide();
        await cargarTodo();
    } catch (error) {
        alertaVal("alertaModalValidar", "Error de conexión.");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    cargarTodo();
    document.getElementById("btnGuardarResultado").addEventListener("click", guardarResultado);
    document.getElementById("btnConfirmarValidar").addEventListener("click", confirmarValidar);
});
