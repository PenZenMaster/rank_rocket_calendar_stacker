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
v1.22

Comments:
- Added missing showSection() function to restore section navigation.
- Fixed sidebar nav visibility toggling to unblock UI routing.
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
      const tbody = document.getElementById("clientsTableBody");
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

function showSection(sectionId) {
  // Hide all sections
  document.querySelectorAll(".section").forEach((section) => {
    section.style.display = "none";
  });

  // Remove 'active' class from all nav links
  document.querySelectorAll(".nav-link").forEach((link) => {
    link.classList.remove("active");
  });

  // Show the selected section
  const section = document.getElementById(sectionId);
  if (section) {
    section.style.display = "block";
  }

  // Add 'active' class to the clicked link
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
  // Additional init if needed
});
