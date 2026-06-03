# CodeGuardian AI

## AI-Powered Python Code Review, Bug Detection & Auto-Fix Assistant

### Day-Wise Project Documentation

---

## 1. Project Overview

**CodeGuardian AI** is an AI-based Python code review platform. It allows users to upload a Python project or paste Python code, then the system analyzes the code and detects bugs, security issues, poor coding practices, missing validations, and improvement suggestions.

The system also provides AI-generated explanations, bug severity levels, corrected code suggestions, and a project health report.

---

## 2. Main Objective

The main objective of this project is to build an intelligent platform that helps Python developers improve their code quality using AI and machine learning.

The project focuses on:

* Python code analysis
* Bug detection
* Security issue detection
* Code quality checking
* AI-based code explanation
* Auto-fix suggestions
* Bug severity prediction
* Report generation

---

## 3. Technology Stack

### Frontend

* HTML
* CSS
* Bootstrap
* JavaScript
* Chart.js

### Backend

* Python
* Flask or FastAPI
* SQLAlchemy
* SQLite / PostgreSQL

### AI / ML

* OpenAI API / Gemini API / Local LLM
* Scikit-learn
* NLP techniques
* Rule-based analysis
* Code embeddings

### Python Code Analysis Tools

* AST module
* Bandit
* Ruff / Pylint
* Radon

### Other Tools

* GitHub API
* Docker
* GitHub Actions
* PDF report generation

---

# 4. Day-Wise Development Plan

## Day 1: Project Planning and Requirement Analysis

### Work to Do

* Understand the project idea clearly.
* Define project scope and features.
* Decide target users.
* Prepare requirement document.
* Finalize technology stack.

### Features Decided

* User login/register
* Upload Python code or project ZIP
* Analyze code
* Detect bugs
* Show severity level
* Suggest fixes
* Generate report

### Deliverables

* Project title
* Project objective
* Feature list
* Basic project flow diagram

---

## Day 2: System Design

### Work to Do

* Design complete system architecture.
* Decide frontend, backend, database, and AI module flow.
* Create basic workflow of the application.

### System Flow

```text
User Uploads Code
        ↓
Backend Receives File
        ↓
Code Parser Reads Files
        ↓
Static Analysis + AI Analysis
        ↓
Bug Detection
        ↓
Severity Prediction
        ↓
Fix Suggestions
        ↓
Dashboard + Report
```

### Deliverables

* System architecture
* Data flow diagram
* Module breakdown

---

## Day 3: Database Design

### Work to Do

* Design database tables.
* Create ER diagram.
* Decide relationships between users, projects, files, and reports.

### Main Tables

```text
users
projects
uploaded_files
code_issues
analysis_reports
fix_suggestions
```

### Example Database Structure

```text
User
- id
- name
- email
- password
- created_at

Project
- id
- user_id
- project_name
- uploaded_date
- status

CodeIssue
- id
- project_id
- file_name
- issue_type
- severity
- line_number
- description
- suggested_fix
```

### Deliverables

* Database schema
* ER diagram
* Table structure

---

## Day 4: Project Folder Setup

### Work to Do

* Create project folder.
* Set up virtual environment.
* Install required libraries.
* Create basic Flask/FastAPI structure.

### Suggested Folder Structure

```text
codeguardian_ai/
│
├── app.py
├── requirements.txt
├── config.py
│
├── models/
│   ├── user_model.py
│   ├── project_model.py
│   └── issue_model.py
│
├── routes/
│   ├── auth_routes.py
│   ├── upload_routes.py
│   ├── analysis_routes.py
│   └── report_routes.py
│
├── services/
│   ├── code_parser.py
│   ├── bug_detector.py
│   ├── ai_reviewer.py
│   ├── severity_model.py
│   └── report_generator.py
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── upload.html
│   └── report.html
│
├── uploads/
├── reports/
└── database.db
```

### Deliverables

* Project setup completed
* Folder structure created
* Basic app running

---

## Day 5: Frontend Home Page Design

### Work to Do

