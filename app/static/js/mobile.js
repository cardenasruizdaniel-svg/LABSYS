/* ==========================================================
   LABSYS DIALIZAR — Mobile PWA JavaScript
   Order-level workflow: Orden → Muestra → Proceso → Validación
   ========================================================== */

let mobileSession = null;

let mobileData = {
    pacientes: [],
    medicos: [],
    examenes: [],
    muestras: [],
    procesamientos: [],
    validaciones: [],
    resultados: [],
    ordenes: [],
    parametros: [],
    configLab: null,
};

let examenesPorOrden = {};

/* ================================================================
   AUTH
   ================================================================ */
async function cargarSesion() {
    try {
        const resp = await fetch("/auth/me");
        if (!resp.ok) { window.location.href = "/mobile"; return null; }
        const data = await resp.json();
        if (!data.acceso_movil) { window.location.href = "/mobile?error=acceso"; return null; }
        mobileSession = data;
        const el = document.getElementById("userName");
        if (el) el.textContent = data.nombres || data.usuario;
        return data;
    } catch (e) { window.location.href = "/mobile"; return null; }
}

async function cerrarSesion() {
    await fetch("/auth/logout", { method: "POST" });
    window.location.href = "/mobile";
}

async function aplicarConfigLab() {
    try {
        const r = await fetch("/configuracion/");
        if (!r.ok) return;
        const cfg = await r.json();
        if (cfg.logo_path) {
            const img = document.getElementById("headerLogo");
            if (img) { img.src = "/static/" + cfg.logo_path; img.style.display = "inline-block"; }
        }
        if (cfg.nombre_laboratorio) {
            const el = document.getElementById("headerNombre");
            if (el) el.textContent = cfg.nombre_laboratorio;
        }
    } catch (e) { /* ignore */ }
}

/* ================================================================
   DATA LOADING
   ================================================================ */
async function cargarDatos() {
    const endpoints = [
        "/ordenes/", "/pacientes/", "/medicos/", "/examenes/",
        "/muestras/", "/procesamientos/", "/validaciones/",
        "/resultados/", "/parametros-examen/"
    ];
    const keys = [
        "ordenes", "pacientes", "medicos", "examenes",
        "muestras", "procesamientos", "validaciones",
        "resultados", "parametros"
    ];
    const promises = endpoints.map(url => fetch(url).then(r => r.ok ? r.json() : []));
    const results = await Promise.all(promises);
    keys.forEach((k, i) => { mobileData[k] = results[i]; });

    examenesPorOrden = {};
    const fetches = mobileData.ordenes.map(o =>
        fetch(`/ordenes/${o.id}/examenes`).then(r => r.ok ? r.json() : []).then(e => { examenesPorOrden[o.id] = e; }).catch(() => { examenesPorOrden[o.id] = []; })
    );
    await Promise.all(fetches);

    try { const cr = await fetch("/configuracion/"); mobileData.configLab = cr.ok ? await cr.json() : null; } catch (e) { mobileData.configLab = null; }
}

/* ================================================================
   HELPERS
   ================================================================ */
function nombrePaciente(pacienteId) {
    const p = mobileData.pacientes.find(x => x.id === pacienteId);
    return p ? `${p.primer_nombre || ""} ${p.segundo_nombre || ""} ${p.primer_apellido || ""} ${p.segundo_apellido || ""}`.trim() : `Paciente #${pacienteId}`;
}

function documentoPaciente(pacienteId) {
    const p = mobileData.pacientes.find(x => x.id === pacienteId);
    return p ? `${p.tipo_documento} ${p.documento}` : "";
}

function nombreMedico(medicoId) {
    const m = mobileData.medicos.find(x => x.id === medicoId);
    return m ? `${m.nombres} ${m.apellidos}` : "";
}

function ordenNumero(ordenId) {
    const o = mobileData.ordenes.find(x => x.id === ordenId);
    return o ? o.numero_orden : `#${ordenId}`;
}

function obtenerMuestra(ordenId) {
    return mobileData.muestras.find(m => m.orden_id === ordenId) || null;
}

function obtenerProcesamiento(muestraId) {
    return mobileData.procesamientos.find(p => p.muestra_id === muestraId) || null;
}

function obtenerValidacion(procesamientoId) {
    return mobileData.validaciones.find(v => v.procesamiento_id === procesamientoId) || null;
}

function contarResultados(validacionId) {
    return mobileData.resultados.filter(r => r.validacion_id === validacionId).length;
}

function estadoOrden(ordenId) {
    const muestra = obtenerMuestra(ordenId);
    if (!muestra) return "SIN_MUESTRA";

    const proc = obtenerProcesamiento(muestra.id);
    if (!proc) return "MUESTRA_TOMADA";

    if (proc.estado === "EN_PROCESO") return "EN_PROCESO";

    const val = obtenerValidacion(proc.id);
    if (!val) return "PROCESADO";

    if (val.estado === "VALIDADO") return "VALIDADO";
    return "POR_VALIDAR";
}

function textoEstado(estado) {
    const textos = {
        SIN_MUESTRA: "Sin muestra",
        MUESTRA_TOMADA: "Muestra tomada",
        EN_PROCESO: "En proceso",
        PROCESADO: "Procesado",
        POR_VALIDAR: "Por validar",
        VALIDADO: "Validado",
        PENDIENTE: "Sin muestras",
    };
    return textos[estado] || estado;
}

function claseBadge(estado) {
    const clases = {
        SIN_MUESTRA: "badge-sin-muestra",
        MUESTRA_TOMADA: "badge-pendiente",
        EN_PROCESO: "badge-proceso",
        PROCESADO: "badge-completado",
        POR_VALIDAR: "badge-completado",
        VALIDADO: "badge-validado",
        PENDIENTE: "badge-sin-muestra",
    };
    return clases[estado] || "badge-pendiente";
}

function formatoFecha(fecha) {
    if (!fecha) return "\u2014";
    const d = new Date(fecha);
    return d.toLocaleDateString("es-CO", { day: "2-digit", month: "short", year: "numeric" });
}

function formatoHora(fecha) {
    if (!fecha) return "";
    const d = new Date(fecha);
    return d.toLocaleTimeString("es-CO", { hour: "2-digit", minute: "2-digit" });
}

