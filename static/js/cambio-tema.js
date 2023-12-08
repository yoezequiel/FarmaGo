function cambiarTema() {
    var enlacesOscuros = document.querySelectorAll('[id$="-oscuro"]');
    var enlacesClaros = document.querySelectorAll('[id$="-claro"]');

    enlacesOscuros.forEach(function (enlace) {
        enlace.disabled = !enlace.disabled;
    });

    enlacesClaros.forEach(function (enlace) {
        enlace.disabled = !enlace.disabled;
    });

    var temaActual = enlacesOscuros[0].disabled ? "claro" : "oscuro";
    localStorage.setItem("tema", temaActual);

    actualizarIconosTema(temaActual);
}

function cargarTema() {
    var temaAlmacenado = localStorage.getItem("tema");

    if (temaAlmacenado === "claro") {
        cambiarTema();
    }
}

function actualizarIconosTema(tema) {
    var sunIcon = document.getElementById("sunIcon");
    var moonIcon = document.getElementById("moonIcon");

    sunIcon.style.display = tema === "oscuro" ? "inline" : "none";
    moonIcon.style.display = tema === "oscuro" ? "none" : "inline";
}

window.onload = function () {
    cargarTema();
    actualizarIconosTema(localStorage.getItem("tema") || "claro");
};
