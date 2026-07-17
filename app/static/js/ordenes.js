/******************************************************************************
 * LABSYS DIALIZAR
 * app/static/js/ordenes.js
 * HU-010 · CRUD de órdenes de laboratorio
 * v3: numeración server-side, vista por fecha, impresión stickers + órdenes
 ******************************************************************************/

let pacientesCache  = [];
let medicosCache    = [];
let epsCache        = [];
let conveniosCache  = [];
let examenesCache   = [];
let ordenesActuales = [];
let fechaActual     = (() => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")}`; })();
let examenesSeleccionados = new Set();

/* ======================================================================
   HELPERS
   ====================================================================== */

function $(id) { return document.getElementById(id); }

function fechaLocalOrd(fecha) {
    const d = new Date(fecha);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function hoyLocalOrd() { return fechaLocalOrd(new Date()); }

function abrirVentanaImpresion(titulo, contenidoHtml) {
    const win = window.open("", "_blank");
    win.document.write(`<!DOCTYPE html>
<html><head><title>${titulo}</title>
<style>
    @page { size: letter; margin: 0; }
    @media print { body { margin: 0; padding: 0; } }
    * { box-sizing: border-box; }
    body { margin: 0; padding: 0; display: flex; flex-direction: column; align-items: center; }
</style>
</head><body>
${contenidoHtml}
<script>window.onload = function() { window.print(); };<\/script>
</body></html>`);
    win.document.close();
}

function alerta(id, msg, tipo = "danger") {
    $(id).innerHTML = `<div class="alert alert-${tipo} py-2">${msg}</div>`;
}

async function extraerMensajeError(resp, fallback) {
    try { const b = await resp.json(); return b.detail || b.message || fallback; }
    catch { return fallback; }
}

function nombrePaciente(id) {
    const p = pacientesCache.find(x => x.id === id);
    return p ? `${p.primer_nombre} ${p.primer_apellido}` : `#${id}`;
}

function nombreMedico(id) {
    const m = medicosCache.find(x => x.id === id);
    return m ? `${m.nombres} ${m.apellidos}` : `#${id}`;
}

function documentoPaciente(id) {
    const p = pacientesCache.find(x => x.id === id);
    return p ? p.documento : "";
}

function nombreEps(id) {
    const e = epsCache.find(x => x.id === id);
    return e ? e.nombre : "";
}

function nombreConvenio(id) {
    const c = conveniosCache.find(x => x.id === id);
    return c ? c.nombre : "";
}

function formatoFechaCorta(iso) {
    const [y, m, d] = iso.split("-");
    return `${d}/${m}/${y}`;
}

function extraerConsecutivo(numero) {
    try { return numero.split("-").pop(); }
    catch { return "?"; }
}

/* ======================================================================
   CATÁLOGOS
   ====================================================================== */

async function cargarCatalogos() {
    const [pacR, medR, epsR, convR, exR] = await Promise.all([
        fetch("/pacientes/"),
        fetch("/medicos/?tipo=MEDICO"),
        fetch("/eps/"),
        fetch("/convenios/"),
        fetch("/examenes/"),
    ]);

    pacientesCache  = pacR.ok  ? await pacR.json()  : [];
    medicosCache    = medR.ok  ? await medR.json()   : [];
    epsCache        = epsR.ok  ? await epsR.json()   : [];
    conveniosCache  = convR.ok ? await convR.json()  : [];
    examenesCache   = exR.ok   ? await exR.json()    : [];

    $("ordenMedico").innerHTML = '<option value="">Seleccione...</option>' +
        medicosCache.map(m =>
            `<option value="${m.id}">${m.nombres} ${m.apellidos}</option>`
        ).join("");

    $("ordenEps").innerHTML = '<option value="">Seleccione...</option>' +
        epsCache.map(e => `<option value="${e.id}">${e.nombre}</option>`).join("");

    $("ordenConvenio").innerHTML = '<option value="">Seleccione...</option>' +
        conveniosCache.map(c =>
            `<option value="${c.id}" data-eps="${c.eps_id}">${c.nombre}</option>`
        ).join("");

    const cont = $("listaExamenesCheckbox");
    if (!examenesCache.length) {
        cont.innerHTML = '<div class="text-muted small">No hay exámenes en el catálogo.</div>';
    } else {
        examenesCache.sort((a, b) => a.nombre.localeCompare(b.nombre, "es"));
        renderExamenesAgrupados("");
    }

    $("buscarExamen").addEventListener("input", (e) => {
        renderExamenesAgrupados(e.target.value.trim().toLowerCase());
    });
    $("btnLimpiarBusqueda").addEventListener("click", () => {
        $("buscarExamen").value = "";
        renderExamenesAgrupados("");
    });

    initPacienteTypeahead();
}

/* ======================================================================
   TIPOAHEAD DE PACIENTE
   ====================================================================== */

function posicionarTypeahead() {
    const input = $("buscarPaciente");
    const list = $("listaPacientes");
    if (!input || !list || !list.classList.contains("active")) return;
    const rect = input.getBoundingClientRect();
    list.style.left = rect.left + "px";
    list.style.top = rect.bottom + "px";
    list.style.width = rect.width + "px";
}

function initPacienteTypeahead() {
    const input    = $("buscarPaciente");
    const hidden   = $("ordenPaciente");
    const list     = $("listaPacientes");
    const infoDiv  = $("pacienteSeleccionado");
    const infoSpan = $("pacienteSeleccionadoNombre");

    let debounceTimer = null;

    input.addEventListener("input", () => {
        hidden.value = "";
        infoDiv.style.display = "none";
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => filtrarPacientes(), 200);
    });

    input.addEventListener("focus", () => {
        if (!hidden.value) {
            filtrarPacientes(true);
        } else {
            hidden.value = "";
            infoDiv.style.display = "none";
            filtrarPacientes(true);
        }
    });

    document.addEventListener("click", (e) => {
        if (!$("pacienteTypeahead").contains(e.target)) {
            list.classList.remove("active");
        }
    });

    window.addEventListener("scroll", posicionarTypeahead, true);
    window.addEventListener("resize", posicionarTypeahead);

    input.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            list.classList.remove("active");
            return;
        }
        const items = list.querySelectorAll(".typeahead-item");
        const current = list.querySelector(".typeahead-item.active-item");
        let idx = Array.from(items).indexOf(current);

        if (e.key === "ArrowDown") {
            e.preventDefault();
            if (current) current.classList.remove("active-item");
            idx = (idx + 1) % items.length;
            items[idx].classList.add("active-item");
            items[idx].scrollIntoView({ block: "nearest" });
        } else if (e.key === "ArrowUp") {
            e.preventDefault();
            if (current) current.classList.remove("active-item");
            idx = (idx - 1 + items.length) % items.length;
            items[idx].classList.add("active-item");
            items[idx].scrollIntoView({ block: "nearest" });
        } else if (e.key === "Enter") {
            e.preventDefault();
            if (current) current.click();
        }
    });
}

