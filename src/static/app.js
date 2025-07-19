/*
Module/Script Name: static/app.js

Description:
Frontend JavaScript for Rank Rocket Calendar Stacker. Handles dashboard, clients, OAuth (Settings) UI/API interactions, including full Add/Edit/Delete Client flow and Event CRUD wiring.

Author(s):
Skippy the Code Slayer

Created Date:
19-07-2025

Last Modified Date:
29-07-2025

Version:
v1.18
*/

// Global variables
let currentClients = [];
let currentEvents = [];
let currentCalendars = [];

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
  loadDashboard();
  loadClients();
  loadOAuthCredentials();
});

// Navigation functions
function showSection(sectionName, event) {
  document
    .querySelectorAll(".section")
    .forEach((sec) => (sec.style.display = "none"));
  document.getElementById(sectionName).style.display = "block";
  document
    .querySelectorAll(".nav-link")
    .forEach((link) => link.classList.remove("active"));
  if (event) event.target.classList.add("active");

  switch (sectionName) {
    case "dashboard":
      loadDashboard();
      break;
    case "clients":
      loadClients();
      break;
    case "events":
      loadClients();
      loadCalendars();
      loadEvents();
      break;
    case "oauth":
      loadClientsForOAuth();
      loadOAuthCredentials();
      break;
  }
}

// Utility functions
function showAlert(message, type = "info", containerId = "globalAlerts") {
  const html = `<div class="alert alert-${type} alert-dismissible fade show" role="alert">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>`;
  document.getElementById(containerId).innerHTML = html;
  setTimeout(() => {
    const alertEl = document.querySelector(`#${containerId} .alert`);
    if (alertEl) alertEl.remove();
  }, 5000);
}

function showLoading(show = true) {
  document
    .querySelectorAll(".loading")
    .forEach((el) => (el.style.display = show ? "block" : "none"));
}

async function apiCall(url, options = {}) {
  try {
    showLoading(true);
    const response = await fetch(url, {
      headers: { "Content-Type": "application/json", ...options.headers },
      ...options,
    });
    const data = await response.json();
    if (!response.ok)
      throw new Error(
        data.error || data.message || `HTTP error ${response.status}`
      );
    return data;
  } catch (error) {
    console.error("API call failed:", error);
    showAlert(`Error: ${error.message}`, "danger");
    throw error;
  } finally {
    showLoading(false);
  }
}

// Dashboard
async function loadDashboard() {
  try {
    const clients = await apiCall("/api/clients");
    const list = Array.isArray(clients) ? clients : [];
    document.getElementById("totalClients").textContent = list.length;
  } catch (error) {
    console.error("Failed to load dashboard:", error);
  }
}

// Clients list & CRUD
async function loadClients() {
  try {
    const clients = await apiCall("/api/clients");
    currentClients = Array.isArray(clients) ? clients : [];
    const tbody = document.getElementById("clientsTableBody");
    tbody.innerHTML = "";
    currentClients.forEach((client) => {
      const row = document.createElement("tr");
      row.innerHTML = `
                <td>${client.name}</td>
                <td>${client.email}</td>
                <td>${client.google_account_email || ""}</td>
                <td>
                    <button class="btn btn-sm btn-warning me-1" onclick="showClientModal(${
                      client.id
                    })">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteClient(${
                      client.id
                    })">Delete</button>
                </td>
            `;
      tbody.appendChild(row);
    });
  } catch (error) {
    console.error("Failed to load clients:", error);
  }
}

function showClientModal(clientId = null) {
  const modalEl = document.getElementById("clientModal");
  const modal = new bootstrap.Modal(modalEl);
  const title = document.getElementById("clientModalTitle");
  document.getElementById("clientForm").reset();
  document.getElementById("clientId").value = clientId || "";
  title.textContent = clientId ? "Edit Client" : "Add Client";
  if (clientId) {
    apiCall(`/api/clients/${clientId}`)
      .then((client) => {
        document.getElementById("clientName").value = client.name;
        document.getElementById("clientEmail").value = client.email;
        document.getElementById("googleAccountEmail").value =
          client.google_account_email || "";
      })
      .catch((err) => console.error("Failed to load client data:", err));
  }
  modal.show();
}

