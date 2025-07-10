// Global variables
let currentClients = [];
let currentSection = 'dashboard';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
    loadClients();
});

// Navigation functions
function showSection(sectionName) {
    // Hide all sections
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.style.display = 'none';
    });
    
    // Show selected section
    document.getElementById(sectionName).style.display = 'block';
    
    // Update navigation
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.classList.remove('active');
    });
    event.target.classList.add('active');
    
    currentSection = sectionName;
    
    // Load section-specific data
    switch(sectionName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'clients':
            loadClients();
            break;
        case 'events':
            loadClientsForEventSection();
            break;
    }
}

// Utility functions
function showAlert(message, type = 'info', containerId = 'globalAlerts') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    document.getElementById(containerId).innerHTML = alertHtml;
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = document.querySelector(`#${containerId} .alert`);
        if (alert) {
            alert.remove();
        }
    }, 5000);
}

function showLoading(show = true) {
    const loadingElements = document.querySelectorAll('.loading');
    loadingElements.forEach(element => {
        element.style.display = show ? 'block' : 'none';
    });
}

// API functions
async function apiCall(url, options = {}) {
    try {
        showLoading(true);
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API call failed:', error);
        showAlert(`Error: ${error.message}`, 'danger');
        throw error;
    } finally {
        showLoading(false);
    }
}

// Dashboard functions
async function loadDashboard() {
    try {
        // Load clients count
        const clientsResponse = await apiCall('/api/clients');
        const totalClients = clientsResponse.data ? clientsResponse.data.length : 0;
        document.getElementById('totalClients').textContent = totalClients;
        
        // TODO: Load other dashboard metrics
        document.getElementById('activeEvents').textContent = '-';
        document.getElementById('oauthStatus').textContent = '-';
        
    } catch (error) {
        console.error('Failed to load dashboard:', error);
    }
}

// Client management functions
async function loadClients() {
    try {
        const response = await apiCall('/api/clients');
        currentClients = response.data || [];
        renderClientsTable();
    } catch (error) {
        console.error('Failed to load clients:', error);
        document.getElementById('clientsTableBody').innerHTML = 
            '<tr><td colspan="5" class="text-center text-danger">Failed to load clients</td></tr>';
    }
}

