/******************************************************************************
 * LABSYS DIALIZAR
 * app/static/js/pacientes.js
 ******************************************************************************/

let pacientesTodosCache = [];
let departamentosCache = [];
let epsCachePaciente = [];

function alertaPac(id, mensaje, tipo = "danger") {
    document.getElementById(id).innerHTML = `<div class="alert alert-${tipo} py-2">${mensaje}</div>`;
}

function calcularEdad(fechaNacimiento) {
    const hoy = new Date();
    const nac = new Date(fechaNacimiento);
    let edad = hoy.getFullYear() - nac.getFullYear();
    const m = hoy.getMonth() - nac.getMonth();
    if (m < 0 || (m === 0 && hoy.getDate() < nac.getDate())) edad--;
    return edad;
}

function nombreEpsPaciente(id) {
    const e = epsCachePaciente.find(x => x.id === id);
    return e ? e.nombre : null;
}

async function cargarCatalogosPaciente() {
    const [depR, epsR] = await Promise.all([
        fetch("/geografia/departamentos"),
        fetch("/eps/"),
    ]);
    departamentosCache = depR.ok ? await depR.json() : [];
    epsCachePaciente = epsR.ok ? await epsR.json() : [];

    document.getElementById("pacienteDepartamento").innerHTML = '<option value="">Seleccione...</option>' +
        departamentosCache.map(d => `<option value="${d.id}">${d.nombre}</option>`).join("");

    document.getElementById("pacienteEps").innerHTML = '<option value="">Seleccione...</option>' +
        epsCachePaciente.map(e => `<option value="${e.id}">${e.nombre}</option>`).join("");
}

async function cargarCiudadesDe(departamentoId, seleccionar) {
    const select = document.getElementById("pacienteMunicipio");
    if (!departamentoId) {
        select.innerHTML = '<option value="">Seleccione un departamento primero</option>';
        return;
    }
    const resp = await fetch(`/geografia/ciudades?departamento_id=${departamentoId}`);
    const ciudades = resp.ok ? await resp.json() : [];
    select.innerHTML = '<option value="">Seleccione...</option>' +
        ciudades.map(c => `<option value="${c.nombre}" ${c.nombre === seleccionar ? "selected" : ""}>${c.nombre}</option>`).join("");
}

async function cargarPacientes() {
    try {
        const resp = await fetch("/pacientes/");
        pacientesTodosCache = resp.ok ? await resp.json() : [];
        renderTablaPacientes(pacientesTodosCache);
    } catch (error) {
        alertaPac("alertaPacientes", "No se pudo cargar el listado de pacientes.");
    }
}

function renderTablaPacientes(lista) {
    const tbody = document.getElementById("tablaPacientes");
    if (!lista.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-muted small">No hay pacientes registrados todavía.</td></tr>';
        return;
    }

    tbody.innerHTML = lista.map(p => {
        let afiliacion;
        if (p.es_particular) {
            afiliacion = '<span class="badge bg-secondary">Particular</span>';
        } else {
            const nombreEps = nombreEpsPaciente(p.eps_id) || "EPS";
            afiliacion = `<span class="badge bg-primary">${nombreEps}</span> ` +
                (p.tiene_copago ? '<span class="badge bg-warning text-dark">Con copago</span>' : '<span class="badge bg-success">Sin copago</span>');
        }

        return `
        <tr>
            <td>${p.tipo_documento} ${p.documento}</td>
            <td>${p.primer_nombre} ${p.segundo_nombre || ''} ${p.primer_apellido} ${p.segundo_apellido || ''}</td>
            <td>${calcularEdad(p.fecha_nacimiento)} años</td>
            <td>${p.sexo}</td>
            <td>${afiliacion}</td>
            <td>${p.celular || p.telefono || '-'}</td>
            <td>
                <button class="btn btn-sm btn-outline-secondary" onclick="editarPaciente(${p.id})">
                    <i class="bi bi-pencil"></i> Editar
                </button>
            </td>
        </tr>`;
    }).join("");
}