async function saveClient() {
  const id = document.getElementById("clientId").value;
  const name = document.getElementById("clientName").value.trim();
  const email = document.getElementById("clientEmail").value.trim();
  const googleEmail = document
    .getElementById("googleAccountEmail")
    .value.trim();
  if (!name || !email || !googleEmail) {
    showAlert("Please fill in all required fields", "danger");
    return;
  }
  const payload = { name, email, google_account_email: googleEmail };
  const endpoint = id ? `/api/clients/${id}` : "/api/clients";
  const method = id ? "PUT" : "POST";
  try {
    await apiCall(endpoint, { method, body: JSON.stringify(payload) });
    showAlert(
      id ? "Client updated successfully" : "Client added successfully",
      "success"
    );
    bootstrap.Modal.getInstance(modalEl).hide();
    loadClients();
  } catch (error) {
    console.error("Failed to save client:", error);
  }
}

async function deleteClient(clientId) {
  if (!confirm("Are you sure you want to delete this client?")) return;
  try {
    await apiCall(`/api/clients/${clientId}`, { method: "DELETE" });
    showAlert("Client deleted", "warning");
    loadClients();
  } catch (error) {
    console.error("Failed to delete client:", error);
  }
}

// OAuth Settings: Add & List
async function loadClientsForOAuth() {
  try {
    const clients = await apiCall("/api/clients");
    const select = document.getElementById("oauthClientSelect");
    select.innerHTML = '<option value="">Select a client.</option>';
    currentClients = Array.isArray(clients) ? clients : [];
    currentClients.forEach((client) => {
      const opt = document.createElement("option");
      opt.value = client.id;
      opt.textContent = `${client.name} (${client.email})`;
      select.appendChild(opt);
    });
  } catch (error) {
    console.error("Error loading clients for OAuth:", error);
  }
}

function showOAuthModal(oauthId = null) {
  const modalEl = document.getElementById("oauthModal");
  const modal = new bootstrap.Modal(modalEl);
  const title = document.getElementById("oauthModalTitle");
  document.getElementById("oauthForm").reset();
  document.getElementById("oauthId").value = oauthId || "";
  title.textContent = oauthId
    ? "Edit OAuth Credentials"
    : "Add OAuth Credentials";
  loadClientsForOAuth();
  modal.show();
}

async function saveOAuthCredentials() {
  const id = document.getElementById("oauthId").value;
  const clientId = document.getElementById("oauthClientSelect").value;
  const googleId = document.getElementById("googleClientId").value.trim();
  const googleSecret = document
    .getElementById("googleClientSecret")
    .value.trim();
  const scopes = document
    .getElementById("oauthScopes")
    .value.split("\n")
    .map((s) => s.trim())
    .filter((s) => s);

  if (!clientId || !googleId || !googleSecret || scopes.length === 0) {
    showAlert("Please fill in all required fields", "danger");
    return;
  }

  const payload = {
    client_id: parseInt(clientId),
    google_client_id: googleId,
    google_client_secret: googleSecret,
    scopes,
  };
  const endpoint = id ? `/api/oauth/${id}` : "/api/oauth";
  const method = id ? "PUT" : "POST";
  try {
    await apiCall(endpoint, { method, body: JSON.stringify(payload) });
    showAlert("OAuth credentials saved", "success");
    bootstrap.Modal.getInstance(modalEl).hide();
    loadOAuthCredentials();
  } catch (error) {
    console.error("Failed to save OAuth credentials:", error);
  }
}

