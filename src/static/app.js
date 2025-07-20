/**
Module/Script Name: static/app.js

Description:
Frontend JavaScript for Rank Rocket Calendar Stacker. Handles dashboard initialization and rendering, Client CRUD, OAuth management, and alerts. This file coordinates API interactions and dynamic DOM updates across all user interactions.

Author(s):
George Penzenik - Rank Rocket Co

Created Date:
07-19-2025

Last Modified Date:
07-20-2025

Version:
v1.28

Comments:
- Added console log in loadClients() to debug undefined client.id issue with Edit button.
*/

let currentClients = [];
let currentOAuthCredentials = [];

function showAlert(message, type = "success") {
  const alertPlaceholder = document.getElementById("alertPlaceholder");
  if (!alertPlaceholder) return; // Prevent crash if placeholder is missing
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
    const contentType = response.headers.get("content-type") || "";
    if (!response.ok) {
      const errorText = contentType.includes("application/json")
        ? await response.json()
        : await response.text();
      throw new Error(
        typeof errorText === "string"
          ? errorText
          : errorText.message || JSON.stringify(errorText)
      );
    }
    return contentType.includes("application/json")
      ? response.json()
      : response.text();
  });
}

function loadClients() {
  apiCall("/api/clients")
    .then((clients) => {
      currentClients = clients;
      const tbody = document.getElementById("clientsTableBody");
      tbody.innerHTML = "";
      if (clients.length === 0) {
        tbody.innerHTML = "<tr><td colspan='4'>No clients found.</td></tr>";
      } else {
        for (const client of clients) {
          console.log("Client Loaded:", client); // Debugging line
          const row = document.createElement("tr");
          row.innerHTML = `
            <td>${client.name}</td>
            <td>${client.email}</td>
            <td>${client.google_account_email}</td>
            <td>
              <button class="btn btn-sm btn-primary" onclick="editClient('${client.id}')">Edit</button>
              <button class="btn btn-sm btn-danger" onclick="deleteClient('${client.id}')">Delete</button>
            </td>`;
          tbody.appendChild(row);
        }
      }
      updateDashboardCounts();
    })
    .catch((err) => {
      showAlert("Failed to load clients", "danger");
    });
}

function editClient(clientId) {
  const client = currentClients.find((c) => c.id === clientId);
  if (!client) return;
  document.getElementById("clientId").value = client.id;
  document.getElementById("clientName").value = client.name;
  document.getElementById("clientEmail").value = client.email;
  document.getElementById("googleAccountEmail").value =
    client.google_account_email;
  document.getElementById("clientModalTitle").textContent = "Edit Client";
  new bootstrap.Modal(document.getElementById("clientModal")).show();
}

function saveClient() {
  const id = document.getElementById("clientId").value;
  const name = document.getElementById("clientName").value;
  const email = document.getElementById("clientEmail").value;
  const google_account_email =
    document.getElementById("googleAccountEmail").value;

  const data = { name, email, google_account_email };
  const url = id ? `/api/clients/${id}` : "/api/clients";
  const method = id ? "PUT" : "POST";

  apiCall(url, method, data)
    .then(() => {
      bootstrap.Modal.getInstance(
        document.getElementById("clientModal")
      ).hide();
      showAlert("Client saved successfully.");
      loadClients();
    })
    .catch((err) => {
      showAlert("Failed to save client: " + err.message, "danger");
    });
}

function deleteClient(clientId) {
  if (!confirm("Are you sure you want to delete this client?")) return;
  apiCall(`/api/clients/${clientId}`, "DELETE")
    .then(() => {
      showAlert("Client deleted successfully.");
      loadClients();
    })
    .catch((err) => {
      showAlert("Failed to delete client: " + err.message, "danger");
    });
}

function updateDashboardCounts() {
  document.getElementById("totalClients").textContent = currentClients.length;
}

function showSection(sectionId) {
  document.querySelectorAll(".section").forEach((section) => {
    section.style.display = "none";
  });
  document.querySelectorAll(".nav-link").forEach((link) => {
    link.classList.remove("active");
  });
  const section = document.getElementById(sectionId);
  if (section) {
    section.style.display = "block";
  }
  const navLink = Array.from(document.querySelectorAll(".nav-link")).find(
    (link) => link.getAttribute("onclick")?.includes(sectionId)
  );
  if (navLink) {
    navLink.classList.add("active");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadClients();
  showSection("dashboard");
});
