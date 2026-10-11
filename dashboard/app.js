/* =========================================================
   MINEGUARD — DASHBOARD ENGINE
========================================================= */

const API_BASE = "";

let previousRiskLevel = "LOW";


/* =========================================================
   HELPERS
========================================================= */

function getRiskClass(level) {

    return (
        level ||
        "LOW"
    ).toLowerCase();

}


function clamp(value, min, max) {

    return Math.max(
        min,
        Math.min(max, value)
    );

}


function animateNumber(
    element,
    target,
    decimals = 0
) {

    const start =
        Number(element.textContent) || 0;

    const difference =
        target - start;

    const duration = 500;

    const startTime =
        performance.now();


    function update(currentTime) {

        const elapsed =
            currentTime - startTime;

        const progress =
            Math.min(
                elapsed / duration,
                1
            );

        const eased =
            1 -
            Math.pow(
                1 - progress,
                3
            );

        const value =
            start +
            difference * eased;

        element.textContent =
            value.toFixed(decimals);

        if (progress < 1) {

            requestAnimationFrame(
                update
            );

        }

    }


    requestAnimationFrame(
        update
    );

}


/* =========================================================
   SENSOR STATUS
========================================================= */

function getGasState(value) {

    if (value > 800) {
        return "CRITICAL";
    }

    if (value > 600) {
        return "HIGH";
    }

    if (value > 300) {
        return "ELEVATED";
    }

    return "NORMAL";

}


function getTemperatureState(value) {

    if (value > 55) {
        return "CRITICAL";
    }

    if (value > 45) {
        return "HIGH";
    }

    if (value > 35) {
        return "ELEVATED";
    }

    return "NORMAL";

}


function getDistanceState(value) {

    if (value < 15) {
        return "CRITICAL";
    }

    if (value < 30) {
        return "HIGH";
    }

    if (value < 60) {
        return "WARNING";
    }

    return "SAFE";

}


function getVibrationState(value) {

    if (value > 70) {
        return "CRITICAL";
    }

    if (value > 50) {
        return "HIGH";
    }

    if (value > 20) {
        return "ELEVATED";
    }

    return "NORMAL";

}


/* =========================================================
   UPDATE SENSOR CARDS
========================================================= */

function updateSensorCards(sensor) {

    if (!sensor) {
        return;
    }


    const gas =
        Number(sensor.gas);

    const temperature =
        Number(sensor.temperature);

    const distance =
        Number(sensor.distance);

    const vibration =
        Number(sensor.vibration);


    animateNumber(
        document.getElementById("gas"),
        gas,
        1
    );


    animateNumber(
        document.getElementById("temperature"),
        temperature,
        1
    );


    animateNumber(
        document.getElementById("distance"),
        distance,
        1
    );


    animateNumber(
        document.getElementById("vibration"),
        vibration,
        1
    );


    document.getElementById(
        "zone"
    ).textContent =
        sensor.zone || "ZONE-A";


    document.getElementById(
        "device"
    ).textContent =
        sensor.device_id ||
        "MINE-EDGE-01";


    if (sensor.timestamp) {

        document.getElementById(
            "last-update"
        ).textContent =
            new Date(
                sensor.timestamp
            ).toLocaleTimeString();

    }


    updateSensorState(
        "gas-state",
        getGasState(gas)
    );


    updateSensorState(
        "temperature-state",
        getTemperatureState(
            temperature
        )
    );


    updateSensorState(
        "distance-state",
        getDistanceState(
            distance
        )
    );


    updateSensorState(
        "vibration-state",
        getVibrationState(
            vibration
        )
    );


    document.getElementById(
        "gas-bar"
    ).style.width =
        `${clamp(gas / 10, 0, 100)}%`;


    document.getElementById(
        "temperature-bar"
    ).style.width =
        `${clamp(
            temperature / 70 * 100,
            0,
            100
        )}%`;


    document.getElementById(
        "distance-bar"
    ).style.width =
        `${clamp(
            distance / 120 * 100,
            0,
            100
        )}%`;


    document.getElementById(
        "vibration-bar"
    ).style.width =
        `${clamp(
            vibration,
            0,
            100
        )}%`;

}


function updateSensorState(
    id,
    state
) {

    const element =
        document.getElementById(id);

    if (!element) {
        return;
    }


    element.textContent =
        state;


    if (
        state === "CRITICAL" ||
        state === "HIGH"
    ) {

        element.style.color =
            "#ff4d67";

    } else if (
        state === "ELEVATED" ||
        state === "WARNING"
    ) {

        element.style.color =
            "#ffd166";

    } else {

        element.style.color =
            "#43f29a";

    }

}


