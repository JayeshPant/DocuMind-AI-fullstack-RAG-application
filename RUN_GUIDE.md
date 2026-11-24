# Quick Start & Run Guide for External Users

Welcome to **DocuMind AI** (*Your Intelligent PDF Question Answering Assistant*). 

This guide provides step-by-step instructions to run the project on your own device (Windows, macOS, or Linux).

---

## 📋 Prerequisites

Before starting, ensure you have the following installed on your machine:

1. **Python 3.10 or higher**  
   👉 [Download Python](https://www.python.org/downloads/) *(On Windows, make sure to check "Add Python to PATH" during installation)*.
2. **Node.js 18 or higher & npm**  
   👉 [Download Node.js](https://nodejs.org/)
3. **Git**  
   👉 [Download Git](https://git-scm.com/)
4. **NVIDIA API Key** (Free)  
   👉 Get a free key at [build.nvidia.com](https://build.nvidia.com/) (sign in, click on any model like `meta/llama-3.3-70b-instruct` or `nvidia/nemotron-3.5-lightning-30b-a3b`, and click **Generate API Key**).

---

## 🚀 Quick Setup (Choose Your Operating System)

### For Windows (PowerShell)

#### 1. Clone the Repository
```powershell
git clone <repository-url>
cd "RAG application"
```

#### 2. Set Up the Python Virtual Environment & Dependencies
```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# If PowerShell blocks script activation, run:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Install backend dependencies
pip install -r requirements.txt
```

#### 3. Configure Your API Key
Copy the template `.env.example` file to `.env`:
```powershell
Copy-Item .env.example .env
Copy-Item .env.example backend\.env
```
Open `.env` (or `backend\.env`) in any text editor (Notepad, VS Code) and add your NVIDIA API key:
```env
NVIDIA_API_KEY=nvapi-your-actual-key-here
```

#### 4. Install Frontend Dependencies
```powershell
cd frontend
npm install
cd ..
```

---

### For macOS / Linux (Bash / Zsh)

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd "RAG application"
```

#### 2. Set Up the Python Virtual Environment & Dependencies
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt
```

#### 3. Configure Your API Key
```bash
cp .env.example .env
cp .env.example backend/.env
```
Open `.env` (or `backend/.env`) and insert your NVIDIA key:
```env
NVIDIA_API_KEY=nvapi-your-actual-key-here
```

#### 4. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## 🏃 Running the Application

You can run DocuMind AI in two ways:

### Option A: Complete Web Application (Recommended)

Open **two separate terminal windows**:

#### Terminal 1 — Start FastAPI Backend:
* **Windows (PowerShell)**:
  ```powershell
  $env:PYTHONPATH="."
  .\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --port 8000
  ```
* **macOS / Linux**:
  ```bash
  export PYTHONPATH="."
  uvicorn backend.app.main:app --reload --port 8000
  ```
*(Backend API documentation will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs))*

#### Terminal 2 — Start React Web Interface:
```bash
cd frontend
npm run dev
```

#### 🎉 Open Your Browser:
Visit **[http://localhost:5173](http://localhost:5173)** to interact with DocuMind AI!

---

### Option B: Standalone Terminal CLI Script

If you only want to test the original RAG terminal pipeline without running the web UI:

```powershell
# Windows
python main.py

# macOS / Linux
python3 main.py
```
This directly loads `document_loader/STATS.pdf`, creates text chunks, computes embeddings in memory, and prints the generated tutor answer directly in your terminal.

---

## 🧪 Running Automated Tests

To run the automated test suite verifying PDF extraction, question number parsing, and RAG isolation:

```powershell
# Windows
$env:PYTHONPATH="."
.\.venv\Scripts\pytest.exe backend/tests/ -v

# macOS / Linux
export PYTHONPATH="."
pytest backend/tests/ -v
```

---

## 💡 How to Use the Web Application

1. **Active Preloaded Document**:
   * The application automatically preloads `STATS.pdf` on startup.
2. **Ask by Question Number** (Primary Feature):
   * Select **Ask by Question Number**.
   * Enter a question number (e.g., `1`, `2`, or `5`) and click **Find and Answer Question**.
   * DocuMind extracts the exact question text from the PDF and synthesizes a grounded tutor response.
3. **Ask Anything**:
   * Select **Ask Anything (Free Text)** to ask any open-ended statistical question.
4. **Inspect Sources**:
   * Expand the **Retrieved Document Evidence** cards under any answer to inspect the exact citations and page numbers.
5. **Upload Your Own PDFs**:
   * Click **Documents** in the navigation bar to drag and drop your own PDF documents up to 25MB.
6. **Interaction History**:
   * Click the clock/history icon in the top-right header to review previous interactions.

---

## ❓ Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `Execution of scripts is disabled on this system` | Windows PowerShell execution policy | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in PowerShell before activating `.venv`. |
| `NVIDIA_API_KEY is missing or empty` | `.env` file not created or key missing | Ensure `.env` exists in either root or `backend/.env` with `NVIDIA_API_KEY=nvapi-...`. |
| `Port 8000 or 5173 already in use` | Another process is occupying the port | Change the port or terminate the conflicting process (e.g. `--port 8001`). |
| `Cannot find module 'backend'` | `PYTHONPATH` not set | Always run with `$env:PYTHONPATH="."` (Windows) or `export PYTHONPATH="."` (Linux/Mac). |
