/******************************************************************************
 * LABSYS DIALIZAR
 * app/static/js/medicos.js
 ******************************************************************************/

let medicosTodos = [];
let filtroActual = "TODOS";

function alertaMedicos(id, mensaje, tipo = "danger") {
    document.getElementById(id).innerHTML = `<div class="alert alert-${tipo} py-2">${mensaje}</div>`;
}

async function cargarMedicos() {
    try {
        const resp = await fetch("/medicos/");
        medicosTodos = resp.ok ? await resp.json() : [];
        renderTabla();
    } catch (error) {
        alertaMedicos("alertaMedicos", "No se pudo cargar el listado.");
    }
}

function badgeTipo(tipo) {
    if (tipo === "MEDICO") return '<span class="badge bg-primary">Médico</span>';
    if (tipo === "ENFERMERO") return '<span class="badge bg-info">Enfermero/a</span>';
    return '<span class="badge bg-purple" style="background:#8e44ad">Bacteriólogo/a</span>';
}

function renderTabla() {
    const tbody = document.getElementById("tablaMedicos");
    const lista = filtroActual === "TODOS"
        ? medicosTodos
        : medicosTodos.filter(m => m.tipo_profesional === filtroActual);

    if (!lista.length) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-muted small">No hay registros.</td></tr>';
        return;
    }

    tbody.innerHTML = lista.map(m => `
        <tr>
            <td>${badgeTipo(m.tipo_profesional)}</td>
            <td>${m.registro_medico}</td>
            <td>${m.nombres} ${m.apellidos}</td>
            <td>${m.especialidad || '-'}</td>
            <td>${m.telefono || '-'}</td>
            <td>${m.correo || '-'}</td>
            <td>${m.firma_path ? '<i class="bi bi-check-circle-fill text-success"></i>' : '<i class="bi bi-dash-circle text-muted"></i>'}</td>
            <td>
                <button class="btn btn-sm btn-outline-secondary" onclick="editarMedico(${m.id})">
                    <i class="bi bi-pencil"></i> Editar
                </button>
                <button class="btn btn-sm btn-outline-primary" onclick="abrirModalFirma(${m.id})">
                    <i class="bi bi-pen"></i> Firma
                </button>
            </td>
        </tr>
    `).join("");
}

function filtrarTipo(event, tipo) {
    event.preventDefault();
    filtroActual = tipo;
    document.querySelectorAll(".nav-tabs .nav-link").forEach(a => a.classList.remove("active"));
    event.target.classList.add("active");
    renderTabla();
}

function limpiarFormularioMedico() {
    document.getElementById("alertaModalMedico").innerHTML = "";
    document.getElementById("medicoId").value = "";
    document.getElementById("medicoRegistro").value = "";
    document.getElementById("medicoNombres").value = "";
    document.getElementById("medicoApellidos").value = "";
    document.getElementById("medicoEspecialidad").value = "";
    document.getElementById("medicoTelefono").value = "";
    document.getElementById("medicoCorreo").value = "";
    document.getElementById("tipoMedico").checked = true;
}

function editarMedico(id) {
    const m = medicosTodos.find(x => x.id === id);
    if (!m) return;

    limpiarFormularioMedico();
    document.getElementById("tituloModalMedico").textContent = "Editar médico / enfermera";
    document.getElementById("medicoId").value = m.id;
    document.getElementById("medicoRegistro").value = m.registro_medico;
    document.getElementById("medicoNombres").value = m.nombres;
    document.getElementById("medicoApellidos").value = m.apellidos;
    document.getElementById("medicoEspecialidad").value = m.especialidad || "";
    document.getElementById("medicoTelefono").value = m.telefono || "";
    document.getElementById("medicoCorreo").value = m.correo || "";
    if (m.tipo_profesional === "ENFERMERO") {
        document.getElementById("tipoEnfermero").checked = true;
    } else {
        document.getElementById("tipoMedico").checked = true;
    }

    new bootstrap.Modal(document.getElementById("modalNuevoMedico")).show();
}

