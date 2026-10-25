# Enterprise Payment & Notification Engine

An enterprise fintech demonstration platform built with a Python 3.12 / FastAPI backend and a responsive, high-performance web dashboard. Designed specifically as the foundational application for DevOps capstone practicals (CI/CD pipelines, containerization, and Kubernetes deployments).

---

## 1. Application Architecture & Repository Structure

### Architecture Overview
The platform decouples transaction processing and dispatch audit notifications:
- **Backend Microservice:** Powered by FastAPI (Python 3.12), exposing RESTful JSON endpoints with CORS support, Pydantic data validation, and automated health checks.
- **Frontend Dashboard:** A responsive dark fintech dashboard providing real-time backend connectivity telemetry, transaction ledger filtering/search, payment simulation modal, and live dispatch notification audit feeds.
- **Inter-service Communication:** Browser client communicates with the backend via configurable HTTP REST API endpoints.

```
payment-notification-engine/
├── .dockerignore                 # Excludes caches, venv, and logs from container contexts
├── .env                          # Local environment settings (ports, URLs, CORS)
├── .env.example                  # Environment configuration template
├── .gitignore                    # Git tracking ignore rules
├── docker-compose.yml            # Multi-container local testing specification
├── README.md                     # Comprehensive architecture and operation guide
├── version.txt                   # Application semantic release version (1.0.0)
│
├── backend/                      # Python 3.12 / FastAPI Backend Microservice
│   ├── app/
│   │   ├── __init__.py           # Package marker & metadata
│   │   ├── config.py             # Environment variable and settings manager
│   │   ├── data.py               # In-memory mock fintech dataset and queries
│   │   ├── models.py             # Pydantic data schemas & Enums
│   │   ├── main.py               # FastAPI application setup and CORS middleware
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── health.py         # GET /health endpoint
│   │       ├── payments.py       # GET/POST /api/payments endpoints
│   │       └── notifications.py  # GET /api/notifications endpoint
│   ├── Dockerfile                # Multi-stage/slim container build definition
│   ├── requirements.txt          # Python runtime and test dependencies
│   └── run.py                    # Server launcher with pre-flight port conflict checking
│
├── frontend/                     # Modern Fintech Web Dashboard
│   ├── app.js                    # Reactive state, fetch logic, and DOM rendering
│   ├── config.js                 # Single source of truth for frontend API URL
│   ├── docker-entrypoint.sh      # Shell entrypoint injecting runtime env into containers
│   ├── Dockerfile                # Production Nginx container build definition
│   ├── index.html                # Semantic HTML5 dashboard layout
│   ├── nginx.conf                # Custom Nginx server configuration (port 28080)
│   ├── server.py                 # Lightweight zero-dependency local Python dev server
│   └── styles.css                # Custom fintech design system stylesheet
│
└── tests/                        # Automated Pytest Suite
    ├── __init__.py
    ├── conftest.py               # Pytest fixtures and FastAPI TestClient setup
    ├── test_cors.py              # CORS preflight and header verification tests
    ├── test_health.py            # /health and root endpoint tests
    ├── test_notifications.py     # /api/notifications schema and query tests
    └── test_payments.py          # /api/payments CRUD, filtering, and validation tests
```

---

## 2. Prerequisites

- **Python:** Python 3.12.x installed and available in system PATH.
- **Operating System:** Windows, Linux, or macOS.
- **Docker & Docker Compose (Optional for local container testing):** Docker Engine 20+ and Docker Compose v2+.

---

## 3. Actual Selected Local Ports & Conflict Detection

Common development ports (`3000`, `5000`, `8000`, `8080`, `8081`) were scanned on the host and identified as occupied or reserved. To prevent clashes, high-numbered ports were verified and allocated:

| Component | Port Type | Selected Port | Binding Address | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend** | Local Dev | **`28080`** | `0.0.0.0:28080` | Verified available |
| **Backend** | Local Dev | **`28081`** | `0.0.0.0:28081` | Verified available |
| **Frontend (K8s)**| Practical Requirement | **`30099`** | NodePort | Required by your Kubernetes capstone practical |

### Port Conflict Safeguard
Both `backend/run.py` and `frontend/server.py` include pre-flight socket inspection. If a port is occupied by another process, the server will not crash silently. Instead, it prints an actionable troubleshooting guide:

