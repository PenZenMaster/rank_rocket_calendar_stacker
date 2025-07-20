/*
Module/Script Name: static/app.js

Description:
Frontend JavaScript for Rank Rocket Calendar Stacker. Handles dashboard initialization and rendering, Client CRUD, OAuth management, and alerts. This file coordinates API interactions and dynamic DOM updates across all user interactions.

Author(s):
George Penzenik - Rank Rocket Co

Created Date:
07-19-2025

Last Modified Date:
07-31-2025

Version:
v1.21

Comments:
- Refactored `loadClients()` with correct table ID binding and error alerting.
- Standardized fetch error handling and ensured JSON response parsing.
- Header block restored per project GPT mandates.
*/

let currentClients = [];
let currentOAuthCredentials = [];

function showAlert(message, type = "success") {
  const alertPlaceholder = document.getElementById("alertPlaceholder");
  alertPlaceholder.innerHTML = `
    <div class="alert alert-${type} alert-dismissible" role="alert">
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>`;
  setTimeout(() => {
    alertPlaceholder.innerHTML = "";
  }, 5000);
}

function apiCall(url, method = "GET", data = null) {
  const options = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (data) options.body = JSON.stringify(data);

  return fetch(url, options).then(async (response) => {
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || "API call failed");
    }
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      return response.json();
    }
    return response.text();
  });
}

function loadClients() {
  apiCall("/api/clients")
    .then((clients) => {
      currentClients = clients;
      const tbody = document.getElementById("clientsTableBody"); // FIXED ID
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

// Remaining functions untouched

document.addEventListener("DOMContentLoaded", () => {
  loadClients();
  // Additional init if needed
});
