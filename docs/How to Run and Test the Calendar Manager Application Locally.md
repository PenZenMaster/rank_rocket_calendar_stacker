# How to Run and Test the Calendar Manager Application Locally

This document provides a step-by-step guide on how to set up, run, and perform basic testing of the `calendar-manager` application in your local development environment.

## 1. Introduction

The `calendar-manager` is a Flask-based web application designed to manage Google Calendar events for multiple clients. It features a web-based user interface for CRUD operations on client data and is built with scalability and maintainability in mind. This guide will help you get the application up and running quickly on your machine.

## 2. Prerequisites

Before you begin, ensure you have the following software installed on your system:

*   **Python 3.8+**: The application is developed using Python. You can download it from [python.org](https://www.python.org/downloads/).
*   **pip**: Python's package installer. It usually comes bundled with Python installations.
*   **Git**: A version control system. You can download it from [git-scm.com](https://git-scm.com/downloads).
*   **A web browser**: For accessing the application's user interface.

## 3. Setup Instructions

Follow these steps to set up the project locally:

### 3.1. Clone the Repository

First, you need to get the application code onto your local machine. If you have received a `.zip` file, extract it to your desired location. If it's in a Git repository, clone it using the following command:

```bash
git clone <repository_url>
cd calendar-manager
```

(Replace `<repository_url>` with the actual URL of your Git repository if applicable. If you received a zip file, navigate to the extracted `calendar-manager` directory.)

### 3.2. Create a Virtual Environment

It is highly recommended to use a Python virtual environment to manage project dependencies. This isolates the project's dependencies from your system's global Python packages.

```bash
python3 -m venv venv
```

### 3.3. Activate the Virtual Environment

Before installing dependencies or running the application, you need to activate the virtual environment. The command varies depending on your operating system:

*   **On Windows (Command Prompt):**
    ```cmd
venv\Scripts\activate.bat
    ```
*   **On Windows (PowerShell):**
    ```powershell
venv\Scripts\Activate.ps1
    ```
*   **On macOS/Linux:**
    ```bash
source venv/bin/activate
    ```

You should see `(venv)` prepended to your terminal prompt, indicating that the virtual environment is active.

### 3.4. Install Dependencies

With the virtual environment activated, install the required Python packages using `pip` and the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

This command will install all the necessary libraries, including Flask, Flask-SQLAlchemy, and Google API client libraries.

## 4. Running the Application

Once all dependencies are installed, you can run the Flask application. Ensure your virtual environment is still active.

```bash
python src/main.py
```

Upon successful execution, you will see output similar to this in your terminal:

```
 * Serving Flask app 'main'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://169.254.0.21:5000
Press CTRL+C to quit
```

This indicates that the Flask development server is running and accessible. You can now open your web browser and navigate to `http://127.0.0.1:5000` (or `http://localhost:5000`).

## 5. Basic Testing

After the application is running, you can perform some basic tests to ensure its core functionality is working.

### 5.1. Accessing the User Interface

Open your web browser and go to `http://localhost:5000`. You should see the main dashboard of the Calendar Manager application.

### 5.2. Adding a Client

1.  Click on the **"Clients"** link in the left sidebar.
2.  Click the **"Add Client"** button.
3.  A modal form will appear. Fill in the required fields:
    *   **Client Name:** e.g., `Test Client Company`
    *   **Email:** e.g., `contact@testclient.com`
    *   **Google Account Email:** e.g., `calendar@testclient.com`
4.  Click the **"Save"** button.

If successful, you should see a 


success message, and the newly added client should appear in the client list table.

### 5.3. Editing a Client

1.  In the client list table, locate the client you just added.
2.  Click the **"Edit"** button (pencil icon) next to the client entry.
3.  The client modal will reappear, pre-filled with the client's current information.
4.  Make changes to any of the fields (e.g., change the client name to `Updated Test Client Company`).
5.  Click the **"Save"** button.

Verify that the client's information has been updated in the table.

### 5.4. Deleting a Client

1.  In the client list table, locate the client you wish to delete.
2.  Click the **"Delete"** button (trash can icon) next to the client entry.
3.  A confirmation dialog will appear. Confirm the deletion.

Verify that the client entry is removed from the table.

### 5.5. Exploring Other Sections

*   **Dashboard**: Navigate back to the Dashboard. You should see the 


total number of clients updated based on your additions/deletions.
*   **Events**: While the event management functionality is not fully implemented in this MVP, you can navigate to this section to see the basic UI layout.
*   **OAuth Settings**: This section is a placeholder for future OAuth credential management.
*   **Settings**: This section is a placeholder for general application settings.

## 6. Troubleshooting

*   **"Import 'src.models.user' could not be resolved"**: This issue was addressed by centralizing the `db` initialization in `main.py` and adjusting imports in model files. Ensure your `main.py`, `src/models/user.py`, and `src/models/client.py` files are updated as per the previous corrections.
*   **"Address already in use"**: If you see this error when running `python src/main.py`, it means another process is already using port 5000. You can either stop the other process or change the port in `src/main.py` (e.g., `app.run(host='0.0.0.0', port=5001, debug=True)`).
*   **Dependencies not found**: If you encounter `ModuleNotFoundError`, ensure your virtual environment is activated and you have run `pip install -r requirements.txt` successfully.

## 7. Conclusion

By following this guide, you should have a functional local instance of the `calendar-manager` application. This MVP provides a solid foundation for further development, including the full integration with the Google Calendar API for event management and robust OAuth credential handling. You can now begin to explore the codebase, implement new features, and contribute to the project.

---

**Document Information**
- Author: Manus AI
- Version: 1.0
- Date: July 9, 2025
- Document Type: Local Setup and Testing Guide