async function loadOAuthCredentials() {
  try {
    const creds = await apiCall("/api/oauth");
    const tbody = document.getElementById("oauthTableBody");
    tbody.innerHTML = "";
    (Array.isArray(creds) ? creds : []).forEach((cred) => {
      const row = document.createElement("tr");
      row.innerHTML = `
                <td>${cred.client_name}</td>
                <td>${cred.google_client_id}</td>
                <td>${cred.token_status}</td>
                <td>${new Date(cred.expires_at).toLocaleString()}</td>
                <td><button class="btn btn-sm btn-primary" onclick="showOAuthModal(${
                  cred.id
                })">Edit</button></td>
            `;
      tbody.appendChild(row);
    });
  } catch (error) {
    console.error("Failed to load OAuth credentials:", error);
  }
}

// Events CRUD
async function loadCalendars() {
  const clientId = document.getElementById("clientSelect").value;
  const calSelect = document.getElementById("calendarSelect");
  calSelect.innerHTML = '<option value="">Select a calendar.</option>';
  if (!clientId) return;
  try {
    const cals = await apiCall(`/api/clients/${clientId}/calendars`);
    currentCalendars = Array.isArray(cals) ? cals : [];
    currentCalendars.forEach((cal) => {
      const opt = document.createElement("option");
      opt.value = cal.id;
      opt.textContent = cal.summary;
      calSelect.appendChild(opt);
    });
  } catch (error) {
    console.error("Failed to load calendars:", error);
  }
}
async function loadEvents() {
  const clientId = document.getElementById("clientSelect").value;
  const calendarId = document.getElementById("calendarSelect").value;
  const container = document.getElementById("eventsContainer");
  container.innerHTML = "";

  if (!clientId || !calendarId) {
    container.innerHTML =
      '<p class="text-muted">Select a client and calendar to view events.</p>';
    return;
  }

  try {
    // Fetch events array from backend
    const resp = await apiCall(
      `/api/clients/${clientId}/calendars/${calendarId}/events`
    );
    // The API returns { data: [ ... ] }
    currentEvents = Array.isArray(resp.data) ? resp.data : [];

    if (currentEvents.length === 0) {
      container.innerHTML = '<p class="text-muted">No events found.</p>';
      return;
    }

    // Build HTML table of events
    let html = '<table class="table table-striped">';
    html += "<thead><tr>";
    html += "<th>Event</th><th>Start</th><th>End</th><th>Actions</th>";
    html += "</tr></thead><tbody>";

    currentEvents.forEach((evt) => {
      const startTime = evt.start.dateTime || evt.start.date;
      const endTime = evt.end.dateTime || evt.end.date;
      html += `<tr>
                <td>${evt.summary || ""}</td>
                <td>${startTime}</td>
                <td>${endTime}</td>
                <td>
                    <button class="btn btn-sm btn-primary me-1" onclick="showEventModal('${
                      evt.id
                    }')">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteEvent('${
                      evt.id
                    }')">Delete</button>
                </td>
            </tr>`;
    });

    html += "</tbody></table>";
    container.innerHTML = html;
  } catch (error) {
    console.error("Failed to load events:", error);
    showAlert("Could not load events. See console for details.", "danger");
  }
}

function showEventModal(eventId = null) {
  const modalEl = document.getElementById("eventModal");
  const modal = new bootstrap.Modal(modalEl);
  const title = document.getElementById("eventModalTitle");
  document.getElementById("eventForm").reset();
  document.getElementById("eventId").value = eventId || "";
  if (eventId) {
    title.textContent = "Edit Event";
    const clientId = document.getElementById("clientSelect").value;
    const calendarId = document.getElementById("calendarSelect").value;
    apiCall(
      `/api/clients/${clientId}/calendars/${calendarId}/events/${eventId}`
    )
      .then((evt) => {
        document.getElementById("eventSummary").value = evt.summary || "";
        document.getElementById("eventStart").value =
          evt.start.dateTime || evt.start.date;
        document.getElementById("eventEnd").value =
          evt.end.dateTime || evt.end.date;
      })
      .catch((err) => console.error("Failed to load event data:", err));
  } else {
    title.textContent = "Add Event";
  }
  modal.show();
}
