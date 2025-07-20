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
v1.24

Comments:
- Implemented loadOAuthCredentials to fetch and display OAuth data
- Populates #oauthTableBody with client name, client ID, token status
*/

// Global variables
let currentClients = [];
let currentEvents = [];
let currentCalendars = [];

document.addEventListener("DOMContentLoaded", () => {
  loadClients();
  loadOAuthCredentials();
});

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

function loadClients() {
  apiCall("/api/clients")
    .then((clients) => {
      currentClients = clients;
      const tbody = document.getElementById("clientTableBody");
      tbody.innerHTML = "";
      if (clients.length === 0) {
        tbody.innerHTML = "<tr><td colspan='4'>No clients found.</td></tr>";
        return;
      }
      for (const client of clients) {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${client.name}</td>
          <td>${client.email}</td>
          <td>${client.google_email}</td>
          <td>
            <button class="btn btn-sm btn-primary" onclick="editClient(${client.id})">Edit</button>
            <button class="btn btn-sm btn-danger" onclick="deleteClient(${client.id})">Delete</button>
          </td>`;
        tbody.appendChild(row);
      }
    })
    .catch((err) => {
      showAlert("Failed to load clients", "danger");
    });
}

function loadOAuthCredentials() {
  apiCall("/api/oauth")
    .then((creds) => {
      const tbody = document.getElementById("oauthTableBody");
      tbody.innerHTML = "";
      if (creds.length === 0) {
        tbody.innerHTML =
          "<tr><td colspan='3'>No OAuth credentials found.</td></tr>";
        return;
      }
      for (const cred of creds) {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${cred.client?.name || "Unknown Client"}</td>
          <td>${cred.client_id}</td>
          <td>${cred.token_valid ? "✅ Valid" : "❌ Invalid"}</td>`;
        tbody.appendChild(row);
      }
    })
    .catch((err) => {
      showAlert("Failed to load OAuth credentials", "danger", "oauthAlerts");
    });
}
