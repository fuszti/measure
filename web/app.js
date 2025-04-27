// Configuration
const API_URL = 'http://localhost:8000';

// Global state
let templates = [];
let currentTemplate = null;
let measurements = [];
let charts = {};

// DOM Elements
const navLinks = document.querySelectorAll('.nav-link');
const pages = document.querySelectorAll('.page');
const timeFilters = document.querySelectorAll('.time-filter');
const dashboardTemplateSelect = document.getElementById('dashboard-template-select');
const measurementTemplateFilter = document.getElementById('measurement-template-filter');
const measurementTemplateSelect = document.getElementById('measurement-template-select');
const measurementStartDate = document.getElementById('measurement-start-date');
const measurementEndDate = document.getElementById('measurement-end-date');
const addMeasurementBtn = document.getElementById('add-measurement-btn');
const addTemplateBtn = document.getElementById('add-template-btn');
const saveTemplateBtn = document.getElementById('save-template-btn');
const saveMeasurementBtn = document.getElementById('save-measurement-btn');
const addValueBtn = document.getElementById('add-value-btn');
const valueDefinitionsContainer = document.getElementById('value-definitions-container');
const measurementValuesContainer = document.getElementById('measurement-values-container');

// Bootstrap modals
const addMeasurementModal = new bootstrap.Modal(document.getElementById('add-measurement-modal'));
const addTemplateModal = new bootstrap.Modal(document.getElementById('add-template-modal'));

// Authentication functions
function checkAuth() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login.html';
        return false;
    }
    return true;
}

async function getUserInfo() {
    try {
        const user = await fetchAPI('/users/me');
        if (user && user.username) {
            document.getElementById('username-display').textContent = user.username;
        }
    } catch (error) {
        console.error('Error getting user info:', error);
    }
}

function logout() {
    localStorage.removeItem('access_token');
    window.location.href = '/login.html';
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    // Check if user is authenticated
    if (!checkAuth()) return;
    
    // Get user info
    getUserInfo();
    
    initNavigation();
    initTimeFilters();
    loadTemplates();
    
    // Set default dates for measurement filters
    const today = new Date();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 30);
    
    measurementStartDate.valueAsDate = thirtyDaysAgo;
    measurementEndDate.valueAsDate = today;
    
    // Initialize event listeners
    document.getElementById('apply-measurement-filter').addEventListener('click', loadMeasurements);
    dashboardTemplateSelect.addEventListener('change', loadDashboard);
    addMeasurementBtn.addEventListener('click', showAddMeasurementModal);
    addTemplateBtn.addEventListener('click', showAddTemplateModal);
    saveTemplateBtn.addEventListener('click', saveTemplate);
    saveMeasurementBtn.addEventListener('click', saveMeasurement);
    addValueBtn.addEventListener('click', addValueDefinition);
    document.getElementById('logout-btn').addEventListener('click', logout);
    
    // Event delegation for dynamic elements
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove-value-btn')) {
            removeValueDefinition(e.target);
        }
    });
    
    measurementTemplateSelect.addEventListener('change', populateMeasurementForm);
});

// Navigation system
function initNavigation() {
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetPage = link.getAttribute('data-page');
            
            // Update active nav link
            navLinks.forEach(navLink => navLink.classList.remove('active'));
            link.classList.add('active');
            
            // Show target page
            pages.forEach(page => page.classList.remove('active'));
            document.getElementById(`${targetPage}-page`).classList.add('active');
            
            // Load page-specific data
            if (targetPage === 'dashboard') {
                loadDashboard();
            } else if (targetPage === 'measurements') {
                loadMeasurements();
            } else if (targetPage === 'templates') {
                refreshTemplatesView();
            }
        });
    });
}

// Time filter handling
function initTimeFilters() {
    timeFilters.forEach(filter => {
        filter.addEventListener('click', () => {
            timeFilters.forEach(btn => btn.classList.remove('active'));
            filter.classList.add('active');
            loadDashboard();
        });
    });
}

// API Functions
async function fetchAPI(endpoint, options = {}) {
    // Check if user is authenticated
    const token = localStorage.getItem('access_token');
    if (!token && !endpoint.includes('/token')) {
        // Redirect to login if not authenticated
        window.location.href = '/login.html';
        return null;
    }
    
    try {
        // Add authorization header if token exists
        if (token) {
            if (!options.headers) {
                options.headers = {};
            }
            options.headers['Authorization'] = `Bearer ${token}`;
        }
        
        const response = await fetch(`${API_URL}${endpoint}`, options);
        
        // Handle authentication errors
        if (response.status === 401) {
            // Clear token and redirect to login
            localStorage.removeItem('access_token');
            window.location.href = '/login.html';
            return null;
        }
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        alert(`Error: ${error.message}`);
        return null;
    }
}