* Create landing page.
* Add project introduction.
* Add navigation bar.
* Add modern hero section.
* Add buttons for login and upload.

### Home Page Sections

* Hero section
* Features
* How it works
* Technology used
* Footer

### Deliverables

* `index.html`
* Basic CSS design
* Responsive landing page

---

## Day 6: User Registration Module

### Work to Do

* Create register page.
* Add form validation.
* Store user details in database.
* Hash password before storing.

### Fields

* Full name
* Email
* Password
* Confirm password

### Deliverables

* Register page
* Backend registration route
* User data saved in database

---

## Day 7: User Login and Logout Module

### Work to Do

* Create login page.
* Validate user email and password.
* Create session-based authentication.
* Add logout functionality.

### Deliverables

* Login page
* Logout route
* Session management
* Protected dashboard

---

## Day 8: User Dashboard Design

### Work to Do

* Create dashboard UI.
* Show user projects.
* Show total scans.
* Show total bugs found.
* Show recent reports.

### Dashboard Cards

```text
Total Projects
Total Files Scanned
Total Bugs Found
Critical Issues
Code Quality Score
```

### Deliverables

* Dashboard page
* Dashboard cards
* User-specific data display

---

## Day 9: Project Upload Module

### Work to Do

* Create upload page.
* Allow users to upload `.py` files.
* Allow users to upload `.zip` project files.
* Validate file type.

### Supported Files

```text
.py
.zip
.txt
```

### Deliverables

* Upload form
* File validation
* Files stored in upload folder

---

## Day 10: ZIP File Extraction Module

### Work to Do

* Extract uploaded ZIP files.
* Read project folder structure.
* Detect all Python files inside the project.
* Ignore unnecessary folders.

### Ignored Folders

```text
venv
env
__pycache__
.git
node_modules
migrations
```

### Deliverables

* ZIP extraction working
* Python files detected
* Project file list displayed

---

## Day 11: Python File Reader Module

### Work to Do

* Read Python files line by line.
* Store file content.
* Count number of lines.
* Identify empty files.

### Output Example

```text
File Name: app.py
Total Lines: 150
Status: Ready for Analysis
```

### Deliverables

* Code reader service
* File metadata extraction

---

## Day 12: Basic Code Analysis Using AST

### Work to Do

* Use Python AST module.
* Detect functions, classes, imports, and variables.
* Count number of functions and classes.

### Detect

* Function names
* Class names
* Import statements
* Number of arguments
* Long functions

### Deliverables

* AST-based parser
* Code structure analysis

---

## Day 13: Rule-Based Bug Detection

### Work to Do

* Create custom rules for common Python issues.
* Detect bad coding practices.

### Rules Example

```text
Hardcoded password found
Empty except block found
Use of eval() found
Use of exec() found
Too many nested if statements
Long function found
Print used instead of logging
```

### Deliverables

* Rule-based bug detector
* Issue list generated

---

## Day 14: Security Analysis Module

### Work to Do

* Integrate Bandit for security scanning.
* Detect security vulnerabilities in Python code.

### Security Issues

* Hardcoded secrets
* SQL injection risk
* Weak cryptography
* Unsafe file handling
* Insecure random usage

### Deliverables

* Bandit integration
* Security issue report

---

## Day 15: Code Quality Analysis Module

### Work to Do

* Integrate Ruff or Pylint.
* Check code quality issues.
* Detect formatting and style problems.

### Code Quality Checks

* Unused imports
* Undefined variables
* Too many arguments
* Unused variables
* Long lines
* Naming convention issues

### Deliverables

* Code quality scanner
* Quality issue list

---

## Day 16: Complexity Analysis Module

### Work to Do

* Use Radon for complexity analysis.
* Find complex functions.
* Generate maintainability score.

### Metrics

```text
Cyclomatic Complexity
Maintainability Index
Lines of Code
Function Length
```

### Deliverables

* Complexity report
* Maintainability score

---

## Day 17: Bug Severity Classification

### Work to Do

* Create severity rules.
* Classify issues as Low, Medium, High, or Critical.