/* =========================================================
   RISK
========================================================= */

function updateRisk(risk) {

    if (!risk) {
        return;
    }


    const score =
        Number(
            risk.risk_score || 0
        );


    const level =
        risk.risk_level ||
        "LOW";


    animateNumber(
        document.getElementById(
            "risk-score"
        ),
        score,
        0
    );


    const badge =
        document.getElementById(
            "risk-level-badge"
        );


    badge.textContent =
        level;


    badge.className =
        `badge ${getRiskClass(level)}`;


    const orb =
        document.getElementById(
            "risk-orb"
        );


    orb.className =
        `risk-orb ${getRiskClass(level)}`;


    if (level === "CRITICAL") {

        document.body.classList.add(
            "critical-mode"
        );

    } else {

        document.body.classList.remove(
            "critical-mode"
        );

    }


    if (
        previousRiskLevel !== level
    ) {

        triggerRiskTransition(
            level
        );

    }


    previousRiskLevel =
        level;

}


/* =========================================================
   RISK TRANSITION
========================================================= */

function triggerRiskTransition(
    level
) {

    const status =
        document.getElementById(
            "ai-status"
        );


    if (level === "CRITICAL") {

        status.textContent =
            "CRITICAL EVENT ANALYSIS";

    } else if (level === "HIGH") {

        status.textContent =
            "HIGH-RISK ANALYSIS";

    } else {

        status.textContent =
            "ANALYSIS ACTIVE";

    }

}


/* =========================================================
   AI RECOMMENDATION
========================================================= */

function updateRecommendation(
    recommendation
) {

    if (!recommendation) {
        return;
    }


    const priority =
        recommendation.priority ||
        "NORMAL";


    const badge =
        document.getElementById(
            "priority-badge"
        );


    badge.textContent =
        priority;


    let badgeClass =
        "low";


    if (
        priority === "IMMEDIATE"
    ) {

        badgeClass =
            "critical";

    } else if (
        priority === "URGENT"
    ) {

        badgeClass =
            "high";

    } else if (
        priority === "WARNING"
    ) {

        badgeClass =
            "medium";

    }


    badge.className =
        `badge ${badgeClass}`;


    document.getElementById(
        "recommendation-action"
    ).textContent =
        recommendation.action ||
        "Continue monitoring";


    document.getElementById(
        "recommendation-reason"
    ).textContent =
        recommendation.reason ||
        "No recommendation available.";


    const actions =
        document.getElementById(
            "additional-actions"
        );


    actions.innerHTML = "";


    const additionalActions =
        recommendation.additional_actions ||
        [];


    additionalActions.forEach(
        (action) => {

            const li =
                document.createElement(
                    "li"
                );

            li.textContent =
                action;

            actions.appendChild(
                li
            );

        }
    );

}


/* =========================================================
   HAZARDS
========================================================= */

function updateHazards(
    hazards
) {

    const container =
        document.getElementById(
            "hazards"
        );


    const count =
        document.getElementById(
            "hazard-count"
        );


    container.innerHTML = "";


    if (
        !hazards ||
        hazards.length === 0
    ) {

        count.textContent =
            "0";


        container.innerHTML = `
            <div class="no-hazards">
                ✓ NO ACTIVE HAZARDS
            </div>
        `;

        return;

    }


    count.textContent =
        hazards.length;


    hazards.forEach(
        (hazard) => {

            const div =
                document.createElement(
                    "div"
                );


            div.className =
                "hazard";


            div.textContent =
                `🔴 ${hazard
                    .replaceAll("_", " ")}`;


            container.appendChild(
                div
            );

        }
    );

}


/* =========================================================
   INCIDENTS
========================================================= */

