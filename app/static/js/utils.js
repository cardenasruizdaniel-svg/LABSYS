/******************************************************************************
 * LABSYS DIALIZAR
 * app/static/js/utils.js
 *
 * Utilidades compartidas por todas las pantallas.
 ******************************************************************************/

/**
 * Extrae un mensaje de error legible de una respuesta fetch() que no fue OK.
 * Si el servidor mandó {"detail": "..."} (o una lista de errores de validación
 * de FastAPI), se muestra ese mensaje real. Si la respuesta no es JSON válido
 * (ej. un error 500 sin formato), se muestra el código HTTP y el cuerpo crudo
 * para poder diagnosticarlo, en vez de un mensaje genérico que oculta el motivo.
 */
async function extraerMensajeError(resp, mensajePorDefecto) {
    let texto = "";
    try {
        texto = await resp.text();
    } catch (_) {
        return `${mensajePorDefecto} (HTTP ${resp.status})`;
    }

    try {
        const err = JSON.parse(texto);
        if (err && err.detail) {
            if (Array.isArray(err.detail)) {
                return err.detail.map(d => d.msg || JSON.stringify(d)).join(" · ");
            }
            return err.detail;
        }
    } catch (_) {
        // El cuerpo no era JSON (ej. error 500 con traceback en texto plano).
    }

    return texto
        ? `${mensajePorDefecto} (HTTP ${resp.status}: ${texto.slice(0, 300)})`
        : `${mensajePorDefecto} (HTTP ${resp.status})`;
}