function fechaLocal(fecha) {
    const d = new Date(fecha);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function hoyLocal() {
    return fechaLocal(new Date());
}

function diasDesde(fechaCreacion) {
    const hoy = new Date(); hoy.setHours(0,0,0,0);
    const creacion = new Date(fechaCreacion); creacion.setHours(0,0,0,0);
    return Math.floor((hoy - creacion) / 86400000);
}

function diasBadgeHtml(fechaCreacion) {
    const dias = diasDesde(fechaCreacion);
    if (dias === 0) return ' <span class="badge bg-success ms-1">Hoy</span>';
    if (dias === 1) return ' <span class="badge bg-info ms-1">1 día</span>';
    if (dias <= 3) return ` <span class="badge bg-warning text-dark ms-1">${dias} días</span>`;
    return ` <span class="badge bg-danger ms-1">${dias} días</span>`;
}

function generarCodigoBarras() {
    const ahora = new Date();
    return `M${ahora.getFullYear()}${String(ahora.getMonth() + 1).padStart(2, "0")}${String(ahora.getDate()).padStart(2, "0")}${Math.floor(Math.random() * 90000 + 10000)}`;
}

function renderWorkflowSteps(estadoActual) {
    const pasos = [
        { key: "SIN_MUESTRA", icon: "bi-clipboard2-plus", label: "Orden" },
        { key: "MUESTRA_TOMADA", icon: "bi-eyedropper", label: "Muestra" },
        { key: "PROCESADO", icon: "bi-cpu", label: "Proceso" },
        { key: "VALIDADO", icon: "bi-check-circle", label: "Validaci\u00f3n" },
    ];
    const ordenEstadoIdx = { SIN_MUESTRA: 0, MUESTRA_TOMADA: 1, EN_PROCESO: 1, PROCESADO: 2, POR_VALIDAR: 2, VALIDADO: 3 };
    const idx = ordenEstadoIdx[estadoActual] ?? 0;

    let html = '<div class="workflow-steps">';
    pasos.forEach((paso, i) => {
        let clase = "";
        if (i < idx) clase = "done";
        else if (i === idx) clase = "active";
        html += `<div class="workflow-step ${clase}"><span class="step-icon"><i class="bi ${paso.icon}"></i></span><span class="step-label">${paso.label}</span></div>`;
        if (i < pasos.length - 1) html += '<span class="workflow-arrow"><i class="bi bi-chevron-right"></i></span>';
    });
    html += '</div>';
    return html;
}

/* ================================================================
   DASHBOARD EJECUTIVO
   ================================================================ */
const dashCharts = {};
const DASH_COLORES = ["#0B5ED7","#198754","#ffc107","#dc3545","#0dcaf0","#6f42c1","#fd7e14","#20c997","#d63384","#6c757d"];

function _dashFormatearMoneda(v) {
    return new Intl.NumberFormat("es-CO",{style:"currency",currency:"COP",maximumFractionDigits:0}).format(v||0);
}

function _dashCrearChart(id, config) {
    const ctx = document.getElementById(id);
    if (!ctx || typeof Chart === "undefined") return null;
    if (dashCharts[id]) dashCharts[id].destroy();
    dashCharts[id] = new Chart(ctx, config);
    return dashCharts[id];
}

async function cargarDashboard() {
    const sesion = await cargarSesion();
    if (!sesion) return;
    try {
        const resp = await fetch("/api/dashboard/");
        if (!resp.ok) throw new Error("HTTP " + resp.status);
        const data = await resp.json();
        renderDashboardEjecutivo(data);
    } catch (e) {
        console.error("Dashboard error:", e);
        document.getElementById("mainContent").innerHTML =
            '<div class="empty-state"><i class="bi bi-exclamation-triangle"></i><p>Error al cargar el dashboard</p></div>';
    }
}

function renderDashboardEjecutivo(data) {
    const main = document.getElementById("mainContent");
    document.getElementById("loadingSpinner")?.remove();
    const ind = data.indicadores || {};
    const fin = data.finanzas || {};
    const op = data.operaciones || {};
    const pac = data.pacientes || {};
    const inv = data.inventario || {};
    const alertas = data.alertas || [];
    const actividad = data.actividad || [];
    const por = (op.ordenes_hoy || {}).por_estado || {};
    const ordenes = (op.ordenes_hoy || {}).ordenes || [];

    main.innerHTML = `
    <!-- KPIs -->
    <div class="dash-kpi-grid">
        <div class="dash-kpi-card"><span class="kpi-icon" style="color:var(--primary)"><i class="bi bi-people-fill"></i></span><span class="kpi-label">Pacientes</span><span class="kpi-value">${ind.pacientes??0}</span></div>
        <div class="dash-kpi-card"><span class="kpi-icon" style="color:var(--success)"><i class="bi bi-clipboard-data"></i></span><span class="kpi-label">Hoy / Mes</span><span class="kpi-value">${ind.ordenes_hoy??0} <span class="kpi-sub">/ ${ind.ordenes_mes??0}</span></span></div>
        <div class="dash-kpi-card"><span class="kpi-icon" style="color:#0dcaf0"><i class="bi bi-cash-stack"></i></span><span class="kpi-label">Fact. hoy</span><span class="kpi-value" style="font-size:14px">${_dashFormatearMoneda(ind.facturado_hoy)}</span></div>
        <div class="dash-kpi-card"><span class="kpi-icon" style="color:var(--primary)"><i class="bi bi-graph-up"></i></span><span class="kpi-label">Fact. mes</span><span class="kpi-value" style="font-size:14px">${_dashFormatearMoneda(ind.facturado_mes)}</span></div>
        <div class="dash-kpi-card"><span class="kpi-icon" style="color:var(--warning)"><i class="bi bi-exclamation-triangle"></i></span><span class="kpi-label">Copagos pend.</span><span class="kpi-value" style="font-size:14px">${_dashFormatearMoneda(ind.copagos_pendientes)}</span></div>
        <div class="dash-kpi-card"><span class="kpi-icon" style="color:var(--danger)"><i class="bi bi-box-seam"></i></span><span class="kpi-label">Inv. bajo</span><span class="kpi-value">${ind.inventario_bajo??0}</span></div>
    </div>

    <!-- Pipeline -->
    <div class="dash-section">
        <div class="dash-section-header"><span><i class="bi bi-kanban"></i> Pipeline de hoy</span><span class="badge bg-primary">${(op.ordenes_hoy||{}).total||0}</span></div>
        <div class="dash-section-body">
            <div class="dash-pipeline-row">
                <div class="dash-pipeline-item" style="border-color:#6c757d"><span class="pipe-count" style="color:#6c757d">${por.REGISTRADA||0}</span><span class="pipe-label">Registradas</span></div>
                <div class="dash-pipeline-item" style="border-color:#0dcaf0"><span class="pipe-count" style="color:#0dcaf0">${por.EN_MUESTRA||0}</span><span class="pipe-label">Muestra</span></div>
                <div class="dash-pipeline-item" style="border-color:#ffc107"><span class="pipe-count" style="color:#ffc107">${por.EN_PROCESAMIENTO||0}</span><span class="pipe-label">Procesando</span></div>
                <div class="dash-pipeline-item" style="border-color:#198754"><span class="pipe-count" style="color:#198754">${por.VALIDADO||0}</span><span class="pipe-label">Validadas</span></div>
            </div>
            ${ordenes.length ? `
            <div class="dash-scroll">
                <table class="dash-table">
                    <thead><tr><th>#</th><th>Orden</th><th>Paciente</th><th>Estado</th></tr></thead>
                    <tbody>${ordenes.map((o,i) => {
                        const col={REGISTRADA:"secondary",EN_MUESTRA:"info",EN_PROCESAMIENTO:"warning",VALIDADO:"success"};
                        return `<tr><td>${i+1}</td><td><strong>${o.numero_orden}</strong></td><td>${o.paciente}</td><td><span class="badge bg-${col[o.estado]||"secondary"}">${o.estado}</span></td></tr>`;
                    }).join("")}</tbody>
                </table>
            </div>` : '<div class="text-center text-muted small py-2">Sin ordenes hoy</div>'}
        </div>
    </div>

    <!-- Ingresos vs Gastos -->
    <div class="dash-section">
        <div class="dash-section-header"><i class="bi bi-bar-chart-line"></i> Ingresos vs Gastos (30 dias)</div>
        <div class="dash-section-body"><div class="dash-chart-container"><canvas id="mChartIngresosGastos"></canvas></div></div>
    </div>

    <!-- Gastos por categoria -->
    ${(fin.gastos_categoria||{}).categorias?.length ? `
    <div class="dash-section">
        <div class="dash-section-header"><i class="bi bi-pie-chart"></i> Gastos por categoria</div>
        <div class="dash-section-body"><div class="dash-chart-container"><canvas id="mChartGastosCategoria"></canvas></div></div>
    </div>` : ''}

    <!-- Ordenes por dia -->
    <div class="dash-section">
        <div class="dash-section-header"><i class="bi bi-calendar-week"></i> Ordenes por dia (7 dias)</div>
        <div class="dash-section-body"><div class="dash-chart-container"><canvas id="mChartOrdenesDia"></canvas></div></div>
    </div>

    <!-- Examenes top -->
    ${(op.examenes_top||{}).nombres?.length ? `
    <div class="dash-section">
        <div class="dash-section-header"><i class="bi bi-file-medical"></i> Examenes mas solicitados</div>
        <div class="dash-section-body"><div class="dash-chart-container"><canvas id="mChartExamenesTop"></canvas></div></div>
    </div>` : ''}

    <!-- Medicos top -->
    ${(op.medicos_top||{}).nombres?.length ? `
    <div class="dash-section">
        <div class="dash-section-header"><i class="bi bi-person-badge"></i> Medicos referenciadores</div>
        <div class="dash-section-body"><div class="dash-chart-container"><canvas id="mChartMedicosTop"></canvas></div></div>
    </div>` : ''}

    <!-- Pacientes nuevos por mes -->
    <div class="dash-section">
        <div class="dash-section-header"><i class="bi bi-person-plus"></i> Pacientes nuevos por mes</div>
        <div class="dash-section-body"><div class="dash-chart-container"><canvas id="mChartPacientesMes"></canvas></div></div>
    </div>

    <!-- Pacientes por EPS -->
    ${(pac.por_eps||{}).nombres?.length ? `
    <div class="dash-section">
        <div class="dash-section-header"><i class="bi bi-shield-check"></i> Pacientes por EPS</div>
        <div class="dash-section-body"><div class="dash-chart-container"><canvas id="mChartPacientesEPS"></canvas></div></div>
    </div>` : ''}

    <!-- Stock por categoria -->
    ${(inv.por_categoria||{}).categorias?.length ? `
    <div class="dash-section">
        <div class="dash-section-header"><i class="bi bi-boxes"></i> Stock por categoria</div>
        <div class="dash-section-body"><div class="dash-chart-container"><canvas id="mChartInventario"></canvas></div></div>
    </div>` : ''}

    <!-- Stock bajo -->
    ${(inv.stock_bajo||[]).length ? `
    <div class="dash-section">
        <div class="dash-section-header"><i class="bi bi-exclamation-diamond"></i> Stock bajo</div>
        <div class="dash-section-body">
            <div class="dash-scroll">
                <table class="dash-table">
                    <thead><tr><th>Item</th><th>Cat.</th><th>Stock</th><th>Min.</th></tr></thead>
                    <tbody>${inv.stock_bajo.map(i => `<tr><td>${i.nombre}</td><td><span class="badge bg-secondary">${i.categoria}</span></td><td style="color:var(--danger);font-weight:700">${i.stock_actual}</td><td>${i.stock_minimo}</td></tr>`).join("")}</tbody>
                </table>
            </div>
        </div>
    </div>` : ''}

    <!-- Alertas -->
    <div class="dash-section">
        <div class="dash-section-header"><i class="bi bi-bell"></i> Alertas</div>
        <div class="dash-section-body">
            ${alertas.length ? alertas.map(a => `<div class="dash-alert ${a.tipo||"info"}"><strong>${a.titulo}</strong>${a.mensaje}</div>`).join("") : '<div class="dash-alert success"><strong>Sin alertas</strong>Todo en orden</div>'}
        </div>
    </div>

    <!-- Actividad -->
    <div class="dash-section">
        <div class="dash-section-header"><i class="bi bi-clock-history"></i> Actividad reciente</div>
        <div class="dash-section-body">
            ${actividad.length ? `
            <div class="dash-scroll" style="max-height:250px">
                <table class="dash-table">
                    <thead><tr><th>Fecha</th><th>Mod.</th><th>Descripcion</th></tr></thead>
                    <tbody>${actividad.map(item => {
                        const iconos={Orden:"bi-clipboard-data",Facturacion:"bi-cash-stack",Gastos:"bi-dash-circle",Inventario:"bi-box-seam"};
                        const colores={Orden:"primary",Facturacion:"success",Gastos:"danger",Inventario:"warning"};
                        const f=item.fecha?new Date(item.fecha):null;
                        const ff=f&&!isNaN(f)?f.toLocaleString("es-CO",{dateStyle:"short",timeStyle:"short"}):"-";
                        return `<tr><td style="white-space:nowrap">${ff}</td><td><span class="badge bg-${colores[item.modulo]||"secondary"}"><i class="bi ${iconos[item.modulo]||"bi-circle"}"></i></span></td><td>${item.descripcion}</td></tr>`;
                    }).join("")}</tbody>
                </table>
            </div>` : '<div class="text-center text-muted small py-2">Sin actividad</div>'}
        </div>
    </div>
    `;

    // Render charts after DOM is ready
    requestAnimationFrame(() => _renderDashboardCharts(data));
}

function _renderDashboardCharts(data) {
    const fin = data.finanzas || {};
    const op = data.operaciones || {};
    const pac = data.pacientes || {};
    const inv = data.inventario || {};

    // Ingresos vs Gastos
    const ig = fin.ingresos_gastos || {};
    if (ig.fechas && ig.fechas.length) {
        _dashCrearChart("mChartIngresosGastos", {
            type: "bar",
            data: {
                labels: ig.fechas.map(f => { const p=f.split("-"); return p[2]+"/"+p[1]; }),
                datasets: [
                    { label:"Ingresos", data:ig.ingresos||[], backgroundColor:"rgba(11,94,215,0.7)", borderRadius:3 },
                    { label:"Gastos", data:ig.gastos||[], backgroundColor:"rgba(220,53,69,0.7)", borderRadius:3 }
                ]
            },
            options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{position:"top",labels:{boxWidth:10,font:{size:10}}}}, scales:{y:{beginAtZero:true,ticks:{font:{size:10},callback:v=>"$"+(v/1000).toFixed(0)+"k"}}} }
        });
    }

    // Gastos por categoria
    const gc = fin.gastos_categoria || {};
    if (gc.categorias && gc.categorias.length) {
        _dashCrearChart("mChartGastosCategoria", {
            type: "doughnut",
            data: { labels:gc.categorias, datasets:[{data:gc.valores,backgroundColor:DASH_COLORES}] },
            options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{position:"right",labels:{boxWidth:10,font:{size:10}}}} }
        });
    }

    // Ordenes por dia
    const od = op.ordenes_dia || {};
    if (od.fechas && od.fechas.length) {
        _dashCrearChart("mChartOrdenesDia", {
            type: "line",
            data: { labels:od.fechas, datasets:[{label:"Ordenes",data:od.totales||[],borderColor:"#0B5ED7",backgroundColor:"rgba(11,94,215,0.1)",fill:true,tension:0.3,pointRadius:3,pointBackgroundColor:"#0B5ED7"}] },
            options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{y:{beginAtZero:true,ticks:{font:{size:10},precision:0}}} }
        });
    }

    // Examenes top
    const et = op.examenes_top || {};
    if (et.nombres && et.nombres.length) {
        _dashCrearChart("mChartExamenesTop", {
            type: "bar",
            data: { labels:et.nombres, datasets:[{label:"Solicitudes",data:et.totales,backgroundColor:DASH_COLORES.slice(0,et.nombres.length),borderRadius:3}] },
            options: { indexAxis:"y", responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{x:{beginAtZero:true,ticks:{font:{size:10},precision:0}}} }
        });
    }

    // Medicos top
    const mt = op.medicos_top || {};
    if (mt.nombres && mt.nombres.length) {
        _dashCrearChart("mChartMedicosTop", {
            type: "bar",
            data: { labels:mt.nombres, datasets:[{label:"Ordenes",data:mt.totales,backgroundColor:DASH_COLORES.slice(0,mt.nombres.length),borderRadius:3}] },
            options: { indexAxis:"y", responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{x:{beginAtZero:true,ticks:{font:{size:10},precision:0}}} }
        });
    }

    // Pacientes nuevos por mes
    const nm = pac.nuevos_mes || {};
    if (nm.labels && nm.labels.length) {
        _dashCrearChart("mChartPacientesMes", {
            type: "bar",
            data: { labels:nm.labels, datasets:[{label:"Nuevos",data:nm.totales||[],backgroundColor:"rgba(25,135,84,0.7)",borderRadius:3}] },
            options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{y:{beginAtZero:true,ticks:{font:{size:10},precision:0}}} }
        });
    }

    // Pacientes por EPS
    const pe = pac.por_eps || {};
    if (pe.nombres && pe.nombres.length) {
        _dashCrearChart("mChartPacientesEPS", {
            type: "doughnut",
            data: { labels:pe.nombres, datasets:[{data:pe.totales,backgroundColor:DASH_COLORES}] },
            options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{position:"right",labels:{boxWidth:10,font:{size:10}}}} }
        });
    }

    // Inventario por categoria
    const ic = inv.por_categoria || {};
    if (ic.categorias && ic.categorias.length) {
        _dashCrearChart("mChartInventario", {
            type: "bar",
            data: { labels:ic.categorias, datasets:[{label:"Items",data:ic.items,backgroundColor:DASH_COLORES.slice(0,ic.categorias.length),borderRadius:3}] },
            options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{y:{beginAtZero:true,ticks:{font:{size:10},precision:0}}} }
        });
    }
}

