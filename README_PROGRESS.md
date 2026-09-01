# CodeGuardian AI - Progress & Work Log

This document serves as the central progress log and architectural reference for **CodeGuardian AI**. It details completed milestones, system architecture, API endpoints, user interface routes, static analysis engines, AI integrations, recent fixes, and the upcoming product backlog.

---

## 📌 Project Overview & Tech Stack

**CodeGuardian AI** is an intelligent, multi-engine Python code review and automated remediation platform. It combines static AST analysis, security scanning (Bandit), linting (Ruff), regex-based secret detection, and LLM-powered reasoning (Google Gemini) to detect vulnerabilities, explain bugs, generate Git-compatible diff patches, create Pytest test suites, and produce downloadable PDF audit reports.

* **Backend Framework**: Django 5.2, Django REST Framework (DRF), SimpleJWT
* **Static Analysis & Security**: Python AST, Bandit, Ruff, Custom Regex Secret Detectors
* **AI & Remediation**: Google Gemini (`gemini-1.5-flash`), `difflib` unified diff engine
* **Reporting & Exports**: ReportLab PDF Generator
* **Frontend / UI**: Django Templates, Vanilla CSS Design System, Responsive Glassmorphism UI, Vanilla JavaScript AJAX / Fetch API
* **Database & Auth**: SQLite (Dev) / PostgreSQL (Prod), Custom User Model with Role-Based Access Control (`user`, `admin`)
* **DevOps & CI/CD**: Docker, Docker Compose, GitHub Actions CI workflows

---

## 🚀 Completed Modules & System Features

### 1. Database & Authentication Module (`accounts` app)
* **Custom User Model (`CustomUser`)**: Extends Django's `AbstractUser` with custom role fields (`user`, `admin`).
* **JWT Authentication**: Configured via `djangorestframework-simplejwt` for secure stateless REST API communication.
* **Session & Token Management**: Supports simultaneous browser session authentication and localStorage JWT token persistence.
* **Authentication UI Templates**:
  * `accounts/templates/login.html` - Modern login interface with client-side credential validation, animated loader, and automatic dashboard redirect.
  * `accounts/templates/register.html` - Interactive registration interface with live password strength calculation, match verification, and role handling.
  * `static/js/login.js` & `static/js/register.js` - Client-side AJAX submission and token lifecycle managers.

### 2. Project Ingestion & Extraction Engine (`scanner` app)
* **Multi-Modal Project Ingestion**:
  * **ZIP Archive Upload**: Direct extraction and recursive directory mapping.
  * **Single File Upload**: Instant single `.py` script scanning and evaluation.
  * **GitHub Repository Import**: Automated download and extraction of public GitHub repository archives via `github_downloader.py`.
* **Path Traversal & Security Sanitization**: Implements rigorous path traversal checks to neutralize *Zip Slip* vulnerabilities during extraction.
* **Framework Auto-Detection**: Heuristically detects and classifies projects as **Django**, **Flask**, **FastAPI**, or standard **Python** scripts by inspecting project structure and imports.
* **Code File Indexing**: Recursively traverses extracted directories (ignoring `.git`, `node_modules`, `venv`, `migrations`, `__pycache__`) and persists indexed source files into the `CodeFile` model.
* **Project Management UI**:
  * `scanner/templates/upload.html` - Interactive drag-and-drop file upload and GitHub repository URL import form with progress indicator.
  * `scanner/templates/projects.html` - Project card view listing all uploaded projects, framework badges, status indicators, scan triggers, and direct navigation to issues.

### 3. Multi-Engine Static Code Analysis & Scoring Pipeline (`scanner` app)
* **Custom AST Quality Analyzer (`ast_parser.py`)**:
  * `AST001`: Bare `except:` clauses that silence exceptions.
  * `AST002`: Use of dangerous dynamic evaluation functions (`eval()`, `exec()`).
  * `AST003`: Functions exceeding 50 lines (modularity and complexity warning).
  * `AST004`: Functions with more than 6 parameters (design smell warning).
* **Bandit Security Scanner (`bandit_runner.py`)**:
  * Programmatically invokes Bandit via subprocess with JSON AST reporting.
  * Captures security issues (SQL injection, weak cryptography, insecure temporary files, shell execution) and maps them to `HIGH` and `CRITICAL` severity levels.
* **Ruff Fast Linter Integration (`ruff_runner.py`)**:
  * Runs Ruff against target project workspaces to catch code quality, syntax, and style anti-patterns.
  * Normalizes and maps Ruff rule codes directly into CodeGuardian issue categories and severity tiers.