function updateIncidents(
    incidents
) {

    const container =
        document.getElementById(
            "incidents"
        );


    const count =
        document.getElementById(
            "incident-count"
        );


    count.textContent =
        incidents
            ? incidents.length
            : 0;


    container.innerHTML = "";


    if (
        !incidents ||
        incidents.length === 0
    ) {

        container.innerHTML = `
            <div class="empty-state">
                No active incidents
            </div>
        `;

        return;

    }


    incidents.forEach(
        (incident) => {

            const card =
                document.createElement(
                    "div"
                );


            card.className =
                `incident-card ${
                    getRiskClass(
                        incident.risk_level
                    )
                }`;


            card.innerHTML = `

                <h3>
                    ${incident.risk_level}
                    — ${incident.zone}
                </h3>

                <p>
                    <strong>Risk:</strong>
                    ${Number(
                        incident.risk_score
                    ).toFixed(1)}
                    / 100
                </p>

                <p>
                    <strong>Hazard:</strong>
                    ${incident.hazard_type}
                </p>

                <p>
                    <strong>Action:</strong>
                    ${incident.action_required}
                </p>

                <button
                    class="resolve-button"
                    onclick="resolveIncident(
                        ${incident.id}
                    )"
                >
                    RESOLVE INCIDENT
                </button>

            `;


            container.appendChild(
                card
            );

        }
    );

}


/* =========================================================
   READINGS
========================================================= */

function updateReadingsTable(
    readings
) {

    const table =
        document.getElementById(
            "readings-table"
        );


    table.innerHTML = "";


    if (
        !readings ||
        readings.length === 0
    ) {

        table.innerHTML = `
            <tr>
                <td colspan="5">
                    Waiting for sensor data...
                </td>
            </tr>
        `;

        return;

    }


    readings
        .slice(0, 10)
        .forEach(
            (reading) => {

                const row =
                    document.createElement(
                        "tr"
                    );


                const time =
                    reading.timestamp
                        ? new Date(
                            reading.timestamp
                        ).toLocaleTimeString()
                        : "--";


                row.innerHTML = `

                    <td>
                        ${time}
                    </td>

                    <td>
                        ${Number(
                            reading.gas
                        ).toFixed(1)}
                    </td>

                    <td>
                        ${Number(
                            reading.temperature
                        ).toFixed(1)}°C
                    </td>

                    <td>
                        ${Number(
                            reading.distance
                        ).toFixed(1)} cm
                    </td>

                    <td>
                        ${Number(
                            reading.vibration
                        ).toFixed(1)}
                    </td>

                `;


                table.appendChild(
                    row
                );

            }
        );

}


/* =========================================================
   LOAD DASHBOARD
========================================================= */

async function loadDashboard() {

    try {

        const response =
            await fetch(
                `${API_BASE}/api/dashboard`,
                {
                    cache: "no-store"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Dashboard API failed"
            );

        }


        const data =
            await response.json();


        updateSensorCards(
            data.latest_sensor
        );


        updateRisk(
            data.risk
        );


        updateRecommendation(
            data.recommendation
        );


        updateHazards(
            data.risk?.hazards
        );


        updateIncidents(
            data.active_incidents
        );


        updateReadingsTable(
            data.recent_readings
        );


        document.getElementById(
            "system-status"
        ).textContent =
            "SYSTEM ONLINE";


        document.getElementById(
            "status-dot"
        ).className =
            "status-dot online";


    } catch (error) {

        console.error(error);


        document.getElementById(
            "system-status"
        ).textContent =
            "BACKEND OFFLINE";


        document.getElementById(
            "status-dot"
        ).className =
            "status-dot";


    }

}


/* =========================================================
   RESOLVE INCIDENT
========================================================= */

async function resolveIncident(
    id
) {

    try {

        const response =
            await fetch(
                `${API_BASE}/api/incidents/${id}/resolve`,
                {
                    method: "POST"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Could not resolve incident"
            );

        }


        await loadDashboard();


    } catch (error) {

        console.error(error);


        alert(
            "Could not resolve incident."
        );

    }

}


window.resolveIncident =
    resolveIncident;


/* =========================================================
   DEMO CONTROL
========================================================= */

function runDemo(
    scenario
) {

    const commands = {

        normal:
            "python edge\\simulator\\sensor_simulator.py --scenario normal --interval 2",

        gas_leak:
            "python edge\\simulator\\sensor_simulator.py --scenario gas_leak --interval 2",

        structural_hazard:
            "python edge\\simulator\\sensor_simulator.py --scenario structural_hazard --interval 2",

        critical:
            "python edge\\simulator\\sensor_simulator.py --scenario critical --interval 2"

    };


    const command =
        commands[scenario];


    if (!command) {
        return;
    }


    navigator.clipboard
        ?.writeText(command)
        .catch(() => {});


    alert(
        `Demo scenario: ${scenario.toUpperCase()}\n\n` +
        `Run this command in a new VS Code terminal:\n\n` +
        command
    );

}


window.runDemo =
    runDemo;


/* =========================================================
   START
========================================================= */

loadDashboard();


setInterval(
    loadDashboard,
    3000
);