/* ================================================================
   PROCESAR — Order-level workflow page
   ================================================================ */
async function cargarProcesar() {
    const sesion = await cargarSesion();
    if (!sesion) return;
    await cargarDatos();
    const main = document.getElementById("mainContent");
    document.getElementById("loadingSpinner")?.remove();
    const hoy = hoyLocal();
    main.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px" id="statsProcesar"></div>
        <div class="filter-bar">
            <input type="text" id="busquedaProcesar" placeholder="Buscar por orden o paciente..." oninput="filtrarProcesar()">
            <input type="date" id="filtroFechaProcesar" value="${hoy}" onchange="filtrarProcesar()">
        </div>
        <div class="filter-bar">
            <select id="filtroEstadoProcesar" onchange="filtrarProcesar()">
                <option value="">Todos los estados</option>
                <option value="SIN_MUESTRA">Sin muestra</option>
                <option value="MUESTRA_TOMADA">Muestra tomada</option>
                <option value="EN_PROCESO">En proceso</option>
                <option value="PROCESADO">Procesado</option>
                <option value="POR_VALIDAR">Por validar</option>
                <option value="VALIDADO">Validado</option>
            </select>
            <button class="btn-filter-clear" id="btnLimpiarProcesar" onclick="document.getElementById('busquedaProcesar').value='';document.getElementById('filtroFechaProcesar').value='${hoy}';document.getElementById('filtroEstadoProcesar').value='';filtrarProcesar()"><i class="bi bi-x-circle"></i> Limpiar</button>
        </div>
        <div id="listaResultadosProcesar"></div>
    `;
    filtrarProcesar();
}

function filtrarProcesar() {
    const filtro = (document.getElementById("busquedaProcesar")?.value || "").toLowerCase();
    const fechaFiltro = document.getElementById("filtroFechaProcesar")?.value || hoyLocal();
    const estadoFiltro = document.getElementById("filtroEstadoProcesar")?.value || "";

    const ordenesFiltradas = mobileData.ordenes.filter(o => {
        if (o.fecha_creacion && fechaLocal(o.fecha_creacion) !== fechaFiltro) return false;
        if (estadoFiltro) {
            const est = estadoOrden(o.id);
            if (est !== estadoFiltro) return false;
        }
        if (filtro) {
            const pac = nombrePaciente(o.paciente_id).toLowerCase();
            const num = (o.numero_orden || "").toLowerCase();
            if (!pac.includes(filtro) && !num.includes(filtro)) return false;
        }
        return true;
    });

    ordenesFiltradas.sort((a, b) => (a.numero_orden || "").localeCompare(b.numero_orden || "", "es", { numeric: true }));

    let pendientes = 0, completadas = 0;
    mobileData.ordenes.filter(o => o.fecha_creacion && fechaLocal(o.fecha_creacion) === fechaFiltro).forEach(o => {
        const est = estadoOrden(o.id);
        if (est === "VALIDADO") completadas++;
        else if (est !== "SIN_MUESTRA") pendientes++;
    });

    const statsEl = document.getElementById("statsProcesar");
    if (statsEl) statsEl.innerHTML = `<span class="badge bg-success">${completadas} validadas</span><span class="badge bg-warning">${pendientes} pendientes</span>`;

    const container = document.getElementById("listaResultadosProcesar");
    if (!container) return;
    container.innerHTML = ordenesFiltradas.length === 0
        ? '<div class="empty-state"><i class="bi bi-check-circle"></i><p>No hay \u00f3rdenes para mostrar</p></div>'
        : ordenesFiltradas.map(o => renderOrdenCard(o)).join("");
}

function renderOrdenCard(orden) {
    const estado = estadoOrden(orden.id);
    const paciente = nombrePaciente(orden.paciente_id);
    const doc = documentoPaciente(orden.paciente_id);
    const medico = nombreMedico(orden.medico_id);
    const examenes = examenesPorOrden[orden.id] || [];

    let accionesHtml = "";
    if (estado === "SIN_MUESTRA") {
        accionesHtml = `<button class="btn-examen-accion btn-examen-tomar" onclick="event.stopPropagation();abrirTomarMuestra(${orden.id})"><i class="bi bi-eyedropper"></i> Tomar muestra</button>`;
    } else if (estado === "MUESTRA_TOMADA") {
        const muestra = obtenerMuestra(orden.id);
        accionesHtml = `<button class="btn-examen-accion btn-examen-procesar" onclick="event.stopPropagation();abrirProcesar(${muestra.id})"><i class="bi bi-cpu"></i> Procesar</button>`;
    } else if (estado === "PROCESADO" || estado === "POR_VALIDAR") {
        accionesHtml = `<button class="btn-examen-accion btn-examen-validar" onclick="event.stopPropagation();abrirValidar(${orden.id})"><i class="bi bi-check-circle"></i> Validar</button>`;
    } else if (estado === "VALIDADO") {
        const numRes = (() => {
            const m = obtenerMuestra(orden.id);
            const p = m ? obtenerProcesamiento(m.id) : null;
            const v = p ? obtenerValidacion(p.id) : null;
            return v ? contarResultados(v.id) : 0;
        })();
        accionesHtml = `
            <span class="btn-examen-accion btn-examen-ok"><i class="bi bi-check-circle-fill"></i> OK ${numRes > 0 ? `(${numRes})` : ""}</span>
            <a href="/resultados/orden/${orden.id}/pdf" target="_blank" class="btn-examen-accion" style="color:var(--danger);text-decoration:none" onclick="event.stopPropagation()"><i class="bi bi-file-earmark-pdf"></i> PDF</a>
            <button class="btn-examen-accion btn-examen-validar" onclick="event.stopPropagation();imprimirResultadosOrden(${orden.id}, 'general')"><i class="bi bi-printer"></i> Imprimir</button>`;
    }

    const examenesHtml = examenes.map(ex => {
        return `<span class="badge me-1 mb-1 bg-light text-dark border">${ex.nombre}</span>`;
    }).join("");

    return `
    <div class="orden-card">
        <div class="orden-card-header">
            <div>
                <span class="orden-numero">${orden.numero_orden}</span>
                <span class="list-item-badge ${claseBadge(estado)} ms-2">${textoEstado(estado)}</span>
            </div>
            <span class="orden-fecha">${formatoFecha(orden.fecha_creacion)}${diasBadgeHtml(orden.fecha_creacion)}</span>
        </div>
        <div class="orden-card-body">
            <div class="orden-paciente">${paciente}</div>
            <div class="orden-detalle">${doc} \u00b7 ${medico}</div>
            <div class="orden-resumen mt-1">${examenesHtml || '<span class="text-muted small">Sin ex\u00e1menes</span>'}</div>
            <div class="mt-2">${accionesHtml}</div>
            ${renderWorkflowSteps(estado)}
        </div>
    </div>`;
}

/* ================================================================
   TOMAR MUESTRA — Order-level (all exams in one sample)
   ================================================================ */
async function abrirTomarMuestra(ordenId) {
    const orden = mobileData.ordenes.find(o => o.id === ordenId);
    if (!orden) return;

    const examenes = examenesPorOrden[ordenId] || [];
    const codigoBarras = generarCodigoBarras();

    const opcionesMuestra = ["SANGRE", "ORINA", "HECES", "HISOPADO", "Liquido cefalorraqu\u00eddeo", "OTRO"];
    const tiposUnicos = [...new Set(examenes.map(e => e.tipo_muestra || "SANGRE"))];

    const main = document.getElementById("mainContent");
    main.innerHTML = `
        <a href="javascript:cargarProcesar()" class="btn-back"><i class="bi bi-arrow-left"></i> Volver</a>

        <div class="detail-header">
            <div class="list-item-title" style="margin-bottom:4px">Tomar Muestra</div>
            <div class="detail-row"><span class="detail-label">Orden</span><span class="detail-value">${orden.numero_orden}</span></div>
            <div class="detail-row"><span class="detail-label">Paciente</span><span class="detail-value">${nombrePaciente(orden.paciente_id)}</span></div>
            <div class="detail-row"><span class="detail-label">Ex\u00e1menes</span><span class="detail-value">${examenes.length}</span></div>
            <div class="detail-row"><span class="detail-label">Tipo(s)</span><span class="detail-value">${tiposUnicos.join(", ") || "SANGRE"}</span></div>
        </div>

        <div id="alertaMuestra"></div>

        <div class="card-mobile">
            <div class="form-group">
                <label>C\u00f3digo de barras</label>
                <input type="text" id="tmCodigo" value="${codigoBarras}" readonly style="background:#e2e8f0;font-family:monospace;font-weight:700;">
            </div>
            <div class="form-group">
                <label>Tipo de muestra</label>
                <select id="tmTipo">
                    ${opcionesMuestra.map(op => `<option value="${op}" ${tiposUnicos.includes(op) ? "selected" : ""}>${op}</option>`).join("")}
                </select>
            </div>
            <div class="form-group">
                <label>Recipiente / Tubo</label>
                <input type="text" id="tmRecip" value="${examenes[0]?.recipiente || ""}" placeholder="Ej: Tubo tapa morada...">
            </div>
        </div>

        ${examenes.length > 0 ? `
        <div class="card-mobile">
            <div class="card-mobile-header"><span class="card-mobile-title">Ex\u00e1menes incluidos</span></div>
            ${examenes.map((ex, i) => `
                <div class="detail-row"><span class="detail-label">${i + 1}. ${ex.nombre}</span><span class="detail-value">${ex.tipo_muestra || "SANGRE"}</span></div>
            `).join("")}
        </div>` : ''}

        <button class="btn-primary-mobile" onclick="guardarMuestra(${ordenId})">
            <i class="bi bi-check-lg"></i> Registrar Muestra
        </button>
    `;
}

async function guardarMuestra(ordenId) {
    const codigo_barras = document.getElementById("tmCodigo").value;
    const tipo_muestra = document.getElementById("tmTipo").value;
    const recipiente = document.getElementById("tmRecip").value || null;

    try {
        const resp = await fetch("/muestras/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ orden_id: ordenId, codigo_barras, tipo_muestra, recipiente }),
        });

        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            document.getElementById("alertaMuestra").innerHTML = `<div class="alert-mobile danger">${err.detail || 'Error al guardar muestra.'}</div>`;
            return;
        }

        document.getElementById("mainContent").innerHTML = `
            <div class="empty-state">
                <i class="bi bi-check-circle" style="color:var(--success)"></i>
                <p style="color:var(--success);font-weight:600">Muestra registrada</p>
            </div>
        `;
        setTimeout(() => cargarProcesar(), 1000);
    } catch (e) {
        document.getElementById("alertaMuestra").innerHTML = '<div class="alert-mobile danger">Error de conexi\u00f3n.</div>';
    }
}

/* ================================================================
   PROCESAR — Order-level (process the whole sample)
   ================================================================ */
async function abrirProcesar(muestraId) {
    const muestra = mobileData.muestras.find(m => m.id === muestraId);
    if (!muestra) return;

    const orden = mobileData.ordenes.find(o => o.id === muestra.orden_id);
    const examenes = orden ? (examenesPorOrden[orden.id] || []) : [];

    const analizadores = ["Hemograma automatizado", "Qu\u00edmica sangu\u00ednea", "Urian\u00e1lisis", "Coproparasitol\u00f3gico", "Cultivo", "Biolog\u00eda molecular", "Coagulaci\u00f3n", "Otro"];

    const main = document.getElementById("mainContent");
    main.innerHTML = `
        <a href="javascript:cargarProcesar()" class="btn-back"><i class="bi bi-arrow-left"></i> Volver</a>

        <div class="detail-header">
            <div class="list-item-title" style="margin-bottom:4px">Procesar Orden</div>
            <div class="detail-row"><span class="detail-label">Orden</span><span class="detail-value">${orden ? orden.numero_orden : `#${muestra.orden_id}`}</span></div>
            <div class="detail-row"><span class="detail-label">Paciente</span><span class="detail-value">${orden ? nombrePaciente(orden.paciente_id) : ""}</span></div>
            <div class="detail-row"><span class="detail-label">Muestra</span><span class="detail-value">${muestra.codigo_barras} (${muestra.tipo_muestra})</span></div>
            <div class="detail-row"><span class="detail-label">Ex\u00e1menes</span><span class="detail-value">${examenes.length}</span></div>
        </div>

        <div id="alertaProcesar"></div>

        <div class="card-mobile">
            <div class="form-group">
                <label>Analizador / Equipo *</label>
                <select id="prAnalizador">
                    <option value="">Seleccionar...</option>
                    ${analizadores.map(a => `<option value="${a}">${a}</option>`).join("")}
                </select>
            </div>
            <div class="form-group">
                <label>Observaciones</label>
                <textarea id="prObs" rows="2" placeholder="Opcional..."></textarea>
            </div>
        </div>

        ${examenes.length > 0 ? `
        <div class="card-mobile">
            <div class="card-mobile-header"><span class="card-mobile-title">Ex\u00e1menes incluidos</span></div>
            ${examenes.map((ex, i) => `
                <div class="detail-row"><span class="detail-label">${i + 1}. ${ex.nombre}</span><span class="detail-value">${ex.categoria || ""}</span></div>
            `).join("")}
        </div>` : ''}

        <button class="btn-primary-mobile" onclick="guardarProcesamiento(${muestra.id})">
            <i class="bi bi-check-lg"></i> Procesar Orden
        </button>
    `;
}

async function guardarProcesamiento(muestraId) {
    const analizador = document.getElementById("prAnalizador").value;
    const observaciones = document.getElementById("prObs").value;

    if (!analizador) {
        document.getElementById("alertaProcesar").innerHTML = '<div class="alert-mobile danger">Seleccione un analizador.</div>';
        return;
    }

    try {
        const resp = await fetch("/procesamientos/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ muestra_id: muestraId, analizador, observaciones }),
        });

        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            document.getElementById("alertaProcesar").innerHTML = `<div class="alert-mobile danger">${err.detail || 'Error al guardar.'}</div>`;
            return;
        }

        const proc = await resp.json();
        await fetch(`/procesamientos/${proc.id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ estado: "COMPLETADO", fecha_fin: new Date().toISOString() }),
        });

        document.getElementById("mainContent").innerHTML = `
            <div class="empty-state">
                <i class="bi bi-check-circle" style="color:var(--success)"></i>
                <p style="color:var(--success);font-weight:600">Proceso registrado</p>
            </div>
        `;
        setTimeout(() => cargarProcesar(), 1000);
    } catch (e) {
        document.getElementById("alertaProcesar").innerHTML = '<div class="alert-mobile danger">Error de conexi\u00f3n.</div>';
    }
}