function limpiarFormularioPaciente() {
    document.getElementById("alertaModalPaciente").innerHTML = "";
    document.getElementById("pacienteId").value = "";
    document.getElementById("pacienteTipoDocumento").value = "CC";
    document.getElementById("pacienteDocumento").value = "";
    document.getElementById("pacienteSexo").value = "Femenino";
    document.getElementById("pacientePrimerNombre").value = "";
    document.getElementById("pacienteSegundoNombre").value = "";
    document.getElementById("pacientePrimerApellido").value = "";
    document.getElementById("pacienteSegundoApellido").value = "";
    document.getElementById("pacienteFechaNacimiento").value = "";
    document.getElementById("pacienteTelefono").value = "";
    document.getElementById("pacienteCelular").value = "";
    document.getElementById("pacienteCorreo").value = "";
    document.getElementById("pacienteDireccion").value = "";
    document.getElementById("pacienteDepartamento").value = "";
    document.getElementById("pacienteMunicipio").innerHTML = '<option value="">Seleccione un departamento primero</option>';
    document.getElementById("afiliacionEps").checked = true;
    document.getElementById("pacienteEps").value = "";
    document.getElementById("pacienteTieneCopago").checked = true;
    document.getElementById("grupoPacienteEps").style.display = "block";
}

async function editarPaciente(id) {
    const p = pacientesTodosCache.find(x => x.id === id);
    if (!p) return;

    limpiarFormularioPaciente();
    document.getElementById("tituloModalPaciente").textContent = "Editar paciente";
    document.getElementById("pacienteId").value = p.id;
    document.getElementById("pacienteTipoDocumento").value = p.tipo_documento;
    document.getElementById("pacienteDocumento").value = p.documento;
    document.getElementById("pacienteSexo").value = p.sexo;
    document.getElementById("pacientePrimerNombre").value = p.primer_nombre;
    document.getElementById("pacienteSegundoNombre").value = p.segundo_nombre || "";
    document.getElementById("pacientePrimerApellido").value = p.primer_apellido;
    document.getElementById("pacienteSegundoApellido").value = p.segundo_apellido || "";
    document.getElementById("pacienteFechaNacimiento").value = p.fecha_nacimiento;
    document.getElementById("pacienteTelefono").value = p.telefono || "";
    document.getElementById("pacienteCelular").value = p.celular || "";
    document.getElementById("pacienteCorreo").value = p.correo || "";
    document.getElementById("pacienteDireccion").value = p.direccion || "";

    const dep = departamentosCache.find(d => d.nombre === p.departamento);
    if (dep) {
        document.getElementById("pacienteDepartamento").value = dep.id;
        await cargarCiudadesDe(dep.id, p.municipio);
    }

    if (p.es_particular) {
        document.getElementById("afiliacionParticular").checked = true;
        document.getElementById("grupoPacienteEps").style.display = "none";
    } else {
        document.getElementById("afiliacionEps").checked = true;
        document.getElementById("grupoPacienteEps").style.display = "block";
        document.getElementById("pacienteEps").value = p.eps_id || "";
    }
    document.getElementById("pacienteTieneCopago").checked = p.tiene_copago;

    new bootstrap.Modal(document.getElementById("modalPaciente")).show();
}

