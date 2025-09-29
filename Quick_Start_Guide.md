# AI Intelligent Recruitment System - Quick Start Guide

## 🚀 Requirements
- Python 3.8+
- Node.js 16.0+
- Git

## 📦 Quick Installation

### 1. Download Project
```bash
git clone <project-repository-url>
cd AI-intelligent-recruitment-system--Test-Sample
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Configure Environment
Copy `backend/.env.example` to `backend/.env` and configure:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
GOOGLE_AI_API_KEY=your-google-ai-api-key
```

## 🎯 Start System

### Start Backend (Terminal 1)
```bash
cd backend
python manage.py runserver
```
Access: http://localhost:8000

### Start Frontend (Terminal 2)
```bash
cd frontend
npm start
```
Access: http://localhost:3000

## 📋 Main Features
- **Resume Upload**: http://localhost:3000/resume-upload
- **Job Upload**: http://localhost:3000/job-upload  
- **Matching Analysis**: http://localhost:3000/matching (Default homepage)

## ⚡ Common Issues
- **Port in use**: Change port or kill process
- **Dependencies fail**: Use domestic mirrors
- **API errors**: Check `GOOGLE_AI_API_KEY` in `.env` file

## 🔧 Optional Steps
```bash
# Create admin account
python manage.py createsuperuser

# Create demo data
python create_demo_data.py
```

---
**Note**: For detailed instructions, see `安装说明书.md` or `Installation_Guide.md`