/* ================================================================
   VALIDAR — Order-level
   ================================================================ */
async function cargarValidar() {
    const sesion = await cargarSesion();
    if (!sesion) return;
    await cargarDatos();
    const main = document.getElementById("mainContent");
    document.getElementById("loadingSpinner")?.remove();
    const hoy = hoyLocal();
    main.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px" id="statsValidar"></div>
        <div class="filter-bar">
            <input type="text" id="busquedaValidar" placeholder="Buscar por orden o paciente..." oninput="filtrarValidar()">
            <input type="date" id="filtroFechaValidar" value="${hoy}" onchange="filtrarValidar()">
        </div>
        <div class="filter-bar">
            <select id="filtroEstadoValidar" onchange="filtrarValidar()">
                <option value="">Todos los estados</option>
                <option value="MUESTRA_TOMADA">Muestra tomada</option>
                <option value="EN_PROCESO">En proceso</option>
                <option value="PROCESADO">Procesado</option>
                <option value="POR_VALIDAR">Por validar</option>
                <option value="VALIDADO">Validado</option>
            </select>
            <button class="btn-filter-clear" onclick="document.getElementById('busquedaValidar').value='';document.getElementById('filtroFechaValidar').value='${hoy}';document.getElementById('filtroEstadoValidar').value='';filtrarValidar()"><i class="bi bi-x-circle"></i> Limpiar</button>
        </div>
        <div id="listaResultadosValidar"></div>
    `;
    filtrarValidar();
}

function filtrarValidar() {
    const filtro = (document.getElementById("busquedaValidar")?.value || "").toLowerCase();
    const fechaFiltro = document.getElementById("filtroFechaValidar")?.value || hoyLocal();
    const estadoFiltro = document.getElementById("filtroEstadoValidar")?.value || "";

    const pendientes = mobileData.ordenes.filter(o => {
        if (o.fecha_creacion && fechaLocal(o.fecha_creacion) !== fechaFiltro) return false;
        const est = estadoOrden(o.id);
        if (est === "SIN_MUESTRA" || est === "PENDIENTE" || est === "VALIDADO") return false;
        if (estadoFiltro && est !== estadoFiltro) return false;
        if (filtro) {
            const pac = nombrePaciente(o.paciente_id).toLowerCase();
            const num = (o.numero_orden || "").toLowerCase();
            if (!pac.includes(filtro) && !num.includes(filtro)) return false;
        }
        return true;
    });

    const validados = mobileData.ordenes.filter(o => {
        if (o.fecha_creacion && fechaLocal(o.fecha_creacion) !== fechaFiltro) return false;
        const est = estadoOrden(o.id);
        if (estadoFiltro && est !== estadoFiltro) return false;
        if (filtro) {
            const pac = nombrePaciente(o.paciente_id).toLowerCase();
            const num = (o.numero_orden || "").toLowerCase();
            if (!pac.includes(filtro) && !num.includes(filtro)) return false;
        }
        return est === "VALIDADO";
    });

    const ordenar = (arr) => arr.sort((a, b) => (a.numero_orden || "").localeCompare(b.numero_orden || "", "es", { numeric: true }));
    ordenar(pendientes);
    ordenar(validados);

    const statsEl = document.getElementById("statsValidar");
    if (statsEl) statsEl.innerHTML = `<span class="badge bg-warning">${pendientes.length} pendientes</span><span class="badge bg-success">${validados.length} validadas</span>`;

    const container = document.getElementById("listaResultadosValidar");
    if (!container) return;

    let html = "";
    if (pendientes.length === 0 && validados.length === 0) {
        html = '<div class="empty-state"><i class="bi bi-check-circle"></i><p>No hay procesamientos pendientes de validaci\u00f3n</p></div>';
    } else {
        if (pendientes.length > 0) {
            html += `<div class="card-mobile">
                <div class="card-mobile-header"><span class="card-mobile-title">Pendientes por validar (${pendientes.length})</span></div>
                ${pendientes.map(o => {
                    const examenes = examenesPorOrden[o.id] || [];
                    const muestra = obtenerMuestra(o.id);
                    const proc = muestra ? obtenerProcesamiento(muestra.id) : null;
                    return `
                    <div class="list-item" onclick="abrirValidar(${o.id})">
                        <div class="list-item-header">
                            <span class="list-item-title">${o.numero_orden}</span>
                            <span class="list-item-badge ${claseBadge(estadoOrden(o.id))}">${textoEstado(estadoOrden(o.id))}</span>
                        </div>
                        <div class="list-item-sub">${nombrePaciente(o.paciente_id)} \u00b7 ${examenes.length} ex\u00e1menes</div>
                        <div class="list-item-sub">${muestra?.codigo_barras || ''} \u2014 ${proc?.analizador || ''}</div>
                    </div>`;
                }).join("")}
            </div>`;
        }
        if (validados.length > 0) {
            html += `<div class="card-mobile">
                <div class="card-mobile-header"><span class="card-mobile-title">Ya validados (${validados.length})</span></div>
                ${validados.map(o => {
                    const examenes = examenesPorOrden[o.id] || [];
                    const val = (() => { const m = obtenerMuestra(o.id); const p = m ? obtenerProcesamiento(m.id) : null; return p ? obtenerValidacion(p.id) : null; })();
                    const numRes = val ? contarResultados(val.id) : 0;
                    return `
                    <div class="list-item list-item-readonly" onclick="verDetalleValidado(${o.id})">
                        <div class="list-item-header">
                            <span class="list-item-title">${o.numero_orden}</span>
                            <span class="list-item-badge badge-validado"><i class="bi bi-check-circle-fill"></i> Validado</span>
                        </div>
                        <div class="list-item-sub">${nombrePaciente(o.paciente_id)} \u00b7 ${examenes.length} ex\u00e1menes \u00b7 ${numRes} resultados</div>
                    </div>`;
                }).join("")}
            </div>`;
        }
    }
    container.innerHTML = html;
}

async function abrirValidar(ordenId) {
    const orden = mobileData.ordenes.find(o => o.id === ordenId);
    if (!orden) return;

    const muestra = obtenerMuestra(ordenId);
    if (!muestra) return;

    const proc = obtenerProcesamiento(muestra.id);
    if (!proc) return;

    let val = obtenerValidacion(proc.id);
    if (!val) {
        try {
            const resp = await fetch("/validaciones/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ procesamiento_id: proc.id }),
            });
            if (resp.ok) {
                val = await resp.json();
                mobileData.validaciones.push(val);
            } else {
                const reResp = await fetch("/validaciones/");
                if (reResp.ok) {
                    mobileData.validaciones = await reResp.json();
                    val = mobileData.validaciones.find(v => v.procesamiento_id === proc.id);
                }
            }
        } catch (e) { /* ignore */ }
    }

    const examenes = examenesPorOrden[ordenId] || [];
    const paciente = nombrePaciente(orden.paciente_id);

    let parametrosHtml = "";
    for (const examen of examenes) {
        const params = mobileData.parametros.filter(p => p.examen_id === examen.id);
        parametrosHtml += `<div class="parametro-grupo" data-examen-id="${examen.id}">`;
        parametrosHtml += `<h6 class="param-examen-title">${examen.nombre} <small class="text-muted">(${examen.categoria || ""})</small></h6>`;

        if (!params.length) {
            parametrosHtml += `
                <div class="parametro-fila">
                    <input class="param-input" data-tipo="libre-nombre" data-examen="${examen.nombre}" placeholder="Nombre">
                    <input class="param-input" data-tipo="libre-valor" placeholder="Resultado">
                    <input class="param-input" data-tipo="libre-unidad" placeholder="Und.">
                    <input class="param-input" data-tipo="libre-ref" placeholder="Ref.">
                </div>`;
        } else {
            for (const param of params) {
                let inputHtml = "";
                if (param.tipo === "SELECT" && param.opciones) {
                    const opciones = param.opciones.split(",").map(o => o.trim());
                    inputHtml = `<select class="param-input" data-param-id="${param.id}" data-min="${param.valor_minimo || ""}" data-max="${param.valor_maximo || ""}">
                        <option value="">...</option>
                        ${opciones.map(o => `<option value="${o}">${o}</option>`).join("")}
                    </select>`;
                } else {
                    inputHtml = `<input type="number" step="any" class="param-input" data-param-id="${param.id}" data-min="${param.valor_minimo || ""}" data-max="${param.valor_maximo || ""}" placeholder="...">`;
                }
                parametrosHtml += `
                    <div class="parametro-fila">
                        <span class="param-nombre">${param.nombre}</span>
                        <span class="param-und">${param.unidad || ""}</span>
                        <span class="param-ref">${param.valor_referencia || ""}</span>
                        ${inputHtml}
                    </div>`;
            }
        }
        parametrosHtml += `</div>`;
    }

    const main = document.getElementById("mainContent");
    main.innerHTML = `
        <a href="javascript:cargarValidar()" class="btn-back"><i class="bi bi-arrow-left"></i> Volver</a>

        <div class="detail-header">
            <div class="list-item-title" style="margin-bottom:8px">${orden.numero_orden}</div>
            <div class="detail-row"><span class="detail-label">Paciente</span><span class="detail-value">${paciente}</span></div>
            <div class="detail-row"><span class="detail-label">Documento</span><span class="detail-value">${documentoPaciente(orden.paciente_id)}</span></div>
            <div class="detail-row"><span class="detail-label">Muestra</span><span class="detail-value">${muestra.codigo_barras} (${muestra.tipo_muestra})</span></div>
            <div class="detail-row"><span class="detail-label">Analizador</span><span class="detail-value">${proc.analizador}</span></div>
            <div class="detail-row"><span class="detail-label">Ex\u00e1menes</span><span class="detail-value">${examenes.length}</span></div>
        </div>

        <div class="card-mobile">
            <div class="card-mobile-header"><span class="card-mobile-title">Resultados por ex\u00e1men</span></div>
            <div id="formParametros">${parametrosHtml}</div>
        </div>

        <div id="alertaValidar"></div>

        <div class="card-mobile">
            <div class="form-group">
                <label>Observaciones</label>
                <textarea id="valObservaciones" rows="2" placeholder="Observaciones de validaci\u00f3n..."></textarea>
            </div>
        </div>

        <button class="btn-success-mobile" onclick="confirmarValidacion(${val?.id || 0})">
            <i class="bi bi-check-circle"></i> Validar orden completa
        </button>
    `;
}

async function confirmarValidacion(validacionId) {
    if (!validacionId) {
        document.getElementById("alertaValidar").innerHTML = '<div class="alert-mobile danger">No se pudo identificar la validaci\u00f3n.</div>';
        return;
    }

    const container = document.getElementById("formParametros");
    const inputs = container ? container.querySelectorAll(".param-input") : [];
    const resultados = [];

    inputs.forEach(input => {
        const valor = input.value;
        if (!valor) return;

        const paramId = input.dataset.paramId;

        if (paramId) {
            const param = mobileData.parametros.find(p => p.id === parseInt(paramId, 10));
            if (param) {
                const examen = mobileData.examenes.find(e => e.id === param.examen_id);
                const valorNumerico = param.tipo === "NUMERICO" ? parseFloat(valor) : null;
                resultados.push({
                    examen: param.nombre,
                    examen_codigo: examen ? examen.codigo : null,
                    resultado: param.tipo === "SELECT" ? valor : null,
                    valor_numerico: valorNumerico,
                    unidad: param.unidad || null,
                    valor_referencia: param.valor_referencia || null,
                    critico: false,
                });
            }
        } else {
            const grupo = input.closest(".parametro-grupo");
            const examenId = grupo ? parseInt(grupo.dataset.examenId, 10) : null;
            const examen = examenId ? mobileData.examenes.find(e => e.id === examenId) : null;
            const nombreInput = grupo ? grupo.querySelector("[data-tipo='libre-nombre']") : null;
            resultados.push({
                examen: nombreInput ? `${nombreInput.dataset.examen} - ${nombreInput.value}` : "Resultado",
                examen_codigo: examen ? examen.codigo : null,
                resultado: valor,
                valor_numerico: null,
                unidad: null,
                valor_referencia: null,
                critico: false,
            });
        }
    });

    if (!resultados.length) {
        document.getElementById("alertaValidar").innerHTML = '<div class="alert-mobile danger">Ingrese al menos un resultado.</div>';
        return;
    }

    const observaciones = document.getElementById("valObservaciones").value;
    const validadorId = mobileSession?.user_id || null;

    try {
        for (const r of resultados) {
            await fetch("/resultados/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ validacion_id: validacionId, ...r }),
            });
        }

        const resp = await fetch(`/validaciones/${validacionId}/validar`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ validador_id: validadorId, observaciones }),
        });

        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            document.getElementById("alertaValidar").innerHTML = `<div class="alert-mobile danger">${err.detail || 'Error al validar.'}</div>`;
            return;
        }

        document.getElementById("mainContent").innerHTML = `
            <div class="empty-state">
                <i class="bi bi-check-circle" style="color:var(--success)"></i>
                <p style="color:var(--success);font-weight:600">Orden validada \u2014 ${resultados.length} resultados guardados</p>
            </div>
        `;
        setTimeout(() => cargarValidar(), 1500);
    } catch (e) {
        document.getElementById("alertaValidar").innerHTML = '<div class="alert-mobile danger">Error de conexi\u00f3n.</div>';
    }
}

/* ================================================================
   DETALLE VALIDADO (read-only)
   ================================================================ */
function verDetalleValidado(ordenId) {
    const orden = mobileData.ordenes.find(o => o.id === ordenId);
    if (!orden) return;

    const paciente = nombrePaciente(orden.paciente_id);
    const doc = documentoPaciente(orden.paciente_id);
    const examenes = examenesPorOrden[orden.id] || [];
    const muestra = obtenerMuestra(ordenId);
    const proc = muestra ? obtenerProcesamiento(muestra.id) : null;
    const val = proc ? obtenerValidacion(proc.id) : null;
    const validador = val?.validador_id ? nombreMedico(val.validador_id) : "\u2014";
    const numRes = val ? contarResultados(val.id) : 0;

    const resultados = val ? mobileData.resultados.filter(r => r.validacion_id === val.id) : [];

    const main = document.getElementById("mainContent");
    main.innerHTML = `
        <a href="javascript:cargarValidar()" class="btn-back"><i class="bi bi-arrow-left"></i> Volver</a>

        <div class="detail-header">
            <div class="list-item-title" style="margin-bottom:8px">${orden.numero_orden}</div>
            <span class="list-item-badge badge-validado" style="margin-bottom:8px"><i class="bi bi-check-circle-fill"></i> Validado</span>
            <div class="detail-row"><span class="detail-label">Paciente</span><span class="detail-value">${paciente}</span></div>
            <div class="detail-row"><span class="detail-label">Documento</span><span class="detail-value">${doc}</span></div>
            <div class="detail-row"><span class="detail-label">Muestra</span><span class="detail-value">${muestra?.codigo_barras || '\u2014'} (${muestra?.tipo_muestra || '\u2014'})</span></div>
            <div class="detail-row"><span class="detail-label">Analizador</span><span class="detail-value">${proc?.analizador || '\u2014'}</span></div>
            <div class="detail-row"><span class="detail-label">Validado por</span><span class="detail-value">${validador}</span></div>
            <div class="detail-row"><span class="detail-label">Fecha</span><span class="detail-value">${val?.fecha_validacion ? formatoFecha(val.fecha_validacion) + ' ' + formatoHora(val.fecha_validacion) : '\u2014'}</span></div>
            ${val?.observaciones ? `<div class="detail-row"><span class="detail-label">Obs.</span><span class="detail-value">${val.observaciones}</span></div>` : ''}
            <div class="detail-row"><span class="detail-label">Ex\u00e1menes</span><span class="detail-value">${examenes.length} \u00b7 ${numRes} resultados</span></div>
        </div>

        <div class="card-mobile">
            <div class="card-mobile-header"><span class="card-mobile-title">Ex\u00e1menes</span></div>
            ${examenes.map(ex => `<div class="detail-row"><span class="detail-label">${ex.nombre}</span><span class="detail-value"><span class="list-item-badge badge-validado" style="font-size:.7rem">OK</span></span></div>`).join("")}
        </div>

        ${resultados.length > 0 ? `
        <div class="card-mobile">
            <div class="card-mobile-header"><span class="card-mobile-title">Resultados (${numRes})</span></div>
            <table class="results-table">
                <thead><tr><th>Par\u00e1metro</th><th>Resultado</th><th>Ref.</th></tr></thead>
                <tbody>
                ${resultados.map(r => `
                    <tr class="${r.critico ? 'result-critico' : ''}">
                        <td>${r.examen || ''}</td>
                        <td><strong>${r.resultado || r.valor_numerico || '\u2014'}</strong> ${r.unidad || ''}</td>
                        <td>${r.valor_referencia || ''}</td>
                    </tr>
                `).join("")}
                </tbody>
            </table>
        </div>` : ''}
    `;
}

/* ================================================================
   PRINT RESULTS — order-level (from validated state)
   ================================================================ */
async function imprimirResultadosOrden(ordenId, modo) {
    if (!modo) modo = "general";

    const orden = mobileData.ordenes.find(o => o.id === ordenId);
    if (!orden) return;

    const muestra = obtenerMuestra(ordenId);
    const proc = muestra ? obtenerProcesamiento(muestra.id) : null;
    const val = proc ? obtenerValidacion(proc.id) : null;

    const validador = val && val.validador_id ? mobileData.medicos.find(m => m.id === val.validador_id) : null;

    let examenes = [];
    try {
        const r = await fetch(`/ordenes/${ordenId}/examenes`);
        examenes = r.ok ? await r.json() : [];
    } catch (e) { /* ignore */ }

    let resultadosValidacion = [];
    if (val) {
        resultadosValidacion = mobileData.resultados.filter(r => r.validacion_id === val.id);
    }

    const observaciones = val ? (val.observaciones || "") : "";

    if (modo === "general") {
        _imprimirResultadosOrdenGeneral(examenes, resultadosValidacion, orden, muestra, proc, validador, observaciones);
    } else {
        _imprimirResultadosOrdenEspecifico(examenes, resultadosValidacion, orden, muestra, proc, validador, observaciones);
    }
}

function _getResultadosExamen(examenes, resultadosValidacion, examen) {
    let res = resultadosValidacion.filter(r => r.examen_codigo && r.examen_codigo === examen.codigo);
    if (!res.length) {
        const paramsExamen = mobileData.parametros.filter(p => p.examen_id === examen.id);
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

function _encabezadoImpresion(subtitulo) {
    const c = mobileData.configLab || {};
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

function _pieImpresion(validador) {
    const fecha = new Date().toLocaleDateString("es-CO", { day: "2-digit", month: "long", year: "numeric" });
    const firmaHtml = validador && validador.firma_path
        ? `<img src="/static/${validador.firma_path}" style="height:40px;">`
        : `<div style="border-top:1px solid #333;width:130px;margin:0 auto;"></div>`;
    const validadorNombre = validador ? `${validador.nombres} ${validador.apellidos}` : "\u2014";
    const pie = mobileData.configLab?.pie_pagina || "";

    return `
    <div style="margin-top:auto;padding-top:4mm;border-top:1px solid #ddd;">
        <div style="display:flex;justify-content:space-between;align-items:flex-end;flex-shrink:0;">
            <div style="text-align:center;width:35%;">
                ${firmaHtml}
                <div style="font-size:8pt;font-weight:600;color:#333;border-top:1px solid #333;padding-top:2mm;margin-top:2mm;">Firma del Validador<br><span style="font-weight:400;">${validadorNombre}</span></div>
            </div>
            <div style="text-align:center;width:30%;">
                <div style="font-size:7.5pt;color:#777;">Fecha de impresi\u00f3n:<br>${fecha}</div>
            </div>
            <div style="text-align:center;width:35%;">
                <div style="border-top:1px solid #333;padding-top:2mm;margin-top:10mm;font-size:8pt;color:#333;">Firma del M\u00e9dico</div>
            </div>
        </div>
        ${pie ? `<div style="text-align:center;font-size:6.5pt;color:#999;margin-top:3mm;">${pie}</div>` : ""}
    </div>`;
}

function _abrirVentanaImpresion(titulo, contenidoHtml) {
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

function _imprimirResultadosOrdenGeneral(examenes, resultadosValidacion, orden, muestra, proc, validador, observaciones) {
    let todasFilas = "";

    for (const examen of examenes) {
        const resultadosExamen = _getResultadosExamen(examenes, resultadosValidacion, examen);

        if (resultadosExamen.length) {
            resultadosExamen.forEach(r => {
                todasFilas += `<tr>
                    <td style="padding:1.5mm;">${examen.nombre}</td>
                    <td style="padding:1.5mm;">${r.examen}</td>
                    <td style="padding:1.5mm;text-align:center;font-weight:bold;">${r.resultado || r.valor_numerico || "\u2014"}</td>
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

    const html = `
        <div class="pagina-a4" style="width:215mm;height:279mm;overflow:hidden;padding:4mm 6mm;font-family:Arial,sans-serif;font-size:10pt;page-break-after:always;page-break-inside:avoid;display:flex;flex-direction:column;box-sizing:border-box;">
            ${_encabezadoImpresion("Resultados Generales")}

            <div style="display:flex;gap:6mm;margin-bottom:2mm;font-size:9pt;">
                <div style="flex:1;border:1px solid #e0e0e0;padding:2mm 3mm;border-radius:3px;background:#f9fafb;">
                    <strong>Orden:</strong> ${orden.numero_orden}<br>
                    <strong>Paciente:</strong> ${nombrePaciente(orden.paciente_id)}<br>
                    <strong>Documento:</strong> ${documentoPaciente(orden.paciente_id)}<br>
                    <strong>M\u00e9dico:</strong> ${nombreMedico(orden.medico_id)}
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
                        <th style="padding:1.5mm 1.5mm;text-align:left;">Par\u00e1metro</th>
                        <th style="padding:1.5mm 1.5mm;text-align:center;">Resultado</th>
                        <th style="padding:1.5mm 1.5mm;text-align:center;">Unidad</th>
                        <th style="padding:1.5mm 1.5mm;text-align:center;">Referencia</th>
                    </tr></thead>
                    <tbody>${todasFilas}</tbody>
                </table>
            </div>

            ${observaciones ? `<div style="margin-bottom:2mm;font-size:9pt;"><strong>Observaciones:</strong> ${observaciones}</div>` : ""}

            ${_pieImpresion(validador)}
        </div>`;

    _abrirVentanaImpresion(`Resultados ${orden.numero_orden}`, html);
}