async function guardarPaciente() {
    const id = document.getElementById("pacienteId").value;
    const esParticular = document.getElementById("afiliacionParticular").checked;
    const depSelect = document.getElementById("pacienteDepartamento");
    const nombreDepartamento = depSelect.selectedOptions[0]?.textContent || null;

    const payload = {
        tipo_documento: document.getElementById("pacienteTipoDocumento").value,
        documento: document.getElementById("pacienteDocumento").value,
        primer_nombre: document.getElementById("pacientePrimerNombre").value,
        segundo_nombre: document.getElementById("pacienteSegundoNombre").value || null,
        primer_apellido: document.getElementById("pacientePrimerApellido").value,
        segundo_apellido: document.getElementById("pacienteSegundoApellido").value || null,
        fecha_nacimiento: document.getElementById("pacienteFechaNacimiento").value,
        sexo: document.getElementById("pacienteSexo").value,
        telefono: document.getElementById("pacienteTelefono").value || null,
        celular: document.getElementById("pacienteCelular").value || null,
        correo: document.getElementById("pacienteCorreo").value || null,
        direccion: document.getElementById("pacienteDireccion").value || null,
        departamento: depSelect.value ? nombreDepartamento : null,
        municipio: document.getElementById("pacienteMunicipio").value || null,
        es_particular: esParticular,
        eps_id: esParticular ? null : (parseInt(document.getElementById("pacienteEps").value, 10) || null),
        tiene_copago: esParticular ? true : document.getElementById("pacienteTieneCopago").checked,
    };

    if (!payload.documento || !payload.primer_nombre || !payload.primer_apellido || !payload.fecha_nacimiento) {
        alertaPac("alertaModalPaciente", "Documento, primer nombre, primer apellido y fecha de nacimiento son obligatorios.");
        return;
    }

    if (!esParticular && !payload.eps_id) {
        alertaPac("alertaModalPaciente", "Seleccione la EPS del paciente, o marque \"Particular\".");
        return;
    }

    const esEdicion = !!id;
    const url = esEdicion ? `/pacientes/${id}` : "/pacientes/";
    const metodo = esEdicion ? "PUT" : "POST";
    if (esEdicion) payload.activo = true;

    try {
        const resp = await fetch(url, {
            method: metodo,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!resp.ok) {
            alertaPac("alertaModalPaciente", await extraerMensajeError(resp, "No se pudo guardar el paciente."));
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById("modalPaciente")).hide();
        await cargarPacientes();
    } catch (error) {
        alertaPac("alertaModalPaciente", "Error de conexión al guardar.");
    }
}

async function importarExcelPacientes() {
    const input = document.getElementById("archivoImportarPacientes");
    const archivo = input.files[0];

    document.getElementById("alertaImportarPacientes").innerHTML = "";
    document.getElementById("resultadoImportarPacientes").innerHTML = "";

    if (!archivo) {
        alertaPac("alertaImportarPacientes", "Seleccione un archivo .xlsx primero.");
        return;
    }

    const formData = new FormData();
    formData.append("archivo", archivo);

    try {
        const resp = await fetch("/pacientes/importar/excel", { method: "POST", body: formData });

        if (!resp.ok) {
            alertaPac("alertaImportarPacientes", await extraerMensajeError(resp, "No se pudo importar el archivo."));
            return;
        }

        const resultado = await resp.json();
        let html = `<div class="alert alert-success py-2">Se crearon ${resultado.creados} de ${resultado.total_filas} paciente(s).</div>`;
        if (resultado.errores.length) {
            html += `<div class="alert alert-warning py-2"><strong>Filas con error:</strong><br>${resultado.errores.join("<br>")}</div>`;
        }
        document.getElementById("resultadoImportarPacientes").innerHTML = html;

        await cargarPacientes();
    } catch (error) {
        alertaPac("alertaImportarPacientes", "Error de conexión al importar.");
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    await cargarCatalogosPaciente();
    await cargarPacientes();

    document.getElementById("btnNuevoPaciente").addEventListener("click", () => {
        limpiarFormularioPaciente();
        document.getElementById("tituloModalPaciente").textContent = "Nuevo paciente";
        new bootstrap.Modal(document.getElementById("modalPaciente")).show();
    });

    document.getElementById("btnGuardarPaciente").addEventListener("click", guardarPaciente);

    document.getElementById("pacienteDepartamento").addEventListener("change", (e) => {
        cargarCiudadesDe(e.target.value, null);
    });

    document.querySelectorAll('input[name="pacienteAfiliacion"]').forEach(radio => {
        radio.addEventListener("change", (e) => {
            const esParticular = e.target.value === "PARTICULAR";
            document.getElementById("grupoPacienteEps").style.display = esParticular ? "none" : "block";
            if (esParticular) document.getElementById("pacienteTieneCopago").checked = true;
        });
    });

    document.getElementById("btnImportarPacientes").addEventListener("click", () => {
        document.getElementById("alertaImportarPacientes").innerHTML = "";
        document.getElementById("resultadoImportarPacientes").innerHTML = "";
        document.getElementById("archivoImportarPacientes").value = "";
        new bootstrap.Modal(document.getElementById("modalImportarPacientes")).show();
    });

    document.getElementById("btnSubirImportarPacientes").addEventListener("click", importarExcelPacientes);

    document.getElementById("buscarPaciente").addEventListener("input", (e) => {
        const texto = e.target.value.toLowerCase();
        const filtrados = pacientesTodosCache.filter(p =>
            `${p.primer_nombre} ${p.primer_apellido} ${p.documento}`.toLowerCase().includes(texto)
        );
        renderTablaPacientes(filtrados);
    });
});
