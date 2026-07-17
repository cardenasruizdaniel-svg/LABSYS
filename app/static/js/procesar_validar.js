/******************************************************************************
 * LABSYS DIALIZAR
 * app/static/js/procesar_validar.js
 *
 * Página unificada de Procesar y Validar Muestras.
 * Reemplaza muestras, procesamientos, validaciones y resultados
 * en una sola vista con flujo de pasos.
 ******************************************************************************/

class ProcesarValidar {

    constructor() {
        this.ordenes = [];
        this.pacientes = [];
        this.medicos = [];
        this.examenes = [];
        this.muestras = [];
        this.procesamientos = [];
        this.validaciones = [];
        this.resultados = [];
        this.parametros = [];
        this.enfermeras = [];
        this.rolesUsuario = [];

        this.ordenSeleccionada = null;
        this.ordenExamenSeleccionado = null;
        this.muestraSeleccionada = null;
        this.procesamientoSeleccionado = null;
        this.validacionSeleccionada = null;
        this.configLab = null;
    }

    async init() {
        await this.cargarSesion();
        await this.cargarTodo();
        this.bindEventos();
    }

    async cargarSesion() {
        try {
            const r = await fetch("/auth/me");
            if (r.ok) {
                const data = await r.json();
                this.rolesUsuario = data.roles || [];
            }
        } catch (e) { /* ignore */ }
    }

    esValidador() {
        return this.rolesUsuario.some(r =>
            r === "Bacteriologo" || r === "Administrador"
        );
    }

    bindEventos() {
        document.getElementById("filtroBusqueda").addEventListener("input", () => this.filtrar());
        document.getElementById("filtroFecha").addEventListener("change", () => this.filtrar());
        document.getElementById("filtroEstado").addEventListener("change", () => this.filtrar());
        document.getElementById("btnLimpiarFiltros").addEventListener("click", () => this.limpiarFiltros());

        document.getElementById("btnGuardarMuestra").addEventListener("click", () => this.guardarMuestra());
        document.getElementById("btnGuardarProcesamiento").addEventListener("click", () => this.guardarProcesamiento());
        document.getElementById("btnConfirmarValidar").addEventListener("click", () => this.guardarValidacion());
    }

    async cargarTodo() {
        try {
            const [ordenesR, pacientesR, medicosR, examenesR, muestrasR, procesamientosR, validacionesR, resultadosR, parametrosR, enfermerasR] = await Promise.all([
                fetch("/ordenes/"),
                fetch("/pacientes/"),
                fetch("/medicos/"),
                fetch("/examenes/"),
                fetch("/muestras/"),
                fetch("/procesamientos/"),
                fetch("/validaciones/"),
                fetch("/resultados/"),
                fetch("/parametros-examen/"),
                fetch("/medicos/?tipo=ENFERMERO"),
            ]);

            this.ordenes = ordenesR.ok ? await ordenesR.json() : [];
            this.pacientes = pacientesR.ok ? await pacientesR.json() : [];
            this.medicos = medicosR.ok ? await medicosR.json() : [];
            this.examenes = examenesR.ok ? await examenesR.json() : [];
            this.muestras = muestrasR.ok ? await muestrasR.json() : [];
            this.procesamientos = procesamientosR.ok ? await procesamientosR.json() : [];
            this.validaciones = validacionesR.ok ? await validacionesR.json() : [];
            this.resultados = resultadosR.ok ? await resultadosR.json() : [];
            this.parametros = parametrosR.ok ? await parametrosR.json() : [];
            this.enfermeras = enfermerasR.ok ? await enfermerasR.json() : [];

            try { const cr = await fetch("/configuracion/"); this.configLab = cr.ok ? await cr.json() : null; } catch (e) { this.configLab = null; }

            this.examenesPorOrden = {};
            await Promise.all(this.ordenes.map(async (o) => {
                try {
                    const r = await fetch(`/ordenes/${o.id}/examenes`);
                    this.examenesPorOrden[o.id] = r.ok ? await r.json() : [];
                } catch (e) {
                    this.examenesPorOrden[o.id] = [];
                }
            }));

            this.poblarSelectEnfermeras();
            this.poblarSelectProfesionales();
            this.poblarSelectValidadores();

            // Default date filter to today
            document.getElementById("filtroFecha").value = this.hoyLocal();

            this.renderOrdenes();
        } catch (error) {
            this.mostrarAlerta("alertaProcesarValidar", "Error al cargar datos del sistema.");
        }
    }

    // --- Helpers ---

    nombrePaciente(id) {
        const p = this.pacientes.find(x => x.id === id);
        return p ? `${p.primer_nombre} ${p.segundo_nombre || ""} ${p.primer_apellido} ${p.segundo_apellido || ""}`.trim() : `Paciente #${id}`;
    }

    documentoPaciente(id) {
        const p = this.pacientes.find(x => x.id === id);
        return p ? `${p.tipo_documento} ${p.documento}` : "";
    }

    nombreMedico(id) {
        const m = this.medicos.find(x => x.id === id);
        return m ? `${m.nombres} ${m.apellidos}` : `Médico #${id}`;
    }

    nombreExamen(id) {
        const e = this.examenes.find(x => x.id === id);
        return e ? e.nombre : `Examen #${id}`;
    }

    examenesDeOrden(ordenId) {
        return this.examenesPorOrden[ordenId] || [];
    }

    obtenerMuestra(ordenId) {
        return this.muestras.find(m => m.orden_id === ordenId) || null;
    }

    obtenerProcesamiento(muestraId) {
        return this.procesamientos.find(p => p.muestra_id === muestraId) || null;
    }

    obtenerValidacion(procesamientoId) {
        return this.validaciones.find(v => v.procesamiento_id === procesamientoId) || null;
    }

    estadoOrden(ordenId) {
        const muestra = this.obtenerMuestra(ordenId);
        if (!muestra) return "SIN_MUESTRA";

        const proc = this.obtenerProcesamiento(muestra.id);
        if (!proc) return "MUESTRA_TOMADA";

        if (proc.estado === "EN_PROCESO") return "EN_PROCESO";

        const val = this.obtenerValidacion(proc.id);
        if (!val) return "PROCESADO";

        if (val.estado === "VALIDADO") return "VALIDADO";
        return "POR_VALIDAR";
    }

    mostrarAlerta(id, mensaje, tipo = "danger") {
        document.getElementById(id).innerHTML = `<div class="alert alert-${tipo} py-2">${mensaje}</div>`;
    }

    generarCodigoBarras() {
        const ahora = new Date();
        return `M${ahora.getFullYear()}${String(ahora.getMonth() + 1).padStart(2, "0")}${String(ahora.getDate()).padStart(2, "0")}${Math.floor(Math.random() * 90000 + 10000)}`;
    }

    fechaLocal(fecha) {
        const d = new Date(fecha);
        return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
    }

    hoyLocal() {
        return this.fechaLocal(new Date());
    }

    diasDesde(fechaCreacion) {
        const hoy = new Date();
        hoy.setHours(0,0,0,0);
        const creacion = new Date(fechaCreacion);
        creacion.setHours(0,0,0,0);
        const diff = Math.floor((hoy - creacion) / 86400000);
        return diff;
    }

    diasBadgeHtml(fechaCreacion) {
        const dias = this.diasDesde(fechaCreacion);
        if (dias === 0) return '<span class="badge bg-success ms-1">Hoy</span>';
        if (dias === 1) return '<span class="badge bg-info ms-1">1 día</span>';
        if (dias <= 3) return `<span class="badge bg-warning text-dark ms-1">${dias} días</span>`;
        return `<span class="badge bg-danger ms-1">${dias} días</span>`;
    }