function filtrarPacientes(mostrarTodos) {
    const input    = $("buscarPaciente");
    const hidden   = $("ordenPaciente");
    const list     = $("listaPacientes");
    const infoDiv  = $("pacienteSeleccionado");
    const infoSpan = $("pacienteSeleccionadoNombre");

    const q = (input.value || "").trim().toLowerCase();

    if (!mostrarTodos && q.length < 1) {
        list.classList.remove("active");
        return;
    }

    const filtrados = pacientesCache.filter(p => {
        if (mostrarTodos && !q) return true;
        const nombre = `${p.primer_nombre || ""} ${p.segundo_nombre || ""} ${p.primer_apellido || ""} ${p.segundo_apellido || ""}`.toLowerCase();
        const doc = (p.documento || "").toLowerCase();
        return nombre.includes(q) || doc.includes(q);
    }).slice(0, 20);

    if (!filtrados.length) {
        list.innerHTML = '<div class="typeahead-empty"><i class="bi bi-search"></i> No se encontraron pacientes</div>';
        list.classList.add("active");
        posicionarTypeahead();
        return;
    }

    list.innerHTML = filtrados.map(p => {
        const nombre = `${p.primer_nombre || ""} ${p.segundo_nombre || ""} ${p.primer_apellido || ""} ${p.segundo_apellido || ""}`.trim();
        const tipo = p.tipo_documento || "CC";
        return `<div class="typeahead-item" data-id="${p.id}" data-nombre="${nombre} (${p.documento})">
            <span class="nombre">${nombre}</span>
            <span class="documento">${tipo} ${p.documento}</span>
        </div>`;
    }).join("");

    list.querySelectorAll(".typeahead-item").forEach(item => {
        item.addEventListener("click", () => {
            hidden.value = item.dataset.id;
            input.value = item.dataset.nombre;
            infoDiv.style.display = "block";
            infoSpan.textContent = item.dataset.nombre;
            list.classList.remove("active");
        });
    });

    list.classList.add("active");
    posicionarTypeahead();
}

function seleccionarPaciente(id, nombreCompleto) {
    $("ordenPaciente").value = id;
    $("buscarPaciente").value = nombreCompleto;
    $("pacienteSeleccionado").style.display = "block";
    $("pacienteSeleccionadoNombre").textContent = nombreCompleto;
}

