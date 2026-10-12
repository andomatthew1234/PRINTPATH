(function () {
    "use strict";

    const DELIVERY_POLICY = {
        name: "PrintPath business delivery areas",
        // Metadata only: qualification uses the postcode rules below, never geographic distance.
        originPostcode: "3111",
        postcodeOverrides: {
            "2000": "standard",
            "3111": "standard",
            "6743": "extended"
        },
        standardRanges: [
            ["0800", "0832"], ["2000", "2234"], ["2280", "2310"], ["2500", "2530"],
            ["2600", "2620"], ["2900", "2920"], ["3000", "3207"], ["3211", "3220"],
            ["3350", "3356"], ["3550", "3556"], ["4000", "4207"], ["4210", "4230"],
            ["4300", "4305"], ["4350", "4352"], ["4550", "4575"], ["4810", "4818"],
            ["4868", "4870"], ["5000", "5199"], ["6000", "6214"], ["7000", "7055"],
            ["7248", "7250"]
        ],
        australianCoverageRanges: [
            ["0200", "0299"], ["0800", "0999"], ["2000", "2999"], ["3000", "3999"],
            ["4000", "4999"], ["5000", "5799"], ["6000", "6797"], ["7000", "7799"]
        ]
    };

    const PHOTON_ENDPOINT = "https://photon.komoot.io/api/";
    const SEARCH_DEBOUNCE_MS = 350;
    const SEARCH_TIMEOUT_MS = 7000;
    const MINIMUM_QUERY_LENGTH = 3;

    function postcodeIsInRanges(postcode, ranges) {
        const numericPostcode = Number(postcode);
        return ranges.some(function (range) {
            return numericPostcode >= Number(range[0]) && numericPostcode <= Number(range[1]);
        });
    }

    function classifyPostcode(postcode) {
        const normalizedPostcode = String(postcode || "").trim();
        if (!/^\d{4}$/.test(normalizedPostcode)) {
            return "unclassified";
        }
        if (DELIVERY_POLICY.postcodeOverrides[normalizedPostcode]) {
            return DELIVERY_POLICY.postcodeOverrides[normalizedPostcode];
        }
        if (postcodeIsInRanges(normalizedPostcode, DELIVERY_POLICY.standardRanges)) {
            return "standard";
        }
        if (postcodeIsInRanges(normalizedPostcode, DELIVERY_POLICY.australianCoverageRanges)) {
            return "extended";
        }
        return "unclassified";
    }

    const input = document.querySelector("#shipping-address");
    const suggestions = document.querySelector("#shipping-suggestions");
    const result = document.querySelector("#shipping-result");
    const mapElement = document.querySelector("#shipping-map");
    const addressHost = document.querySelector(".shipping-address-host");

    if (!input || !suggestions || !result || !mapElement || !addressHost) {
        return;
    }

    function setResult(type, title, copy) {
        result.className = "shipping-result is-" + type;
        result.setAttribute("aria-busy", "false");
        result.querySelector(".shipping-result-title").textContent = title;
        result.querySelector(".shipping-result-copy").textContent = copy;
    }

    function setLoadingResult() {
        result.className = "shipping-result is-loading";
        result.setAttribute("aria-busy", "true");
        result.querySelector(".shipping-result-title").textContent = "Searching addresses…";
        result.querySelector(".shipping-result-copy").textContent = "Looking for Australian address matches.";
    }

    if (!window.L) {
        setResult("neutral", "Delivery checker unavailable", "Please refresh the page or contact us to confirm your delivery area.");
        return;
    }

    const map = window.L.map(mapElement, {
        center: [-25.2744, 133.7751], zoom: 4, minZoom: 3, scrollWheelZoom: false, zoomControl: false
    });

    window.L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    window.L.control.zoom({ position: "bottomright" }).addTo(map);

    const markerIcon = window.L.divIcon({
        className: "shipping-marker-shell",
        html: '<span class="shipping-marker" aria-hidden="true"></span>',
        iconSize: [28, 36], iconAnchor: [14, 34]
    });

    let marker = null;
    let debounceTimer = null;
    let requestController = null;
    let requestNumber = 0;
    let activeSuggestion = -1;
    const queryCache = new Map();

    function formatAddress(properties) {
        const street = [properties.housenumber, properties.street].filter(Boolean).join(" ");
        const locality = properties.city || properties.town || properties.village || properties.district || properties.county;
        const region = [properties.state, properties.postcode].filter(Boolean).join(" ");
        return [street, locality, region].filter(function (part, index, parts) {
            return part && parts.indexOf(part) === index;
        }).join(", ");
    }

    function hideSuggestions() {
        suggestions.hidden = true;
        suggestions.replaceChildren();
        input.setAttribute("aria-expanded", "false");
        input.removeAttribute("aria-activedescendant");
        activeSuggestion = -1;
    }

    function cancelPendingSearch() {
        window.clearTimeout(debounceTimer);
        debounceTimer = null;
        requestNumber += 1;
        if (requestController) {
            requestController.abort();
            requestController = null;
        }
    }

    function updateActiveSuggestion(index) {
        const options = Array.from(suggestions.querySelectorAll('[role="option"]'));
        if (!options.length) {
            return;
        }
        activeSuggestion = (index + options.length) % options.length;
        options.forEach(function (option, optionIndex) {
            const isActive = optionIndex === activeSuggestion;
            option.classList.toggle("is-active", isActive);
            option.setAttribute("aria-selected", String(isActive));
        });
        input.setAttribute("aria-activedescendant", options[activeSuggestion].id);
        options[activeSuggestion].scrollIntoView({ block: "nearest" });
    }

    function selectAddress(feature, label) {
        const properties = feature.properties || {};
        const coordinates = feature.geometry && feature.geometry.coordinates;
        const longitude = coordinates && Number(coordinates[0]);
        const latitude = coordinates && Number(coordinates[1]);

        cancelPendingSearch();
        input.value = label;
        hideSuggestions();

        if (Number.isFinite(latitude) && Number.isFinite(longitude)) {
            if (marker) {
                marker.setLatLng([latitude, longitude]);
            } else {
                marker = window.L.marker([latitude, longitude], { icon: markerIcon, title: label }).addTo(map);
            }
            if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
                map.setView([latitude, longitude], 15);
            } else {
                map.flyTo([latitude, longitude], 15, { duration: 1.25 });
            }
        }

        const classification = classifyPostcode(properties.postcode);
        if (classification === "standard") {
            setResult("standard", "✓ Standard Area Delivery", "Your address qualifies for PrintPath’s standard delivery rates.");
        } else if (classification === "extended") {
            setResult("extended", "✓ Extended Area Delivery", "This postcode is in PrintPath’s configured extended delivery area.");
        } else {
            setResult("neutral", "Delivery area not yet classified", "We couldn’t confidently match this address to a configured postcode area. Please contact us before ordering.");
        }
    }

    function renderSuggestions(features) {
        suggestions.replaceChildren();
        const seenLabels = new Set();

        features.forEach(function (feature) {
            const properties = feature.properties || {};
            if (String(properties.countrycode || "").toUpperCase() !== "AU") {
                return;
            }
            const label = formatAddress(properties);
            if (!label || seenLabels.has(label)) {
                return;
            }
            seenLabels.add(label);

            const item = document.createElement("li");
            item.setAttribute("role", "presentation");
            const option = document.createElement("button");
            option.type = "button";
            option.id = "shipping-suggestion-" + seenLabels.size;
            option.setAttribute("role", "option");
            option.setAttribute("aria-selected", "false");
            option.tabIndex = -1;
            option.textContent = label;
            option.addEventListener("click", function () { selectAddress(feature, label); });
            item.appendChild(option);
            suggestions.appendChild(item);
        });

        if (!suggestions.children.length) {
            hideSuggestions();
            setResult("neutral", "No matching addresses found", "Try adding a street number, suburb, state or postcode.");
            return;
        }

        setResult("neutral", "Select an address", "Choose the matching Australian address from the suggestions.");
        suggestions.hidden = false;
        input.setAttribute("aria-expanded", "true");
        activeSuggestion = -1;
    }

    async function searchAddresses(query, currentRequest) {
        const cacheKey = query.toLowerCase();
        if (queryCache.has(cacheKey)) {
            if (currentRequest === requestNumber) {
                renderSuggestions(queryCache.get(cacheKey));
            }
            return;
        }

        const controller = new AbortController();
        requestController = controller;
        let timedOut = false;
        const timeoutTimer = window.setTimeout(function () {
            timedOut = true;
            controller.abort();
        }, SEARCH_TIMEOUT_MS);
        setLoadingResult();

        try {
            const url = new URL(PHOTON_ENDPOINT);
            url.searchParams.set("q", query);
            url.searchParams.set("countrycode", "AU");
            url.searchParams.set("limit", "8");
            url.searchParams.set("lang", "en");
            const response = await fetch(url, { headers: { Accept: "application/json" }, signal: controller.signal });
            if (!response.ok) {
                throw new Error("Address service returned " + response.status);
            }
            const data = await response.json();
            if (currentRequest !== requestNumber) {
                return;
            }
            const features = Array.isArray(data.features) ? data.features : [];
            queryCache.set(cacheKey, features);
            renderSuggestions(features);
        } catch (error) {
            if (currentRequest !== requestNumber) {
                return;
            }
            hideSuggestions();
            if (timedOut) {
                setResult("neutral", "Address search timed out", "Please try again. If the problem continues, contact us to confirm your delivery area.");
            } else if (error.name !== "AbortError") {
                setResult("neutral", "Couldn’t search addresses", "Please try again shortly or contact us to confirm your delivery area.");
            }
        } finally {
            window.clearTimeout(timeoutTimer);
            if (requestController === controller) {
                requestController = null;
            }
        }
    }

    input.addEventListener("input", function () {
        cancelPendingSearch();
        hideSuggestions();
        const query = input.value.trim();
        if (query.length < MINIMUM_QUERY_LENGTH) {
            setResult("neutral", "Select an address to check delivery", "Enter at least three characters, then choose an Australian address from the suggestions.");
            return;
        }

        const currentRequest = requestNumber;
        debounceTimer = window.setTimeout(function () {
            if (currentRequest === requestNumber) {
                searchAddresses(query, currentRequest);
            }
        }, SEARCH_DEBOUNCE_MS);
    });

    input.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            cancelPendingSearch();
            hideSuggestions();
            return;
        }
        if (suggestions.hidden) {
            return;
        }
        if (event.key === "ArrowDown") {
            event.preventDefault();
            updateActiveSuggestion(activeSuggestion + 1);
        } else if (event.key === "ArrowUp") {
            event.preventDefault();
            updateActiveSuggestion(activeSuggestion - 1);
        } else if (event.key === "Enter" && activeSuggestion >= 0) {
            event.preventDefault();
            suggestions.querySelectorAll('[role="option"]')[activeSuggestion].click();
        }
    });

    addressHost.addEventListener("focusout", function () {
        window.setTimeout(function () {
            if (!addressHost.contains(document.activeElement)) {
                cancelPendingSearch();
                hideSuggestions();
            }
        }, 0);
    });

    document.addEventListener("click", function (event) {
        if (!event.target.closest(".shipping-address-host")) {
            cancelPendingSearch();
            hideSuggestions();
        }
    });
}());