* **Regex Secret Detector (`secret_detector.py`)**:
  * Scans codebases for hardcoded credentials (AWS Access Keys, Slack API Tokens, Google API Keys, and generic secret tokens).
  * Intelligently filters out placeholder strings (e.g., `your_api_key`, `dummy_secret`).
* **Issue Aggregator & Weighted Health Scoring (`issue_aggregator.py`)**:
  * Deduplicates findings across AST, Bandit, Ruff, and Secret detectors.
  * Computes severity-weighted deductions from a baseline score of 100:
    * **Critical**: -15 pts | **High**: -10 pts | **Medium**: -5 pts | **Low**: -2 pts.
  * Generates independent metric scores for **Security**, **Code Quality**, **Maintainability**, and an aggregated **Overall Health Score**.

### 4. AI Explanation, Auto-Fix & Test Suite Generation (`fixes` & `issues` apps)
* **On-Demand AI Explanation Engine (`llm_agent.py`)**:
  * Powered by Google Gemini (`gemini-1.5-flash`).
  * Provides structured 3-part breakdowns for any discovered issue:
    1. **Explain the Bug**: Root cause analysis.
    2. **Risks**: Security, performance, or stability implications.
    3. **Remediation**: Actionable guidance for fixing the defect.
* **AI Auto-Fix & Diff Engine (`fix_generator.py`)**:
  * Generates corrected code snippets via Gemini LLM.
  * Produces standard Git-compatible unified diff patches using Python's `difflib`.
* **Fix Lifecycle & Issue Resolution Synchronization**:
  * Supports fix workflow states: `suggested` ➔ `accepted` / `rejected` ➔ `applied`.
  * Marking a fix as `applied` automatically marks the parent `Issue` as resolved (`is_fixed = True`).
* **Automated Pytest Test Suite Generator (`test_generator.py`)**:
  * Generates unit test suites for any indexed `CodeFile` using Gemini.
* **Issue Management & Remediation UI (`issues/templates/issue_list.html`)**:
  * Interactive filtering by severity (Critical, High, Medium, Low), issue type, and search keyword.
  * Built-in modals:
    * **AI Explanation Modal**: Displays real-time generated analysis.
    * **AI Auto-Fix Modal**: Side-by-side original vs. fixed code view with diff patch preview and "Apply Fix" action.
    * **Test Suite Modal**: View and copy generated Pytest test cases.
    * **Status Toggles**: Instantly mark issues as resolved or false positives.

### 5. Reporting & Analytics (`reports` & `dashboard` apps)
* **Dashboard Aggregations (`dashboard/views.py`)**:
  * User-scoped statistics: Total Projects, Total Scans, Total Issues, Severity Distribution, and Issue Type Breakdown.
  * Real-time average scores (Overall, Security, Quality, Maintainability).
  * Recent scan history and Top 5 Most Risky Files ranking.
* **Interactive Dashboard UI (`dashboard/templates/dashboard.html`)**:
  * Responsive analytics page with SVG circular health score gauges, severity breakdown progress bars, project filter dropdown, recent scan logs, and quick PDF export triggers.
* **PDF Audit Report Generator (`reports/services/pdf_generator.py`)**:
  * Generates branded PDF reports via `ReportLab`.
  * Includes executive summary, metric health score cards, scan metadata, severity distribution charts, and detailed issue breakdowns.
  * Serves direct downloads with automatic on-demand generation and disk caching.

### 6. Frontend UI & Design System
* **Shared App Shell (`templates/base.html`)**:
  * Unified dark glassmorphism navbar and sidebar layout with active route detection, user role badges, and mobile-responsive drawer.
* **Landing Page (`home/templates/index.html`)**:
  * Hero banner with interactive typing terminal simulation showcasing CLI scanning.
  * Animated feature cards, dynamic counters, and scan workflow roadmap.
* **Design Tokens & Stylesheets**:
  * `static/css/main.css` & `home/static/css/index.css`: Curated HSL color palette, dark mode gradients, clean typography, badge utilities, and animated cards.

### 7. DevOps, CI/CD & Containerization
* **GitHub Actions Workflows (`.github/workflows/`)**:
  * `summary.yml`: Automated issue summarization workflow.
  * CI pipeline configuring automated linting and unit test execution on pull requests.
* **Containerization**:
  * `Dockerfile`: Multi-stage Python 3.11 build for the Django web service.
  * `docker-compose.yml`: Multi-container composition (Django web application + database service).
  * `.dockerignore` and `.gitignore`: Configured to exclude virtual environments, SQLite databases, and transient media.

---

## 📡 API & Web Route Directory

