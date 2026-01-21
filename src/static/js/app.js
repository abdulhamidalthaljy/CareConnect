// This file contains JavaScript code for client-side functionality, including API calls and dynamic content updates.

document.addEventListener('DOMContentLoaded', function () {
    // read CSRF token from meta tag (if present)
    window.__CARECONNECT_CSRF_TOKEN = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || null;
    // Load existing vitals and draw chart
    loadVitals();

    // Event listener for vitals form submissions
    const vitalForm = document.getElementById('vital-form');
    if (vitalForm) {
        vitalForm.addEventListener('submit', function (event) {
            event.preventDefault();
            addVital();
        });
    }

    // dynamic label updates when type changes
    const typeSelect = document.getElementById('vital-type');
    if (typeSelect) {
        typeSelect.addEventListener('change', function () {
            updateVitalLabels(this.value);
        });
        // initialize labels
        updateVitalLabels(typeSelect.value);
    }

    // File upload wiring
    const uploadBtn = document.getElementById('upload-btn');
    if (uploadBtn) {
        uploadBtn.addEventListener('click', function () {
            uploadFile();
        });
    }
});

function fetchUserData() {
    fetch('/api/user')
        .then(response => response.json())
        .then(data => {
            // Update the dashboard with user data
            document.getElementById('user-name').textContent = data.name;
            document.getElementById('user-email').textContent = data.email;
        })
        .catch(error => console.error('Error fetching user data:', error));
}

// ---------------- File upload functions ----------------
function uploadFile() {
    const input = document.getElementById('file-input');
    const area = document.getElementById('file-message');
    if (!input || !input.files || input.files.length === 0) {
        if (area) area.innerHTML = '<div class="p-2 rounded bg-red-100 text-red-800">Please select a file to upload.</div>';
        return;
    }
    const file = input.files[0];
    const fd = new FormData();
    fd.append('file', file);

    fetch('/upload_file', {
        method: 'POST',
        body: fd,
        headers: window.__CARECONNECT_CSRF_TOKEN ? { 'X-CSRFToken': window.__CARECONNECT_CSRF_TOKEN } : {}
    })
        .then(res => res.json())
        .then(resp => {
            if (resp.status === 'ok') {
                if (area) area.innerHTML = '<div class="p-2 rounded bg-green-100 text-green-800">Upload successful.</div>';
                // reload page to show new file in list (simple approach)
                setTimeout(() => { location.reload(); }, 700);
            } else if (resp.error) {
                if (area) area.innerHTML = `<div class="p-2 rounded bg-red-100 text-red-800">${resp.error}</div>`;
            } else {
                if (area) area.innerHTML = '<div class="p-2 rounded bg-red-100 text-red-800">Upload failed.</div>';
            }
        })
        .catch(err => {
            console.error('Upload error', err);
            if (area) area.innerHTML = '<div class="p-2 rounded bg-red-100 text-red-800">Upload failed.</div>';
        });
}

function submitForm() {
    const formData = new FormData(document.getElementById('user-form'));
    fetch('/api/submit', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            // Handle successful form submission
            alert('Form submitted successfully!');
        })
        .catch(error => console.error('Error submitting form:', error));
}

// ---------------- Vitals-related functions ----------------
let vitalsChart = null;

function loadVitals() {
    fetch('/api/get_vitals')
        .then(res => res.json())
        .then(data => {
            renderVitalsTable(data);
            renderVitalsChart(data);
        })
        .catch(err => console.error('Error loading vitals:', err));
}

function addVital() {
    const type = document.getElementById('vital-type').value;
    const value1 = document.getElementById('vital-value1').value;
    const value2 = document.getElementById('vital-value2').value;

    // client-side validation
    if (!value1 || isNaN(parseFloat(value1))) {
        showVitalMessage('Value 1 is required and must be a number.', 'danger');
        return;
    }
    if (type === 'bp' && value2 && isNaN(parseFloat(value2))) {
        showVitalMessage('Value 2 must be a number.', 'danger');
        return;
    }

    const payload = { type: type, value1: value1, value2: value2 };

    const headers = { 'Content-Type': 'application/json' };
    if (window.__CARECONNECT_CSRF_TOKEN) {
        headers['X-CSRFToken'] = window.__CARECONNECT_CSRF_TOKEN;
    }

    fetch('/add_vital', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(payload)
    })
        .then(res => res.json())
        .then(resp => {
            if (resp.status === 'ok') {
                // reload vitals
                loadVitals();
                document.getElementById('vital-form').reset();
                showVitalMessage('Vital added.', 'success');
            } else if (resp.error) {
                showVitalMessage(resp.error, 'danger');
            } else {
                showVitalMessage('Failed to add vital.', 'danger');
            }
        })
        .catch(err => console.error('Error adding vital:', err));
}