function _imprimirResultadosOrdenEspecifico(examenes, resultadosValidacion, orden, muestra, proc, validador, observaciones) {
    let paginasHtml = "";

    for (const examen of examenes) {
        const resultadosExamen = _getResultadosExamen(examenes, resultadosValidacion, examen);

        let paramsHtml = "";
        if (resultadosExamen.length) {
            paramsHtml = resultadosExamen.map(r => `<tr><td style="padding:2mm;">${r.examen}</td><td style="padding:2mm;text-align:center;font-weight:bold;">${r.resultado || r.valor_numerico || "\u2014"}</td><td style="padding:2mm;text-align:center;">${r.unidad || ""}</td><td style="padding:2mm;text-align:center;">${r.valor_referencia || ""}</td></tr>`).join("");
        } else {
            paramsHtml = '<tr><td colspan="4" class="text-muted" style="padding:2mm;text-align:center;">Sin resultados registrados para este examen</td></tr>';
        }

        paginasHtml += `
        <div class="pagina-a4" style="width:215mm;height:279mm;overflow:hidden;padding:4mm 6mm;font-family:Arial,sans-serif;font-size:10pt;page-break-after:always;page-break-inside:avoid;display:flex;flex-direction:column;box-sizing:border-box;">
            ${_encabezadoImpresion("Resultado de Examen")}

            <div style="display:flex;gap:6mm;margin-bottom:2mm;font-size:9pt;">
                <div style="flex:1;border:1px solid #e0e0e0;padding:2mm 3mm;border-radius:3px;background:#f9fafb;">
                    <strong>Orden:</strong> ${orden.numero_orden}<br>
                    <strong>Paciente:</strong> ${nombrePaciente(orden.paciente_id)}<br>
                    <strong>Documento:</strong> ${documentoPaciente(orden.paciente_id)}<br>
                    <strong>M\u00e9dico:</strong> ${nombreMedico(orden.medico_id)}
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
                        <th style="padding:1.5mm 1.5mm;text-align:left;">Par\u00e1metro</th>
                        <th style="padding:1.5mm 1.5mm;text-align:center;">Resultado</th>
                        <th style="padding:1.5mm 1.5mm;text-align:center;">Unidad</th>
                        <th style="padding:1.5mm 1.5mm;text-align:center;">Referencia</th>
                    </tr></thead>
                    <tbody>${paramsHtml}</tbody>
                </table>
            </div>

            ${observaciones ? `<div style="margin-bottom:2mm;font-size:9pt;"><strong>Observaciones:</strong> ${observaciones}</div>` : ""}

            ${_pieImpresion(validador)}
        </div>`;
    }

    if (!paginasHtml) {
        return;
    }

    _abrirVentanaImpresion(`Resultados ${orden.numero_orden}`, paginasHtml);
}