### Severity Levels

```text
Low: Style or naming issue
Medium: Code quality issue
High: Runtime bug or logic issue
Critical: Security issue or data leak
```

### Deliverables

* Severity classification module
* Severity badge on dashboard

---

## Day 18: Machine Learning Severity Prediction

### Work to Do

* Create dataset for bug severity.
* Train ML model using Scikit-learn.
* Predict severity using issue description.

### Model Options

* Logistic Regression
* Random Forest
* Naive Bayes
* SVM

### Features

```text
Issue type
Keyword
File type
Line count
Security category
Description text
```

### Deliverables

* Trained severity model
* Model saved as `.pkl`
* Prediction function created

---

## Day 19: AI Code Explanation Module

### Work to Do

* Connect LLM API.
* Send detected issue to AI.
* Generate simple explanation.

### AI Explanation Output

```text
Problem:
This code stores the password directly in the database.

Why it is dangerous:
If the database is leaked, user passwords will be exposed.

Solution:
Use password hashing with bcrypt or werkzeug.security.
```

### Deliverables

* AI reviewer module
* Simple issue explanation

---

## Day 20: AI Auto-Fix Suggestion Module

### Work to Do

* Generate corrected code using AI.
* Show before and after comparison.
* Add copy button for fixed code.

### Output Format

```text
Original Code
Corrected Code
Explanation
```

### Deliverables

* AI fix suggestion system
* Before/after code view

---

## Day 21: Test Case Generator Module

### Work to Do

* Generate unit test cases for Python functions.
* Create pytest-based test suggestions.
* Show generated test code.

### Example

```python
def test_add_user():
    response = client.post("/register", data={
        "email": "test@gmail.com",
        "password": "123456"
    })
    assert response.status_code == 200
```

### Deliverables

* Test case generator
* Test code display page

---

## Day 22: Report Page Design

### Work to Do

* Create detailed report page.
* Show all detected issues.
* Add filters by severity.
* Add file-wise issue grouping.

### Filters

```text
All Issues
Low
Medium
High
Critical
Security
Code Quality
Complexity
```

### Deliverables

* Report page
* Filter system
* File-wise issue table

---

## Day 23: Dashboard Charts

### Work to Do

* Add charts using Chart.js.
* Show bug distribution.
* Show severity chart.
* Show code quality score.

### Charts

```text
Severity Pie Chart
Issue Type Bar Chart
File-wise Bug Count
Code Quality Score Chart
```

### Deliverables

* Interactive charts
* Visual dashboard

---

## Day 24: PDF Report Generation

### Work to Do

* Generate downloadable PDF report.
* Include project name, scan date, issue summary, and suggestions.

### PDF Sections

```text
Project Summary
Total Files Scanned
Total Issues Found
Critical Issues
Security Issues
AI Suggestions
Final Score
```

### Deliverables

* PDF report generator
* Download report button

---

## Day 25: GitHub Repository Analysis

### Work to Do

* Add GitHub repository URL input.
* Download or clone public GitHub repo.
* Analyze repo files.

### Features

* GitHub repo link input
* Python file detection
* Repo scan report

### Deliverables

* GitHub analysis module
* Repo scanning feature

---

## Day 26: Project Health Score

### Work to Do

* Create scoring logic.
* Calculate overall project score.

### Example Score Formula

```text
Code Health Score = 100 - Issue Penalty
Critical Issue = -15
High Issue = -10
Medium Issue = -5
Low Issue = -2
```

### Score Categories

```text
90-100: Excellent
75-89: Good
50-74: Needs Improvement
Below 50: Poor
```

### Deliverables

* Code health score
* Score badge
* Improvement suggestions

---

## Day 27: Admin Panel

### Work to Do

* Create admin dashboard.
* Show total users.
* Show total projects.
* Show reports generated.
* Allow admin to view user activity.

### Admin Features

```text
Manage users
View projects
View reports
Delete reports
Monitor scans
```

### Deliverables

* Admin dashboard
* Admin login
* User activity table

---

