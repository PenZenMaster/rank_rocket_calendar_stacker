/*
Module/Script Name: src/app.js

Description:
Frontend JavaScript for Rank Rocket Calendar Stacker. Handles dashboard, clients, OAuth (Settings) UI/API interactions, including full Add OAuth Credentials flow and Event CRUD wiring.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
14-07-2025

Last Modified Date:
18-07-2025

Version:
v1.15

Comments:
- Added event CRUD: loadCalendars, loadEvents, showEventModal, saveEvent, deleteEvent
- Wired client and calendar selects to API JSON endpoints.
*/

// Global variables
let currentClients = [];
let currentEvents = [];
let currentCalendars = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
    loadClients();
    loadOAuthCredentials();
});

// Navigation functions
function showSection(sectionName, event) {
    document.querySelectorAll('.section').forEach(sec => sec.style.display = 'none');
    document.getElementById(sectionName).style.display = 'block';
    document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
    if (event) event.target.classList.add('active');

    switch (sectionName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'clients':
            loadClients();
            break;
        case 'events':
            loadClients();
            loadCalendars();
            loadEvents();
            break;
        case 'oauth':
            loadClientsForOAuth();
            loadOAuthCredentials();
            break;
    }
}

// Utility functions
function showAlert(message, type = 'info', containerId = 'globalAlerts') {
    const html = `<div class="alert alert-${type} alert-dismissible fade show" role="alert">${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>`;
    document.getElementById(containerId).innerHTML = html;
    setTimeout(() => { const a = document.querySelector(`#${containerId} .alert`); if (a) a.remove(); }, 5000);
}

function showLoading(show = true) {
    document.querySelectorAll('.loading').forEach(el => el.style.display = show ? 'block' : 'none');
}

async function apiCall(url, options = {}) {
    try {
        showLoading(true);
        const response = await fetch(url, { headers: { 'Content-Type': 'application/json', ...options.headers }, ...options });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || `HTTP error ${response.status}`);
        return data;
    } catch (error) {
        console.error('API call failed:', error);
        showAlert(`Error: ${error.message}`, 'danger');
        throw error;
    } finally {
        showLoading(false);
    }
}

// Dashboard
async function loadDashboard() {
    try {
        const resp = await apiCall('/api/clients');
        const clients = Array.isArray(resp.data) ? resp.data : [];
        document.getElementById('totalClients').textContent = clients.length;
    } catch (error) {
        console.error('Failed to load dashboard:', error);
    }
}

