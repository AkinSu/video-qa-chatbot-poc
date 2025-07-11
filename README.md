# ChatBot POC: Video Upload App



## Setup Instructions

### 1. Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  
uvicorn app:app --reload
```

- The backend runs on `http://localhost:8000` by default.

### 2. Frontend (Next.js)

```bash
cd frontend
npm install
cp .env.local.example .env.local 
npm run dev
```

- The frontend runs on `http://localhost:3000` by default.

---

## .gitignore