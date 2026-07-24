# CodeGuardian AI - Progress & Work Log

This document serves as a tracking README to log completed milestones, system architecture details, API endpoints, recent changes, and proposed next tasks. Use this file to pick up development exactly where we left off.

---

## 🚀 Completed Work & Features

### 1. Database & Authentication Module (`accounts` app)
* **Custom User Model (`CustomUser`)**: Extends Django's `AbstractUser` to support user roles (`user`, `admin`).
* **JWT Authentication**: Implemented via Django REST Framework (DRF) and `rest_framework_simplejwt`.
* **Endpoints**:
  * `POST /api/auth/register/` - Registers a user and returns JWT access/refresh tokens.
  * `POST /api/auth/login/` - Standard JWT token generation (DRF SimpleJWT).
  * `POST /api/auth/token/refresh/` - Refreshes expired access tokens.
  * `GET /api/auth/me/` - Retrieves current authenticated user profile.

### 2. Project Ingestion & Extraction Module (`scanner` app)
* **Ingestion Types**: Supports ZIP upload, single `.py` file upload, or importing via a public GitHub repository URL.
* **Extraction Security**: Implements path traversal checks during extraction to prevent *Zip Slip* vulnerabilities.
* **Framework Auto-Detection**: Scans directory structures and imports to classify projects as **Django**, **Flask**, **FastAPI**, or generic **Python**.
* **Ignored Paths**: Automatically ignores system/dependency directories like `.git`, `venv`, `node_modules`, `migrations`, and `__pycache__` to keep results clean.
* **Endpoints**:
  * `POST /api/projects/upload/` - Uploads a ZIP or `.py` file, extracts and indexes code files.
  * `POST /api/projects/github/` - Pulls a public GitHub repository, extracts and indexes it.

### 3. Static Code Analysis & Scoring Engine (`scanner` app)
* **Security Scanner (Bandit)**: Invokes Bandit security scanner programmatically on the extracted workspace directory.
* **Custom AST Parser**: Parses Python files to AST representation to find quality/reliability issues:
  * `AST001`: Bare `except:` clauses.
  * `AST002`: Use of dangerous functions like `eval()` and `exec()`.
  * `AST003`: Functions exceeding 50 lines (encourages modularity).
  * `AST004`: Functions with more than 6 arguments.
* **Regex Secret Detector**: Identifies potential credentials matching patterns for AWS Access Keys, Slack Tokens, Google API Keys, and generic secret assignments, ignoring placeholder values like `your_api_key`.
* **Scoring Metrics**: Computes score deductions from a base of 100 based on issue severity:
  * **Critical** (-15 pts) | **High** (-10 pts) | **Medium** (-5 pts) | **Low** (-2 pts).
  * Outputs individual scores for **Security**, **Code Quality**, **Maintainability**, and an overall **Health Score**.
* **Endpoints**:
  * `POST /api/scans/start/` - Starts analysis on an indexed project.
  * `GET /api/scans/<int:id>/status/` - Returns the current run state (`pending`, `running`, `completed`, `failed`).
  * `GET /api/scans/<int:scan_id>/results/` - Returns issues found, optionally filtered by severity.

### 4. AI Explanation & Auto-Fix Engine (`fixes` & `issues` apps)
* **AI Explanations**: Uses Gemini (`gemini-1.5-flash`) to generate detailed explanations structured into: **Explain the Bug**, **Risks**, and **Remediation**.
* **Auto-Fix Code & Diff**: Generates fixed code blocks via Gemini and produces Git-style unified diff patches using `difflib`.
* **Interactive Fix States**: Users can change fix status to `accepted`, `rejected`, or `applied` (which marks the parent issue as fixed in the DB).
* **Test Case Generator**: Generates `pytest` test suites for specific `CodeFile` resources.
* **Endpoints**:
  * `GET /api/issues/<int:id>/` - Returns detailed issue metadata and generates AI explanations on-demand.
  * `PATCH /api/issues/<int:id>/` - Marks issues as resolved or false positives.
  * `GET /api/fixes/issue/<int:issue_id>/` - Generates/retrieves an AI-powered code fix and unified diff.
  * `PATCH /api/fixes/<int:id>/status/` - Promotes fix status (marks parent issue resolved if status is `applied`).
  * `GET /api/codefiles/<int:code_file_id>/tests/` - Generates a unit test suite.

### 5. Reporting & Analytics (`reports` & `dashboard` apps)
* **Dashboard Aggregations**: Calculates global stats (total projects, total scans, average health scores, severity counts, recent scans list, and top 5 most risky files).
* **PDF Report Generation**: Creates downloadable PDF reports with a premium look (using `ReportLab`) showing metric scores and detailed issue listings.
* **Endpoints**:
  * `GET /api/dashboard/stats/` - Fetches global project and scan metrics.
  * `GET /api/reports/scan/<int:scan_id>/` - Retrieves or creates report metadata.
  * `GET /api/reports/<int:id>/download/` - Dynamic PDF download with automatic regeneration on disk if missing.

### 6. Templates
* **Landing Page**: Implemented a responsive, modern HTML landing page (`index.html`) under `home/templates` using vanilla CSS, modern typography, grid layouts, scroll animations, dynamic counter animations, and an interactive typing command-line terminal simulation.

---

## 🛠️ Recent Fixes & Housekeeping
* **Fixed `codeguardian/settings.py`**: Cleaned up syntax errors at the bottom of the file caused by a duplicate unclosed `TEMPLATES` block and misplaced Git diff conflict hunks.
* **Proper Static Configuration**: Formatted `STATICFILES_DIRS = [BASE_DIR / "static"]` cleanly to support custom frontend styling files.

---

## 🔮 Next Tasks & Backlog

1. **Database Migrations & Running Server**:
   * Run `python manage.py makemigrations` and `python manage.py migrate` to apply any pending database updates (such as CustomUser additions).
   * Create a Django superuser.
2. **Frontend UI Integration**:
   * Build the Django/React dashboard views. A React app setup on port 3000 or an SPA served from Django static files can consume the existing REST API endpoints.
3. **Scan Execution Verification**:
   * Verify scanning functionality against an uploaded ZIP or file on disk. Ensure Bandit and local AST rules execute properly and save records.
4. **Third-Party Linting Integration**:
   * Extend scanning capabilities to run `ruff` or `pylint` programmatically as outlined in the day-wise documentation (Day 15).
