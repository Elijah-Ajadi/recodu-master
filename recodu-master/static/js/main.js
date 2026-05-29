document.addEventListener("DOMContentLoaded", function () {
    initSessionTimeout();
    initModals();
});

function initSessionTimeout() {
    const TIMEOUT_MS = 15 * 60 * 1000;
    const WARNING_MS = 2 * 60 * 1000;
    let timeoutId;
    let warningId;

    function resetTimer() {
        clearTimeout(timeoutId);
        clearTimeout(warningId);
        warningId = setTimeout(showWarning, TIMEOUT_MS - WARNING_MS);
        timeoutId = setTimeout(logout, TIMEOUT_MS);
    }

    function showWarning() {
        const warning = document.createElement("div");
        warning.className = "alert alert-warning";
        warning.style.position = "fixed";
        warning.style.bottom = "1rem";
        warning.style.right = "1rem";
        warning.style.zIndex = "200";
        warning.innerHTML = "Session expiring in 2 minutes. <button onclick='this.parentElement.remove()'>Stay Active</button>";
        document.body.appendChild(warning);
    }

    function logout() {
        window.location.href = "/accounts/logout/";
    }

    ["mousedown", "keydown", "touchstart", "scroll"].forEach(function (event) {
        document.addEventListener(event, resetTimer, true);
    });

    resetTimer();
}

function initModals() {
    document.querySelectorAll("[data-modal-target]").forEach(function (trigger) {
        trigger.addEventListener("click", function () {
            const target = document.getElementById(this.dataset.modalTarget);
            if (target) target.classList.add("active");
        });
    });

    document.querySelectorAll(".modal-close, .modal-overlay").forEach(function (el) {
        el.addEventListener("click", function (e) {
            if (e.target === this) {
                this.closest(".modal-overlay").classList.remove("active");
            }
        });
    });
}

function debounce(func, wait) {
    let timeout;
    return function () {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(function () {
            func.apply(context, args);
        }, wait);
    };
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