function renderClientsTable() {
    const tbody = document.getElementById('clientsTableBody');
    
    if (currentClients.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No clients found</td></tr>';
        return;
    }
    
    tbody.innerHTML = currentClients.map(client => `
        <tr>
            <td>${escapeHtml(client.name)}</td>
            <td>${escapeHtml(client.email)}</td>
            <td>${escapeHtml(client.google_account_email)}</td>
            <td>
                <span class="badge ${client.is_active ? 'bg-success' : 'bg-secondary'} status-badge">
                    ${client.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="editClient('${client.id}')">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteClient('${client.id}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

function showClientModal(clientId = null) {
    const modal = new bootstrap.Modal(document.getElementById('clientModal'));
    const form = document.getElementById('clientForm');
    const title = document.getElementById('clientModalTitle');
    
    // Reset form
    form.reset();
    document.getElementById('clientId').value = '';
    
    if (clientId) {
        // Edit mode
        const client = currentClients.find(c => c.id === clientId);
        if (client) {
            title.textContent = 'Edit Client';
            document.getElementById('clientId').value = client.id;
            document.getElementById('clientName').value = client.name;
            document.getElementById('clientEmail').value = client.email;
            document.getElementById('googleAccountEmail').value = client.google_account_email;
        }
    } else {
        // Add mode
        title.textContent = 'Add Client';
    }
    
    modal.show();
}

function editClient(clientId) {
    showClientModal(clientId);
}

async function saveClient() {
    const form = document.getElementById('clientForm');
    const clientId = document.getElementById('clientId').value;
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const clientData = {
        name: document.getElementById('clientName').value,
        email: document.getElementById('clientEmail').value,
        google_account_email: document.getElementById('googleAccountEmail').value
    };
    
    try {
        let response;
        if (clientId) {
            // Update existing client
            response = await apiCall(`/api/clients/${clientId}`, {
                method: 'PUT',
                body: JSON.stringify(clientData)
            });
        } else {
            // Create new client
            response = await apiCall('/api/clients', {
                method: 'POST',
                body: JSON.stringify(clientData)
            });
        }
        
        showAlert(response.message || 'Client saved successfully', 'success');
        
        // Close modal and reload clients
        const modal = bootstrap.Modal.getInstance(document.getElementById('clientModal'));
        modal.hide();
        loadClients();
        
    } catch (error) {
        console.error('Failed to save client:', error);
    }
}

async function deleteClient(clientId) {
    const client = currentClients.find(c => c.id === clientId);
    if (!client) return;
    
    if (!confirm(`Are you sure you want to delete client "${client.name}"?`)) {
        return;
    }
    
    try {
        const response = await apiCall(`/api/clients/${clientId}`, {
            method: 'DELETE'
        });
        
        showAlert(response.message || 'Client deleted successfully', 'success');
        loadClients();
        
    } catch (error) {
        console.error('Failed to delete client:', error);
    }
}

// Event management functions
async function loadClientsForEventSection() {
    try {
        const response = await apiCall('/api/clients');
        const clients = response.data || [];
        
        const clientSelect = document.getElementById('clientSelect');
        clientSelect.innerHTML = '<option value="">Select a client...</option>';
        
        clients.forEach(client => {
            const option = document.createElement('option');
            option.value = client.id;
            option.textContent = client.name;
            clientSelect.appendChild(option);
        });
        
    } catch (error) {
        console.error('Failed to load clients for events:', error);
    }
}

async function loadCalendars() {
    const clientId = document.getElementById('clientSelect').value;
    const calendarSelect = document.getElementById('calendarSelect');
    
    calendarSelect.innerHTML = '<option value="">Select a calendar...</option>';
    
    if (!clientId) {
        return;
    }
    
    try {
        // TODO: Implement calendar loading via API
        // This would require the Google Calendar service integration
        console.log('Loading calendars for client:', clientId);
        
    } catch (error) {
        console.error('Failed to load calendars:', error);
    }
}

async function loadEvents() {
    const clientId = document.getElementById('clientSelect').value;
    const calendarId = document.getElementById('calendarSelect').value;
    const container = document.getElementById('eventsContainer');
    
    if (!clientId || !calendarId) {
        container.innerHTML = '<p class="text-muted">Select a client and calendar to view events.</p>';
        return;
    }
    
    try {
        // TODO: Implement event loading via API
        container.innerHTML = '<p class="text-muted">Loading events...</p>';
        console.log('Loading events for client:', clientId, 'calendar:', calendarId);
        
    } catch (error) {
        console.error('Failed to load events:', error);
        container.innerHTML = '<p class="text-danger">Failed to load events.</p>';
    }
}

function showEventModal() {
    // TODO: Implement event modal
    showAlert('Event creation will be implemented in the next phase', 'info');
}

// Utility functions
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}


// OAuth Credentials Management
function showOAuthModal(oauthId = null) {
    const modal = new bootstrap.Modal(document.getElementById('oauthModal'));
    const modalTitle = document.getElementById('oauthModalTitle');
    const form = document.getElementById('oauthForm');
    
    // Reset form
    form.reset();
    document.getElementById('oauthId').value = '';
    
    // Load clients for the dropdown
    loadClientsForOAuth();
    
    if (oauthId) {
        modalTitle.textContent = 'Edit OAuth Credentials';
        loadOAuthCredential(oauthId);
    } else {
        modalTitle.textContent = 'Add OAuth Credentials';
        // Set default scopes
        document.getElementById('oauthScopes').value = 'https://www.googleapis.com/auth/calendar\nhttps://www.googleapis.com/auth/calendar.events';
    }
    
    modal.show();
}

function loadClientsForOAuth() {
    fetch('/api/clients')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('oauthClientSelect');
            select.innerHTML = '<option value="">Select a client...</option>';
            
            if (data.success && data.data) {
                data.data.forEach(client => {
                    const option = document.createElement('option');
                    option.value = client.id;
                    option.textContent = `${client.name} (${client.email})`;
                    select.appendChild(option);
                });
            }
        })
        .catch(error => {
            console.error('Error loading clients:', error);
            showAlert('Error loading clients', 'danger');
        });
}

function loadOAuthCredential(oauthId) {
    // This would load existing OAuth credential data for editing
    // For now, we'll implement the basic structure
    document.getElementById('oauthId').value = oauthId;
}

function saveOAuthCredentials() {
    const form = document.getElementById('oauthForm');
    const formData = new FormData(form);
    
    const oauthData = {
        client_id: document.getElementById('oauthClientSelect').value,
        google_client_id: document.getElementById('googleClientId').value,
        google_client_secret: document.getElementById('googleClientSecret').value,
        scopes: document.getElementById('oauthScopes').value.replace(/\n/g, ',')
    };
    
    // Validate required fields
    if (!oauthData.client_id || !oauthData.google_client_id || !oauthData.google_client_secret) {
        showAlert('Please fill in all required fields', 'danger');
        return;
    }
    
    const oauthId = document.getElementById('oauthId').value;
    const url = oauthId ? `/api/oauth/${oauthId}` : '/api/oauth';
    const method = oauthId ? 'PUT' : 'POST';
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(oauthData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(data.message || 'OAuth credentials saved successfully', 'success');
            bootstrap.Modal.getInstance(document.getElementById('oauthModal')).hide();
            loadOAuthCredentials();
        } else {
            showAlert(data.error || 'Error saving OAuth credentials', 'danger');
        }
    })
    .catch(error => {
        console.error('Error saving OAuth credentials:', error);
        showAlert('Error saving OAuth credentials', 'danger');
    });
}

function loadOAuthCredentials() {
    fetch('/api/oauth')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('oauthTableBody');
            tbody.innerHTML = '';
            
            if (data.success && data.data && data.data.length > 0) {
                data.data.forEach(oauth => {
                    const row = document.createElement('tr');
                    
                    // Get client name (we'll need to fetch this or include it in the response)
                    const clientName = oauth.client_name || 'Unknown Client';
                    
                    // Format token status
                    let tokenStatus = 'No Token';
                    let statusClass = 'secondary';
                    if (oauth.access_token) {
                        if (oauth.token_expires_at) {
                            const expiresAt = new Date(oauth.token_expires_at);
                            const now = new Date();
                            if (expiresAt > now) {
                                tokenStatus = 'Valid';
                                statusClass = 'success';
                            } else {
                                tokenStatus = 'Expired';
                                statusClass = 'warning';
                            }
                        } else {
                            tokenStatus = 'Valid';
                            statusClass = 'success';
                        }
                    }
                    
                    // Format expiration date
                    const expiresAt = oauth.token_expires_at ? 
                        new Date(oauth.token_expires_at).toLocaleString() : 
                        'N/A';
                    
                    row.innerHTML = `
                        <td>${clientName}</td>
                        <td>${oauth.google_client_id}</td>
                        <td><span class="badge bg-${statusClass}">${tokenStatus}</span></td>
                        <td>${expiresAt}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary me-1" onclick="authorizeOAuth('${oauth.id}')" title="Authorize">
                                <i class="fas fa-key"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-secondary me-1" onclick="showOAuthModal('${oauth.id}')" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteOAuthCredentials('${oauth.id}')" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No OAuth credentials found</td></tr>';
            }
        })
        .catch(error => {
            console.error('Error loading OAuth credentials:', error);
            showAlert('Error loading OAuth credentials', 'danger');
        });
}