```
================================================================================
[ERROR] PORT CONFLICT DETECTED
================================================================================
The configured backend port 28081 on 0.0.0.0 is currently OCCUPIED or in use.
To resolve this conflict:
  1. Set the PORT environment variable:
     PowerShell:  $env:BACKEND_PORT="28091"; python backend/run.py
     Bash/Linux:  BACKEND_PORT=28091 python backend/run.py
  2. Or edit the .env file:
     BACKEND_PORT=28091
================================================================================
```

---

## 4. How to Install Dependencies & Run Locally

### Step 1: Create and Activate Virtual Environment
```bash
# Navigate to project root
cd payment-notification-engine

# Create virtual environment (Python 3.12)
python -m venv .venv

# Activate on Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# OR on Windows CMD:
.\.venv\Scripts\activate.bat
# OR on Linux/macOS:
source .venv/bin/activate
```

### Step 2: Install Backend Dependencies
```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### Step 3: Run the Backend
```bash
python backend/run.py
```
*Backend will start on `http://localhost:28081`.*
*Interactive API Swagger Documentation: `http://localhost:28081/docs`.*
*Health Check endpoint: `http://localhost:28081/health`.*

### Step 4: Run the Frontend (in a separate terminal)
```bash
# In another terminal window:
python frontend/server.py
```
*Frontend will start on `http://localhost:28080` and connect to backend on `http://localhost:28081`.*

---

## 5. How to Run Automated Tests

The test suite runs with `pytest` using FastAPI's `TestClient` (backed by `httpx`). All 15 tests validate input constraints, status codes, schemas, and CORS headers without needing a running server process.

```bash
# Run entire test suite with verbose output
pytest -v

# Run with test coverage report
pytest --tb=short
```

### Test Suite Coverage:
- `tests/test_health.py`: Validates `GET /health` and `GET /`, uptime reporting, and service metadata.
- `tests/test_payments.py`: Validates `GET /api/payments`, query filters (`status=COMPLETED`, `search=...`), detail retrieval (`GET /api/payments/{id}`), 404 handling, and input validation on `POST /api/payments` (e.g., rejecting negative amounts with HTTP 422).
- `tests/test_notifications.py`: Validates `GET /api/notifications`, status filtering, schema validation, and 404 responses.
- `tests/test_cors.py`: Validates preflight `OPTIONS` and standard `GET` requests with CORS origin headers.

---

## 6. How to Build & Run with Docker

### Option A: Using Docker Compose (Recommended for Local Container Testing)
Build and launch both services connected via an internal bridge network:

```bash
# Build and start services in background
docker compose up --build -d

# Check running container status
docker compose ps

# Inspect logs
docker compose logs -f

# Teardown containers
docker compose down
```

Access the application:
- **Frontend Dashboard:** `http://localhost:28080`
- **Backend API & Swagger:** `http://localhost:28081/docs`

### Option B: Building & Running Standalone Images

#### Build Backend Image:
```bash
docker build -t payment-backend:1.0.0 -f backend/Dockerfile ./backend

# Run Backend Container
docker run -d -p 28081:28081 --name payment-backend payment-backend:1.0.0
```

#### Build Frontend Image:
```bash
docker build -t payment-frontend:1.0.0 -f frontend/Dockerfile ./frontend

# Run Frontend Container (passing target backend URL)
docker run -d -p 28080:28080 -e BACKEND_API_URL="http://localhost:28081" --name payment-frontend payment-frontend:1.0.0
```

---

## 7. How to Configure the Frontend API URL

The application provides three convenient ways to adjust the Backend API endpoint:

1. **Via Environment Variable / Docker:**
   Set `BACKEND_API_URL` when starting the container or server:
   ```bash
   BACKEND_API_URL="http://192.168.1.100:28081" python frontend/server.py
   ```
2. **Via `frontend/config.js`:**
   Edit the default fallback in `frontend/config.js`:
   ```javascript
   window.__APP_CONFIG__ = {
     backendApiUrl: "http://localhost:28081",
     ...
   };
   ```
3. **In-Browser Quick Settings (No rebuild or restart needed):**
   - Click the **"Settings" (gear icon)** or the **Health Status pill** in the top navigation header.
   - Enter your target backend URL.
   - Click **"Test Backend Connection"** to verify live connectivity (checks for HTTP 200 from `/health`).
   - Click **"Save & Apply"**. The override is persisted in browser `localStorage`.

