# Installation Guide - Story Creator

## System Requirements
- **Python**: 3.7+ (recommended: 3.11+)
- **Node.js**: 18+
- **RAM**: 1GB+
- **OS**: Windows 10/11, macOS, or Linux

## 1. Clone the Repository
```bash
git clone <your-repo-url>
cd story-creator
```

## 2. Python Environment Setup
```bash
python -m venv .venv
.venv/Scripts/activate  # Windows
# or
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

## 3. Node.js Frontend Setup
```bash
cd frontend
npm install
cd ..
```

## 4. GPT API Key (Optional, for AI features)
- Create a `.env` file in the project root:
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
- Get your key from https://platform.openai.com/

## 5. Run the Application
- **Full stack (recommended):**
```bash
npm run dev
```
- **Or, run backend and frontend separately:**
```bash
python main.py -i api
cd frontend && npm run dev
```

## 6. Access
- React UI: http://localhost:3000
- API Swagger: http://localhost:5000/api/docs