function authorizeOAuth(oauthId) {
    fetch(`/api/oauth/${oauthId}/authorize`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Open the authorization URL in a new window
            window.open(data.data.authorization_url, 'oauth_window', 'width=600,height=600');
            showAlert('Authorization window opened. Please complete the OAuth flow.', 'info');
        } else {
            showAlert(data.error || 'Error initiating OAuth authorization', 'danger');
        }
    })
    .catch(error => {
        console.error('Error authorizing OAuth:', error);
        showAlert('Error initiating OAuth authorization', 'danger');
    });
}

function deleteOAuthCredentials(oauthId) {
    if (confirm('Are you sure you want to delete these OAuth credentials?')) {
        fetch(`/api/oauth/${oauthId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert(data.message || 'OAuth credentials deleted successfully', 'success');
                loadOAuthCredentials();
            } else {
                showAlert(data.error || 'Error deleting OAuth credentials', 'danger');
            }
        })
        .catch(error => {
            console.error('Error deleting OAuth credentials:', error);
            showAlert('Error deleting OAuth credentials', 'danger');
        });
    }
}

// Update the showSection function to load OAuth credentials when the oauth section is shown
const originalShowSection = showSection;
showSection = function(sectionName) {
    originalShowSection(sectionName);
    
    if (sectionName === 'oauth') {
        loadOAuthCredentials();
    }
};

