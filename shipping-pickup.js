(function () {
    "use strict";

    const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
    if (!tabs.length) {
        return;
    }

    function activateTab(tab, moveFocus) {
        tabs.forEach(function (candidate) {
            const selected = candidate === tab;
            candidate.classList.toggle("is-active", selected);
            candidate.setAttribute("aria-selected", String(selected));
            candidate.tabIndex = selected ? 0 : -1;
            const panel = document.getElementById(candidate.getAttribute("aria-controls"));
            if (panel) {
                panel.hidden = !selected;
            }
        });

        if (moveFocus) {
            tab.focus();
        }
        if (tab.id === "shipping-tab") {
            window.setTimeout(function () { window.dispatchEvent(new Event("resize")); }, 0);
        }
    }

    tabs.forEach(function (tab, index) {
        tab.addEventListener("click", function () { activateTab(tab, false); });
        tab.addEventListener("keydown", function (event) {
            let nextIndex = null;
            if (event.key === "ArrowRight") nextIndex = (index + 1) % tabs.length;
            if (event.key === "ArrowLeft") nextIndex = (index - 1 + tabs.length) % tabs.length;
            if (event.key === "Home") nextIndex = 0;
            if (event.key === "End") nextIndex = tabs.length - 1;
            if (nextIndex !== null) {
                event.preventDefault();
                activateTab(tabs[nextIndex], true);
            }
        });
    });
}());
