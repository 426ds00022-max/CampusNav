/**
 * Campus Navigator - Frontend JavaScript
 * Handles:
 * 1. Dynamic SVG schematic campus map rendering.
 * 2. User interactions (dropdown selection, node click-to-route, swap, reset, presets).
 * 3. Route API communication (sending start & destination to Flask backend).
 * 4. Highlighting active BFS paths and nodes on the campus map.
 */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const form = document.getElementById("route-form");
    const startSelect = document.getElementById("start-location");
    const destSelect = document.getElementById("dest-location");
    const btnSwap = document.getElementById("btn-swap");
    const btnReset = document.getElementById("btn-reset");
    const btnResetMap = document.getElementById("btn-reset-map");
    const presetChips = document.querySelectorAll(".preset-chip");

    // Result Area Elements
    const resultPlaceholder = document.getElementById("result-placeholder");
    const resultLoading = document.getElementById("result-loading");
    const resultError = document.getElementById("result-error");
    const errorTitle = document.getElementById("error-title");
    const errorMessage = document.getElementById("error-message");
    const resultDetails = document.getElementById("result-details");
    const statConnections = document.getElementById("stat-connections");
    const statStops = document.getElementById("stat-stops");
    const routeTimeline = document.getElementById("route-timeline");

    // SVG Layers
    const edgesLayer = document.getElementById("map-edges");
    const activeEdgesLayer = document.getElementById("map-active-edges");
    const nodesLayer = document.getElementById("map-nodes");

    // Campus Data Cache
    let campusGraph = null;
    let locationCoords = {};
    let currentRoutePath = [];

    // Fallback campus coordinates in case API fetch is delayed
    const FALLBACK_COORDINATES = {
        "Main Gate": { x: 120, y: 500, category: "Entrance" },
        "Main Block": { x: 110, y: 320, category: "Academic" },
        "Quadrangle": { x: 260, y: 380, category: "Central" },
        "St. Thomas's Hall": { x: 300, y: 520, category: "Residence" },
        "Martin Junction": { x: 490, y: 520, category: "Junction" },
        "Library": { x: 670, y: 500, category: "Academic" },
        "Botany Tank": { x: 860, y: 420, category: "Scenic" },
        "Principal's Residence": { x: 870, y: 240, category: "Admin" },
        "MRF": { x: 750, y: 120, category: "Facility" },
        "Bell Tower": { x: 560, y: 100, category: "Landmark" },
        "CUS": { x: 380, y: 120, category: "Dining" },
        "Zoology Tank": { x: 480, y: 230, category: "Scenic" },
        "Bishop Heber Hall": { x: 310, y: 220, category: "Residence" },
        "Selaiyur Hall": { x: 400, y: 340, category: "Residence" },
    };

    const FALLBACK_EDGES = [
        { from: "Main Gate", to: "Quadrangle" },
        { from: "Main Gate", to: "St. Thomas's Hall" },
        { from: "Quadrangle", to: "Main Block" },
        { from: "Quadrangle", to: "Selaiyur Hall" },
        { from: "Quadrangle", to: "St. Thomas's Hall" },
        { from: "St. Thomas's Hall", to: "Martin Junction" },
        { from: "Martin Junction", to: "Library" },
        { from: "Library", to: "Botany Tank" },
        { from: "Botany Tank", to: "Principal's Residence" },
        { from: "Principal's Residence", to: "MRF" },
        { from: "MRF", to: "Bell Tower" },
        { from: "Bell Tower", to: "CUS" },
        { from: "CUS", to: "Zoology Tank" },
        { from: "Zoology Tank", to: "Selaiyur Hall" },
        { from: "Zoology Tank", to: "Bishop Heber Hall" }
    ];

    // ========================================================================
    // 1. INITIALIZE CAMPUS MAP & GRAPH DATA
    // ========================================================================
    async function initCampusMap() {
        try {
            const response = await fetch("/api/graph");
            if (response.ok) {
                const data = await response.json();
                campusGraph = data;
                locationCoords = data.coordinates || FALLBACK_COORDINATES;
                renderMap(data.edges, locationCoords);
                return;
            }
        } catch (err) {
            console.warn("Could not fetch /api/graph, using built-in campus layout:", err);
        }

        // Use fallback if API is not yet reachable
        locationCoords = FALLBACK_COORDINATES;
        renderMap(FALLBACK_EDGES, FALLBACK_COORDINATES);
    }

    // ========================================================================
    // 2. RENDER SCHEMATIC SVG MAP
    // ========================================================================
    function renderMap(edges, coordinates) {
        // Clear previous SVG contents
        edgesLayer.innerHTML = "";
        activeEdgesLayer.innerHTML = "";
        nodesLayer.innerHTML = "";

        // Render base walkway edges (roads)
        edges.forEach(edge => {
            const startPt = coordinates[edge.from];
            const endPt = coordinates[edge.to];

            if (startPt && endPt) {
                const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                line.setAttribute("x1", startPt.x);
                line.setAttribute("y1", startPt.y);
                line.setAttribute("x2", endPt.x);
                line.setAttribute("y2", endPt.y);
                line.setAttribute("class", "edge-line");
                const edgeKey = [edge.from, edge.to].sort().join("---");
                line.setAttribute("data-edge-key", edgeKey);
                edgesLayer.appendChild(line);
            }
        });

        // Render location nodes
        Object.keys(coordinates).forEach(locName => {
            const pt = coordinates[locName];
            const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
            g.setAttribute("class", "node-group");
            g.setAttribute("data-name", locName);

            // Outer ring
            const outerCircle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            outerCircle.setAttribute("cx", pt.x);
            outerCircle.setAttribute("cy", pt.y);
            outerCircle.setAttribute("r", "16");
            outerCircle.setAttribute("class", "node-circle-outer");

            // Inner core
            const innerCircle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            innerCircle.setAttribute("cx", pt.x);
            innerCircle.setAttribute("cy", pt.y);
            innerCircle.setAttribute("r", "7");
            innerCircle.setAttribute("class", "node-circle-inner");

            // Label background box
            const textBg = document.createElementNS("http://www.w3.org/2000/svg", "rect");
            const approxWidth = Math.max(locName.length * 7.5, 60);
            textBg.setAttribute("x", pt.x - approxWidth / 2);
            textBg.setAttribute("y", pt.y + 20);
            textBg.setAttribute("width", approxWidth);
            textBg.setAttribute("height", 20);
            textBg.setAttribute("class", "node-label-bg");

            // Text label
            const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
            text.setAttribute("x", pt.x);
            text.setAttribute("y", pt.y + 34);
            text.setAttribute("class", "node-label-text");
            text.textContent = locName;

            // Assemble node
            g.appendChild(outerCircle);
            g.appendChild(innerCircle);
            g.appendChild(textBg);
            g.appendChild(text);

            // Click listener: allows selecting location directly by clicking the map
            g.addEventListener("click", () => handleMapNodeClick(locName));

            nodesLayer.appendChild(g);
        });
    }

    // ========================================================================
    // 3. INTERACTIVE NODE CLICK HANDLER
    // ========================================================================
    function handleMapNodeClick(locationName) {
        const currentStart = startSelect.value;
        const currentDest = destSelect.value;

        if (!currentStart) {
            // First click selects Start
            startSelect.value = locationName;
            updateMapHighlightsOnly();
        } else if (!currentDest && currentStart !== locationName) {
            // Second click selects Destination and automatically runs BFS
            destSelect.value = locationName;
            findRoute(currentStart, locationName);
        } else {
            // If already filled, start a new selection with this location as Start
            startSelect.value = locationName;
            destSelect.value = "";
            clearRouteHighlights();
            updateMapHighlightsOnly();
        }
    }

    // ========================================================================
    // 4. FIND ROUTE (FETCH FROM BACKEND API)
    // ========================================================================
    async function findRoute(start, destination) {
        if (!start || !destination) {
            showError("Missing Selection", "Please choose both a start location and a destination.");
            return;
        }

        // Show loading state
        showLoading();

        try {
            const response = await fetch("/api/route", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    start: start,
                    destination: destination
                })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                showError("Route Not Found", data.error || "An error occurred while computing the route.");
                clearRouteHighlights();
                return;
            }

            // Display results and highlight map
            displayRouteResults(data);
            highlightRouteOnMap(data.path);

        } catch (error) {
            console.error("Network or server error:", error);
            showError("Server Connection Error", "Unable to contact the Campus Navigator server. Please make sure the Flask application is running.");
        }
    }

    // ========================================================================
    // 5. DISPLAY ROUTE RESULTS IN UI
    // ========================================================================
    function displayRouteResults(data) {
        const { path, connections, start, destination } = data;
        currentRoutePath = path;

        // Hide other result panels
        resultPlaceholder.classList.add("hidden");
        resultLoading.classList.add("hidden");
        resultError.classList.add("hidden");
        resultDetails.classList.remove("hidden");

        // Update statistics cards
        statConnections.textContent = connections;
        statStops.textContent = path.length;

        // Build step-by-step timeline
        routeTimeline.innerHTML = "";

        path.forEach((location, index) => {
            const stepEl = document.createElement("div");
            stepEl.className = "timeline-step";

            let markerClass = "transit";
            let roleText = `Step ${index}`;

            if (index === 0) {
                markerClass = "start";
                roleText = "Starting Point";
            } else if (index === path.length - 1) {
                markerClass = "dest";
                roleText = index === 0 ? "Starting Point & Destination" : "Final Destination";
            }

            stepEl.innerHTML = `
                <div class="step-marker ${markerClass}">
                    ${index === 0 ? '<i class="fa-solid fa-flag"></i>' : (index === path.length - 1 ? '<i class="fa-solid fa-location-dot"></i>' : index)}
                </div>
                <div class="step-info">
                    <span class="step-name">${location}</span>
                    <span class="step-role">${roleText}</span>
                </div>
            `;

            routeTimeline.appendChild(stepEl);
        });
    }

    // ========================================================================
    // 6. HIGHLIGHT ROUTE ON SCHEMATIC MAP
    // ========================================================================
    function highlightRouteOnMap(path) {
        // Clear previous active edges
        activeEdgesLayer.innerHTML = "";

        if (!path || path.length === 0) {
            clearRouteHighlights();
            return;
        }

        const startNode = path[0];
        const destNode = path[path.length - 1];
        const pathSet = new Set(path);

        // 1. Update Node Groups
        const nodeGroups = nodesLayer.querySelectorAll(".node-group");
        nodeGroups.forEach(g => {
            const name = g.getAttribute("data-name");
            g.classList.remove("is-start", "is-dest", "is-path", "is-dimmed");

            if (name === startNode) {
                g.classList.add("is-start");
            } else if (name === destNode) {
                g.classList.add("is-dest");
            } else if (pathSet.has(name)) {
                g.classList.add("is-path");
            } else {
                // Dim nodes not on the path
                g.classList.add("is-dimmed");
            }
        });

        // 2. Dim normal edges and draw active glowing path lines
        const edgeLines = edgesLayer.querySelectorAll(".edge-line");
        edgeLines.forEach(line => {
            line.style.opacity = "0.2";
        });

        // Draw active route edges between adjacent steps
        for (let i = 0; i < path.length - 1; i++) {
            const u = path[i];
            const v = path[i + 1];
            const ptU = locationCoords[u];
            const ptV = locationCoords[v];

            if (ptU && ptV) {
                const activeLine = document.createElementNS("http://www.w3.org/2000/svg", "line");
                activeLine.setAttribute("x1", ptU.x);
                activeLine.setAttribute("y1", ptU.y);
                activeLine.setAttribute("x2", ptV.x);
                activeLine.setAttribute("y2", ptV.y);
                activeLine.setAttribute("class", "edge-line-active");
                activeEdgesLayer.appendChild(activeLine);
            }
        }
    }

    // Highlight start or dest if only one is selected so far
    function updateMapHighlightsOnly() {
        const start = startSelect.value;
        const dest = destSelect.value;

        activeEdgesLayer.innerHTML = "";
        const nodeGroups = nodesLayer.querySelectorAll(".node-group");

        nodeGroups.forEach(g => {
            const name = g.getAttribute("data-name");
            g.classList.remove("is-start", "is-dest", "is-path", "is-dimmed");

            if (name === start) {
                g.classList.add("is-start");
            } else if (name === dest) {
                g.classList.add("is-dest");
            }
        });

        // Reset base edges opacity
        const edgeLines = edgesLayer.querySelectorAll(".edge-line");
        edgeLines.forEach(line => {
            line.style.opacity = "1";
        });
    }

    // Reset all map highlights to default idle state
    function clearRouteHighlights() {
        activeEdgesLayer.innerHTML = "";
        const nodeGroups = nodesLayer.querySelectorAll(".node-group");
        nodeGroups.forEach(g => {
            g.classList.remove("is-start", "is-dest", "is-path", "is-dimmed");
        });

        const edgeLines = edgesLayer.querySelectorAll(".edge-line");
        edgeLines.forEach(line => {
            line.style.opacity = "1";
        });
    }

    // ========================================================================
    // 7. UI FEEDBACK STATES (LOADING / ERROR / RESET)
    // ========================================================================
    function showLoading() {
        resultPlaceholder.classList.add("hidden");
        resultError.classList.add("hidden");
        resultDetails.classList.add("hidden");
        resultLoading.classList.remove("hidden");
    }

    function showError(title, message) {
        resultPlaceholder.classList.add("hidden");
        resultLoading.classList.add("hidden");
        resultDetails.classList.add("hidden");
        resultError.classList.remove("hidden");

        errorTitle.textContent = title;
        errorMessage.textContent = message;
    }

    function resetAll() {
        startSelect.value = "";
        destSelect.value = "";
        currentRoutePath = [];

        resultLoading.classList.add("hidden");
        resultError.classList.add("hidden");
        resultDetails.classList.add("hidden");
        resultPlaceholder.classList.remove("hidden");

        clearRouteHighlights();
    }

    // ========================================================================
    // 8. EVENT LISTENERS
    // ========================================================================

    // Form submission
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const start = startSelect.value;
        const dest = destSelect.value;
        findRoute(start, dest);
    });

    // Swap button
    btnSwap.addEventListener("click", () => {
        const temp = startSelect.value;
        startSelect.value = destSelect.value;
        destSelect.value = temp;

        if (startSelect.value && destSelect.value) {
            findRoute(startSelect.value, destSelect.value);
        } else {
            updateMapHighlightsOnly();
        }
    });

    // Reset buttons
    btnReset.addEventListener("click", resetAll);
    btnResetMap.addEventListener("click", resetAll);

    // Dropdown change listeners
    startSelect.addEventListener("change", () => {
        if (destSelect.value) {
            findRoute(startSelect.value, destSelect.value);
        } else {
            updateMapHighlightsOnly();
        }
    });

    destSelect.addEventListener("change", () => {
        if (startSelect.value) {
            findRoute(startSelect.value, destSelect.value);
        } else {
            updateMapHighlightsOnly();
        }
    });

    // Preset chips
    presetChips.forEach(chip => {
        chip.addEventListener("click", () => {
            const start = chip.getAttribute("data-start");
            const dest = chip.getAttribute("data-dest");
            startSelect.value = start;
            destSelect.value = dest;
            findRoute(start, dest);
        });
    });

    // Initial Map Render
    initCampusMap();
});
