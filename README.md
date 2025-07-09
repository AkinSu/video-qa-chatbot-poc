# ChatBot POC: Video Upload App

## Overview
A full-stack app for uploading MP4 (libx264) videos. Built with Next.js (frontend) and FastAPI (backend). Files are stored locally. Environment variables are managed securely with `.env` files.

---

## Project Structure

```
ChatBot POC/
│
├── backend/         # Python FastAPI backend
│   ├── app.py
│   ├── requirements.txt
│   └── .env
│
└── frontend/        # Next.js frontend
    ├── package.json
    ├── .env.local
    └── (Next.js files)
```

---

## Setup Instructions

### 1. Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Edit .env as needed
uvicorn app:app --reload
```

- The backend runs on `http://localhost:8000` by default.

### 2. Frontend (Next.js)

```bash
cd frontend
npm install
cp .env.local.example .env.local  # Edit .env.local as needed
npm run dev
```

- The frontend runs on `http://localhost:3000` by default.

---

## Usage
1. Open the frontend in your browser.
2. Use the upload form to select and upload an MP4 video.
3. The backend saves the file locally in the `backend/uploads/` folder.

---

## Environment Variables
- **Backend:** See `backend/.env.example` for required variables.
- **Frontend:** See `frontend/.env.local.example` for required variables.

---

## Dependencies
- **Backend:** FastAPI, uvicorn, python-dotenv, python-multipart
- **Frontend:** Next.js, axios

---

## .gitignore
- Both backend and frontend have `.gitignore` files to exclude environment files, dependencies, and build artifacts. 