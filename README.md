# Orion Web Portal Data Tracker

This project is a Python application that automates data extraction from the Orion Web Portal. It uses Selenium to scrape course data and posts updates to a Discord webhook. The system runs in a Dockerized environment and includes a Selenium grid for automated browser interaction.

## Features

- **Automated Login:** Logs into the Orion portal using credentials stored in environment variables.
- **Data Scraping:** Extracts and formats data from tables based on a specific term (`TERM_TO_SEARCH`).
- **Change Detection:** Compares newly scraped data with the previous data to identify changes.
- **Notification System:** Sends updates via a Discord webhook when changes are detected.
- **Dockerized Setup:** Runs the application and Selenium grid within Docker containers for isolated execution.
- **Duo Authentication Support:** Requires manual approval of Duo Mobile authentication for secure access.

---

## Prerequisites

- Docker and Docker Compose installed
- Python 3.11 or later (if running outside Docker)
- Environment variables for the application setup

### Required Environment Variables

- `ORION_USERNAME`: Orion portal username
- `ORION_PASSWORD`: Orion portal password
- `WEBHOOK_URL`: Discord webhook URL for notifications
- `TERM_TO_SEARCH`: Term to filter the table data

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Create a `.env` File

Create a `.env` file in the root directory with the following format:

```env
ORION_USERNAME=your_username
ORION_PASSWORD=your_password
WEBHOOK_URL=https://discord.com/api/webhooks/...
TERM_TO_SEARCH=Fall 2024
```

### 3. Build and Run with Docker Compose

```bash
docker-compose up --build
```

- The `selenium` service provides the Selenium WebDriver grid.
- The `app` service runs the Python scraper.

---

## Application Workflow

1. **Login:** 
   - Navigates to the Orion portal and logs in using provided credentials.
   - Requires Duo Mobile authentication approval during login.

2. **Data Extraction:**
   - Scrapes table data, filters by the specified term, and formats it.

3. **Change Detection:**
   - Compares the current data with the previous data to detect changes.

4. **Notifications:**
   - Sends formatted updates to the Discord webhook if changes are detected.

5. **Loop and Refresh:**
   - Continuously refreshes the page and repeats the process every 5 minutes.

---

## Docker Configuration

### `Dockerfile`

- **Base Image:** Python 3.11
- **Dependencies:** Installed from `requirements.txt`
- **Entrypoint:** Starts the main Python script.

### `docker-compose.yml`

- **Services:**
  - `selenium`: Provides a Selenium WebDriver grid for automated browser interaction.
  - `app`: Runs the Python application.
- **Health Checks:** Ensures the Selenium service is healthy before starting the app.

---

## Debugging Tips

- **Log Outputs:** Check container logs for detailed information:
  ```bash
  docker logs pinger
  ```
- **Error Handling:** If the script fails, ensure that all environment variables are set correctly and Duo authentication is approved.

---

## License

This project is licensed under the MIT License.
