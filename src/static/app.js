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
v1.33

Comments:
- Sanitized scope input before submitting OAuth credentials
*/

let currentClients = [];
let currentOAuthCredentials = [];

function showAlert(message, type = "success") {
  const alertPlaceholder = document.getElementById("alertPlaceholder");
  if (!alertPlaceholder) return;
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

// ... other functions remain unchanged ...

function saveOAuthCredentials() {
  const id = document.getElementById("oauthId").value;
  const client_id = document.getElementById("oauthClientSelect").value;
  const google_client_id = document.getElementById("googleClientId").value;
  const google_client_secret =
    document.getElementById("googleClientSecret").value;

  if (!client_id || !google_client_id || !google_client_secret) {
    showAlert("All OAuth fields are required.", "danger");
    return;
  }

  // ✅ Trim and filter scopes to eliminate blank lines
  const rawScopes = document.getElementById("oauthScopes").value;
  const scopes = rawScopes
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .join("\n");

  const data = { client_id, google_client_id, google_client_secret, scopes };
  console.log("OAuth Save Payload:", data);

  const url = id ? `/api/oauth/${id}` : "/api/oauth";
  const method = id ? "PUT" : "POST";

  apiCall(url, method, data)
    .then((response) => {
      bootstrap.Modal.getInstance(document.getElementById("oauthModal")).hide();
      showAlert("OAuth credentials saved successfully.");
      if (response.auth_url) {
        window.open(response.auth_url, "_blank");
      }
    })
    .catch((err) => {
      bootstrap.Modal.getInstance(document.getElementById("oauthModal")).hide();
      showAlert("Failed to save OAuth credentials: " + err.message, "danger");
    });
}

document.addEventListener("DOMContentLoaded", () => {
  loadClients();
  showSection("dashboard");
});
