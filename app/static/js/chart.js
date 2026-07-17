/**
 * ==========================================================
 * LABSYS DIALIZAR
 * Dashboard Ejecutivo
 * dashboard-chart.js
 * ==========================================================
 */

"use strict";

let chartOrdenes = null;
let chartFacturas = null;

/*==========================================================
=            Destruir gráfico existente                    =
==========================================================*/

function destroyChart(chart) {
    if (chart) {
        chart.destroy();
    }
}

/*==========================================================
=            Colores corporativos                          =
==========================================================*/

const COLORS = [
    "#2563eb",
    "#16a34a",
    "#f59e0b",
    "#dc2626",
    "#9333ea",
    "#06b6d4",
    "#64748b",
    "#84cc16",
    "#f97316",
    "#ec4899"
];

/*==========================================================
=            ÓRDENES POR ESTADO                            =
==========================================================*/

window.renderOrdenesChart = function (datos) {

    const canvas = document.getElementById("chartOrdenes");

    if (!canvas || typeof Chart === "undefined") {
        return;
    }

    destroyChart(chartOrdenes);

    chartOrdenes = new Chart(canvas, {

        type: "doughnut",

        data: {

            labels: datos.map(item => item[0]),

            datasets: [{

                label: "Órdenes",

                data: datos.map(item => item[1]),

                backgroundColor: COLORS,

                borderWidth: 2,

                hoverOffset: 10

            }]
        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {

                    position: "bottom"

                },

                title: {

                    display: true,

                    text: "Órdenes por Estado"

                }

            }

        }

    });

};

/*==========================================================
=            FACTURACIÓN POR ESTADO                        =
==========================================================*/

window.renderFacturasChart = function (datos) {

    const canvas = document.getElementById("chartFacturas");

    if (!canvas || typeof Chart === "undefined") {
        return;
    }

    destroyChart(chartFacturas);

    chartFacturas = new Chart(canvas, {

        type: "bar",

        data: {

            labels: datos.map(item => item[0]),

            datasets: [{

                label: "Cantidad",

                data: datos.map(item => item[1]),

                backgroundColor: COLORS,

                borderRadius: 8

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {

                    display: false

                },

                title: {

                    display: true,

                    text: "Facturación por Estado"

                }

            },

            scales: {

                y: {

                    beginAtZero: true,

                    ticks: {

                        precision: 0

                    }

                }

            }

        }

    });

};

/*==========================================================
=            Función futura para nuevos gráficos           =
==========================================================*/

window.createDashboardChart = function (
    canvasId,
    type,
    labels,
    values,
    title
) {

    const canvas = document.getElementById(canvasId);

    if (!canvas || typeof Chart === "undefined") {
        return;
    }

    return new Chart(canvas, {

        type,

        data: {

            labels,

            datasets: [{

                label: title,

                data: values,

                backgroundColor: COLORS,

                borderRadius: 8

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {

                    position: "bottom"

                },

                title: {

                    display: true,

                    text: title

                }

            }

        }

    });

};