// Clients list
async function loadClients() {
    try {
        const resp = await apiCall('/api/clients');
        currentClients = Array.isArray(resp.data) ? resp.data : [];
        const tbody = document.getElementById('clientsTableBody');
        tbody.innerHTML = '';
        currentClients.forEach(client => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${client.name}</td>
                <td>${client.email}</td>
                <td>${client.google_account_email || ''}</td>
                <td>
                    <button class="btn btn-sm btn-info" onclick="showOAuthModal()">OAuth</button>
                    <button class="btn btn-sm btn-warning" onclick="showEditClientModal(${client.id})">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteClient(${client.id})">Delete</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Failed to load clients:', error);
    }
}

// OAuth Settings: Add & List
async function loadClientsForOAuth() {
    try {
        const resp = await apiCall('/api/clients');
        const select = document.getElementById('oauthClientSelect');
        select.innerHTML = '<option value="">Select a client.</option>';
        (Array.isArray(resp.data) ? resp.data : []).forEach(client => {
            const opt = document.createElement('option');
            opt.value = client.id;
            opt.textContent = `${client.name} (${client.email})`;
            select.appendChild(opt);
        });
    } catch (error) {
        console.error('Error loading clients for OAuth:', error);
    }
}

function showOAuthModal(oauthId = null) {
    const modal = new bootstrap.Modal(document.getElementById('oauthModal'));
    const title = document.getElementById('oauthModalTitle');
    document.getElementById('oauthForm').reset();
    document.getElementById('oauthId').value = oauthId || '';
    title.textContent = oauthId ? 'Edit OAuth Credentials' : 'Add OAuth Credentials';
    loadClientsForOAuth();
    modal.show();
}

async function saveOAuthCredentials() {
    const id = document.getElementById('oauthId').value;
    const clientId = document.getElementById('oauthClientSelect').value;
    const googleId = document.getElementById('googleClientId').value;
    const googleSecret = document.getElementById('googleClientSecret').value;
    const scopes = document.getElementById('oauthScopes').value.split("\n");

    if (!clientId || !googleId || !googleSecret) {
        showAlert('Please fill in all required fields', 'danger');
        return;
    }

    const payload = { client_id: clientId, google_client_id: googleId, google_client_secret: googleSecret, scopes };
    try {
        const method = id ? 'PUT' : 'POST';
        const endpoint = id ? `/api/oauth/${id}` : '/api/oauth';
        const resp = await apiCall(endpoint, { method, body: JSON.stringify(payload) });
        showAlert(resp.message || 'Credentials saved', 'success');
        bootstrap.Modal.getInstance(document.getElementById('oauthModal')).hide();
        loadOAuthCredentials();
    } catch (error) {
        console.error('Failed to save OAuth credentials:', error);
    }
}

async function loadOAuthCredentials() {
    try {
        const resp = await apiCall('/api/oauth');
        const tbody = document.getElementById('oauthTableBody');
        tbody.innerHTML = '';
        (Array.isArray(resp.data) ? resp.data : []).forEach(cred => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${cred.client_name}</td>
                <td>${cred.google_client_id}</td>
                <td>${cred.token_status}</td>
                <td>${new Date(cred.expires_at).toLocaleString()}</td>
                <td><button class="btn btn-sm btn-primary" onclick="showOAuthModal(${cred.id})">Edit</button></td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Failed to load OAuth credentials:', error);
    }
}

// Events CRUD
async function loadCalendars() {
    const clientId = document.getElementById('clientSelect').value;
    const calSelect = document.getElementById('calendarSelect');
    calSelect.innerHTML = '<option value="">Select a calendar.</option>';
    if (!clientId) return;
    try {
        const resp = await apiCall(`/api/clients/${clientId}/calendars`);
        currentCalendars = Array.isArray(resp.data) ? resp.data : [];
        currentCalendars.forEach(cal => {
            const opt = document.createElement('option');
            opt.value = cal.id;
            opt.textContent = cal.summary;
            calSelect.appendChild(opt);
        });
    } catch (error) {
        console.error('Failed to load calendars:', error);
    }
}

async function loadEvents() {
    const clientId = document.getElementById('clientSelect').value;
    const calendarId = document.getElementById('calendarSelect').value;
    const container = document.getElementById('eventsContainer');
    container.innerHTML = '';
    if (!clientId || !calendarId) {
        container.innerHTML = '<p class="text-muted">Select a client and calendar to view events.</p>';
        return;
    }
    try {
        const resp = await apiCall(`/api/clients/${clientId}/calendars/${calendarId}/events`);
        currentEvents = Array.isArray(resp.data) ? resp.data : [];
        if (currentEvents.length === 0) {
            container.innerHTML = '<p class="text-muted">No events found.</p>';
            return;
        }
        let html = '<table class="table table-striped"><thead><tr><th>Summary</th><th>Start</th><th>End</th><th>Actions</th></tr></thead><tbody>';
        currentEvents.forEach(evt => {
            const start = evt.start.dateTime || evt.start.date;
            const end = evt.end.dateTime || evt.end.date;
            html += `<tr>
                <td>${evt.summary}</td>
                <td>${new Date(start).toLocaleString()}</td>
                <td>${new Date(end).toLocaleString()}</td>
                <td>
                    <button class="btn btn-sm btn-primary me-1" onclick="showEventModal('${evt.id}')">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteEvent('${evt.id}')">Delete</button>
                </td>
            </tr>`;
        });
        html += '</tbody></table>';
        container.innerHTML = html;
    } catch (error) {
        console.error('Failed to load events:', error);
    }
}

function showEventModal(eventId = null) {
    const modalEl = document.getElementById('eventModal');
    const modal = new bootstrap.Modal(modalEl);
    const title = document.getElementById('eventModalTitle');
    document.getElementById('eventForm').reset();
    document.getElementById('eventId').value = eventId || '';
    if (eventId) {
        title.textContent = 'Edit Event';
        const clientId = document.getElementById('clientSelect').value;
        const calendarId = document.getElementById('calendarSelect').value;
        apiCall(`/api/clients/${clientId}/calendars/${calendarId}/events/${eventId}`)
            .then(resp => {
                const evt = resp.data;
                document.getElementById('eventSummary').value = evt.summary || '';
                document.getElementById('eventStart').value = evt.start.dateTime || evt.start.date;
                document.getElementById('eventEnd').value = evt.end.dateTime || evt.end.date;
            })
            .catch(err => console.error('Failed to load event for editing:', err));
    } else {
        title.textContent = 'Add Event';
    }
    modal.show();
}

async function saveEvent() {
    const id = document.getElementById('eventId').value;
    const clientId = document.getElementById('clientSelect').value;
    const calendarId = document.getElementById('calendarSelect').value;
    const summary = document.getElementById('eventSummary').value;
    const start = document.getElementById('eventStart').value;
    const end = document.getElementById('eventEnd').value;
    if (!clientId || !calendarId || !summary || !start || !end) {
        showAlert('Please fill in all required fields for the event.', 'danger');
        return;
    }
    const payload = { summary, start: { dateTime: start }, end: { dateTime: end } };
    try {
        const method = id ? 'PUT' : 'POST';
        const endpoint = id
            ? `/api/clients/${clientId}/calendars/${calendarId}/events/${id}`
            : `/api/clients/${clientId}/calendars/${calendarId}/events`;
        const resp = await apiCall(endpoint, { method, body: JSON.stringify(payload) });
        showAlert(resp.message || 'Event saved', 'success');
        bootstrap.Modal.getInstance(document.getElementById('eventModal')).hide();
        loadEvents();
    } catch (error) {
        console.error('Failed to save event:', error);
    }
}

async function deleteEvent(eventId) {
    if (!confirm('Are you sure you want to delete this event?')) return;
    const clientId = document.getElementById('clientSelect').value;
    const calendarId = document.getElementById('calendarSelect').value;
    try {
        const resp = await apiCall(`/api/clients/${clientId}/calendars/${calendarId}/events/${eventId}`, { method: 'DELETE' });
        showAlert(resp.message || 'Event deleted', 'warning');
        loadEvents();
    } catch (error) {
        console.error('Failed to delete event:', error);
    }
}

// The rest of client & settings code remains unchanged.