/* ======================================================================
   RENDER EXÁMENES AGRUPADOS POR CATEGORÍA
   ====================================================================== */

function renderExamenesAgrupados(filtro) {
    const cont = $("listaExamenesCheckbox");

    let examenesFiltrados = examenesCache;
    if (filtro) {
        examenesFiltrados = examenesCache.filter(ex =>
            ex.nombre.toLowerCase().includes(filtro) ||
            (ex.codigo || "").toLowerCase().includes(filtro) ||
            (ex.categoria || "").toLowerCase().includes(filtro)
        );
    }

    if (!examenesFiltrados.length) {
        cont.innerHTML = '<div class="text-muted small p-2">No se encontraron exámenes.</div>';
        return;
    }

    const porCategoria = {};
    for (const ex of examenesFiltrados) {
        const cat = ex.categoria || "Sin categoría";
        if (!porCategoria[cat]) porCategoria[cat] = [];
        porCategoria[cat].push(ex);
    }

    const categorias = Object.keys(porCategoria).sort((a, b) => a.localeCompare(b, "es"));

    let html = "";
    for (const cat of categorias) {
        const examenes = porCategoria[cat];
        html += `<div class="mb-2">
            <div class="fw-bold text-primary small text-uppercase border-bottom pb-1 mb-1">${cat} <span class="text-muted">(${examenes.length})</span></div>`;
        for (const ex of examenes) {
            const checked = examenesSeleccionados.has(String(ex.id)) ? "checked" : "";
            html += `<div class="form-check ms-2">
                <input class="form-check-input examen-check" type="checkbox" value="${ex.id}" id="ex${ex.id}" ${checked}>
                <label class="form-check-label" for="ex${ex.id}">
                    ${ex.nombre}
                    <small class="text-muted">· $${Number(ex.precio).toLocaleString("es-CO")}</small>
                    ${ex.tipo_muestra ? `<small class="badge bg-light text-dark border ms-1">${ex.tipo_muestra}</small>` : ""}
                </label>
            </div>`;
        }
        html += `</div>`;
    }

    cont.innerHTML = html;

    cont.querySelectorAll(".examen-check").forEach(cb => {
        cb.addEventListener("change", () => {
            if (cb.checked) {
                examenesSeleccionados.add(cb.value);
            } else {
                examenesSeleccionados.delete(cb.value);
            }
        });
    });
}

/* ======================================================================
   CARGAR ÓRDENES
   ====================================================================== */

async function cargarOrdenes(fecha) {
    if (!fecha) fecha = fechaActual;
    fechaActual = fecha;

    try {
        let data;
        if (fecha === hoyLocalOrd()) {
            const r = await fetch("/ordenes/hoy");
            if (!r.ok) throw new Error();
            data = await r.json();
        } else {
            const r = await fetch(`/ordenes/fecha/${fecha}`);
            if (!r.ok) throw new Error();
            data = await r.json();
        }

        $("numHoy").textContent = fecha === hoyLocalOrd()
            ? data.total : "—";

        const hoy = hoyLocalOrd();
        if (fecha === hoy) {
            $("tituloFecha").innerHTML = `<i class="bi bi-calendar-event text-primary"></i> Órdenes de hoy — ${formatoFechaCorta(fecha)}`;
        } else {
            $("tituloFecha").innerHTML = `<i class="bi bi-calendar-date text-secondary"></i> Órdenes del ${formatoFechaCorta(fecha)} (${data.total} total)`;
        }

        ordenesActuales = data.ordenes || [];
        renderTabla(ordenesActuales);
    } catch (e) {
        alerta("alertaOrdenes", "No se pudieron cargar las órdenes.");
    }
}