    // --- Poblar selects ---

    poblarSelectEnfermeras() {
        const select = document.getElementById("tmEnfermera");
        select.innerHTML = '<option value="">Sin especificar</option>' +
            this.enfermeras.map(e => `<option value="${e.nombres} ${e.apellidos}">${e.nombres} ${e.apellidos}</option>`).join("");
    }

    poblarSelectProfesionales() {
        const select = document.getElementById("prProfesional");
        select.innerHTML = '<option value="">Sin especificar</option>' +
            this.medicos.map(m => `<option value="${m.id}">${m.nombres} ${m.apellidos} (${m.tipo_profesional})</option>`).join("");
    }

    poblarSelectValidadores() {
        const bact = this.medicos.filter(m => m.tipo_profesional === "BACTERIOLOGO");
        const select = document.getElementById("vdValidador");
        if (!bact.length) {
            select.innerHTML = '<option value="">No hay bacteriólogos registrados</option>';
            return;
        }
        select.innerHTML = '<option value="">Seleccione...</option>' +
            bact.map(b => `<option value="${b.id}">${b.nombres} ${b.apellidos}</option>`).join("");
    }

    // --- Renderizado principal ---

    renderOrdenes() {
        const container = document.getElementById("listaOrdenes");
        let ordenesFiltradas = this.filtrarOrdenes();

        let pendientes = 0;
        let completadas = 0;

        ordenesFiltradas.forEach(o => {
            const estado = this.estadoOrden(o.id);
            if (estado === "VALIDADO") completadas++;
            else pendientes++;
        });

        document.getElementById("statPendientes").textContent = `${pendientes} pendientes`;
        document.getElementById("statCompletadas").textContent = `${completadas} validadas`;

        if (!ordenesFiltradas.length) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="bi bi-inbox display-4 text-muted"></i>
                    <p class="text-muted mt-2">No hay órdenes que mostrar con los filtros actuales.</p>
                </div>`;
            return;
        }

        // Ordenar por numero de consecutivo (ORD-YYYYMMDD-NN) ascendente
        ordenesFiltradas.sort((a, b) => {
            const numA = a.numero_orden || "";
            const numB = b.numero_orden || "";
            return numA.localeCompare(numB, "es", { numeric: true });
        });

        container.innerHTML = ordenesFiltradas.map(o => this.renderOrdenCard(o)).join("");
    }

    renderOrdenCard(orden) {
        const estado = this.estadoOrden(orden.id);
        const paciente = this.nombrePaciente(orden.paciente_id);
        const doc = this.documentoPaciente(orden.paciente_id);
        const medico = this.nombreMedico(orden.medico_id);

        const examenesOrden = this.examenesPorOrden[orden.id] || [];
        const totalExamenes = examenesOrden.length;

        let examenesHtml = "";
        let accionesHtml = "";

        if (totalExamenes) {
            examenesHtml = examenesOrden.map(ex => {
                return `<span class="badge me-1 mb-1 bg-light text-dark border">${ex.nombre}</span>`;
            }).join("");

            const muestra = this.obtenerMuestra(orden.id);
            const proc = muestra ? this.obtenerProcesamiento(muestra.id) : null;
            const val = proc ? this.obtenerValidacion(proc.id) : null;

            if (estado === "SIN_MUESTRA") {
                accionesHtml = `<button class="btn btn-sm btn-outline-primary" onclick="pv.abrirTomarMuestra(${orden.id})" title="Tomar muestra"><i class="bi bi-eyedropper"></i> Tomar muestra</button>`;
            } else if (estado === "MUESTRA_TOMADA") {
                accionesHtml = `<button class="btn btn-sm btn-outline-warning" onclick="pv.abrirProcesar(${muestra.id})" title="Procesar"><i class="bi bi-cpu"></i> Procesar</button>`;
            } else if (estado === "PROCESADO" || estado === "POR_VALIDAR") {
                if (this.esValidador()) {
                    accionesHtml = `<button class="btn btn-sm btn-outline-success" onclick="pv.abrirValidar(${orden.id})" title="Validar"><i class="bi bi-check-circle"></i> Validar</button>`;
                } else {
                    accionesHtml = `<span class="text-muted small"><i class="bi bi-lock"></i> Pendiente validación</span>`;
                }
            } else if (estado === "VALIDADO") {
                const numResultados = val ? this.resultados.filter(r => r.validacion_id === val.id).length : 0;
                accionesHtml = `
                    <span class="text-success fw-semibold me-2">
                        <i class="bi bi-check-circle-fill"></i> Validado
                        ${numResultados > 0 ? `(${numResultados})` : ""}
                    </span>
                    <a href="/resultados/orden/${orden.id}/pdf" target="_blank" class="btn btn-sm btn-outline-danger me-1" title="Descargar PDF general">
                        <i class="bi bi-file-earmark-pdf"></i> PDF
                    </a>
                    <button class="btn btn-sm btn-outline-secondary me-1" onclick="pv.imprimirResultadosOrden(${orden.id}, 'general')" title="Imprimir reporte general">
                        <i class="bi bi-printer"></i> General
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="pv.imprimirResultadosOrden(${orden.id}, 'especifico')" title="Imprimir por examen">
                        <i class="bi bi-printer"></i> Por examen
                    </button>`;
            }
        } else {
            examenesHtml = '<span class="text-muted small">Sin exámenes asociados</span>';
        }

        return `
        <div class="orden-card">
            <div class="orden-card-header">
                <div>
                    <span class="orden-numero">${orden.numero_orden}</span>
                    <span class="estado-badge estado-${estado} ms-2">${this.estadoTexto(estado)}</span>
                    ${orden.prioridad === "URGENTE" ? '<span class="badge bg-danger ms-1">URGENTE</span>' : ""}
                    ${totalExamenes > 0 ? `<span class="badge bg-secondary ms-1">${totalExamenes} exámenes</span>` : ""}
                </div>
                <span class="orden-fecha">${new Date(orden.fecha_creacion).toLocaleDateString("es-CO")}${this.diasBadgeHtml(orden.fecha_creacion)}</span>
            </div>
            <div class="orden-card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div style="flex:1">
                        <div class="orden-paciente">${paciente}</div>
                        <div class="orden-detalle">${doc} · ${medico}</div>
                        <div class="orden-examenes mt-1">${examenesHtml}</div>
                        <div class="mt-1">${accionesHtml}</div>
                    </div>
                </div>
                ${this.renderWorkflowSteps(estado)}
            </div>
        </div>`;
    }

    renderWorkflowSteps(estadoActual) {
        const pasos = [
            { key: "SIN_MUESTRA", icon: "bi-clipboard2-plus", label: "Orden" },
            { key: "MUESTRA_TOMADA", icon: "bi-eyedropper", label: "Muestra" },
            { key: "EN_PROCESO", icon: "bi-cpu", label: "Procesamiento" },
            { key: "VALIDADO", icon: "bi-check-circle", label: "Validación" },
        ];

        const ordenEstado = { SIN_MUESTRA: 0, MUESTRA_TOMADA: 1, EN_PROCESO: 2, PROCESADO: 2, POR_VALIDAR: 2, VALIDADO: 3, PENDIENTE: 0 };
        const idxActual = ordenEstado[estadoActual] ?? 0;

        let html = '<div class="workflow-steps">';
        pasos.forEach((paso, i) => {
            let clase = "";
            if (i < idxActual) clase = "done";
            else if (i === idxActual) clase = "active";

            html += `
                <div class="workflow-step ${clase}">
                    <span class="step-icon"><i class="bi ${paso.icon}"></i></span>
                    <span>${paso.label}</span>
                </div>`;

            if (i < pasos.length - 1) {
                html += '<span class="workflow-arrow"><i class="bi bi-chevron-right"></i></span>';
            }
        });
        html += '</div>';
        return html;
    }

    estadoTexto(estado) {
        const textos = {
            PENDIENTE: "Pendiente",
            SIN_MUESTRA: "Sin muestra",
            MUESTRA_TOMADA: "Muestra tomada",
            EN_PROCESO: "En proceso",
            PROCESADO: "Procesado",
            POR_VALIDAR: "Por validar",
            MUESTRA: "Muestra tomada",
            PROCESANDO: "En procesamiento",
            VALIDADO: "Validado",
        };
        return textos[estado] || estado;
    }

    estadoTextoCorto(estado) {
        const textos = {
            SIN_MUESTRA: "Pendiente",
            MUESTRA_TOMADA: "Muestra",
            EN_PROCESO: "Procesando",
            PROCESADO: "Procesado",
            POR_VALIDAR: "Validar",
            VALIDADO: "OK",
        };
        return textos[estado] || estado;
    }

    // --- Filtros ---

    filtrarOrdenes() {
        const busqueda = (document.getElementById("filtroBusqueda").value || "").toLowerCase();
        const fecha = document.getElementById("filtroFecha").value || this.hoyLocal();
        const estadoFiltro = document.getElementById("filtroEstado").value;

        return this.ordenes.filter(o => {
            const paciente = this.nombrePaciente(o.paciente_id).toLowerCase();
            const numero = (o.numero_orden || "").toLowerCase();

            if (busqueda && !paciente.includes(busqueda) && !numero.includes(busqueda)) return false;

            if (fecha) {
                const fechaOrden = this.fechaLocal(o.fecha_creacion);
                if (fechaOrden !== fecha) return false;
            }

            if (estadoFiltro) {
                const estado = this.estadoOrden(o.id);
                if (estado !== estadoFiltro) return false;
            }

            return true;
        });
    }

    filtrar() {
        this.renderOrdenes();
    }

    limpiarFiltros() {
        document.getElementById("filtroBusqueda").value = "";
        document.getElementById("filtroFecha").value = this.hoyLocal();
        document.getElementById("filtroEstado").value = "";
        this.renderOrdenes();
    }

    // --- Tomar Muestra ---

    async abrirTomarMuestra(ordenId) {
        const orden = this.ordenes.find(o => o.id === ordenId);
        if (!orden) return;

        this.ordenSeleccionada = orden;
        this.ordenExamenSeleccionado = null;

        document.getElementById("alertaTomarMuestra").innerHTML = "";
        document.getElementById("tmNumeroOrden").textContent = orden.numero_orden;
        document.getElementById("tmPaciente").textContent = this.nombrePaciente(orden.paciente_id);
        document.getElementById("tmEnfermera").value = "";

        try {
            const resp = await fetch(`/ordenes/${ordenId}/examenes`);
            const examenes = resp.ok ? await resp.json() : [];
            this.examenesMuestraActual = examenes;

            document.getElementById("tmCantidadExamenes").textContent = examenes.length;

            const tiposMuestra = [...new Set(examenes.map(e => e.tipo_muestra || "SANGRE"))];
            document.getElementById("tmTiposMuestra").textContent = tiposMuestra.join(", ") || "SANGRE";

            const opcionesMuestra = ["SANGRE", "ORINA", "HECES", "HISOPADO", "OTRO"];

            let tablaHtml = `<table class="table table-sm table-bordered mb-0" style="font-size:.85rem;">
                <thead><tr class="table-light">
                    <th style="width:30px">#</th>
                    <th>Examen</th>
                    <th style="width:130px">Tipo de muestra</th>
                    <th>Recipiente / Tubo</th>
                </tr></thead><tbody>`;
            examenes.forEach((ex, i) => {
                const tipoActual = ex.tipo_muestra || "SANGRE";
                const recipActual = ex.recipiente || "";
                tablaHtml += `<tr>
                    <td>${i + 1}</td>
                    <td>${ex.nombre}</td>
                    <td>
                        <select class="form-select form-select-sm tm-tipo-muestra" data-examen-idx="${i}">
                            ${opcionesMuestra.map(op => `<option value="${op}" ${op === tipoActual ? "selected" : ""}>${op}</option>`).join("")}
                        </select>
                    </td>
                    <td>
                        <input class="form-control form-control-sm tm-recipiente" data-examen-idx="${i}"
                               value="${recipActual}" placeholder="Recipiente...">
                    </td>
                </tr>`;
            });
            tablaHtml += "</tbody></table>";
            document.getElementById("tmTablaExamenes").innerHTML = tablaHtml;
        } catch (e) {
            document.getElementById("tmTablaExamenes").innerHTML = "";
            document.getElementById("tmCantidadExamenes").textContent = "0";
            document.getElementById("tmTiposMuestra").textContent = "—";
        }

        new bootstrap.Modal(document.getElementById("modalTomarMuestra")).show();
    }

    async guardarMuestra() {
        if (!this.ordenSeleccionada) return;

        const responsable_toma = document.getElementById("tmEnfermera").value || null;

        const selects = document.querySelectorAll(".tm-tipo-muestra");
        const inputs = document.querySelectorAll(".tm-recipiente");
        const tipo_muestra = selects.length > 0 ? selects[0].value : "SANGRE";
        const recipiente = inputs.length > 0 ? inputs[0].value || null : null;

        const codigo_barras = this.generarCodigoBarras();

        try {
            const payload = {
                orden_id: this.ordenSeleccionada.id,
                codigo_barras,
                tipo_muestra,
                recipiente,
                responsable_toma,
            };
            const resp = await fetch("/muestras/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            if (!resp.ok) {
                const err = await resp.json().catch(() => ({}));
                this.mostrarAlerta("alertaTomarMuestra", err.detail || "No se pudo registrar la muestra.");
                return;
            }

            const modalInst = bootstrap.Modal.getInstance(document.getElementById("modalTomarMuestra"));
            if (modalInst) modalInst.hide();
            await this.cargarTodo();
        } catch (error) {
            this.mostrarAlerta("alertaTomarMuestra", "Error de conexión.");
        }
    }

    // --- Procesar ---

    async abrirProcesar(muestraId) {
        const muestra = this.muestras.find(m => m.id === muestraId);
        if (!muestra) return;

        this.muestraSeleccionada = muestra;

        document.getElementById("alertaProcesar").innerHTML = "";
        document.getElementById("prCodigoBarras").textContent = muestra.codigo_barras;
        document.getElementById("prTipoMuestra").textContent = muestra.tipo_muestra;
        document.getElementById("prAnalizador").value = "";
        document.getElementById("prProfesional").value = "";
        document.getElementById("prObservaciones").value = "";

        try {
            const resp = await fetch(`/ordenes/${muestra.orden_id}/examenes`);
            const examenes = resp.ok ? await resp.json() : [];

            document.getElementById("prCantidadExamenes").textContent = examenes.length;

            let tablaHtml = `<table class="table table-sm table-bordered mb-0 mt-2" style="font-size:.85rem;">
                <thead><tr>
                    <th>#</th><th>Examen</th><th>Categoría</th>
                </tr></thead><tbody>`;
            examenes.forEach((ex, i) => {
                tablaHtml += `<tr>
                    <td>${i + 1}</td>
                    <td>${ex.nombre}</td>
                    <td>${ex.categoria || ""}</td>
                </tr>`;
            });
            tablaHtml += "</tbody></table>";
            document.getElementById("prTablaExamenes").innerHTML = tablaHtml;
        } catch (e) {
            document.getElementById("prTablaExamenes").innerHTML = "";
            document.getElementById("prCantidadExamenes").textContent = "0";
        }

        new bootstrap.Modal(document.getElementById("modalProcesar")).show();
    }

    async guardarProcesamiento() {
        if (!this.muestraSeleccionada) return;

        const analizador = document.getElementById("prAnalizador").value;
        const profesional_id = document.getElementById("prProfesional").value || null;
        const observaciones = document.getElementById("prObservaciones").value || null;

        if (!analizador) {
            this.mostrarAlerta("alertaProcesar", "Indique el analizador o equipo usado.");
            return;
        }

        try {
            const resp = await fetch("/procesamientos/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    muestra_id: this.muestraSeleccionada.id,
                    analizador,
                    profesional_id: profesional_id ? parseInt(profesional_id, 10) : null,
                    observaciones,
                }),
            });

            if (!resp.ok) {
                const err = await resp.json().catch(() => ({}));
                this.mostrarAlerta("alertaProcesar", err.detail || "No se pudo iniciar el procesamiento.");
                return;
            }

            // Completar procesamiento automaticamente
            const proc = await resp.json();
            await fetch(`/procesamientos/${proc.id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    estado: "COMPLETADO",
                    fecha_fin: new Date().toISOString(),
                }),
            });

            const modalInst = bootstrap.Modal.getInstance(document.getElementById("modalProcesar"));
            if (modalInst) modalInst.hide();
            await this.cargarTodo();
        } catch (error) {
            this.mostrarAlerta("alertaProcesar", "Error de conexión.");
        }
    }

    // --- Validar ---

    async abrirValidar(ordenId) {
        if (!this.esValidador()) {
            this.mostrarAlerta("alertaProcesarValidar", "Solo los bacteriólogos o administradores pueden validar resultados.");
            return;
        }

        const orden = this.ordenes.find(o => o.id === ordenId);
        if (!orden) return;

        const muestra = this.obtenerMuestra(ordenId);
        if (!muestra) return;

        const proc = this.obtenerProcesamiento(muestra.id);
        if (!proc) return;

        let val = this.obtenerValidacion(proc.id);
        if (!val) {
            try {
                const resp = await fetch("/validaciones/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ procesamiento_id: proc.id }),
                });
                if (!resp.ok) {
                    this.mostrarAlerta("alertaProcesarValidar", "No se pudo iniciar la validación.");
                    return;
                }
                val = await resp.json();
                this.validaciones.push(val);
            } catch (e) {
                this.mostrarAlerta("alertaProcesarValidar", "Error de conexión al iniciar validación.");
                return;
            }
        }

        this.ordenSeleccionada = orden;
        this.muestraSeleccionada = muestra;
        this.procesamientoSeleccionado = proc;
        this.validacionSeleccionada = val;

        document.getElementById("alertaValidar").innerHTML = "";
        document.getElementById("vdPaciente").textContent = this.nombrePaciente(orden.paciente_id);
        document.getElementById("vdMuestra").textContent = `${muestra.codigo_barras} (${muestra.tipo_muestra})`;
        document.getElementById("vdAnalizador").textContent = proc.analizador;
        document.getElementById("vdObservaciones").value = "";
        document.getElementById("vdValidador").value = "";
        document.getElementById("vdFirmaPreview").style.display = "none";

        document.getElementById("vdValidador").onchange = () => {
            const medicoId = parseInt(document.getElementById("vdValidador").value, 10);
            const medico = this.medicos.find(m => m.id === medicoId);
            const img = document.getElementById("vdFirmaPreview");
            if (medico && medico.firma_path) {
                img.src = `/static/${medico.firma_path}`;
                img.style.display = "block";
            } else {
                img.style.display = "none";
            }
        };

        await this.cargarFormularioValidacion(orden);

        new bootstrap.Modal(document.getElementById("modalValidar")).show();
    }

    async cargarFormularioValidacion(orden) {
        const container = document.getElementById("formParametros");

        try {
            const resp = await fetch(`/ordenes/${orden.id}/examenes`);
            const examenes = resp.ok ? await resp.json() : [];

            if (!examenes.length) {
                container.innerHTML = '<div class="text-muted small">Esta orden no tiene exámenes asociados.</div>';
                return;
            }

            let html = "";

            for (const examen of examenes) {
                const params = this.parametros.filter(p => p.examen_id === examen.id);

                html += `<div class="parametro-grupo" data-examen-id="${examen.id}">`;
                html += `<h6>${examen.nombre} <small class="text-muted">(${examen.categoria || ""})</small></h6>`;

                if (!params.length) {
                    html += `<div class="text-muted small">Este examen no tiene parámetros predefinidos. Agregue resultados manualmente.</div>`;
                    html += `
                        <div class="parametro-fila">
                            <input class="form-control form-control-sm" data-examen="${examen.nombre}" data-tipo="libre-nombre" placeholder="Nombre del parámetro">
                            <input class="form-control form-control-sm" data-tipo="libre-valor" placeholder="Resultado">
                            <input class="form-control form-control-sm" data-tipo="libre-unidad" placeholder="Unidad">
                            <input class="form-control form-control-sm" data-tipo="libre-ref" placeholder="Ref.">
                            <span></span>
                        </div>`;
                } else {
                    html += `
                        <div class="parametro-fila" style="font-weight:700;color:var(--texto-suave);font-size:.75rem;">
                            <span>Parámetro</span>
                            <span style="text-align:center">Valor</span>
                            <span style="text-align:center">Unidad</span>
                            <span style="text-align:center">Referencia</span>
                            <span></span>
                        </div>`;

                    for (const param of params) {
                        let inputHtml = "";

                        if (param.tipo === "SELECT" && param.opciones) {
                            const opciones = param.opciones.split(",").map(o => o.trim());
                            inputHtml = `<select class="form-select form-select-sm param-input" data-param-id="${param.id}" data-min="${param.valor_minimo || ""}" data-max="${param.valor_maximo || ""}">
                                <option value="">...</option>
                                ${opciones.map(o => `<option value="${o}">${o}</option>`).join("")}
                            </select>`;
                        } else {
                            inputHtml = `<input type="number" step="any" class="form-control form-control-sm param-input" data-param-id="${param.id}" data-min="${param.valor_minimo || ""}" data-max="${param.valor_maximo || ""}" placeholder="...">`;
                        }

                        html += `
                            <div class="parametro-fila">
                                <span class="param-nombre">${param.nombre}</span>
                                ${inputHtml}
                                <span class="text-muted small" style="text-align:center">${param.unidad || "-"}</span>
                                <span class="param-referencia">${param.valor_referencia || "-"}</span>
                                <span class="param-estado" id="estado-param-${param.id}"></span>
                            </div>`;
                    }
                }

                html += `<div class="mt-2 mb-3">
                    <label class="form-label small fw-bold">Observaciones del examen ${examen.nombre}</label>
                    <textarea class="form-control form-control-sm vd-observacion-examen" data-examen-id="${examen.id}" rows="1" placeholder="Observaciones para este examen (opcional)"></textarea>
                </div>`;

                html += `</div>`;
            }

            container.innerHTML = html;

            container.querySelectorAll(".param-input").forEach(input => {
                input.addEventListener("change", () => this.validarParametro(input));
                input.addEventListener("input", () => this.validarParametro(input));
            });

        } catch (error) {
            container.innerHTML = '<div class="text-danger small">Error al cargar los parámetros del examen.</div>';
        }
    }

    validarParametro(input) {
        const min = parseFloat(input.dataset.min);
        const max = parseFloat(input.dataset.max);
        const valor = parseFloat(input.value);
        const paramId = input.dataset.paramId;
        const estadoEl = document.getElementById(`estado-param-${paramId}`);

        if (isNaN(valor) || !estadoEl) {
            if (estadoEl) estadoEl.innerHTML = "";
            input.classList.remove("valor-fuera-rango");
            return;
        }

        if (!isNaN(min) && !isNaN(max)) {
            if (valor < min || valor > max) {
                input.classList.add("valor-fuera-rango");
                estadoEl.innerHTML = '<i class="bi bi-exclamation-triangle-fill text-danger"></i>';
            } else {
                input.classList.remove("valor-fuera-rango");
                estadoEl.innerHTML = '<i class="bi bi-check-circle-fill text-success"></i>';
            }
        } else {
            input.classList.remove("valor-fuera-rango");
            estadoEl.innerHTML = "";
        }
    }

    async guardarValidacion() {
        if (!this.validacionSeleccionada) return;

        const validador_id = document.getElementById("vdValidador").value;
        const observaciones = document.getElementById("vdObservaciones").value || null;

        if (!validador_id) {
            this.mostrarAlerta("alertaValidar", "Seleccione quién está validando.");
            return;
        }

        // Recoger todos los parametros del formulario
        const container = document.getElementById("formParametros");
        const inputs = container.querySelectorAll(".param-input");
        const resultados = [];

        inputs.forEach(input => {
            const valor = input.value;
            if (!valor) return;

            const paramId = input.dataset.paramId;

            if (paramId) {
                const param = this.parametros.find(p => p.id === parseInt(paramId, 10));
                if (param) {
                    const examen = this.examenes.find(e => e.id === param.examen_id);
                    const valorNumerico = param.tipo === "NUMERICO" ? parseFloat(valor) : null;
                    const critico = valorNumerico !== null && param.valor_minimo !== null && param.valor_maximo !== null
                        && (valorNumerico < param.valor_minimo || valorNumerico > param.valor_maximo);

                    resultados.push({
                        examen: param.nombre,
                        examen_codigo: examen ? examen.codigo : null,
                        resultado: param.tipo === "SELECT" ? valor : null,
                        valor_numerico: valorNumerico,
                        unidad: param.unidad || null,
                        valor_referencia: param.valor_referencia || null,
                        critico,
                    });
                }
            } else {
                const grupo = input.closest(".parametro-grupo");
                const examenId = parseInt(grupo.dataset.examenId, 10);
                const examen = this.examenes.find(e => e.id === examenId);
                const nombreInput = grupo.querySelector("[data-tipo='libre-nombre']");
                const unidadInput = grupo.querySelector("[data-tipo='libre-unidad']");
                const refInput = grupo.querySelector("[data-tipo='libre-ref']");

                resultados.push({
                    examen: nombreInput ? `${nombreInput.dataset.examen} - ${nombreInput.value}` : "Resultado",
                    examen_codigo: examen ? examen.codigo : null,
                    resultado: valor,
                    valor_numerico: null,
                    unidad: unidadInput ? unidadInput.value : null,
                    valor_referencia: refInput ? refInput.value : null,
                    critico: false,
                });
            }
        });

        if (!resultados.length) {
            this.mostrarAlerta("alertaValidar", "Ingrese al menos un resultado.");
            return;
        }

        // Guardar resultados
        let resultadosGuardados = 0;
        for (const r of resultados) {
            try {
                const resp = await fetch("/resultados/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        validacion_id: this.validacionSeleccionada.id,
                        ...r,
                    }),
                });
                if (resp.ok) resultadosGuardados++;
            } catch (e) {
                // Continuar con los demas
            }
        }

        // Validar
        try {
            const resp = await fetch(`/validaciones/${this.validacionSeleccionada.id}/validar`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    validador_id: parseInt(validador_id, 10),
                    observaciones,
                }),
            });

            if (!resp.ok) {
                this.mostrarAlerta("alertaValidar", "Los resultados se guardaron pero no se pudo marcar como validado.");
                return;
            }
        } catch (e) {
            this.mostrarAlerta("alertaValidar", "Error de conexión al validar.");
            return;
        }

        const modalInst = bootstrap.Modal.getInstance(document.getElementById("modalValidar"));
        if (modalInst) modalInst.hide();
        await this.cargarTodo();
    }

    imprimirResultados() {
        if (!this.ordenSeleccionada) return;

        const orden = this.ordenSeleccionada;
        const muestra = this.muestraSeleccionada;
        const proc = this.procesamientoSeleccionado;
        const validador_id = parseInt(document.getElementById("vdValidador").value, 10);
        const validador = this.medicos.find(m => m.id === validador_id);
        const observacionesGenerales = document.getElementById("vdObservaciones").value || "";
        const modo = document.getElementById("vdModoImpresion").value;

        const grupoHtml = document.getElementById("formParametros");
        const grupos = grupoHtml.querySelectorAll(".parametro-grupo");

        if (modo === "general") {
            this._imprimirResultadosGeneral(grupos, orden, muestra, proc, validador, observacionesGenerales);
        } else {
            this._imprimirResultadosEspecifico(grupos, orden, muestra, proc, validador, observacionesGenerales);
        }
    }

    _paginaA4(contenidoInterno) {
        return `<div class="pagina-a4" style="width:215mm;height:279mm;overflow:hidden;border:1px solid #000;font-family:Arial,sans-serif;font-size:10pt;display:flex;flex-direction:column;page-break-after:always;box-sizing:border-box;">
            ${contenidoInterno}
        </div>`;
    }

    _abrirVentanaImpresion(titulo, contenidoHtml) {
        const win = window.open("", "_blank");
        win.document.write(`<!DOCTYPE html>
<html><head><title>${titulo}</title>
<style>
    @page { size: letter; margin: 0; }
    @media print { body { margin: 0; padding: 0; } }
    * { box-sizing: border-box; }
    html, body { margin: 0; padding: 0; }
    body { display: block; }
    .pagina-a4 { page-break-after: always; page-break-inside: avoid; }
    .pagina-a4:last-child { page-break-after: auto; }
</style>
</head><body>
${contenidoHtml}
<script>window.onload = function() { window.print(); };<\/script>
</body></html>`);
        win.document.close();
    }

    _encabezadoImpresion(subtitulo) {
        const c = this.configLab || {};
        const logoUrl = c.logo_path ? `/static/${c.logo_path}` : "";
        const logoHtml = logoUrl
            ? `<img src="${logoUrl}" style="height:70px;max-width:100px;object-fit:contain;">`
            : `<div style="width:65px;height:65px;border:2px solid #0B5ED7;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:9pt;font-weight:bold;color:#0B5ED7;">LAB</div>`;

        const labName = c.nombre_laboratorio || "LABSYS DIALIZAR";
        const lines = [];
        if (c.nit) lines.push(`NIT: ${c.nit}`);
        if (c.resolucion_habilitacion) lines.push(`Res. ${c.resolucion_habilitacion}`);
        if (c.direccion) lines.push(c.direccion);
        if (c.ciudad) lines.push(c.ciudad);
        if (c.telefono) lines.push(`Tel: ${c.telefono}`);
        if (c.correo) lines.push(c.correo);
        const labInfo = lines.join("<br>");

        return `
        <div style="width:100%;display:flex;align-items:center;gap:10px;padding-bottom:2mm;border-bottom:2px solid #0B5ED7;margin-bottom:2mm;">
            <div style="flex-shrink:0;">${logoHtml}</div>
            <div style="flex:1;">
                <div style="font-size:12pt;font-weight:700;color:#0B5ED7;margin-bottom:0.5mm;">${labName}</div>
                <div style="font-size:7pt;color:#555;line-height:1.2;">${labInfo}</div>
            </div>
            <div style="text-align:right;flex-shrink:0;">
                <div style="font-size:8pt;color:#555;">${subtitulo}</div>
            </div>
        </div>`;
    }

    _pieImpresion(validador) {
        const fecha = new Date().toLocaleDateString("es-CO", { day: "2-digit", month: "long", year: "numeric" });
        const firmaHtml = validador && validador.firma_path
            ? `<img src="/static/${validador.firma_path}" style="height:40px;">`
            : `<div style="border-top:1px solid #333;width:130px;margin:0 auto;"></div>`;
        const validadorNombre = validador ? `${validador.nombres} ${validador.apellidos}` : "\u2014";
        const pie = this.configLab?.pie_pagina || "";

        return `
        <div style="margin-top:auto;padding-top:4mm;border-top:1px solid #ddd;">
            <div style="display:flex;justify-content:space-between;align-items:flex-end;flex-shrink:0;">
                <div style="text-align:center;width:35%;">
                    ${firmaHtml}
                    <div style="font-size:8pt;font-weight:600;color:#333;border-top:1px solid #333;padding-top:2mm;margin-top:2mm;">Firma del Validador<br><span style="font-weight:400;">${validadorNombre}</span></div>
                </div>
                <div style="text-align:center;width:30%;">
                    <div style="font-size:7.5pt;color:#777;">Fecha de impresión:<br>${fecha}</div>
                </div>
                <div style="text-align:center;width:35%;">
                    <div style="border-top:1px solid #333;padding-top:2mm;margin-top:10mm;font-size:8pt;color:#333;">Firma del Médico</div>
                </div>
            </div>
            ${pie ? `<div style="text-align:center;font-size:6.5pt;color:#999;margin-top:3mm;">${pie}</div>` : ""}
        </div>`;
    }

    _imprimirResultadosGeneral(grupos, orden, muestra, proc, validador, observacionesGenerales) {
        let todasFilas = "";
        let obsSeccion = "";

        for (const grupo of grupos) {
            const examenId = parseInt(grupo.dataset.examenId, 10);
            const examen = this.examenes.find(e => e.id === examenId);
            const nombreExamen = examen ? examen.nombre : `Examen #${examenId}`;

            const filas = grupo.querySelectorAll(".parametro-fila");
            let esPrimera = true;

            filas.forEach(fila => {
                if (esPrimera) { esPrimera = false; return; }
                const nombre = fila.querySelector(".param-nombre");
                const input = fila.querySelector(".param-input, input[data-tipo='libre-valor'], select[data-tipo='libre-valor']");
                const spans = fila.querySelectorAll("span");
                const ref = fila.querySelector(".param-referencia");

                if (nombre && input && input.value) {
                    let unidad = "";
                    if (spans.length >= 3) unidad = spans[2].textContent;
                    todasFilas += `<tr>
                        <td style="padding:1.5mm;">${nombreExamen}</td>
                        <td style="padding:1.5mm;">${nombre.textContent}</td>
                        <td style="padding:1.5mm;text-align:center;font-weight:bold;">${input.value}</td>
                        <td style="padding:1.5mm;text-align:center;">${unidad}</td>
                        <td style="padding:1.5mm;text-align:center;">${ref ? ref.textContent : ""}</td>
                    </tr>`;
                }
            });

            const obsEl = grupo.querySelector(".vd-observacion-examen");
            if (obsEl && obsEl.value) {
                obsSeccion += `<div style="margin-bottom:1mm;"><strong>${nombreExamen}:</strong> ${obsEl.value}</div>`;
            }
        }

        if (!todasFilas) {
            todasFilas = '<tr><td colspan="5" class="text-muted" style="padding:2mm;text-align:center;">Sin resultados registrados</td></tr>';
        }

        const firmaHtml = validador && validador.firma_path
            ? `<img src="/static/${validador.firma_path}" style="height:40px;">`
            : `<div style="border-top:1px solid #000;width:120px;margin:0 auto;"></div>`;

        const html = `
        <div class="pagina-a4" style="width:215mm;height:279mm;overflow:hidden;padding:4mm 6mm;font-family:Arial,sans-serif;font-size:10pt;page-break-after:always;page-break-inside:avoid;display:flex;flex-direction:column;box-sizing:border-box;">
            ${this._encabezadoImpresion("Resultados Generales")}

            <div style="display:flex;gap:6mm;margin-bottom:2mm;font-size:9pt;">
                <div style="flex:1;border:1px solid #e0e0e0;padding:2mm 3mm;border-radius:3px;background:#f9fafb;">
                    <strong>Orden:</strong> ${orden.numero_orden}<br>
                    <strong>Paciente:</strong> ${this.nombrePaciente(orden.paciente_id)}<br>
                    <strong>Documento:</strong> ${this.documentoPaciente(orden.paciente_id)}<br>
                    <strong>Médico:</strong> ${this.nombreMedico(orden.medico_id)}
                </div>
                <div style="flex:1;border:1px solid #e0e0e0;padding:2mm 3mm;border-radius:3px;background:#f9fafb;">
                    <strong>Fecha orden:</strong> ${new Date(orden.fecha_creacion).toLocaleDateString("es-CO")}<br>
                    <strong>Prioridad:</strong> ${orden.prioridad}<br>
                    <strong>Muestra:</strong> ${muestra ? `${muestra.codigo_barras} (${muestra.tipo_muestra})` : "\u2014"}<br>
                    <strong>Analizador:</strong> ${proc ? proc.analizador : "\u2014"}
                </div>
            </div>

            <div style="flex:1;overflow:hidden;margin-bottom:2mm;">
                <table style="width:100%;border-collapse:collapse;font-size:9pt;">
                    <thead><tr style="background:#0B5ED7;color:#fff;">
                        <th style="padding:1.5mm 1.5mm;text-align:left;">Examen</th>
                        <th style="padding:1.5mm 1.5mm;text-align:left;">Parámetro</th>
                        <th style="padding:1.5mm 1.5mm;text-align:center;">Resultado</th>
                        <th style="padding:1.5mm 1.5mm;text-align:center;">Unidad</th>
                        <th style="padding:1.5mm 1.5mm;text-align:center;">Referencia</th>
                    </tr></thead>
                    <tbody>${todasFilas}</tbody>
                </table>
            </div>
            ${obsSeccion ? `<div style="margin-bottom:1.5mm;font-size:9pt;"><strong>Observaciones:</strong><br>${obsSeccion}</div>` : ""}
            ${observacionesGenerales ? `<div style="margin-bottom:2mm;font-size:9pt;"><strong>Observaciones generales:</strong> ${observacionesGenerales}</div>` : ""}

            ${this._pieImpresion(validador)}
        </div>`;

        this._abrirVentanaImpresion(`Resultados ${orden.numero_orden}`, html);
    }

    _imprimirResultadosEspecifico(grupos, orden, muestra, proc, validador, observacionesGenerales) {
        let paginasHtml = "";

        for (const grupo of grupos) {
            const examenId = parseInt(grupo.dataset.examenId, 10);
            const examen = this.examenes.find(e => e.id === examenId);
            if (!examen) continue;

            const observacionExamen = grupo.querySelector(".vd-observacion-examen");
            const obsExamen = observacionExamen ? observacionExamen.value : "";

            const filas = grupo.querySelectorAll(".parametro-fila");
            let paramsHtml = "";
            let esPrimera = true;

            filas.forEach(fila => {
                if (esPrimera) { esPrimera = false; return; }

                const nombre = fila.querySelector(".param-nombre");
                const input = fila.querySelector(".param-input, input[data-tipo='libre-valor'], select[data-tipo='libre-valor']");
                const spans = fila.querySelectorAll("span");
                const ref = fila.querySelector(".param-referencia");

                if (nombre && input && input.value) {
                    let unidad = "";
                    if (spans.length >= 3) unidad = spans[2].textContent;
                    paramsHtml += `<tr>
                        <td style="padding:2mm;">${nombre.textContent}</td>
                        <td style="padding:2mm;text-align:center;font-weight:bold;">${input.value}</td>
                        <td style="padding:2mm;text-align:center;">${unidad}</td>
                        <td style="padding:2mm;text-align:center;">${ref ? ref.textContent : ""}</td>
                    </tr>`;
                }
            });

            if (!paramsHtml) {
                paramsHtml = '<tr><td colspan="4" class="text-muted" style="padding:2mm;text-align:center;">Sin resultados registrados para este examen</td></tr>';
            }

            const firmaHtml = validador && validador.firma_path
                ? `<img src="/static/${validador.firma_path}" style="height:40px;">`
                : `<div style="border-top:1px solid #000;width:120px;margin:0 auto;"></div>`;

            paginasHtml += `
            <div class="pagina-a4" style="width:215mm;height:279mm;overflow:hidden;padding:4mm 6mm;font-family:Arial,sans-serif;font-size:10pt;page-break-after:always;page-break-inside:avoid;display:flex;flex-direction:column;box-sizing:border-box;">
                ${this._encabezadoImpresion("Resultado de Examen")}

                <div style="display:flex;gap:6mm;margin-bottom:2mm;font-size:9pt;">
                    <div style="flex:1;border:1px solid #e0e0e0;padding:2mm 3mm;border-radius:3px;background:#f9fafb;">
                        <strong>Orden:</strong> ${orden.numero_orden}<br>
                        <strong>Paciente:</strong> ${this.nombrePaciente(orden.paciente_id)}<br>
                        <strong>Documento:</strong> ${this.documentoPaciente(orden.paciente_id)}<br>
                        <strong>Médico:</strong> ${this.nombreMedico(orden.medico_id)}
                    </div>
                    <div style="flex:1;border:1px solid #e0e0e0;padding:2mm 3mm;border-radius:3px;background:#f9fafb;">
                        <strong>Fecha orden:</strong> ${new Date(orden.fecha_creacion).toLocaleDateString("es-CO")}<br>
                        <strong>Prioridad:</strong> ${orden.prioridad}<br>
                        <strong>Muestra:</strong> ${muestra ? `${muestra.codigo_barras} (${muestra.tipo_muestra})` : "\u2014"}<br>
                        <strong>Analizador:</strong> ${proc ? proc.analizador : "\u2014"}
                    </div>
                </div>

                <div style="flex:1;overflow:hidden;margin-bottom:2mm;">
                    <div style="font-size:11pt;font-weight:700;color:#0B5ED7;margin-bottom:1.5mm;">${examen.nombre} <span style="font-weight:400;color:#777;font-size:9pt;">(${examen.categoria || ""})</span></div>
                    <table style="width:100%;border-collapse:collapse;font-size:9pt;">
                        <thead><tr style="background:#0B5ED7;color:#fff;">
                            <th style="padding:1.5mm 1.5mm;text-align:left;">Parámetro</th>
                            <th style="padding:1.5mm 1.5mm;text-align:center;">Resultado</th>
                            <th style="padding:1.5mm 1.5mm;text-align:center;">Unidad</th>
                            <th style="padding:1.5mm 1.5mm;text-align:center;">Referencia</th>
                        </tr></thead>
                        <tbody>${paramsHtml}</tbody>
                    </table>
                </div>

                ${obsExamen ? `<div style="margin-bottom:2mm;font-size:9pt;"><strong>Observaciones:</strong> ${obsExamen}</div>` : ""}

                ${this._pieImpresion(validador)}
            </div>`;
        }

        if (!paginasHtml) {
            this.mostrarAlerta("alertaValidar", "No hay exámenes para imprimir.");
            return;
        }

        this._abrirVentanaImpresion(`Resultados ${orden.numero_orden}`, paginasHtml);
    }

    async imprimirResultadosOrden(ordenId, modo) {
        if (!modo) modo = "especifico";

        const orden = this.ordenes.find(o => o.id === ordenId);
        if (!orden) return;

        const muestra = this.obtenerMuestra(ordenId);
        const proc = muestra ? this.obtenerProcesamiento(muestra.id) : null;
        const val = proc ? this.obtenerValidacion(proc.id) : null;

        const validador = val && val.validador_id ? this.medicos.find(m => m.id === val.validador_id) : null;

        let examenes = [];
        try {
            const r = await fetch(`/ordenes/${ordenId}/examenes`);
            examenes = r.ok ? await r.json() : [];
        } catch (e) { /* ignore */ }

        let resultadosValidacion = [];
        if (val) {
            resultadosValidacion = this.resultados.filter(r => r.validacion_id === val.id);
        }

        const observaciones = val ? (val.observaciones || "") : "";

        if (modo === "general") {
            this._imprimirResultadosOrdenGeneral(examenes, resultadosValidacion, orden, muestra, proc, validador, observaciones);
        } else {
            this._imprimirResultadosOrdenEspecifico(examenes, resultadosValidacion, orden, muestra, proc, validador, observaciones);
        }
    }

    _getResultadosExamen(examenes, resultadosValidacion, examen) {
        let res = resultadosValidacion.filter(r => r.examen_codigo && r.examen_codigo === examen.codigo);
        if (!res.length) {
            const paramsExamen = this.parametros.filter(p => p.examen_id === examen.id);
            const paramNames = paramsExamen.map(p => p.nombre.toLowerCase());
            res = resultadosValidacion.filter(r => {
                const rExamen = (r.examen || "").toLowerCase();
                return paramNames.some(pn => rExamen.includes(pn));
            });
        }
        if (!res.length) {
            const examenNombre = examen.nombre.toLowerCase();
            res = resultadosValidacion.filter(r => {
                const rExamen = (r.examen || "").toLowerCase();
                return rExamen.includes(examenNombre) || examenNombre.includes(rExamen);
            });
        }
        if (!res.length) {
            res = resultadosValidacion.filter(r => {
                const rCodigo = (r.examen_codigo || "").toLowerCase();
                const eCodigo = (examen.codigo || "").toLowerCase();
                return rCodigo === eCodigo;
            });
        }
        return res;
    }

    _imprimirResultadosOrdenGeneral(examenes, resultadosValidacion, orden, muestra, proc, validador, observaciones) {
        let todasFilas = "";

        for (const examen of examenes) {
            const resultadosExamen = this._getResultadosExamen(examenes, resultadosValidacion, examen);

            if (resultadosExamen.length) {
                resultadosExamen.forEach(r => {
                    todasFilas += `<tr>
                        <td style="padding:1.5mm;">${examen.nombre}</td>
                        <td style="padding:1.5mm;">${r.examen}</td>
                        <td style="padding:1.5mm;text-align:center;font-weight:bold;">${r.resultado || r.valor_numerico || "—"}</td>
                        <td style="padding:1.5mm;text-align:center;">${r.unidad || ""}</td>
                        <td style="padding:1.5mm;text-align:center;">${r.valor_referencia || ""}</td>
                    </tr>`;
                });
            } else {
                todasFilas += `<tr><td style="padding:1.5mm;">${examen.nombre}</td><td colspan="4" style="padding:1.5mm;text-align:center;color:#999;">Sin resultados</td></tr>`;
            }
        }

        if (!todasFilas) {
            todasFilas = '<tr><td colspan="5" class="text-muted" style="padding:2mm;text-align:center;">Sin resultados registrados</td></tr>';
        }

        const firmaHtml = validador && validador.firma_path
            ? `<img src="/static/${validador.firma_path}" style="height:40px;">`
            : `<div style="border-top:1px solid #000;width:120px;margin:0 auto;"></div>`;

        const html = `
        <div class="pagina-a4" style="width:215mm;height:279mm;overflow:hidden;padding:4mm 6mm;font-family:Arial,sans-serif;font-size:10pt;page-break-after:always;page-break-inside:avoid;display:flex;flex-direction:column;box-sizing:border-box;">
            ${this._encabezadoImpresion("Resultados Generales")}

            <div style="display:flex;gap:6mm;margin-bottom:2mm;font-size:9pt;">
                <div style="flex:1;border:1px solid #e0e0e0;padding:2mm 3mm;border-radius:3px;background:#f9fafb;">
                    <strong>Orden:</strong> ${orden.numero_orden}<br>
                    <strong>Paciente:</strong> ${this.nombrePaciente(orden.paciente_id)}<br>
                    <strong>Documento:</strong> ${this.documentoPaciente(orden.paciente_id)}<br>
                    <strong>Médico:</strong> ${this.nombreMedico(orden.medico_id)}
                </div>
                <div style="flex:1;border:1px solid #e0e0e0;padding:2mm 3mm;border-radius:3px;background:#f9fafb;">
                    <strong>Fecha orden:</strong> ${new Date(orden.fecha_creacion).toLocaleDateString("es-CO")}<br>
                    <strong>Prioridad:</strong> ${orden.prioridad}<br>
                    <strong>Muestra:</strong> ${muestra ? `${muestra.codigo_barras} (${muestra.tipo_muestra})` : "\u2014"}<br>
                    <strong>Analizador:</strong> ${proc ? proc.analizador : "\u2014"}
                </div>
            </div>

            <div style="flex:1;overflow:hidden;margin-bottom:2mm;">
                <table style="width:100%;border-collapse:collapse;font-size:9pt;">
                    <thead><tr style="background:#0B5ED7;color:#fff;">
                        <th style="padding:1.5mm 1.5mm;text-align:left;">Examen</th>
                        <th style="padding:1.5mm 1.5mm;text-align:left;">Parámetro</th>
                        <th style="padding:1.5mm 1.5mm;text-align:center;">Resultado</th>
                        <th style="padding:1.5mm 1.5mm;text-align:center;">Unidad</th>
                        <th style="padding:1.5mm 1.5mm;text-align:center;">Referencia</th>
                    </tr></thead>
                    <tbody>${todasFilas}</tbody>
                </table>
            </div>

            ${observaciones ? `<div style="margin-bottom:2mm;font-size:9pt;"><strong>Observaciones:</strong> ${observaciones}</div>` : ""}

            ${this._pieImpresion(validador)}
        </div>`;

        this._abrirVentanaImpresion(`Resultados ${orden.numero_orden}`, html);
    }

    _imprimirResultadosOrdenEspecifico(examenes, resultadosValidacion, orden, muestra, proc, validador, observaciones) {
        let paginasHtml = "";

        for (const examen of examenes) {
            const resultadosExamen = this._getResultadosExamen(examenes, resultadosValidacion, examen);

            let paramsHtml = "";
            if (resultadosExamen.length) {
                paramsHtml = resultadosExamen.map(r => `<tr><td style="padding:2mm;">${r.examen}</td><td style="padding:2mm;text-align:center;font-weight:bold;">${r.resultado || r.valor_numerico || "—"}</td><td style="padding:2mm;text-align:center;">${r.unidad || ""}</td><td style="padding:2mm;text-align:center;">${r.valor_referencia || ""}</td></tr>`).join("");
            } else {
                paramsHtml = '<tr><td colspan="4" class="text-muted" style="padding:2mm;text-align:center;">Sin resultados registrados para este examen</td></tr>';
            }

            const firmaHtml = validador && validador.firma_path
                ? `<img src="/static/${validador.firma_path}" style="height:40px;">`
                : `<div style="border-top:1px solid #000;width:120px;margin:0 auto;"></div>`;

            paginasHtml += `
            <div class="pagina-a4" style="width:215mm;height:279mm;overflow:hidden;padding:4mm 6mm;font-family:Arial,sans-serif;font-size:10pt;page-break-after:always;page-break-inside:avoid;display:flex;flex-direction:column;box-sizing:border-box;">
                ${this._encabezadoImpresion("Resultado de Examen")}

                <div style="display:flex;gap:6mm;margin-bottom:2mm;font-size:9pt;">
                    <div style="flex:1;border:1px solid #e0e0e0;padding:2mm 3mm;border-radius:3px;background:#f9fafb;">
                        <strong>Orden:</strong> ${orden.numero_orden}<br>
                        <strong>Paciente:</strong> ${this.nombrePaciente(orden.paciente_id)}<br>
                        <strong>Documento:</strong> ${this.documentoPaciente(orden.paciente_id)}<br>
                        <strong>Médico:</strong> ${this.nombreMedico(orden.medico_id)}
                    </div>
                    <div style="flex:1;border:1px solid #e0e0e0;padding:2mm 3mm;border-radius:3px;background:#f9fafb;">
                        <strong>Fecha orden:</strong> ${new Date(orden.fecha_creacion).toLocaleDateString("es-CO")}<br>
                        <strong>Prioridad:</strong> ${orden.prioridad}<br>
                        <strong>Muestra:</strong> ${muestra ? `${muestra.codigo_barras} (${muestra.tipo_muestra})` : "\u2014"}<br>
                        <strong>Analizador:</strong> ${proc ? proc.analizador : "\u2014"}
                    </div>
                </div>

                <div style="flex:1;overflow:hidden;margin-bottom:2mm;">
                    <div style="font-size:11pt;font-weight:700;color:#0B5ED7;margin-bottom:1.5mm;">${examen.nombre} <span style="font-weight:400;color:#777;font-size:9pt;">(${examen.categoria || ""})</span></div>
                    <table style="width:100%;border-collapse:collapse;font-size:9pt;">
                        <thead><tr style="background:#0B5ED7;color:#fff;">
                            <th style="padding:1.5mm 1.5mm;text-align:left;">Parámetro</th>
                            <th style="padding:1.5mm 1.5mm;text-align:center;">Resultado</th>
                            <th style="padding:1.5mm 1.5mm;text-align:center;">Unidad</th>
                            <th style="padding:1.5mm 1.5mm;text-align:center;">Referencia</th>
                        </tr></thead>
                        <tbody>${paramsHtml}</tbody>
                    </table>
                </div>

                ${observaciones ? `<div style="margin-bottom:2mm;font-size:9pt;"><strong>Observaciones:</strong> ${observaciones}</div>` : ""}

                ${this._pieImpresion(validador)}
            </div>`;
        }

        if (!paginasHtml) {
            this.mostrarAlerta("alertaProcesarValidar", "No hay exámenes para imprimir.");
            return;
        }

        this._abrirVentanaImpresion(`Resultados ${orden.numero_orden}`, paginasHtml);
    }
}

const pv = new ProcesarValidar();
document.addEventListener("DOMContentLoaded", () => pv.init());
