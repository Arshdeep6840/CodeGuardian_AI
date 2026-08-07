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
* **Dashboard Page Template**: Designed a modern responsive HTML dashboard (`dashboard.html`) under `dashboard/templates` with cards for metrics, SVG health score circular progress rings, issue severity breakdown bars, and tables/lists for recent scans and top risky files.
* **Endpoints**:
  * `GET /api/dashboard/stats/` - Fetches global project and scan metrics.
  * `GET /api/reports/scan/<int:scan_id>/` - Retrieves or creates report metadata.
  * `GET /api/reports/<int:id>/download/` - Dynamic PDF download with automatic regeneration on disk if missing.

### 6. Templates & Frontend Assets
* **Landing Page**: Implemented a responsive, modern HTML landing page (`index.html`) under `home/templates` using vanilla CSS, modern typography, grid layouts, scroll animations, dynamic counter animations, and an interactive typing command-line terminal simulation.
* **Authentication Pages**: Built responsive and elegant templates for registration (`register.html`) and login (`login.html`) under `accounts/templates` using custom stylesheets, password strength calculations, eye toggle visibility icons, and error handling elements.
* **Static Assets**: Created custom `style.css` and helper script files `login.js` and `register.js` to manage CSRF tokens, client-side validation, loader states, and AJAX submission.

### 7. Third-Party Linting Integration
* **Ruff Static Code Analyzer**: Integrated Ruff programmatically in `ruff_runner.py` inside the scan pipeline. Maps Ruff rule codes to CodeGuardian severity levels (`critical`, `high`, `medium`, `low`) and reports issues back to the scanner.

---

## 🛠️ Recent Fixes & Housekeeping
* **Fixed `codeguardian/settings.py`**: Cleaned up syntax errors at the bottom of the file caused by a duplicate unclosed `TEMPLATES` block and misplaced Git diff conflict hunks.
* **Proper Static Configuration**: Formatted `STATICFILES_DIRS = [BASE_DIR / "static"]` cleanly to support custom frontend styling files.
* **User Authentication Model**: Configured `AUTH_USER_MODEL = "accounts.CustomUser"` inside `settings.py` to enable the custom user role system.

---

## 🔮 Next Tasks & Backlog

1. **Frontend-Backend Integration**:
   * Wire up the newly added `dashboard.html` to a Django rendering view at `/dashboard/`.
   * Add dynamic JSON fetching via AJAX using stored JWT tokens from `/api/dashboard/stats/` to populate metric cards, circular rings, and tables on the dashboard page.
   * Correct the login endpoint URL in `login.js` and ensure successful login redirects users to `/dashboard/`.
2. **Database Migrations & Running Server**:
   * Run `python manage.py makemigrations` and `python manage.py migrate` to apply any pending database updates (such as CustomUser additions).
   * Create a Django superuser.
3. **Scan Execution Verification**:
   * Verify scanning functionality against an uploaded ZIP or file on disk. Ensure Bandit, Ruff, and local AST rules execute properly and save records.