async function guardarMedico() {
    const id = document.getElementById("medicoId").value;

    const payload = {
        tipo_profesional: document.querySelector('input[name="tipoProfesional"]:checked').value,
        registro_medico: document.getElementById("medicoRegistro").value,
        nombres: document.getElementById("medicoNombres").value,
        apellidos: document.getElementById("medicoApellidos").value,
        especialidad: document.getElementById("medicoEspecialidad").value || null,
        telefono: document.getElementById("medicoTelefono").value || null,
        correo: document.getElementById("medicoCorreo").value || null,
    };

    if (!payload.registro_medico || !payload.nombres || !payload.apellidos) {
        alertaMedicos("alertaModalMedico", "Registro, nombres y apellidos son obligatorios.");
        return;
    }

    const esEdicion = !!id;
    const url = esEdicion ? `/medicos/${id}` : "/medicos/";
    const metodo = esEdicion ? "PUT" : "POST";
    if (esEdicion) payload.activo = true;

    try {
        const resp = await fetch(url, {
            method: metodo,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!resp.ok) {
                        alertaMedicos("alertaModalMedico", await extraerMensajeError(resp, "No se pudo guardar."));
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById("modalNuevoMedico")).hide();
        await cargarMedicos();
    } catch (error) {
        alertaMedicos("alertaModalMedico", "Error de conexión al guardar.");
    }
}

async function importarExcelMedicos() {
    const input = document.getElementById("archivoImportarMedicos");
    const archivo = input.files[0];

    document.getElementById("alertaImportarMedicos").innerHTML = "";
    document.getElementById("resultadoImportarMedicos").innerHTML = "";

    if (!archivo) {
        alertaMedicos("alertaImportarMedicos", "Seleccione un archivo .xlsx primero.");
        return;
    }

    const formData = new FormData();
    formData.append("archivo", archivo);

    try {
        const resp = await fetch("/medicos/importar/excel", { method: "POST", body: formData });

        if (!resp.ok) {
            alertaMedicos("alertaImportarMedicos", await extraerMensajeError(resp, "No se pudo importar el archivo."));
            return;
        }

        const resultado = await resp.json();
        let html = `<div class="alert alert-success py-2">Se crearon ${resultado.creados} de ${resultado.total_filas} profesional(es).</div>`;
        if (resultado.errores.length) {
            html += `<div class="alert alert-warning py-2"><strong>Filas con error:</strong><br>${resultado.errores.join("<br>")}</div>`;
        }
        document.getElementById("resultadoImportarMedicos").innerHTML = html;

        await cargarMedicos();
    } catch (error) {
        alertaMedicos("alertaImportarMedicos", "Error de conexión al importar.");
    }
}

function abrirModalFirma(id) {
    const m = medicosTodos.find(x => x.id === id);
    if (!m) return;

    document.getElementById("alertaModalFirma").innerHTML = "";
    document.getElementById("firmaMedicoId").value = id;
    document.getElementById("archivoFirma").value = "";

    const preview = document.getElementById("previewFirma");
    if (m.firma_path) {
        preview.src = `/static/${m.firma_path}?t=${Date.now()}`;
        preview.style.display = "inline-block";
    } else {
        preview.style.display = "none";
    }

    const canvas = document.getElementById("canvasFirma");
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const tabSubir = document.querySelector('[data-bs-target="#tabSubirFirma"]');
    const tabSubirPane = document.getElementById("tabSubirFirma");
    tabSubir.classList.add("active");
    tabSubirPane.classList.add("show", "active");
    const tabDibujar = document.querySelector('[data-bs-target="#tabDibujarFirma"]');
    const tabDibujarPane = document.getElementById("tabDibujarFirma");
    tabDibujar.classList.remove("active");
    tabDibujarPane.classList.remove("show", "active");

    new bootstrap.Modal(document.getElementById("modalFirma")).show();
}

let _firmaDibujando = false;
let _firmaCanvasInit = false;

function _initCanvasFirma() {
    if (_firmaCanvasInit) return;
    _firmaCanvasInit = true;

    const canvas = document.getElementById("canvasFirma");
    const ctx = canvas.getContext("2d");

    ctx.strokeStyle = "#000";
    ctx.lineWidth = 2.5;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";

    function getPos(e) {
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;
        if (e.touches) {
            return {
                x: (e.touches[0].clientX - rect.left) * scaleX,
                y: (e.touches[0].clientY - rect.top) * scaleY,
            };
        }
        return {
            x: (e.clientX - rect.left) * scaleX,
            y: (e.clientY - rect.top) * scaleY,
        };
    }

    function iniciar(e) {
        e.preventDefault();
        _firmaDibujando = true;
        const pos = getPos(e);
        ctx.beginPath();
        ctx.moveTo(pos.x, pos.y);
    }

    function dibujar(e) {
        if (!_firmaDibujando) return;
        e.preventDefault();
        const pos = getPos(e);
        ctx.lineTo(pos.x, pos.y);
        ctx.stroke();
    }

    function terminar(e) {
        _firmaDibujando = false;
    }

    canvas.addEventListener("mousedown", iniciar);
    canvas.addEventListener("mousemove", dibujar);
    canvas.addEventListener("mouseup", terminar);
    canvas.addEventListener("mouseleave", terminar);

    canvas.addEventListener("touchstart", iniciar, { passive: false });
    canvas.addEventListener("touchmove", dibujar, { passive: false });
    canvas.addEventListener("touchend", terminar);
    canvas.addEventListener("touchcancel", terminar);

    document.getElementById("btnLimpiarCanvas").addEventListener("click", () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    });
}

