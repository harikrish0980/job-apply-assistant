# Job Apply Assistant (Safe, Reliable, End-to-End Starter)

This project **automates job discovery + matching + document tailoring + tracking**.
It **does not auto-submit applications** on LinkedIn/Indeed/Dice/Workday (those sites have bot/captcha/ToS constraints).
Instead, it generates **application packets** (tailored resume + cover letter + recruiter message + match report)
and a **one-click “Apply Link” list** so you can submit quickly with a human-in-the-loop.

## What it does
- Pulls jobs from **Greenhouse** and **Lever** public company boards
- Imports jobs from **LinkedIn/Indeed/Dice** via:
  - CSV export / saved-job links (manual export), OR
  - email alert parsing (optional extension)
- Scores jobs vs your profile (truth-locked) and ranks them
- Generates per-job application packet folders:
  - `resume_tailored.docx`
  - `cover_letter.md`
  - `recruiter_message.txt`
  - `match_report.json`
- Tracks everything in a local **SQLite** DB

## Repo scaffold
```
job-apply-assistant/
  README.md
  .env.example
  requirements.txt
  run.sh
  data/
    packets/               # generated output
    db.sqlite3             # auto-created
    templates/
      resume_base.docx     # you provide
      cover_letter.md      # template included
  app/
    __init__.py
    main.py
    config.py
    db.py
    models.py
    schemas.py
    utils.py
    scoring.py
    tailoring.py
    docgen.py
    sources/
      __init__.py
      greenhouse.py
      lever.py
    importers/
      __init__.py
      csv_import.py
  scripts/
    init_db.py
```

---

## Install + run

### A) Create venv + install
```bash
cd job-apply-assistant
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
# .venv\Scripts\activate  # Windows PowerShell

pip install -r requirements.txt
```

### B) Create your .env
```bash
cp .env.example .env
```

### C) Put your base resume template
Place your master resume template at:
```
data/templates/resume_base.docx
```
Optional placeholders supported:
`{{FULL_NAME}} {{EMAIL}} {{PHONE}} {{LOCATION}} {{LINKEDIN}} {{SUMMARY}} {{SKILLS}}`

### D) Run the API
```bash
./run.sh
# or
uvicorn app.main:app --reload
```

Open:
- API docs: http://127.0.0.1:8000/docs

---

## How to use (step-by-step)

### Step 1 — Create your profile (one time)
In Swagger UI (`/docs`) call: **POST `/profile`**

Provide:
- personal details
- skills list
- **truth_bullets**: real bullet points you have actually done (truth lock)

### Step 2 — Add targets (Greenhouse / Lever)
- **POST** `/targets/greenhouse`
- **POST** `/targets/lever`

### Step 3 — Refresh jobs from targets
- **POST** `/jobs/refresh`

### Step 4 — Import LinkedIn / Indeed / Dice jobs (recommended approach)
Because these sites often restrict scraping and automated logins, use **import**:
- Export saved jobs as CSV (or copy/paste job URLs into a CSV)
- Then upload CSV:
  - **POST** `/jobs/import/csv`

CSV columns supported:
`source, company, title, location, url, description`

### Step 5 — Match + rank jobs
- **GET** `/jobs/top?limit=25`

### Step 6 — Generate application packet
- **POST** `/packets/generate/{job_id}`

Output folder:
`data/packets/<company>_<role>_<jobid>/`

---

## Next upgrades 
- Add scoring & cover-letter generation (optional; requires API key)
- Add Workday “public postings” parsers for specific companies (each Workday tenant differs)
- Add email-alert ingestion (Gmail → parse → import jobs)
- Add UI (simple web dashboard)