### REST API Endpoints

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register/` | Register new user and issue JWT tokens | No |
| `POST` | `/api/auth/login/` | Obtain JWT access/refresh token pair | No |
| `POST` | `/api/auth/token/refresh/` | Refresh expired JWT access token | No |
| `GET` | `/api/auth/me/` | Retrieve authenticated user profile | Yes |
| `GET` | `/api/projects/` | List all projects belonging to user | Yes |
| `POST` | `/api/projects/upload/` | Upload ZIP or `.py` file for extraction | Optional/Fallback |
| `POST` | `/api/projects/github/` | Import public GitHub repository by URL | Optional/Fallback |
| `POST` | `/api/scans/start/` | Trigger static & security scan pipeline | Optional/Fallback |
| `GET` | `/api/scans/<id>/status/` | Check scan run status & scores | No |
| `GET` | `/api/scans/<scan_id>/results/`| Fetch issues found in scan with severity filter | No |
| `GET` | `/api/issues/` | List issues with project/scan/severity filters | Yes |
| `GET` | `/api/issues/<id>/` | Fetch issue details + on-demand Gemini AI explanation | Yes |
| `PATCH` | `/api/issues/<id>/` | Mark issue as resolved or false positive | Yes |
| `GET` | `/api/fixes/issue/<issue_id>/` | Fetch or generate AI code fix and diff patch | Yes |
| `PATCH` | `/api/fixes/<id>/status/` | Update fix status (`applied` resolves issue) | Yes |
| `GET` | `/api/codefiles/<id>/tests/` | Generate Pytest test suite for code file | Yes |
| `GET` | `/api/dashboard/stats/` | Fetch aggregated security & quality metrics | Yes |
| `GET` | `/api/reports/scan/<scan_id>/` | Fetch or create report metadata | No |
| `GET` | `/api/reports/<id>/download/` | Download generated ReportLab PDF audit report | No |

### Web UI Pages (HTML Views)

| Method | Route | Template | Purpose |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | `home/templates/index.html` | Public landing page with live terminal demo & features |
| `GET` | `/login/` | `accounts/templates/login.html` | User login page |
| `GET` | `/register/` | `accounts/templates/register.html` | User registration page |
| `GET` | `/dashboard/` | `dashboard/templates/dashboard.html` | Analytics dashboard with score gauges & risky files |
| `GET` | `/projects/` | `scanner/templates/projects.html` | Project portfolio & scan triggering interface |
| `GET` | `/scan/upload/` | `scanner/templates/upload.html` | Project ZIP / `.py` upload & GitHub import page |
| `GET` | `/issues/` | `issues/templates/issue_list.html` | Issue inspection, AI fix & test generation UI |

---

## 🛠️ Recent Fixes, Improvements & Housekeeping

* **Cleaned `codeguardian/settings.py`**:
  * Resolved unclosed `TEMPLATES` block syntax errors and removed misplaced Git diff conflict hunks.
  * Formatted `STATICFILES_DIRS = [BASE_DIR / "static"]` cleanly and established default static directories.
  * Properly bound custom user model: `AUTH_USER_MODEL = "accounts.CustomUser"`.
* **Cleaned View Imports**:
  * Removed deprecated/unused `aiohttp` import in `accounts/views.py` that was triggering startup errors.
* **GitHub Ingestion & Extraction Fix**:
  * Updated `extract_and_map_project` in `file_extractor.py` to support `github` upload types, extracting downloaded repository archives that were previously bypassed.
* **Test Isolation & Media Cleanliness**:
  * Added directory pre-cleaning in `file_extractor.py` before extracting into target project directories, preventing artifact bleeding across test executions.
* **Unit Test Suite Validation**:
  * Verified all 5 unit tests in `scanner/tests.py` passing cleanly (`Ran 5 tests in 15.980s, OK`).
* **Superuser Account Configured**:
  * Admin superuser available for administrative and local evaluation: `admin` / `adminpassword`.

---

## 🔮 Next Tasks & Product Roadmap

1. **Live Browser End-to-End Verification**:
   * Run local Django dev server: `python codeguardian/manage.py runserver`.
   * Test user sign-in (`/login/`) and verify redirect to `/dashboard/`.
   * Test uploading a sample project archive via `/scan/upload/` and monitoring scan progress.
   * Verify generated findings appear on `/issues/` with functional AI Explanation and Auto-Fix modals.
2. **Gemini API Key Configuration**:
   * Populate `GEMINI_API_KEY` in `codeguardian/.env` to enable live LLM explanation and test suite generation in development.
3. **Background Job Queue (Celery + Redis)**:
   * Offload heavy multi-file repository scanning, Bandit analysis, and PDF compilation into asynchronous Celery background tasks for enterprise scalability.
4. **Repository-Wide RAG Context**:
   * Implement vector embeddings (FAISS / ChromaDB) across extracted multi-file codebases to give Gemini cross-file contextual awareness during code remediation.
