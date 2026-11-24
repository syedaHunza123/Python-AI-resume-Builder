# ResumeAI – AI Powered Resume Builder

A modern, full-stack AI Resume Builder web application built with **Python (Flask)**, **SQLite**, **OpenRouter AI**, and **ReportLab PDF generation**.

---

## 🌟 Key Features

1. **AI-Powered Resume Writing Assistant (OpenRouter API)**:
   - **Executive Summary Generator**: Crafts 3-4 sentence summaries based strictly on candidate inputs.
   - **Job Description & Responsibilities Generator**: Suggests industry-standard responsibility bullets.
   - **Experience Improver**: Rewrites duty descriptions into high-impact accomplishment bullets with strong action power verbs.
   - **AI Skills Suggestions**: Intelligent skill categorization (technical, soft, tools, languages) for target roles.
   - **AI Resume Review & Feedback**: Actionable critique, structure evaluation, and scoring.
   - **AI Cover Letter Generator**: Generates customized cover letters pairing verified resume details with job requirements.
   - **Interactive Demo Mode**: Full fallback demo mode if no OpenRouter API key is configured.

2. **5 ATS-Optimized Resume Templates**:
   - **Modern Professional**: Balanced dual-tone colored header, clear hierarchy, and clean typography.
   - **Minimal Clean**: Single-column classic serif design with maximum compatibility across traditional applicant tracking systems.
   - **Corporate Executive**: Structured divider borders and authoritative weight for leadership, consulting, and finance.
   - **Creative Dynamic**: Modern aesthetic with skill badges and portfolio links for creative and product roles.
   - **Developer / Technical**: Monospace tech stack headers, project repositories, and technical competencies.
   - **Zero Data Loss**: Switch between any of the 5 templates instantly.

3. **Real-Time Live A4 Preview**:
   - Split-screen builder with instant typing synchronization into an A4 page view.
   - Live color palette customization and typography settings.

4. **ATS Resume Checker & Keyword Matcher**:
   - Upload existing PDF resumes or paste resume text.
   - Evaluates structure, essential sections, and direct contact details.
   - Compare resume text against any target job description to reveal matching and missing keywords with an estimated match score.

5. **Full Vector PDF Export**:
   - High-resolution, printable A4 PDF export using **ReportLab**.
   - Download resumes and saved cover letters with one click.

6. **Secure User Authentication & Database**:
   - User registration, login, and logout.
   - Passwords hashed using `werkzeug.security` (PBKDF2-SHA256).
   - Foreign-key protected SQLite database (`database.db`).
   - Strict session isolation: users can only view, edit, duplicate, and delete their own resumes.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+ installed.

### 2. Installation
Clone or navigate to the project root directory:
```bash
cd "c:\Users\SONY\Desktop\Python"
```

Install the required Python libraries:
```bash
python -m pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```
Edit `.env` and optionally set your OpenRouter API key:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=meta-llama/llama-3.3-70b-instruct:free
SECRET_KEY=resumeai-super-secret-key-2026
```
*(Note: If `OPENROUTER_API_KEY` is left blank, the app will run in Demo Mode).*

### 4. Database Setup
The SQLite database (`database.db`) is automatically initialized with all tables on first application run.

To verify or initialize manually:
```bash
python -c "from database.db import init_db; init_db(); print('Database schema initialized!')"
```

### 5. Running the Application
Start the Flask development server:
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Running Automated Tests
Run the included unit test suite:
```bash
python test_suite.py
```
Tests cover:
- User registration and authentication hashing.
- Full resume CRUD and duplication operations.
- AI fallback and demo generation logic.
- ATS scanner structure and keyword parsing.
- ReportLab vector PDF generation.