function renderTabla(ordenes) {
    const tbody = $("tablaOrdenes");
    if (!ordenes.length) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-muted small">No hay órdenes para esta fecha.</td></tr>';
        return;
    }

    const ordenadas = [...ordenes].sort((a, b) => {
        const na = parseInt(extraerConsecutivo(a.numero_orden), 10) || 0;
        const nb = parseInt(extraerConsecutivo(b.numero_orden), 10) || 0;
        return na - nb;
    });

    const colores = {
        REGISTRADA: "secondary", EN_PROCESO: "primary",
        COMPLETADA: "success",   CANCELADA: "danger",
    };

    tbody.innerHTML = ordenadas.map(o => `
        <tr>
            <td><input type="checkbox" class="check-orden" value="${o.id}"></td>
            <td><strong>${o.numero_orden}</strong></td>
            <td>${extraerConsecutivo(o.numero_orden)}</td>
            <td>${nombrePaciente(o.paciente_id)}</td>
            <td>${nombreMedico(o.medico_id)}</td>
            <td><span class="badge bg-${o.prioridad === "URGENTE" ? "danger" : "secondary"}">${o.prioridad}</span></td>
            <td><span class="badge bg-${colores[o.estado] || "secondary"}">${o.estado}</span></td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-secondary" onclick="verExamenes(${o.id}, '${o.numero_orden}')" title="Ver exámenes">
                        <i class="bi bi-clipboard2-check"></i>
                    </button>
                    <button class="btn btn-outline-info" onclick="imprimirSticker(${o.id})" title="Imprimir sticker">
                        <i class="bi bi-upc-scan"></i>
                    </button>
                    <button class="btn btn-outline-dark" onclick="imprimirOrden(${o.id})" title="Imprimir orden">
                        <i class="bi bi-printer"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join("");
}

/* ======================================================================
   SIGUIENTE NÚMERO (server-side)
   ====================================================================== */

async function cargarSiguienteNumero() {
    try {
        const r = await fetch("/ordenes/siguiente");
        if (!r.ok) return;
        const d = await r.json();
        $("ordenNumero").value = d.numero_orden;
        $("ordenConsecutivo").value = d.consecutivo;
    } catch (e) { /* usar placeholder */ }
}

/* ======================================================================
   VER EXÁMENES
   ====================================================================== */

async function verExamenes(ordenId, numero) {
    const modal = new bootstrap.Modal($("modalVerExamenes"));
    $("contenidoVerExamenes").innerHTML = "Cargando...";
    modal.show();

    try {
        const r = await fetch(`/ordenes/${ordenId}/examenes`);
        const examenes = r.ok ? await r.json() : [];

        if (!examenes.length) {
            $("contenidoVerExamenes").innerHTML =
                `<p class="text-muted">La orden <strong>${numero}</strong> no tiene exámenes.</p>`;
            return;
        }

        $("contenidoVerExamenes").innerHTML = `
            <p><strong>${numero}</strong></p>
            <ul class="list-group">
                ${examenes.map(ex =>
                    `<li class="list-group-item">${ex.nombre} <span class="text-muted small">(${ex.categoria || ""})</span></li>`
                ).join("")}
            </ul>`;
    } catch (e) {
        $("contenidoVerExamenes").innerHTML = '<p class="text-danger">Error al cargar.</p>';
    }
}

/* ======================================================================
   GUARDAR ORDEN
   ====================================================================== */

async function guardarOrden() {
    const paciente_id  = $("ordenPaciente").value;
    const medico_id    = $("ordenMedico").value;
    const eps_id       = $("ordenEps").value;
    const convenio_id  = $("ordenConvenio").value;
    const prioridad    = $("ordenPrioridad").value;
    const observaciones = $("ordenObservaciones").value;

    const examenes_ids = Array.from(examenesSeleccionados).map(id => parseInt(id, 10));

    if (!paciente_id || !medico_id || !eps_id || !convenio_id) {
        alerta("alertaModalOrden", "Paciente, médico, EPS y convenio son obligatorios.");
        return;
    }
    if (!examenes_ids.length) {
        alerta("alertaModalOrden", "Seleccione al menos un examen.");
        return;
    }

    const payload = {
        paciente_id:  parseInt(paciente_id, 10),
        medico_id:    parseInt(medico_id, 10),
        eps_id:       parseInt(eps_id, 10),
        convenio_id:  parseInt(convenio_id, 10),
        prioridad,
        observaciones: observaciones || null,
        examenes_ids,
    };

    try {
        const r = await fetch("/ordenes/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!r.ok) {
            alerta("alertaModalOrden", await extraerMensajeError(r, "No se pudo crear la orden."));
            return;
        }

        const ordenCreada = await r.json();
        bootstrap.Modal.getInstance($("modalNuevaOrden")).hide();
        await cargarOrdenes(fechaActual);

        /* preguntar si desea imprimir sticker */
        if (confirm(`Orden ${ordenCreada.numero_orden} creada.\n\n¿Desea imprimir el sticker de rotulación?`)) {
            await imprimirSticker(ordenCreada.id);
        }
    } catch (e) {
        alerta("alertaModalOrden", "Error de conexión al crear la orden.");
    }
}

/* ======================================================================
   CREAR PACIENTE RÁPIDO
   ====================================================================== */

async function guardarPacienteRapido() {
    const payload = {
        tipo_documento:   $("npTipoDoc").value,
        documento:        $("npDocumento").value.trim(),
        primer_nombre:    $("npPrimerNombre").value.trim(),
        segundo_nombre:   $("npSegundoNombre").value.trim() || null,
        primer_apellido:  $("npPrimerApellido").value.trim(),
        segundo_apellido: $("npSegundoApellido").value.trim() || null,
        fecha_nacimiento: $("npFechaNacimiento").value,
        sexo:             $("npSexo").value,
        telefono:         $("npTelefono").value.trim() || null,
        direccion:        $("npDireccion").value.trim() || null,
        es_particular:    true,
        tiene_copago:     false,
    };

    if (!payload.documento || !payload.primer_nombre || !payload.primer_apellido
        || !payload.fecha_nacimiento || !payload.sexo) {
        alerta("alertaNuevoPaciente", "Documento, nombres, apellidos, fecha de nacimiento y sexo son obligatorios.");
        return;
    }

    try {
        const r = await fetch("/pacientes/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!r.ok) {
            alerta("alertaNuevoPaciente", await extraerMensajeError(r, "No se pudo crear el paciente."));
            return;
        }

        const nuevo = await r.json();
        pacientesCache.push(nuevo);

        const nombreCompleto = `${nuevo.primer_nombre} ${nuevo.primer_apellido} (${nuevo.documento})`;
        seleccionarPaciente(nuevo.id, nombreCompleto);

        bootstrap.Modal.getInstance($("modalNuevoPaciente")).hide();
        $("modalNuevoPaciente").querySelectorAll("input").forEach(i => (i.value = ""));
    } catch (e) {
        alerta("alertaNuevoPaciente", "Error de conexión al crear el paciente.");
    }
}

/* ======================================================================
   IMPRESIÓN DE STICKER
   ====================================================================== */

async function imprimirSticker(ordenId) {
    let orden = ordenesActuales.find(o => o.id === ordenId);

    if (!orden) {
        try {
            const r = await fetch(`/ordenes/${ordenId}`);
            if (r.ok) orden = await r.json();
        } catch (e) { /* ignore */ }
    }
    if (!orden) return alerta("alertaOrdenes", "No se pudo cargar la orden para imprimir.");

    let examenes = [];
    try {
        const r = await fetch(`/ordenes/${ordenId}/examenes`);
        if (r.ok) examenes = await r.json();
    } catch (e) { /* ignore */ }

    if (!examenes.length) {
        return alerta("alertaOrdenes", "La orden no tiene exámenes para imprimir stickers.");
    }

    let stickersHtml = "";
    for (const ex of examenes) {
        const tipoMuestra = ex.tipo_muestra || "SANGRE";
        const recipiente = ex.recipiente || "—";
        stickersHtml += `
            <div class="sticker" style="width:60mm;height:40mm;border:1px solid #000;padding:3mm;font-family:Arial,sans-serif;font-size:9pt;page-break-after:always;overflow:hidden;">
                <div style="text-align:center;font-weight:bold;font-size:8pt;border-bottom:1px solid #000;padding-bottom:1mm;margin-bottom:1mm;">
                    LABSYS DIALIZAR — Laboratorio Clínico
                </div>
                <div style="display:flex;justify-content:space-between;">
                    <div>
                        <div><strong>Orden:</strong> ${orden.numero_orden}</div>
                        <div><strong>Paciente:</strong> ${nombrePaciente(orden.paciente_id)}</div>
                        <div><strong>Doc:</strong> ${documentoPaciente(orden.paciente_id)}</div>
                    </div>
                    <div style="text-align:right;">
                        <div><strong>Fecha:</strong> ${formatoFechaCorta(orden.fecha_creacion.slice(0, 10))}</div>
                        <div><strong>Prioridad:</strong> ${orden.prioridad}</div>
                    </div>
                </div>
                <div style="margin-top:1mm;border-top:1px dashed #000;padding-top:1mm;">
                    <div><strong>Examen:</strong> ${ex.nombre}</div>
                    <div><strong>Muestra:</strong> ${tipoMuestra} — ${recipiente}</div>
                </div>
            </div>`;
    }

    abrirVentanaImpresion(`Stickers ${orden.numero_orden}`, `
        ${stickersHtml}
        <script>window.onload = function() { window.print(); window.close(); };<\/script>
    `);
}

/* ======================================================================
   IMPRESIÓN DE ORDEN COMPLETA
   ====================================================================== */

async function imprimirOrden(ordenId) {
    let orden = ordenesActuales.find(o => o.id === ordenId);
    if (!orden) {
        try {
            const r = await fetch(`/ordenes/${ordenId}`);
            if (r.ok) orden = await r.json();
        } catch (e) { /* ignore */ }
    }
    if (!orden) return alerta("alertaOrdenes", "No se pudo cargar la orden.");

    let examenes = [];
    try {
        const r = await fetch(`/ordenes/${ordenId}/examenes`);
        if (r.ok) examenes = await r.json();
    } catch (e) { /* ignore */ }

    const examenesRows = examenes.map((ex, i) => `
        <tr>
            <td style="padding:2mm;text-align:center;font-size:11pt;">${i + 1}</td>
            <td style="padding:2mm;">${ex.nombre}</td>
            <td style="padding:2mm;">${ex.categoria || ""}</td>
            <td style="padding:2mm;">${ex.tipo_muestra || "—"}</td>
            <td style="padding:2mm;">${ex.recipiente || "—"}</td>
            <td style="padding:2mm;text-align:center;font-size:14pt;">☐</td>
        </tr>
    `).join("");

    const total = examenes.reduce((s, e) => s + Number(e.precio), 0);

    const html = `
    <div style="width:210mm;min-height:120mm;border:1px solid #000;padding:8mm;font-family:Arial,sans-serif;font-size:10pt;">
        <div style="text-align:center;border-bottom:2px solid #000;padding-bottom:3mm;margin-bottom:4mm;">
            <div style="font-size:14pt;font-weight:bold;">LABSYS DIALIZAR</div>
            <div style="font-size:9pt;color:#555;">Laboratorio Clínico · Lista de Verificación Diaria</div>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:4mm;">
            <div>
                <strong>Orden N.°:</strong> ${orden.numero_orden}<br>
                <strong>Fecha:</strong> ${formatoFechaCorta(orden.fecha_creacion.slice(0, 10))}
            </div>
            <div style="text-align:right;">
                <strong>Prioridad:</strong> ${orden.prioridad}<br>
                <strong>Total exámenes:</strong> ${examenes.length}
            </div>
        </div>
        <div style="display:flex;gap:4mm;margin-bottom:4mm;">
            <div style="flex:1;border:1px solid #ccc;padding:2mm;">
                <strong>Paciente:</strong> ${nombrePaciente(orden.paciente_id)}<br>
                <strong>Documento:</strong> ${documentoPaciente(orden.paciente_id)}
            </div>
            <div style="flex:1;border:1px solid #ccc;padding:2mm;">
                <strong>Médico:</strong> ${nombreMedico(orden.medico_id)}<br>
                <strong>EPS:</strong> ${nombreEps(orden.eps_id)}
            </div>
        </div>
        <table style="width:100%;border-collapse:collapse;margin-top:2mm;">
            <thead>
                <tr style="border-bottom:2px solid #000;background:#f5f5f5;">
                    <th style="padding:2mm;text-align:center;width:8mm;">#</th>
                    <th style="padding:2mm;text-align:left;">Examen</th>
                    <th style="padding:2mm;text-align:left;">Categoría</th>
                    <th style="padding:2mm;text-align:left;">Muestra</th>
                    <th style="padding:2mm;text-align:left;">Recipiente</th>
                    <th style="padding:2mm;text-align:center;width:18mm;">Listo ☐</th>
                </tr>
            </thead>
            <tbody>${examenesRows}</tbody>
        </table>
        <div style="margin-top:4mm;text-align:right;font-weight:bold;border-top:1px solid #000;padding-top:2mm;">
            Total: $${total.toLocaleString("es-CO")}
        </div>
        <div style="margin-top:8mm;display:flex;justify-content:space-between;">
            <div style="text-align:center;width:35%;border-top:1px solid #000;padding-top:2mm;font-size:9pt;">
                Firma quien recibe
            </div>
            <div style="text-align:center;width:35%;border-top:1px solid #000;padding-top:2mm;font-size:9pt;">
                Firma laboratorio
            </div>
        </div>
    </div>`;

    abrirVentanaImpresion(`Lista ${orden.numero_orden}`, html);
}

/* ======================================================================
   IMPRESIÓN MASIVA
   ====================================================================== */

async function imprimirSeleccionadas() {
    const checks = document.querySelectorAll(".check-orden:checked");
    if (!checks.length) return alerta("alertaOrdenes", "Seleccione al menos una orden.");

    await imprimirStickersMultiples(Array.from(checks).map(ch => parseInt(ch.value, 10)));
}

async function imprimirTodoElDia() {
    if (!ordenesActuales.length) return alerta("alertaOrdenes", "No hay órdenes para imprimir.");

    await imprimirOrdenesMultiples(ordenesActuales.map(o => o.id));
}

/* ======================================================================
   IMPRESIÓN CONSOLIDADA (un solo popup)
   ====================================================================== */

async function imprimirOrdenesMultiples(ordenIds) {
    const datos = [];

    for (const ordenId of ordenIds) {
        let orden = ordenesActuales.find(o => o.id === ordenId);
        if (!orden) {
            try {
                const r = await fetch(`/ordenes/${ordenId}`);
                if (r.ok) orden = await r.json();
            } catch (e) { /* ignore */ }
        }
        if (!orden) continue;

        let examenes = [];
        try {
            const r = await fetch(`/ordenes/${ordenId}/examenes`);
            if (r.ok) examenes = await r.json();
        } catch (e) { /* ignore */ }

        datos.push({ orden, examenes });
    }

    if (!datos.length) return alerta("alertaOrdenes", "No se pudieron cargar las órdenes.");

    let filas = "";
    let numFila = 0;
    for (const { orden, examenes } of datos) {
        const paciente = nombrePaciente(orden.paciente_id);
        const doc = documentoPaciente(orden.paciente_id);
        const medico = nombreMedico(orden.medico_id);
        const numExam = examenes.length;

        for (let i = 0; i < examenes.length; i++) {
            numFila++;
            const ex = examenes[i];
            filas += `<tr>
                <td style="padding:1.5mm;text-align:center;border:1px solid #999;">${numFila}</td>
                <td style="padding:1.5mm;border:1px solid #999;font-weight:bold;">${orden.numero_orden}</td>
                <td style="padding:1.5mm;border:1px solid #999;">${i === 0 ? paciente : ""}</td>
                <td style="padding:1.5mm;border:1px solid #999;">${i === 0 ? doc : ""}</td>
                <td style="padding:1.5mm;border:1px solid #999;">${i === 0 ? medico : ""}</td>
                <td style="padding:1.5mm;border:1px solid #999;">${ex.nombre}</td>
                <td style="padding:1.5mm;border:1px solid #999;">${ex.categoria || ""}</td>
                <td style="padding:1.5mm;border:1px solid #999;">${ex.tipo_muestra || ""}</td>
                <td style="padding:1.5mm;border:1px solid #999;">${ex.recipiente || ""}</td>
                <td style="padding:1.5mm;text-align:center;border:1px solid #999;font-size:12pt;">☐</td>
            </tr>`;
        }
    }

    const html = `
    <div style="width:210mm;height:297mm;overflow:hidden;border:1px solid #000;padding:6mm 8mm;font-family:Arial,sans-serif;font-size:8.5pt;display:flex;flex-direction:column;box-sizing:border-box;">
        <div style="text-align:center;border-bottom:2px solid #000;padding-bottom:2mm;margin-bottom:3mm;">
            <div style="font-size:13pt;font-weight:bold;">LABSYS DIALIZAR</div>
            <div style="font-size:9pt;color:#555;">Laboratorio Clínico · Lista de Verificación Diaria — ${formatoFechaCorta(fechaActual)}</div>
        </div>
        <div style="flex:1;overflow:hidden;">
            <table style="width:100%;border-collapse:collapse;">
                <thead>
                    <tr style="background:#e8e8e8;">
                        <th style="padding:1.5mm;text-align:center;border:2px solid #000;width:6mm;">#</th>
                        <th style="padding:1.5mm;text-align:left;border:2px solid #000;width:22mm;">Orden</th>
                        <th style="padding:1.5mm;text-align:left;border:2px solid #000;">Paciente</th>
                        <th style="padding:1.5mm;text-align:left;border:2px solid #000;width:22mm;">Documento</th>
                        <th style="padding:1.5mm;text-align:left;border:2px solid #000;">Médico</th>
                        <th style="padding:1.5mm;text-align:left;border:2px solid #000;">Examen</th>
                        <th style="padding:1.5mm;text-align:left;border:2px solid #000;width:20mm;">Categoría</th>
                        <th style="padding:1.5mm;text-align:left;border:2px solid #000;width:18mm;">Muestra</th>
                        <th style="padding:1.5mm;text-align:left;border:2px solid #000;width:20mm;">Recipiente</th>
                        <th style="padding:1.5mm;text-align:center;border:2px solid #000;width:10mm;">☐</th>
                    </tr>
                </thead>
                <tbody>${filas}</tbody>
            </table>
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:3mm;flex-shrink:0;font-size:8pt;">
            <div>Total órdenes: ${datos.length} · Total exámenes: ${numFila}</div>
            <div style="display:flex;gap:10mm;">
                <div style="width:50mm;border-top:1px solid #000;text-align:center;padding-top:1mm;">Firma quien recibe</div>
                <div style="width:50mm;border-top:1px solid #000;text-align:center;padding-top:1mm;">Firma laboratorio</div>
            </div>
        </div>
    </div>`;

    abrirVentanaImpresion(`Órdenes del día — ${formatoFechaCorta(fechaActual)}`, html);
}

async function imprimirStickersMultiples(ordenIds) {
    let allHtml = "";

    for (const ordenId of ordenIds) {
        let orden = ordenesActuales.find(o => o.id === ordenId);
        if (!orden) {
            try {
                const r = await fetch(`/ordenes/${ordenId}`);
                if (r.ok) orden = await r.json();
            } catch (e) { /* ignore */ }
        }
        if (!orden) continue;

        let examenes = [];
        try {
            const r = await fetch(`/ordenes/${ordenId}/examenes`);
            if (r.ok) examenes = await r.json();
        } catch (e) { /* ignore */ }

        for (const ex of examenes) {
            const tipoMuestra = ex.tipo_muestra || "SANGRE";
            const recipiente = ex.recipiente || "—";
            allHtml += `
                <div class="sticker" style="width:60mm;height:40mm;border:1px solid #000;padding:3mm;font-family:Arial,sans-serif;font-size:9pt;page-break-after:always;overflow:hidden;">
                    <div style="text-align:center;font-weight:bold;font-size:8pt;border-bottom:1px solid #000;padding-bottom:1mm;margin-bottom:1mm;">
                        LABSYS DIALIZAR — Laboratorio Clínico
                    </div>
                    <div style="display:flex;justify-content:space-between;">
                        <div>
                            <div><strong>Orden:</strong> ${orden.numero_orden}</div>
                            <div><strong>Paciente:</strong> ${nombrePaciente(orden.paciente_id)}</div>
                            <div><strong>Doc:</strong> ${documentoPaciente(orden.paciente_id)}</div>
                        </div>
                        <div style="text-align:right;">
                            <div><strong>Fecha:</strong> ${formatoFechaCorta(orden.fecha_creacion.slice(0, 10))}</div>
                            <div><strong>Prioridad:</strong> ${orden.prioridad}</div>
                        </div>
                    </div>
                    <div style="margin-top:1mm;border-top:1px dashed #000;padding-top:1mm;">
                        <div><strong>Examen:</strong> ${ex.nombre}</div>
                        <div><strong>Muestra:</strong> ${tipoMuestra} — ${recipiente}</div>
                    </div>
                </div>`;
        }
    }

    if (!allHtml) return alerta("alertaOrdenes", "No se pudieron cargar los stickers.");

    abrirVentanaImpresion("Stickers", `
        ${allHtml}
        <script>window.onload = function() { window.print(); window.close(); };<\/script>
    `);
}

/* ======================================================================
   FILTRO DE FECHA
   ====================================================================== */

function setupFiltroFecha() {
    const input = $("filtroFecha");
    input.value = fechaActual;
    input.addEventListener("change", () => {
        cargarOrdenes(input.value);
    });

    $("btnVerHoy").addEventListener("click", () => {
        input.value = hoyLocalOrd();
        cargarOrdenes(input.value);
    });
}

/* ======================================================================
   CHECK ALL
   ====================================================================== */

function setupCheckAll() {
    $("checkAll").addEventListener("change", (e) => {
        document.querySelectorAll(".check-orden").forEach(cb => {
            cb.checked = e.target.checked;
        });
    });
}

/* ======================================================================
   INICIALIZACIÓN
   ====================================================================== */

document.addEventListener("DOMContentLoaded", async () => {
    await cargarCatalogos();
    await cargarOrdenes(fechaActual);

    setupFiltroFecha();
    setupCheckAll();

    $("btnNuevaOrden").addEventListener("click", async () => {
        $("alertaModalOrden").innerHTML = "";
        $("ordenPaciente").value   = "";
        $("buscarPaciente").value  = "";
        $("pacienteSeleccionado").style.display = "none";
        $("listaPacientes").classList.remove("active");
        $("ordenMedico").value     = "";
        $("ordenEps").value        = "";
        $("ordenConvenio").value   = "";
        $("ordenObservaciones").value = "";
        examenesSeleccionados.clear();
        $("buscarExamen").value = "";
        renderExamenesAgrupados("");
        await cargarSiguienteNumero();
        new bootstrap.Modal($("modalNuevaOrden")).show();
    });

    $("btnGuardarOrden").addEventListener("click", guardarOrden);
    $("btnNuevoPaciente").addEventListener("click", () => {
        $("alertaNuevoPaciente").innerHTML = "";
        new bootstrap.Modal($("modalNuevoPaciente")).show();
    });
    $("btnGuardarPaciente").addEventListener("click", guardarPacienteRapido);

    $("btnImprimirDia").addEventListener("click", imprimirTodoElDia);
    $("btnImprimirSeleccion").addEventListener("click", imprimirSeleccionadas);
});
