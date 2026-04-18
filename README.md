# GSC Project 🚀

## 📌 Overview

This project is built for the Google Solution Challenge.
It includes backend APIs, agents, and services for content processing and detection.

---

## 🛠 Tech Stack

* Python
* FastAPI (assumed from structure)
* MongoDB / Database services
* Playwright (for crawling/testing)

---

## 📂 Project Structure

* `app/` → Main application code
* `agents/` → AI/logic agents
* `api/` → API routes
* `services/` → Business logic
* `models/` → Database models

---

## ⚙️ Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/codxrrnikhil/GSC-Project.git
cd GSC-Project
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run backend

```bash
python app/main.py
```

Backend defaults to `http://localhost:8001`.

### 4. Run frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:8000` and calls backend APIs on `http://localhost:8001`.

---

## 📌 Notes

* `.env.example` is provided for environment variables
* `node_modules` and cache files are ignored

---