// Template Functions
async function loadTemplates() {
    templates = await fetchAPI('/templates');
    if (!templates) return;
    
    populateTemplateSelects();
}

function populateTemplateSelects() {
    // Clear existing options except the first one
    dashboardTemplateSelect.innerHTML = '<option value="">Select a measurement template</option>';
    measurementTemplateFilter.innerHTML = '<option value="">All Templates</option>';
    measurementTemplateSelect.innerHTML = '<option value="">Select Template</option>';
    
    // Add template options
    templates.forEach(template => {
        const option = document.createElement('option');
        option.value = template.id;
        option.textContent = template.name;
        
        dashboardTemplateSelect.appendChild(option.cloneNode(true));
        measurementTemplateFilter.appendChild(option.cloneNode(true));
        measurementTemplateSelect.appendChild(option.cloneNode(true));
    });
}

function refreshTemplatesView() {
    const templatesContainer = document.getElementById('templates-container');
    templatesContainer.innerHTML = '';
    
    if (!templates || templates.length === 0) {
        templatesContainer.innerHTML = `
            <div class="col-12">
                <div class="alert alert-info">
                    No measurement templates found. Create your first template to get started!
                </div>
            </div>
        `;
        return;
    }
    
    templates.forEach(template => {
        const templateCard = document.createElement('div');
        templateCard.className = 'col-md-4 mb-4';
        templateCard.innerHTML = `
            <div class="card template-card h-100">
                <div class="card-body">
                    <h5 class="card-title">${template.name}</h5>
                    <p class="card-text text-muted">${template.description || 'No description'}</p>
                    <h6 class="mt-3">Values:</h6>
                    <ul class="list-group list-group-flush">
                        ${template.value_definitions.map(val => `
                            <li class="list-group-item">
                                <strong>${val.display_name}</strong> 
                                <span class="badge bg-primary">${val.unit.display_name}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
                <div class="card-footer bg-transparent">
                    <button class="btn btn-sm btn-outline-primary edit-template-btn" data-id="${template.id}">
                        <i class="bi bi-pencil"></i> Edit
                    </button>
                </div>
            </div>
        `;
        templatesContainer.appendChild(templateCard);
    });
}

function showAddTemplateModal() {
    // Reset form
    document.getElementById('add-template-form').reset();
    
    // Clear existing value definitions except the first one
    const valueDefinitions = valueDefinitionsContainer.querySelectorAll('.value-definition');
    for (let i = 1; i < valueDefinitions.length; i++) {
        valueDefinitions[i].remove();
    }
    
    // Reset the first value definition
    const firstValueDef = valueDefinitionsContainer.querySelector('.value-definition');
    if (firstValueDef) {
        firstValueDef.querySelector('.value-name').value = '';
        firstValueDef.querySelector('.value-display-name').value = '';
        firstValueDef.querySelector('.unit-name').value = '';
        firstValueDef.querySelector('.unit-display-name').value = '';
        firstValueDef.querySelector('.unit-description').value = '';
        firstValueDef.querySelector('.value-min').value = '';
        firstValueDef.querySelector('.value-max').value = '';
    }
    
    addTemplateModal.show();
}

function addValueDefinition() {
    const valueDefTemplate = valueDefinitionsContainer.querySelector('.value-definition').cloneNode(true);
    
    // Clear form values
    valueDefTemplate.querySelectorAll('input').forEach(input => input.value = '');
    
    valueDefinitionsContainer.appendChild(valueDefTemplate);
}

function removeValueDefinition(button) {
    const valueDefCount = valueDefinitionsContainer.querySelectorAll('.value-definition').length;
    
    // Don't remove if it's the last value definition
    if (valueDefCount <= 1) return;
    
    const card = button.closest('.value-definition');
    card.remove();
}

async function saveTemplate() {
    // Validate form
    const form = document.getElementById('add-template-form');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    // Get form values
    const name = document.getElementById('template-name').value;
    const description = document.getElementById('template-description').value;
    
    // Build value definitions array
    const valueDefinitions = [];
    const valueDefElements = valueDefinitionsContainer.querySelectorAll('.value-definition');
    
    valueDefElements.forEach(valueDefElement => {
        const valueName = valueDefElement.querySelector('.value-name').value;
        const valueDisplayName = valueDefElement.querySelector('.value-display-name').value;
        const unitName = valueDefElement.querySelector('.unit-name').value;
        const unitDisplayName = valueDefElement.querySelector('.unit-display-name').value;
        const unitDescription = valueDefElement.querySelector('.unit-description').value;
        const valueMin = valueDefElement.querySelector('.value-min').value;
        const valueMax = valueDefElement.querySelector('.value-max').value;
        
        valueDefinitions.push({
            name: valueName,
            display_name: valueDisplayName,
            unit: {
                name: unitName,
                display_name: unitDisplayName,
                description: unitDescription || null
            },
            min_value: valueMin ? parseFloat(valueMin) : null,
            max_value: valueMax ? parseFloat(valueMax) : null
        });
    });
    
    // Build template object
    const template = {
        id: crypto.randomUUID(),
        name,
        description,
        value_definitions: valueDefinitions,
        created_at: new Date().toISOString(),
        is_active: true
    };
    
    // Save template
    const result = await fetchAPI('/templates', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(template)
    });
    
    if (result) {
        // Refresh templates
        await loadTemplates();
        refreshTemplatesView();
        addTemplateModal.hide();
    }
}

// Measurement Functions
async function loadMeasurements() {
    const templateId = measurementTemplateFilter.value;
    const startDate = measurementStartDate.value;
    const endDate = measurementEndDate.value;
    
    let url = '/measurements';
    const params = new URLSearchParams();
    
    if (templateId) params.append('template_id', templateId);
    if (startDate) params.append('start_date', new Date(startDate).toISOString());
    if (endDate) {
        // Set end date to end of day
        const endDateTime = new Date(endDate);
        endDateTime.setHours(23, 59, 59, 999);
        params.append('end_date', endDateTime.toISOString());
    }
    
    if (params.toString()) {
        url += `?${params.toString()}`;
    }
    
    measurements = await fetchAPI(url);
    if (!measurements) return;
    
    displayMeasurements();
}

function displayMeasurements() {
    const tableBody = document.querySelector('#measurements-table tbody');
    tableBody.innerHTML = '';
    
    if (!measurements || measurements.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="4" class="text-center">No measurements found</td>
            </tr>
        `;
        return;
    }
    
    measurements.forEach(measurement => {
        const template = templates.find(t => t.id === measurement.template_id) || { name: 'Unknown Template' };
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${new Date(measurement.measured_at).toLocaleString()}</td>
            <td>${template.name}</td>
            <td>
                <ul class="measurement-values-display">
                    ${measurement.values.map(value => {
                        const valueDefinition = template.value_definitions?.find(vd => vd.name === value.definition_name);
                        const unitDisplay = valueDefinition ? valueDefinition.unit.display_name : '';
                        return `<li><strong>${valueDefinition?.display_name || value.definition_name}:</strong> ${value.value} ${unitDisplay}</li>`;
                    }).join('')}
                </ul>
            </td>
            <td>
                <button class="btn btn-sm btn-outline-primary view-measurement-btn" data-id="${measurement.id}">
                    <i class="bi bi-eye"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger delete-measurement-btn" data-id="${measurement.id}">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;
        tableBody.appendChild(tr);
    });
}

function showAddMeasurementModal() {
    // Reset form
    document.getElementById('add-measurement-form').reset();
    measurementValuesContainer.innerHTML = '';
    
    // Set default date to now
    const now = new Date();
    const localDatetime = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
        .toISOString()
        .slice(0, 16);
    document.getElementById('measurement-date').value = localDatetime;
    
    addMeasurementModal.show();
}

function populateMeasurementForm() {
    const templateId = measurementTemplateSelect.value;
    if (!templateId) {
        measurementValuesContainer.innerHTML = '';
        return;
    }
    
    const template = templates.find(t => t.id === templateId);
    if (!template) return;
    
    measurementValuesContainer.innerHTML = '';
    
    template.value_definitions.forEach(valueDef => {
        const valueField = document.createElement('div');
        valueField.className = 'mb-3';
        valueField.innerHTML = `
            <label class="form-label">${valueDef.display_name} (${valueDef.unit.display_name})</label>
            <input type="number" 
                class="form-control measurement-value" 
                data-name="${valueDef.name}" 
                step="any" 
                ${valueDef.min_value !== null ? `min="${valueDef.min_value}"` : ''} 
                ${valueDef.max_value !== null ? `max="${valueDef.max_value}"` : ''} 
                required>
        `;
        measurementValuesContainer.appendChild(valueField);
    });
}

async function saveMeasurement() {
    // Validate form
    const form = document.getElementById('add-measurement-form');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    // Get template ID
    const templateId = measurementTemplateSelect.value;
    const template = templates.find(t => t.id === templateId);
    if (!template) return;
    
    // Get other form values
    const measuredAt = new Date(document.getElementById('measurement-date').value).toISOString();
    const notes = document.getElementById('measurement-notes').value;
    
    // Get values
    const values = [];
    const valueInputs = measurementValuesContainer.querySelectorAll('.measurement-value');
    valueInputs.forEach(input => {
        values.push({
            definition_name: input.getAttribute('data-name'),
            value: parseFloat(input.value)
        });
    });
    
    // Build measurement object
    const measurement = {
        id: crypto.randomUUID(),
        template_id: templateId,
        values,
        measured_at: measuredAt,
        recorded_at: new Date().toISOString(),
        notes,
        user_id: 'user-1' // In a real app, this would be the logged-in user's ID
    };
    
    // Save measurement
    const result = await fetchAPI('/measurements', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(measurement)
    });
    
    if (result) {
        // Refresh measurements
        await loadMeasurements();
        addMeasurementModal.hide();
    }
}

