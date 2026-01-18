# Quick Start - React Frontend

## 1. Start Full Stack (Recommended)
```bash
npm run dev
# Runs both backend (API) and frontend together
```

## 2. Start Backend or Frontend Separately
```bash
# Backend only
python main.py -i api
# Frontend only
cd frontend && npm run dev
```

## 3. Useful Scripts
- `npm run dev` - Full stack (API + React)
- `npm run dev:backend` - API only
- `npm run dev:frontend` - React only
- `npm run install:all` - Install all dependencies

## 4. Main Files
- `frontend/src/` - React components
- `interfaces/web_interface.py` - Flask API
- `services/` - Business logic
- `storage/` - NoSQL/JSON storage
