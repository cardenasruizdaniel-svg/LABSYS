/******************************************************************************
 * LABSYS DIALIZAR
 * app/static/js/lector_cedula.js
 *
 * Captura la lectura de un lector de codigo de barras USB (HID Keyboard),
 * la envia al backend para decodificar y autocompleta el formulario.
 *
 * Compatible con lectores Honeywell, Zebra, Motorola, Datalogic, etc.
 ******************************************************************************/

var LectorCedula = (function () {

    var config = {
        timeout: 3000,
        minLength: 6,
        endpoint: "/api/lector/leer-cedula",
        checkEndpoint: "/api/lector/verificar-documento",
    };

    var buffer = "";
    var timer = null;
    var escuchando = false;
    var onReadyCallback = null;
    var onErrorCallback = null;

    function limpiarBuffer() {
        buffer = "";
        if (timer) {
            clearTimeout(timer);
            timer = null;
        }
    }

    function reiniciarBuffer() {
        if (timer) {
            clearTimeout(timer);
        }
        timer = setTimeout(function () {
            if (buffer.length >= config.minLength) {
                procesarLectura(buffer);
            } else {
                limpiarBuffer();
            }
        }, config.timeout);
    }

    function manejarTecla(e) {
        if (!escuchando) return;

        if (e.ctrlKey || e.altKey || e.metaKey) return;

        if (e.key === "Enter") {
            e.preventDefault();
            if (buffer.length >= config.minLength) {
                procesarLectura(buffer);
            } else {
                limpiarBuffer();
            }
            return;
        }

        if (e.key === "Escape") {
            limpiarBuffer();
            cancelarEscucha();
            return;
        }

        if (e.key.length === 1) {
            buffer += e.key;
            reiniciarBuffer();
        }
    }

    function iniciarEscucha() {
        if (escuchando) return;
        escuchando = true;
        limpiarBuffer();
        document.addEventListener("keydown", manejarTecla);
    }

    function cancelarEscucha() {
        escuchando = false;
        limpiarBuffer();
        document.removeEventListener("keydown", manejarTecla);
    }

    function procesarLectura(cadena) {
        cancelarEscucha();
        mostrarEstado("leyendo", "Procesando cedula...");

        fetch(config.endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ datos_crudos: cadena }),
        })
            .then(function (r) {
                if (!r.ok) throw new Error("Error en el servidor");
                return r.json();
            })
            .then(function (data) {
                if (data.success) {
                    mostrarEstado("exito", "Cedula leida correctamente.");
                    if (onReadyCallback) onReadyCallback(data);
                } else {
                    mostrarEstado("error", data.error || "No fue posible interpretar el codigo de barras.");
                    if (onErrorCallback) onErrorCallback(data);
                }
            })
            .catch(function (err) {
                mostrarEstado("error", "Error de conexion al procesar la cedula.");
                if (onErrorCallback) onErrorCallback(null);
            });
    }

    function mostrarEstado(tipo, mensaje) {
        var el = document.getElementById("lectorEstado");
        if (!el) return;
        el.style.display = "block";
        if (tipo === "leyendo") {
            el.className = "alert alert-info py-1 small mb-2";
            el.innerHTML = '<i class="bi bi-hourglass-split"></i> ' + mensaje;
        } else if (tipo === "exito") {
            el.className = "alert alert-success py-1 small mb-2";
            el.innerHTML = '<i class="bi bi-check-circle-fill"></i> ' + mensaje;
        } else if (tipo === "error") {
            el.className = "alert alert-warning py-1 small mb-2";
            el.innerHTML = '<i class="bi bi-exclamation-triangle-fill"></i> ' + mensaje;
        } else if (tipo === "reset") {
            el.className = "alert alert-secondary py-1 small mb-2";
            el.innerHTML = '<i class="bi bi-upc-scan"></i> ' + mensaje;
        }
    }

    function llenarFormularioPaciente(datos, prefix) {
        prefix = prefix || "";
        var campos = {
            tipo_documento: "tipo_documento",
            documento: "documento",
            primer_nombre: "primer_nombre",
            segundo_nombre: "segundo_nombre",
            primer_apellido: "primer_apellido",
            segundo_apellido: "segundo_apellido",
            sexo: "sexo",
            fecha_nacimiento: "fecha_nacimiento",
        };
        for (var key in campos) {
            if (!campos.hasOwnProperty(key)) continue;
            var valor = datos[key] || "";
            if (key === "sexo" && valor === "M") valor = "Masculino";
            if (key === "sexo" && valor === "F") valor = "Femenino";
            var el = document.getElementById(prefix + campos[key]);
            if (el) el.value = valor;
        }
    }

    function escanearCedula(onReady, onError) {
        onReadyCallback = onReady || null;
        onErrorCallback = onError || null;
        mostrarEstado("reset", "Esperando lectura del lector de codigo de barras...");
        iniciarEscucha();
    }

    function verificarDocumento(tipoDoc, documento, callback) {
        fetch(config.checkEndpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                tipo_documento: tipoDoc,
                documento: documento,
            }),
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (callback) callback(data);
            })
            .catch(function () {
                if (callback) callback({ existe: false });
            });
    }

    return {
        escanear: escanearCedula,
        cancelar: cancelarEscucha,
        llenarFormulario: llenarFormularioPaciente,
        verificarDocumento: verificarDocumento,
        mostrarEstado: mostrarEstado,
    };

})();
