/******************************************************************************
 * LABSYS DIALIZAR
 * app/static/js/configuracion.js
 ******************************************************************************/

function mostrarAlertaConfig(mensaje, tipo = "danger") {
    document.getElementById("alertaConfig").innerHTML =
        `<div class="alert alert-${tipo} py-2">${mensaje}</div>`;
}

function pintarLogo(logoPath) {
    const img = document.getElementById("previewLogo");
    const sinLogo = document.getElementById("sinLogo");

    if (logoPath) {
        img.src = `/static/${logoPath}?t=${Date.now()}`;
        img.style.display = "inline-block";
        sinLogo.style.display = "none";
    } else {
        img.style.display = "none";
        sinLogo.style.display = "block";
    }
}

async function cargarConfiguracion() {
    try {
        const resp = await fetch("/configuracion/");
        if (!resp.ok) throw new Error();
        const config = await resp.json();

        document.getElementById("nombreLaboratorio").value = config.nombre_laboratorio || "";
        document.getElementById("nit").value = config.nit || "";
        document.getElementById("resolucionHabilitacion").value = config.resolucion_habilitacion || "";
        document.getElementById("ciudad").value = config.ciudad || "";
        document.getElementById("direccion").value = config.direccion || "";
        document.getElementById("telefono").value = config.telefono || "";
        document.getElementById("correo").value = config.correo || "";
        document.getElementById("piePagina").value = config.pie_pagina || "";

        if (document.getElementById("smtpHost")) {
            document.getElementById("smtpHost").value = config.smtp_host || "";
            document.getElementById("smtpPort").value = config.smtp_port || "";
            document.getElementById("smtpUser").value = config.smtp_user || "";
            document.getElementById("smtpFrom").value = config.smtp_from || "";
        }

        pintarLogo(config.logo_path);
    } catch (error) {
        mostrarAlertaConfig("No se pudo cargar la configuración actual.");
    }
}

async function guardarConfiguracion() {
    const payload = {
        nombre_laboratorio: document.getElementById("nombreLaboratorio").value || null,
        nit: document.getElementById("nit").value || null,
        resolucion_habilitacion: document.getElementById("resolucionHabilitacion").value || null,
        ciudad: document.getElementById("ciudad").value || null,
        direccion: document.getElementById("direccion").value || null,
        telefono: document.getElementById("telefono").value || null,
        correo: document.getElementById("correo").value || null,
        pie_pagina: document.getElementById("piePagina").value || null,
    };

    try {
        const resp = await fetch("/configuracion/", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!resp.ok) {
                        mostrarAlertaConfig(await extraerMensajeError(resp, "No se pudo guardar la configuración."));
            return;
        }

        mostrarAlertaConfig("Datos guardados correctamente.", "success");
    } catch (error) {
        mostrarAlertaConfig("Error de conexión al guardar los datos.");
    }
}

async function subirLogo() {
    const input = document.getElementById("inputLogo");
    const archivo = input.files[0];

    if (!archivo) {
        mostrarAlertaConfig("Selecciona primero un archivo de imagen.");
        return;
    }

    const formData = new FormData();
    formData.append("archivo", archivo);

    try {
        const resp = await fetch("/configuracion/logo", {
            method: "POST",
            body: formData,
        });

        if (!resp.ok) {
                        mostrarAlertaConfig(await extraerMensajeError(resp, "No se pudo subir el logo."));
            return;
        }

        const config = await resp.json();
        pintarLogo(config.logo_path);
        mostrarAlertaConfig("Logo actualizado correctamente.", "success");
        input.value = "";
    } catch (error) {
        mostrarAlertaConfig("Error de conexión al subir el logo.");
    }
}

async function guardarSMTP() {
    const smtpHost = document.getElementById("smtpHost").value.trim();
    const smtpPort = document.getElementById("smtpPort").value.trim();
    const smtpUser = document.getElementById("smtpUser").value.trim();
    const smtpPassword = document.getElementById("smtpPassword").value.trim();
    const smtpFrom = document.getElementById("smtpFrom").value.trim();

    if (!smtpHost || !smtpUser) {
        document.getElementById("alertaSMTP").innerHTML =
            '<div class="alert alert-warning py-1 small">Ingrese servidor SMTP y usuario.</div>';
        return;
    }

    const payload = {
        smtp_host: smtpHost,
        smtp_port: smtpPort ? parseInt(smtpPort) : 587,
        smtp_user: smtpUser,
        smtp_from: smtpFrom || null,
    };

    if (smtpPassword) {
        payload.smtp_password = smtpPassword;
    }

    try {
        const resp = await fetch("/configuracion/", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!resp.ok) {
            document.getElementById("alertaSMTP").innerHTML =
                `<div class="alert alert-danger py-1 small">${await extraerMensajeError(resp, "Error al guardar.")}</div>`;
            return;
        }

        document.getElementById("smtpPassword").value = "";
        document.getElementById("alertaSMTP").innerHTML =
            '<div class="alert alert-success py-1 small">Configuracion SMTP guardada.</div>';

        setTimeout(() => {
            const el = document.getElementById("alertaSMTP");
            if (el) el.innerHTML = "";
        }, 3000);
    } catch (error) {
        document.getElementById("alertaSMTP").innerHTML =
            '<div class="alert alert-danger py-1 small">Error de conexion.</div>';
    }
}

document.addEventListener("DOMContentLoaded", () => {
    cargarConfiguracion();
    document.getElementById("btnGuardarConfig").addEventListener("click", guardarConfiguracion);
    document.getElementById("btnSubirLogo").addEventListener("click", subirLogo);

    const btnSMTP = document.getElementById("btnGuardarSMTP");
    if (btnSMTP) btnSMTP.addEventListener("click", guardarSMTP);
});