---

## 8. Frontend & Backend Communication in Kubernetes

When deploying frontend and backend as separate pods in Kubernetes, keep the following networking principles in mind:

### The Architecture Distinction (Client vs Container Network)
- **The frontend is a Single Page Application (SPA):** Even though Nginx serves the HTML/JS from inside a Kubernetes pod, the JavaScript executes **inside the end-user's web browser**, NOT inside the cluster!
- Therefore, the browser must be able to reach the backend through an **external endpoint** (Ingress or NodePort), not a private internal ClusterIP like `http://payment-backend-service:28081`.

### Recommended Patterns for Your Kubernetes Practical:

#### Pattern 1: NodePort Services (Practical Exam Requirement)
- Frontend Service: NodePort `30099` (Target port: `28080`).
- Backend Service: NodePort (e.g., `30098`, Target port: `28081`).
- Configuration: Set `BACKEND_API_URL` in the frontend Deployment environment to `http://<K8S_NODE_IP>:30098`.

#### Pattern 2: Kubernetes Ingress Controller (Production Pattern)
Use an Ingress resource to route traffic under a single domain:
- Route `/` → `payment-frontend-service:28080`
- Route `/api` and `/health` → `payment-backend-service:28081`
- Benefit: Browser communicates with `/api` directly, completely avoiding CORS and cross-port configuration issues.

#### Pattern 3: Kubernetes ConfigMap Injection
Inject `config.js` or `BACKEND_API_URL` into the frontend pod via a Kubernetes `ConfigMap`:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: frontend-config
data:
  BACKEND_API_URL: "http://<NODE_IP>:30098"
```

---

## 9. Files You Will Need to Create or Modify for Jenkins & Kubernetes

To complete your DevOps capstone practical exercises manually, here is the checklist of files you will need to add or customize:

### For Jenkins CI/CD Practical:
1. **`Jenkinsfile`** (Pipeline script):
   - **Checkout Stage:** Clones source code from your Git repository.
   - **Test Stage:** Creates Python virtualenv, installs `backend/requirements.txt`, and executes `pytest -v`.
   - **Build Stage:** Builds Docker images for `payment-backend` and `payment-frontend` tagged with build number or `version.txt`.
   - **Security / Linting Stage (optional):** Runs `flake8` or `bandit`.
   - **Push Stage:** Pushes images to Docker Hub or your container registry.
   - **Deploy Stage:** Triggers Kubernetes deployment manifests using `kubectl` or Helm.

### For Kubernetes Practical:
1. **`k8s/namespace.yaml`:** Isolated namespace definition (e.g. `payments-prod`).
2. **`k8s/backend-deployment.yaml`:**
   - Pod replica count, container image `payment-backend:1.0.0`.
   - Container port `28081`.
   - Liveness and readiness probes pointing to `/health`.
   - Resource limits (CPU/Memory).
3. **`k8s/backend-service.yaml`:**
   - Type `ClusterIP` or `NodePort`.
   - Port `28081`.
4. **`k8s/frontend-deployment.yaml`:**
   - Container image `payment-frontend:1.0.0`.
   - Container port `28080`.
   - Environment variable `BACKEND_API_URL` configured to backend's accessible address.
5. **`k8s/frontend-service.yaml`:**
   - **Type: `NodePort`**
   - **`nodePort: 30099`** *(Matches your practical requirement)*
   - `port: 28080` (or `80`)
   - `targetPort: 28080`
6. **`k8s/configmap.yaml`:** For environment configuration (`BACKEND_API_URL`, `APP_ENV`).
7. **`k8s/ingress.yaml` (Optional):** If Ingress-based routing is evaluated.

---

## 10. Verification Summary

- **Automated Tests:** `15 passed in ~0.20s` (Pytest).
- **Backend Verified:** Health endpoint (`200 OK`), Payments listing (`200 OK`), Notifications (`200 OK`), Payment creation (`201 Created`).
- **Frontend Verified:** Loaded in browser, live status indicator connected, transaction table rendered, data refresh validated, interactive payment simulation verified, port settings modal tested.
- **Port Allocation Confirmed Free:** Frontend: `28080`, Backend: `28081`.
