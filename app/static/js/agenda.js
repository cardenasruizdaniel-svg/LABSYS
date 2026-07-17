/******************************************************************************
 * LABSYS DIALIZAR
 * app/static/js/agenda.js
 *
 * Calendario visual de citas. Consume la API REST /agenda, /pacientes,
 * /medicos y /ordenes. No depende de datos renderizados por el servidor:
 * todo se carga por fetch para que la vista siempre refleje el estado
 * real de la base de datos.
 ******************************************************************************/

class AgendaCalendario {

    constructor() {
        const hoy = new Date();
        this.anio = hoy.getFullYear();
        this.mes = hoy.getMonth(); // 0-11
        this.fechaSeleccionada = this.formatearFecha(hoy);

        this.pacientes = [];
        this.medicos = [];
        this.ordenes = [];

        this.nombresMes = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ];
    }

    async init() {
        this.bindEventos();
        await this.cargarCatalogos();
        await this.renderMes();
        await this.seleccionarDia(this.fechaSeleccionada);
    }

    bindEventos() {
        document.getElementById("btnMesAnterior").addEventListener("click", () => {
            this.mes--;
            if (this.mes < 0) { this.mes = 11; this.anio--; }
            this.renderMes();
        });

        document.getElementById("btnMesSiguiente").addEventListener("click", () => {
            this.mes++;
            if (this.mes > 11) { this.mes = 0; this.anio++; }
            this.renderMes();
        });

        document.getElementById("btnNuevaCita").addEventListener("click", () => {
            this.abrirModalNuevaCita(this.fechaSeleccionada);
        });

        document.getElementById("btnConfigurarCupo").addEventListener("click", () => {
            document.getElementById("cupoFecha").value = this.fechaSeleccionada;
            document.getElementById("alertaModalCupo").innerHTML = "";
            new bootstrap.Modal(document.getElementById("modalCupo")).show();
        });

        document.getElementById("btnGuardarCupo").addEventListener("click", () => this.guardarCupo());
        document.getElementById("btnGuardarCita").addEventListener("click", () => this.guardarCita());
        document.getElementById("btnGuardarAsociarOrden").addEventListener("click", () => this.guardarAsociarOrden());

        document.querySelectorAll('input[name="tipoAtencion"]').forEach(radio => {
            radio.addEventListener("change", (e) => {
                document.getElementById("grupoOrden").style.display =
                    e.target.value === "CON_ORDEN" ? "block" : "none";
            });
        });
    }

    formatearFecha(date) {
        const y = date.getFullYear();
        const m = String(date.getMonth() + 1).padStart(2, "0");
        const d = String(date.getDate()).padStart(2, "0");
        return `${y}-${m}-${d}`;
    }

    mostrarAlerta(contenedorId, mensaje, tipo = "danger") {
        const el = document.getElementById(contenedorId);
        el.innerHTML = `<div class="alert alert-${tipo} py-2">${mensaje}</div>`;
    }

    async cargarCatalogos() {
        try {
            const [pacientesResp, medicosResp, ordenesResp] = await Promise.all([
                fetch("/pacientes/"),
                fetch("/medicos/"),
                fetch("/ordenes/"),
            ]);

            this.pacientes = pacientesResp.ok ? await pacientesResp.json() : [];
            this.medicos = medicosResp.ok ? await medicosResp.json() : [];
            this.ordenes = ordenesResp.ok ? await ordenesResp.json() : [];

            const selectPaciente = document.getElementById("citaPaciente");
            selectPaciente.innerHTML = '<option value="">Seleccione...</option>' +
                this.pacientes.map(p =>
                    `<option value="${p.id}">${p.primer_nombre} ${p.primer_apellido} (${p.documento})</option>`
                ).join("");

            const opcionesMedico = '<option value="">Sin especificar</option>' +
                this.medicos.map(m => `<option value="${m.id}">${m.nombres} ${m.apellidos}</option>`).join("");
            document.getElementById("citaMedico").innerHTML = opcionesMedico;

            const opcionesOrden = '<option value="">Seleccione...</option>' +
                this.ordenes.map(o => `<option value="${o.id}">${o.numero_orden}</option>`).join("");
            document.getElementById("citaOrden").innerHTML = opcionesOrden;
            document.getElementById("asociarOrdenSelect").innerHTML = opcionesOrden;

        } catch (error) {
            this.mostrarAlerta("alertaAgenda", "No se pudieron cargar pacientes/médicos/órdenes.");
        }
    }

    nombrePaciente(id) {
        const p = this.pacientes.find(x => x.id === id);
        return p ? `${p.primer_nombre} ${p.primer_apellido}` : `Paciente #${id}`;
    }

    nombreMedico(id) {
        const m = this.medicos.find(x => x.id === id);
        return m ? `${m.nombres} ${m.apellidos}` : `Médico #${id}`;
    }

    async renderMes() {
        document.getElementById("tituloMes").textContent =
            `${this.nombresMes[this.mes]} ${this.anio}`;

        const primerDia = new Date(this.anio, this.mes, 1);
        // Lunes = 0 ... Domingo = 6
        const offset = (primerDia.getDay() + 6) % 7;
        const diasEnMes = new Date(this.anio, this.mes + 1, 0).getDate();

        const celdas = [];
        for (let i = 0; i < offset; i++) celdas.push(null);
        for (let d = 1; d <= diasEnMes; d++) celdas.push(new Date(this.anio, this.mes, d));

        const contenedor = document.getElementById("calendarioBody");
        contenedor.innerHTML = celdas.map(fecha => {
            if (!fecha) return '<div class="dia-celda fuera-de-mes"></div>';
            const fechaStr = this.formatearFecha(fecha);
            return `<div class="dia-celda" data-fecha="${fechaStr}" id="celda-${fechaStr}">
                        <div class="dia-numero">${fecha.getDate()}</div>
                        <div class="dia-cupo" id="cupo-${fechaStr}"></div>
                    </div>`;
        }).join("");

        contenedor.querySelectorAll(".dia-celda[data-fecha]").forEach(celda => {
            celda.addEventListener("click", () => this.seleccionarDia(celda.dataset.fecha));
        });

        const fechasDelMes = celdas.filter(Boolean).map(f => this.formatearFecha(f));
        await Promise.all(fechasDelMes.map(f => this.pintarCupoDia(f)));

        this.marcarSeleccion();
    }

    async pintarCupoDia(fechaStr) {
        try {
            const resp = await fetch(`/agenda/disponibilidad/${fechaStr}`);
            if (!resp.ok) return;
            const disp = await resp.json();

            const badge = document.getElementById(`cupo-${fechaStr}`);
            if (!badge) return;

            let clase = "verde";
            if (disp.cupo_disponible === 0) clase = "rojo";
            else if (disp.cupo_disponible <= Math.max(1, Math.round(disp.cupo_maximo * 0.2))) clase = "amarillo";

            badge.textContent = `${disp.cupo_usado}/${disp.cupo_maximo}`;
            badge.classList.add(clase);
        } catch (error) {
            // silencioso: si falla un día no bloquea el resto del calendario
        }
    }

    marcarSeleccion() {
        document.querySelectorAll(".dia-celda").forEach(c => c.classList.remove("seleccionado"));
        const actual = document.getElementById(`celda-${this.fechaSeleccionada}`);
        if (actual) actual.classList.add("seleccionado");
    }

    async seleccionarDia(fechaStr) {
        this.fechaSeleccionada = fechaStr;
        this.marcarSeleccion();

        document.getElementById("tituloDiaSeleccionado").textContent =
            new Date(fechaStr + "T00:00:00").toLocaleDateString("es-CO", {
                weekday: "long", year: "numeric", month: "long", day: "numeric"
            });

        try {
            const [dispResp, citasResp] = await Promise.all([
                fetch(`/agenda/disponibilidad/${fechaStr}`),
                fetch(`/agenda/citas?fecha=${fechaStr}`),
            ]);

            const disp = dispResp.ok ? await dispResp.json() : null;
            const citas = citasResp.ok ? await citasResp.json() : [];

            document.getElementById("cupoDiaSeleccionado").textContent = disp
                ? `Cupo: ${disp.cupo_usado} usados de ${disp.cupo_maximo} (${disp.cupo_disponible} disponibles)`
                : "";

            this.renderListaCitas(citas);
        } catch (error) {
            this.mostrarAlerta("alertaAgenda", "No se pudo cargar la información del día.");
        }
    }

    renderListaCitas(citas) {
        const lista = document.getElementById("listaCitasDia");

        if (!citas.length) {
            lista.innerHTML = '<li class="list-group-item text-muted small">Sin citas para este día.</li>';
            return;
        }

        citas = [...citas].sort((a, b) => (a.hora_cita || "99:99").localeCompare(b.hora_cita || "99:99"));

        const coloresEstado = {
            PROGRAMADA: "secondary",
            CONFIRMADA: "primary",
            ATENDIDA: "success",
            CANCELADA: "danger",
            NO_ASISTIO: "warning",
        };

        lista.innerHTML = citas.map(c => `
            <li class="list-group-item">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        ${c.hora_cita ? `<span class="badge bg-dark me-1">${c.hora_cita.slice(0,5)}</span>` : ""}
                        <strong>${this.nombrePaciente(c.paciente_id)}</strong>
                        <span class="badge bg-${coloresEstado[c.estado] || "secondary"} ms-1">${c.estado}</span>
                        <div class="small text-muted">
                            ${c.es_particular ? "Particular (sin orden)" : "Con orden médica"}
                            ${c.medico_id ? " · " + this.nombreMedico(c.medico_id) : ""}
                        </div>
                        ${c.observaciones ? `<div class="small">${c.observaciones}</div>` : ""}
                    </div>
                </div>
                <div class="btn-group btn-group-sm mt-2">
                    <select class="form-select form-select-sm" style="width:auto" onchange="agenda.cambiarEstado(${c.id}, this.value)">
                        <option value="">Cambiar estado...</option>
                        <option value="PROGRAMADA">Programada</option>
                        <option value="CONFIRMADA">Confirmada</option>
                        <option value="ATENDIDA">Atendida</option>
                        <option value="NO_ASISTIO">No asistió</option>
                    </select>
                    ${c.es_particular ? `<button class="btn btn-outline-success" onclick="agenda.generarOrdenParticular(${c.id}, ${c.paciente_id})">Generar orden particular</button>` : ""}
                    ${c.es_particular ? `<button class="btn btn-outline-primary" onclick="agenda.abrirModalAsociarOrden(${c.id})">Asociar orden existente</button>` : ""}
                    <button class="btn btn-outline-danger" onclick="agenda.cancelarCita(${c.id})">Cancelar</button>
                </div>
            </li>
        `).join("");
    }

    abrirModalNuevaCita(fechaStr) {
        document.getElementById("alertaModalCita").innerHTML = "";
        document.getElementById("citaFecha").value = fechaStr;
        document.getElementById("citaHora").value = "";
        document.getElementById("citaPaciente").value = "";
        document.getElementById("citaOrden").value = "";
        document.getElementById("citaMedico").value = "";
        document.getElementById("citaObservaciones").value = "";
        document.getElementById("tipoConOrden").checked = true;
        document.getElementById("grupoOrden").style.display = "block";
        new bootstrap.Modal(document.getElementById("modalNuevaCita")).show();
    }

    async guardarCita() {
        const paciente_id = document.getElementById("citaPaciente").value;
        const fecha_cita = document.getElementById("citaFecha").value;
        const esConOrden = document.getElementById("tipoConOrden").checked;
        const orden_id = esConOrden ? document.getElementById("citaOrden").value : "";
        const medico_id = document.getElementById("citaMedico").value;
        const observaciones = document.getElementById("citaObservaciones").value;

        if (!paciente_id || !fecha_cita) {
            this.mostrarAlerta("alertaModalCita", "Paciente y fecha son obligatorios.");
            return;
        }

        const payload = {
            paciente_id: parseInt(paciente_id, 10),
            fecha_cita,
            hora_cita: document.getElementById("citaHora").value || null,
            orden_id: orden_id ? parseInt(orden_id, 10) : null,
            medico_id: medico_id ? parseInt(medico_id, 10) : null,
            observaciones: observaciones || null,
        };

        try {
            const resp = await fetch("/agenda/citas", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            if (!resp.ok) {
                                this.mostrarAlerta("alertaModalCita", await extraerMensajeError(resp, "No se pudo programar la cita."));
                return;
            }

            bootstrap.Modal.getInstance(document.getElementById("modalNuevaCita")).hide();
            await this.renderMes();
            await this.seleccionarDia(fecha_cita);
        } catch (error) {
            this.mostrarAlerta("alertaModalCita", "Error de conexión al programar la cita.");
        }
    }

    async cambiarEstado(citaId, estado) {
        if (!estado) return;
        try {
            const resp = await fetch(`/agenda/citas/${citaId}/estado`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ estado }),
            });
            if (!resp.ok) {
                                alert(await extraerMensajeError(resp, "No se pudo cambiar el estado."));
                return;
            }
            await this.seleccionarDia(this.fechaSeleccionada);
        } catch (error) {
            alert("Error de conexión al cambiar el estado.");
        }
    }

    async cancelarCita(citaId) {
        if (!confirm("¿Cancelar esta cita?")) return;
        try {
            const resp = await fetch(`/agenda/citas/${citaId}`, { method: "DELETE" });
            if (!resp.ok) {
                alert("No se pudo cancelar la cita.");
                return;
            }
            await this.renderMes();
            await this.seleccionarDia(this.fechaSeleccionada);
        } catch (error) {
            alert("Error de conexión al cancelar la cita.");
        }
    }

    async generarOrdenParticular(citaId, pacienteId) {
        if (!confirm("¿Generar automáticamente una orden particular para esta cita? El paciente pagará el 100% del valor.")) return;

        try {
            const respDatos = await fetch("/configuracion/particular");
            if (!respDatos.ok) {
                                alert(await extraerMensajeError(respDatos, "No se pudieron obtener los datos de 'Particular'. Ejecute create_tables nuevamente."));
                return;
            }
            const { eps_id, convenio_id, medico_id } = await respDatos.json();

            const numeroOrden = `PART-${Date.now()}`;

            const respOrden = await fetch("/ordenes/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    numero_orden: numeroOrden,
                    paciente_id: pacienteId,
                    medico_id,
                    eps_id,
                    convenio_id,
                    observaciones: "Orden particular generada automáticamente desde Agenda.",
                }),
            });

            if (!respOrden.ok) {
                                alert(await extraerMensajeError(respOrden, "No se pudo crear la orden particular."));
                return;
            }

            const orden = await respOrden.json();

            const respAsociar = await fetch(`/agenda/citas/${citaId}/orden`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ orden_id: orden.id }),
            });

            if (!respAsociar.ok) {
                alert("La orden se creó, pero no se pudo asociar a la cita automáticamente.");
                return;
            }

            await this.seleccionarDia(this.fechaSeleccionada);
        } catch (error) {
            alert("Error de conexión al generar la orden particular.");
        }
    }

    abrirModalAsociarOrden(citaId) {
        document.getElementById("alertaModalAsociar").innerHTML = "";
        document.getElementById("asociarCitaId").value = citaId;
        document.getElementById("asociarOrdenSelect").value = "";
        new bootstrap.Modal(document.getElementById("modalAsociarOrden")).show();
    }

    async guardarAsociarOrden() {
        const citaId = document.getElementById("asociarCitaId").value;
        const orden_id = document.getElementById("asociarOrdenSelect").value;

        if (!orden_id) {
            this.mostrarAlerta("alertaModalAsociar", "Selecciona una orden.");
            return;
        }

        try {
            const resp = await fetch(`/agenda/citas/${citaId}/orden`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ orden_id: parseInt(orden_id, 10) }),
            });

            if (!resp.ok) {
                                this.mostrarAlerta("alertaModalAsociar", await extraerMensajeError(resp, "No se pudo asociar la orden."));
                return;
            }

            bootstrap.Modal.getInstance(document.getElementById("modalAsociarOrden")).hide();
            await this.seleccionarDia(this.fechaSeleccionada);
        } catch (error) {
            this.mostrarAlerta("alertaModalAsociar", "Error de conexión al asociar la orden.");
        }
    }

    async guardarCupo() {
        const fecha = document.getElementById("cupoFecha").value;
        const cupo_maximo = document.getElementById("cupoMaximo").value;

        if (!fecha || !cupo_maximo) {
            this.mostrarAlerta("alertaModalCupo", "Fecha y cupo máximo son obligatorios.");
            return;
        }

        try {
            const resp = await fetch("/agenda/cupos", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ fecha, cupo_maximo: parseInt(cupo_maximo, 10) }),
            });

            if (!resp.ok) {
                                this.mostrarAlerta("alertaModalCupo", await extraerMensajeError(resp, "No se pudo guardar el cupo."));
                return;
            }

            bootstrap.Modal.getInstance(document.getElementById("modalCupo")).hide();
            await this.renderMes();
            await this.seleccionarDia(this.fechaSeleccionada);
        } catch (error) {
            this.mostrarAlerta("alertaModalCupo", "Error de conexión al guardar el cupo.");
        }
    }
}

const agenda = new AgendaCalendario();
document.addEventListener("DOMContentLoaded", () => agenda.init());