// Dashboard Functions
async function loadDashboard() {
    const templateId = dashboardTemplateSelect.value;
    if (!templateId) {
        document.getElementById('chart-container').innerHTML = '';
        document.getElementById('stats-container').innerHTML = '';
        return;
    }
    
    const template = templates.find(t => t.id === templateId);
    if (!template) return;
    
    // Get active time filter
    const activeTimeFilter = document.querySelector('.time-filter.active');
    const days = activeTimeFilter ? parseInt(activeTimeFilter.getAttribute('data-days')) : 30;
    
    // Calculate date range
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(endDate.getDate() - days);
    
    // Get statistics
    const statsUrl = `/statistics/${templateId}?start_date=${startDate.toISOString()}&end_date=${endDate.toISOString()}`;
    const statistics = await fetchAPI(statsUrl);
    if (!statistics) return;
    
    // Get measurements for charts
    const measurementsUrl = `/measurements?template_id=${templateId}&start_date=${startDate.toISOString()}&end_date=${endDate.toISOString()}`;
    const chartData = await fetchAPI(measurementsUrl);
    if (!chartData) return;
    
    // Display statistics and charts
    displayStatistics(statistics, template);
    displayCharts(chartData, template);
}

function displayStatistics(statistics, template) {
    const statsContainer = document.getElementById('stats-container');
    statsContainer.innerHTML = '<h3 class="col-12 mb-3">Statistics</h3>';
    
    const row = document.createElement('div');
    row.className = 'row';
    
    template.value_definitions.forEach(valueDef => {
        const stats = statistics[valueDef.name];
        if (!stats || stats.count === 0) return;
        
        const statCard = document.createElement('div');
        statCard.className = 'col-md-3 col-sm-6 mb-3';
        statCard.innerHTML = `
            <div class="card stat-card">
                <div class="card-body">
                    <h5 class="card-title">${valueDef.display_name}</h5>
                    <div class="row">
                        <div class="col-6">
                            <div class="stat-label">Average</div>
                            <div class="stat-value">${stats.avg.toFixed(1)} ${stats.unit}</div>
                        </div>
                        <div class="col-6">
                            <div class="stat-label">Range</div>
                            <div class="stat-value">${stats.min} - ${stats.max}</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        row.appendChild(statCard);
    });
    
    statsContainer.appendChild(row);
}

function displayCharts(measurements, template) {
    const chartContainer = document.getElementById('chart-container');
    chartContainer.innerHTML = '<h3 class="col-12 mb-3">Charts</h3>';
    
    // Destroy existing charts
    Object.values(charts).forEach(chart => chart.destroy());
    charts = {};
    
    // Sort measurements by date
    measurements.sort((a, b) => new Date(a.measured_at) - new Date(b.measured_at));
    
    // Prepare data for each value definition
    template.value_definitions.forEach(valueDef => {
        const chartDiv = document.createElement('div');
        chartDiv.className = 'col-md-6 mb-4';
        chartDiv.innerHTML = `
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">${valueDef.display_name} (${valueDef.unit.display_name})</h5>
                    <div class="chart-container">
                        <canvas id="chart-${valueDef.name}"></canvas>
                    </div>
                </div>
            </div>
        `;
        chartContainer.appendChild(chartDiv);
        
        // Extract data for this value
        const dates = [];
        const values = [];
        
        measurements.forEach(measurement => {
            const value = measurement.values.find(v => v.definition_name === valueDef.name);
            if (value) {
                dates.push(new Date(measurement.measured_at).toLocaleDateString());
                values.push(value.value);
            }
        });
        
        // Create chart
        const ctx = document.getElementById(`chart-${valueDef.name}`).getContext('2d');
        charts[valueDef.name] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: `${valueDef.display_name} (${valueDef.unit.display_name})`,
                    data: values,
                    borderColor: 'rgba(13, 110, 253, 1)',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    borderWidth: 2,
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false
                    }
                }
            }
        });
    });
}