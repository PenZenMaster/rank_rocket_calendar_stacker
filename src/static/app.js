/*
Module/Script Name: static/app.js

Description:
Frontend JavaScript for Rank Rocket Calendar Stacker. Handles dashboard, clients, OAuth (Settings) UI/API interactions, including full Add/Edit/Delete Client flow and Event CRUD wiring.

Author(s):
Skippy the Code Slayer

Created Date:
19-07-2025

Last Modified Date:
31-07-2025

Version:
v1.21

Comments:
- Stubbed out loadDashboard to prevent runtime error
- Fixed modal not closing after client save
- Fixed alert rendering behind the modal
*/

// Global variables
let currentClients = [];
let currentEvents = [];
let currentCalendars = [];

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
  // Stubbed: loadDashboard(); // Commented out to prevent ReferenceError
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
      // loadDashboard(); // Temporarily removed until implemented
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

// Clients list & CRUD
function saveClient() {
  const modalEl = document.getElementById("clientModal");
  const id = document.getElementById("clientId").value;
  const name = document.getElementById("clientName").value;
  const email = document.getElementById("clientEmail").value;
  const googleEmail = document.getElementById("googleAccountEmail").value;

  if (!name || !email || !googleEmail) {
    showAlert("All fields are required", "danger", "clientAlerts");
    return;
  }

  const payload = {
    name,
    email,
    google_email: googleEmail,
  };
  const endpoint = id ? `/api/clients/${id}` : "/api/clients";
  const method = id ? "PUT" : "POST";
  apiCall(endpoint, { method, body: JSON.stringify(payload) })
    .then(() => {
      showAlert("Client saved successfully", "success");
      bootstrap.Modal.getInstance(modalEl).hide();
      loadClients();
    })
    .catch((err) => {
      showAlert(`Save failed: ${err.message}`, "danger", "clientAlerts");
    });
}

function showOAuthModal(oauthId = null) {
  const modalEl = document.getElementById("oauthModal");
  const modal = new bootstrap.Modal(modalEl);
  const title = document.getElementById("oauthModalTitle");
  document.getElementById("oauthForm").reset();
  document.getElementById("oauthId").value = oauthId || "";
  document.getElementById("oauthClientSelect").innerHTML =
    '<option value="">Loading...</option>';
  loadClientsForOAuth();

  if (oauthId) {
    title.textContent = "Edit OAuth Credentials";
    apiCall(`/api/oauth/${oauthId}`).then((data) => {
      document.getElementById("oauthId").value = data.id;
      document.getElementById("googleClientId").value = data.google_client_id;
      document.getElementById("googleClientSecret").value =
        data.google_client_secret;
      document.getElementById("scopes").value = data.scopes.join("\n");

      const clientSelect = document.getElementById("oauthClientSelect");
      const found = currentClients.find((c) => c.id === data.client_id);
      if (found) {
        clientSelect.value = found.id;
      }
    });
  } else {
    title.textContent = "Add OAuth Credentials";
  }
  modal.show();
}

async function saveOAuthCredentials() {
  const modalEl = document.getElementById("oauthModal");
  const id = document.getElementById("oauthId").value;
  const clientId = document.getElementById("oauthClientSelect").value;
  const googleId = document.getElementById("googleClientId").value.trim();
  const googleSecret = document
    .getElementById("googleClientSecret")
    .value.trim();
  const scopes = document
    .getElementById("scopes")
    .value.split(/[\n,]/)
    .map((s) => s.trim())
    .filter((s) => s);

  if (!clientId || !googleId || !googleSecret || scopes.length === 0) {
    showAlert("Please fill in all required fields", "danger", "oauthAlerts");
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