async function subirFirma() {
    const id = document.getElementById("firmaMedicoId").value;

    const tabActiva = document.querySelector("#firmaTabs .nav-link.active");
    const esDibujo = tabActiva && tabActiva.getAttribute("data-bs-target") === "#tabDibujarFirma";

    let archivo;

    if (esDibujo) {
        const canvas = document.getElementById("canvasFirma");
        const ctxCanvas = canvas.getContext("2d");
        const pixels = ctxCanvas.getImageData(0, 0, canvas.width, canvas.height).data;
        let tieneContenido = false;
        for (let i = 3; i < pixels.length; i += 4) {
            if (pixels[i] > 0) { tieneContenido = true; break; }
        }
        if (!tieneContenido) {
            alertaMedicos("alertaModalFirma", "Dibuje una firma primero.");
            return;
        }

        const blob = await new Promise(resolve => canvas.toBlob(resolve, "image/png"));
        archivo = new File([blob], "firma_dibujada.png", { type: "image/png" });
    } else {
        archivo = document.getElementById("archivoFirma").files[0];
        if (!archivo) {
            alertaMedicos("alertaModalFirma", "Seleccione una imagen primero.");
            return;
        }
    }

    const formData = new FormData();
    formData.append("archivo", archivo);

    try {
        const resp = await fetch(`/medicos/${id}/firma`, { method: "POST", body: formData });

        if (!resp.ok) {
            alertaMedicos("alertaModalFirma", await extraerMensajeError(resp, "No se pudo guardar la firma."));
            return;
        }

        alertaMedicos("alertaModalFirma", "Firma actualizada correctamente.", "success");
        await cargarMedicos();
    } catch (error) {
        alertaMedicos("alertaModalFirma", "Error de conexión al guardar la firma.");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    cargarMedicos();
    _initCanvasFirma();

    document.getElementById("btnNuevoMedico").addEventListener("click", () => {
        limpiarFormularioMedico();
        document.getElementById("tituloModalMedico").textContent = "Nuevo médico / enfermera";
        new bootstrap.Modal(document.getElementById("modalNuevoMedico")).show();
    });

    document.getElementById("btnGuardarMedico").addEventListener("click", guardarMedico);
    document.getElementById("btnSubirFirma").addEventListener("click", subirFirma);

    document.getElementById("btnImportarMedicos").addEventListener("click", () => {
        document.getElementById("alertaImportarMedicos").innerHTML = "";
        document.getElementById("resultadoImportarMedicos").innerHTML = "";
        document.getElementById("archivoImportarMedicos").value = "";
        new bootstrap.Modal(document.getElementById("modalImportarMedicos")).show();
    });

    document.getElementById("btnSubirImportarMedicos").addEventListener("click", importarExcelMedicos);
});