function renderVitalsTable(data) {
    const tbody = document.getElementById('vitals-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    data.slice().reverse().forEach(v => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td class="border px-2 py-1 text-sm">${v.type}</td><td class="border px-2 py-1 text-sm">${v.value1}</td><td class="border px-2 py-1 text-sm">${v.value2 || ''}</td><td class="border px-2 py-1 text-sm">${new Date(v.timestamp).toLocaleString()}</td>`;
        tbody.appendChild(tr);
    });
}

function renderVitalsChart(data) {
    const ctx = document.getElementById('vitalsChart');
    if (!ctx) return;
    // Build chart datasets based on types present
    const labels = data.map(v => new Date(v.timestamp).toLocaleString());

    // If data contains BP with value2, show two datasets: Systolic (value1) and Diastolic (value2)
    const hasBP = data.some(v => v.type === 'bp');
    const hasSugar = data.some(v => v.type === 'sugar');

    let datasets = [];
    if (hasBP) {
        const systolic = data.map(v => (v.type === 'bp' ? parseFloat(v.value1) || null : null));
        const diastolic = data.map(v => (v.type === 'bp' ? (v.value2 ? parseFloat(v.value2) : null) : null));
        datasets.push({ label: 'Systolic (BP)', data: systolic, borderColor: 'rgba(220,38,38,1)', backgroundColor: 'rgba(220,38,38,0.15)' });
        datasets.push({ label: 'Diastolic (BP)', data: diastolic, borderColor: 'rgba(34,197,94,1)', backgroundColor: 'rgba(34,197,94,0.15)' });
    }
    if (hasSugar) {
        const sugar = data.map(v => (v.type === 'sugar' ? parseFloat(v.value1) || null : null));
        datasets.push({ label: 'Blood Sugar', data: sugar, borderColor: 'rgba(59,130,246,1)', backgroundColor: 'rgba(59,130,246,0.2)' });
    }

    if (datasets.length === 0) {
        // fallback: show value1
        const values = data.map(v => parseFloat(v.value1) || 0);
        datasets = [{ label: 'Value', data: values, borderColor: 'rgba(59,130,246,1)', backgroundColor: 'rgba(59,130,246,0.2)' }];
    }

    if (vitalsChart) {
        vitalsChart.data.labels = labels;
        vitalsChart.data.datasets = datasets;
        vitalsChart.update();
        return;
    }

    vitalsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            interaction: { mode: 'index', intersect: false },
            stacked: false,
            scales: {
                x: { display: true },
                y: { display: true }
            }
        }
    });
}

// Update labels/placeholder depending on vital type
function updateVitalLabels(type) {
    const label1 = document.querySelector('label[for="vital-value1"]');
    const label2 = document.querySelector('label[for="vital-value2"]');
    const input1 = document.getElementById('vital-value1');
    const input2 = document.getElementById('vital-value2');
    if (!label1 || !label2 || !input1 || !input2) return;
    if (type === 'bp') {
        label1.textContent = 'Systolic (mmHg)';
        input1.placeholder = 'e.g. 120';
        label2.parentElement.style.display = '';
    } else {
        label1.textContent = 'Value';
        input1.placeholder = 'e.g. 5.6';
        // hide value2 for sugar
        label2.parentElement.style.display = 'none';
    }
}

// Simple message/toast area for vitals actions
function showVitalMessage(msg, category) {
    const area = document.getElementById('vital-message');
    if (!area) {
        alert(msg);
        return;
    }
    area.innerHTML = '';
    const div = document.createElement('div');
    div.className = 'p-2 rounded ' + (category === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800');
    div.textContent = msg;
    area.appendChild(div);
    setTimeout(() => { area.innerHTML = ''; }, 4000);
}

// Mobile menu toggle
document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('mobile-menu-btn');
    const menu = document.getElementById('mobile-menu');
    if (btn && menu) {
        btn.addEventListener('click', function () {
            menu.classList.toggle('hidden');
        });
    }
});