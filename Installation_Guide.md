# AI Intelligent Recruitment System - Installation Guide

## System Overview

The AI Intelligent Recruitment System is an artificial intelligence-based resume and job matching platform that helps companies efficiently screen candidates. The system adopts a front-end and back-end separation architecture, with the back-end using the Django framework and the front-end using the React framework.

## System Requirements

### Hardware Requirements
- **Memory**: Minimum 4GB RAM, recommended 8GB or above
- **Storage**: At least 2GB available disk space
- **Processor**: Modern 64-bit processor

### Software Requirements
- **Operating System**: Windows 10/11, macOS 10.14+, Ubuntu 18.04+
- **Python**: Version 3.8 or above
- **Node.js**: Version 16.0 or above
- **npm**: Version 8.0 or above
- **Git**: For code download

## Environment Setup

### 1. Install Python
1. Visit [Python Official Website](https://www.python.org/downloads/)
2. Download and install Python 3.8+ version
3. Check "Add Python to PATH" during installation
4. Verify installation:
   ```bash
   python --version
   pip --version
   ```

### 2. Install Node.js
1. Visit [Node.js Official Website](https://nodejs.org/)
2. Download and install LTS version
3. Verify installation:
   ```bash
   node --version
   npm --version
   ```

### 3. Install Git
1. Visit [Git Official Website](https://git-scm.com/)
2. Download and install Git
3. Verify installation:
   ```bash
   git --version
   ```

## Project Download

### Method 1: Git Clone (Recommended)
```bash
git clone <project-repository-url>
cd AI-intelligent-recruitment-system--Test-Sample
```

### Method 2: Direct Download
1. Download ZIP file from project repository
2. Extract to target directory
3. Navigate to project root directory

## Backend Environment Setup

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
1. Copy environment variable template:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` file and configure necessary parameters:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   GOOGLE_AI_API_KEY=your-google-ai-api-key
   ```

### 5. Database Initialization
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 7. Create Demo Data (Optional)
```bash
python create_demo_data.py
```

## Frontend Environment Setup

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Node.js Dependencies
```bash
npm install
```

## Project Startup

### 1. Start Backend Service
Execute in backend directory:
```bash
cd backend
python manage.py runserver
```
Backend service will start at `http://localhost:8000`

### 2. Start Frontend Service
Execute in frontend directory:
```bash
cd frontend
npm start
```
Frontend service will start at `http://localhost:3000`

## System Access

### Main Function Pages
- **Homepage**: http://localhost:3000 (Default displays matching analysis page)
- **Resume Upload**: http://localhost:3000/resume-upload
- **Job Description Upload**: http://localhost:3000/job-upload
- **Matching Analysis**: http://localhost:3000/matching
- **Backend Admin**: http://localhost:8000/admin

### System Features
1. **Resume Upload**: Supports PDF, DOC, DOCX formats
2. **Job Description Upload**: Supports text and document formats
3. **Intelligent Matching**: AI-driven resume-job matching analysis
4. **Matching Reports**: Detailed matching analysis and recommendations

## Common Issues

### Q1: Python Dependencies Installation Failed
**Solution**:
- Ensure correct Python version (3.8+)
- Upgrade pip: `pip install --upgrade pip`
- Use domestic mirror: `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/`

### Q2: Node.js Dependencies Installation Failed
**Solution**:
- Ensure correct Node.js version (16.0+)
- Clear cache: `npm cache clean --force`
- Use domestic mirror: `npm install --registry https://registry.npmmirror.com`

### Q3: Port Already in Use
**Solution**:
- Backend port conflict: Modify port settings in `backend/config/settings.py`
- Frontend port conflict: Set environment variable `PORT=3001` before starting

### Q4: Database Connection Error
**Solution**:
- Ensure database migration commands have been executed
- Check database configuration in `.env` file
- Delete `db.sqlite3` file and re-migrate

### Q5: Google AI API Error
**Solution**:
- Ensure correct `GOOGLE_AI_API_KEY` is configured in `.env` file
- Check if API key is valid and has sufficient quota
- Ensure network connection is normal

## Development Mode vs Production Mode

### Development Mode (Current Configuration)
- Frontend: `npm start` - Hot reload for development debugging
- Backend: `python manage.py runserver` - Development server
- Database: SQLite (suitable for development testing)

### Production Mode Deployment
- Frontend: `npm run build` to build static files
- Backend: Use Gunicorn or uWSGI
- Database: PostgreSQL or MySQL
- Web Server: Nginx
- Containerization: Use provided `docker-compose.yml`

## Docker Deployment (Optional)

If you are familiar with Docker, you can use containerized deployment:

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d
```

## Technical Support

### Log File Locations
- Backend logs: `backend/logs/`
- Application logs: `backend/logs/recruitment.log`
- Error logs: `backend/logs/critical_errors.log`

### Troubleshooting Steps
1. Check if all services are started normally
2. View browser console error messages
3. Check backend log files
4. Verify environment variable configuration
5. Confirm network connection and port status

### Contact Support
If you encounter technical issues, please provide the following information:
- Operating system version
- Python and Node.js versions
- Error message screenshots
- Relevant log file contents

---

**Notes**:
- First startup may take longer to download dependencies
- Ensure firewall allows access to relevant ports
- Regularly backup important data
- Please modify default keys and configurations for production environment

**Version**: v1.0.0  
**Last Updated**: December 2024