## Day 28: Error Handling and Validation

### Work to Do

* Add proper error messages.
* Handle invalid file uploads.
* Handle broken ZIP files.
* Handle API failure.
* Handle empty code files.

### Error Examples

```text
Invalid file type
No Python file found
AI service unavailable
File size too large
Project analysis failed
```

### Deliverables

* Error handling
* User-friendly messages
* Backend validation

---

## Day 29: Testing

### Work to Do

* Test all modules.
* Test user registration and login.
* Test file upload.
* Test analysis.
* Test AI suggestions.
* Test report download.

### Testing Types

```text
Unit Testing
Integration Testing
UI Testing
API Testing
Security Testing
```

### Deliverables

* Test cases
* Bug fixing
* Final working project

---

## Day 30: Final Deployment and Documentation

### Work to Do

* Prepare final project documentation.
* Create README file.
* Deploy project.
* Prepare presentation.
* Prepare resume description.

### Deployment Options

```text
Render
Railway
PythonAnywhere
AWS
Docker
```

### Deliverables

* Final project
* README file
* Project report
* PPT
* Resume content
* Deployment link

---

# 5. Final Project Modules

## Module 1: Authentication Module

This module manages user registration, login, logout, and session handling.

## Module 2: Project Upload Module

This module allows users to upload Python files or ZIP projects.

## Module 3: Code Parser Module

This module reads Python files and extracts code structure using AST.

## Module 4: Bug Detection Module

This module detects common bugs and bad coding practices.

## Module 5: Security Scanner Module

This module detects security issues using Bandit and custom rules.

## Module 6: AI Reviewer Module

This module explains the code issues using AI.

## Module 7: Auto-Fix Module

This module generates corrected code suggestions.

## Module 8: ML Severity Module

This module predicts whether a bug is Low, Medium, High, or Critical.

## Module 9: Report Module

This module creates a detailed analysis report and PDF download.

## Module 10: Dashboard Module

This module shows project health score, charts, and statistics.

---

# 6. Resume Description

**CodeGuardian AI – AI-Powered Python Code Review & Bug Detection Platform**
Developed an AI-powered platform that analyzes Python projects to detect bugs, security vulnerabilities, poor coding practices, and missing test cases. Built features such as project ZIP upload, AST-based code parsing, rule-based bug detection, ML-based severity classification, AI-generated code explanation, auto-fix suggestions, dashboard analytics, and PDF report generation. Used Python, Flask/FastAPI, SQLAlchemy, Scikit-learn, Bandit, Ruff, Bootstrap, Chart.js, and LLM APIs.

---

# 7. GitHub README Structure

```text
# CodeGuardian AI

## Overview
AI-powered Python code review and bug detection platform.

## Features
- User authentication
- Python project upload
- Code analysis
- Bug detection
- Security scanning
- AI code explanation
- Auto-fix suggestions
- Severity prediction
- Dashboard
- PDF report generation

## Tech Stack
Python, Flask/FastAPI, SQLAlchemy, SQLite, Scikit-learn, Bandit, Ruff, Bootstrap, Chart.js

## Installation
1. Clone repository
2. Create virtual environment
3. Install requirements
4. Run database migrations
5. Start server

## Usage
Upload Python project and generate code review report.

## Future Scope
- GitHub pull request review
- VS Code extension
- Team collaboration
- CI/CD integration
```

---

# 8. Future Scope

* GitHub pull request auto-review
* VS Code extension
* Team-based code review
* CI/CD pipeline integration
* Auto-generated documentation
* Code refactoring assistant
* API security scanner
* Docker image vulnerability scanner
* Multi-language support for JavaScript, Java, and PHP

---

# 9. Final Outcome

After completing this project, you will have a strong portfolio project that proves your skills in:

* Python development
* Flask/FastAPI backend
* AI integration
* Machine learning
* Code analysis
* Database handling
* Dashboard development
* Report generation
* Real-world software engineering

This project is suitable for **Python Developer**, **AI/ML Engineer**, **Backend Developer**, and **AI Application Developer** roles.
