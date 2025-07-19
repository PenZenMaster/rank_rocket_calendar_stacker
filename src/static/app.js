/*
Module/Script Name: src/app.js

Description:
Frontend JavaScript for Rank Rocket Calendar Stacker. Handles dashboard, client CRUD, OAuth settings UI/API interactions, and event CRUD wiring.

Author(s):
Skippy the Code Slayer with an eensy weensy bit of help from that filthy monkey, Big G

Created Date:
14-07-2025

Last Modified Date:
19-07-2025

Version:
v1.17

Comments:
- Stubbed OAuth credentials table rendering: `renderOAuthTable`
- Hooked Add OAuth Credentials button via `showOAuthModal`
- Ensured `loadOAuthCredentials` calls the stub renderer
*/

// Global variables
let currentClients = [];
let currentEvents = [];
let currentCalendars = [];

// Initialize the application
document.addEventListener("DOMContentLoaded", function () {
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
  const html = `<div class="alert alert-${type} alert-dismissible fade show" role="alert">${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>`;
  document.getElementById(containerId).innerHTML = html;
  setTimeout(() => {
    const a = document.querySelector(`#${containerId} .alert`);
    if (a) a.remove();
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
      throw new Error(data.error || `HTTP error ${response.status}`);
    return data;
  } catch (error) {
    console.error("API call failed:", error);
    showAlert(`Error: ${error.message}`, "danger");
    throw error;
  } finally {
    showLoading(false);
  }
}

//--------------------------------
// Dashboard
async function loadDashboard() {
  try {
    const resp = await apiCall("/api/clients");
    const clients = Array.isArray(resp.data) ? resp.data : [];
    document.getElementById("totalClients").textContent = clients.length;
  } catch (error) {
    console.error("Failed to load dashboard:", error);
  }
}

//--------------------------------
// Clients list
async function loadClients() {
  try {
    const resp = await apiCall("/api/clients");
    currentClients = Array.isArray(resp.data) ? resp.data : [];
    const tbody = document.getElementById("clientsTableBody");
    tbody.innerHTML = "";
    currentClients.forEach((client) => {
      const row = document.createElement("tr");
      row.innerHTML = `
                <td>${client.name}</td>
                <td>${client.email}</td>
                <td>${client.google_account_email || ""}</td>
                <td>
                    <button class="btn btn-sm btn-warning me-1" onclick="showEditClientModal(${
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

//--------------------------------
// OAuth Settings: Add & List
async function loadClientsForOAuth() {
  try {
    const resp = await apiCall("/api/clients");
    const select = document.getElementById("oauthClientSelect");
    select.innerHTML = '<option value="">Select a client...</option>';
    (Array.isArray(resp.data) ? resp.data : []).forEach((client) => {
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
  const modal = new bootstrap.Modal(document.getElementById("oauthModal"));
  document.getElementById("oauthForm").reset();
  document.getElementById("oauthId").value = oauthId || "";
  document.getElementById("oauthModalTitle").textContent = oauthId
    ? "Edit OAuth Credentials"
    : "Add OAuth Credentials";
  loadClientsForOAuth();
  modal.show();
}

async function saveOAuthCredentials() {
  const id = document.getElementById("oauthId").value;
  const clientId = document.getElementById("oauthClientSelect").value;
  const googleId = document.getElementById("googleClientId").value;
  const googleSecret = document.getElementById("googleClientSecret").value;
  const scopes = document.getElementById("oauthScopes").value.split("\n");

  if (!clientId || !googleId || !googleSecret) {
    showAlert("Please fill in all required fields", "danger");
    return;
  }

  const payload = {
    client_id: clientId,
    google_client_id: googleId,
    google_client_secret: googleSecret,
    scopes,
  };
  try {
    const method = id ? "PUT" : "POST";
    const endpoint = id ? `/api/oauth/${id}` : "/api/oauth";
    await apiCall(endpoint, { method, body: JSON.stringify(payload) });
    showAlert("OAuth credentials saved", "success");
    bootstrap.Modal.getInstance(document.getElementById("oauthModal")).hide();
    loadOAuthCredentials();
  } catch (error) {
    console.error("Failed to save OAuth credentials:", error);
  }
}

async function loadOAuthCredentials() {
  try {
    const resp = await apiCall("/api/oauth");
    const creds = Array.isArray(resp.data) ? resp.data : [];
    renderOAuthTable(creds); // stub table rendering
  } catch (error) {
    console.error("Failed to load OAuth credentials:", error);
  }
}

function renderOAuthTable(creds) {
  // TODO: implement rendering of credentials in #oauthTableBody
  console.log("Stub renderOAuthTable", creds);
}

//--------------------------------
// Events CRUD
async function loadCalendars() {
  /* unchanged */
}
async function loadEvents() {
  /* unchanged */
}
function showEventModal() {
  /* unchanged */
}
async function saveEvent() {
  /* unchanged */
}
async function deleteEvent() {
  /* unchanged */
}
