const MAX_POINTS = 30;
const statusRing = document.getElementById("statusRing");
const overallStatus = document.getElementById("overallStatus");
const statusMessage = document.getElementById("statusMessage");

function createChart(elementId, label, color) {
    const context = document.getElementById(elementId);

    return new Chart(context, {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label,
                data: [],
                borderColor: color,
                backgroundColor: `${color}33`,
                fill: true,
                tension: 0.35,
                borderWidth: 2.5,
                pointRadius: 0,
                pointHoverRadius: 4,
            }],
        },
        options: {
            maintainAspectRatio: false,
            animation: false,
            plugins: {
                legend: {
                    labels: {
                        color: "#ecf4ff",
                    },
                },
            },
            scales: {
                x: {
                    ticks: { color: "#8fa7c2" },
                    grid: { color: "rgba(143, 201, 255, 0.08)" },
                },
                y: {
                    beginAtZero: true,
                    suggestedMax: 100,
                    ticks: { color: "#8fa7c2" },
                    grid: { color: "rgba(143, 201, 255, 0.08)" },
                },
            },
        },
    });
}

const cpuChart = createChart("cpuChart", "CPU %", "#55f0b5");
const memoryChart = createChart("memoryChart", "Memory %", "#61b4ff");
const diskChart = createChart("diskChart", "Disk %", "#ff8b7b");

function pushPoint(chart, label, value) {
    chart.data.labels.push(label);
    chart.data.datasets[0].data.push(value);

    if (chart.data.labels.length > MAX_POINTS) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
    }

    chart.update();
}

function formatPercent(value) {
    return `${Number(value).toFixed(1)}%`;
}

function updateStatus(status, peakValue) {
    const statusMap = {
        healthy: {
            label: "Healthy",
            color: "#43d9a3",
            message: `Peak utilization is ${formatPercent(peakValue)}. All systems look stable.`,
        },
        warning: {
            label: "Warning",
            color: "#ffbf5f",
            message: `Peak utilization reached ${formatPercent(peakValue)}. Capacity should be reviewed.`,
        },
        critical: {
            label: "Critical",
            color: "#ff6f61",
            message: `Peak utilization reached ${formatPercent(peakValue)}. Immediate attention recommended.`,
        },
    };

    const current = statusMap[status] || statusMap.healthy;
    statusRing.style.background = `radial-gradient(circle at center, rgba(7, 17, 31, 0.98) 54%, transparent 55%), conic-gradient(${current.color} 0deg 360deg)`;
    overallStatus.textContent = current.label;
    statusMessage.textContent = current.message;
}

function applySnapshot(snapshot, label) {
    pushPoint(cpuChart, label, snapshot.cpu);
    pushPoint(memoryChart, label, snapshot.memory);
    pushPoint(diskChart, label, snapshot.disk);

    document.getElementById("cpuValue").textContent = formatPercent(snapshot.cpu);
    document.getElementById("memoryValue").textContent = formatPercent(snapshot.memory);
    document.getElementById("diskValue").textContent = formatPercent(snapshot.disk);
    document.getElementById("loadValue").textContent = Number(snapshot.load_average || 0).toFixed(2);
    document.getElementById("cpuTrend").textContent = `Latest sample at ${label}`;
    document.getElementById("memoryFootprint").textContent = `${snapshot.memory_used_gb} / ${snapshot.memory_total_gb} GB used`;
    document.getElementById("diskFootprint").textContent = `${snapshot.disk_used_gb} / ${snapshot.disk_total_gb} GB used`;
    document.getElementById("timestampValue").textContent = `Captured ${label}`;

    const peakValue = Math.max(snapshot.cpu, snapshot.memory, snapshot.disk);
    updateStatus(snapshot.status, peakValue);
}

async function loadHistory() {
    const response = await fetch(window.dashboardConfig.historyUrl);
    const history = await response.json();

    history.forEach((snapshot) => {
        applySnapshot(snapshot, snapshot.time);
    });
}

async function loadLiveMetrics() {
    const response = await fetch(window.dashboardConfig.metricsUrl);
    const snapshot = await response.json();
    const label = new Date(snapshot.timestamp).toLocaleTimeString();
    applySnapshot(snapshot, label);
}

async function bootstrapDashboard() {
    try {
        await loadHistory();
        await loadLiveMetrics();
        window.setInterval(loadLiveMetrics, window.dashboardConfig.sampleIntervalMs);
    } catch (error) {
        overallStatus.textContent = "Offline";
        statusMessage.textContent = "Unable to fetch telemetry right now.";
        console.error("Dashboard update failed", error);
    }
}

bootstrapDashboard();
