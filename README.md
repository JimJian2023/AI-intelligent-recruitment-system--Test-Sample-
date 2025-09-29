# AI Intelligent Recruitment System

## Project Overview

An AI-powered intelligent recruitment system designed to streamline the hiring process by automatically matching candidates with suitable positions. The system uses advanced algorithms to analyze resumes, job requirements, and candidate profiles to provide accurate matching recommendations.

## Technical Architecture

### Backend Technology Stack
- **Framework**: Django 4.2+ (Python Web Framework)
- **Database**: PostgreSQL (Primary Database), Redis (Cache)
- **API**: Django REST Framework
- **Authentication**: JWT Token Authentication
- **Task Queue**: Celery (Asynchronous Task Processing)
- **AI/ML**: scikit-learn, pandas, numpy (Matching Algorithms)
- **CORS**: django-cors-headers

### Frontend Technology Stack
- **Framework**: React 18+ (JavaScript Library)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Routing**: React Router DOM
- **Build Tool**: Create React App

### Development & Operations
- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx (Reverse Proxy)
- **Environment Management**: Python venv, Node.js npm
- **Development Tools**: Hot Reload, Auto Restart

## Core Feature Modules

### 1. User Management System (users)

- **Profile Management**: Complete user profile system
- **Skill Assessment**: Dynamic skill evaluation system
- **Experience Tracking**: Work experience and project portfolio


### 2. Job Management System (jobs)
- **Job Posting**: Rich text job description editor
- **Skill Requirements**: Detailed skill and experience requirement settings



### 3. Intelligent Matching Engine (matching)
- **AI-Driven Matching**: Advanced candidate-job matching algorithms
- **Multi-dimensional Analysis**: Skills, experience, education, location
- **Scoring System**: Comprehensive match score calculation
- **Recommendation Engine**: Personalized job/candidate recommendations
- **Batch Matching**: Support for large-scale batch matching tasks

### 4. Application Management System (applications)
- **Application Workflow**: Complete application lifecycle management
- **Status Tracking**: Real-time application status updates
- **Interview Scheduling**: Integrated interview management functionality
- **Feedback System**: Employer and candidate feedback collection
- **Application Statistics**: Detailed application data analysis

### 5. Resume Management System (resumes)
- **Resume Upload**: Support for multiple file formats
- **Resume Parsing**: Automatic information extraction
- **Profile Integration**: Seamless profile synchronization
- **Version Control**: Resume history and updates

## Quick Start

### System Requirements
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+ (Optional, SQLite used by default)
- Redis 6+ (Optional, for caching)

### Installation Options

#### Option 1: One-Click Installation (Recommended)
```bash
# Initial Setup
首次安装.bat          # Chinese Windows
setup.bat            # English Windows

# Start Application
启动项目.bat          # Chinese Windows
start.bat            # English Windows

# Stop Application
停止项目.bat          # Chinese Windows
stop.bat             # English Windows
```

#### Option 2: Manual Installation
```bash
# 1. Clone Repository
git clone <repository-url>
cd AI-intelligent-recruitment-system

# 2. Backend Setup
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser

# 3. Frontend Setup
cd ../frontend
npm install

# 4. Environment Configuration
copy .env.example .env
# Edit .env file to configure database and Redis

# 5. Start Services
# Backend (Terminal 1)
cd backend
python manage.py runserver

# Frontend (Terminal 2)
cd frontend
npm start
```

#### Option 3: Docker Deployment
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# Stop services
docker-compose down
```

### Access Application
- **Frontend Interface**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/api/

## Project Structure

```
AI-intelligent-recruitment-system/
├── backend/                    # Django Backend
│   ├── config/                # Django Configuration and Settings
│   │   ├── settings.py       # Main Settings File
│   │   ├── urls.py           # URL Routing Configuration
│   │   └── wsgi.py           # WSGI Configuration
│   ├── users/                 # User Management App
│   │   ├── models.py         # User Models (User, StudentProfile, EmployerProfile)
│   │   ├── views.py          # User Views and APIs
│   │   └── serializers.py    # Data Serializers
│   ├── jobs/                  # Job Management App
│   │   ├── models.py         # Job Models (Job, JobCategory, JobAlert)
│   │   ├── views.py          # Job API Views
│   │   └── serializers.py    # Job Data Serialization
│   ├── applications/          # Application Management App
│   │   ├── models.py         # Application Models (Application, Interview, Feedback)
│   │   ├── views.py          # Application Processing APIs
│   │   └── serializers.py    # Application Data Serialization
│   ├── matching/              # Intelligent Matching Engine
│   │   ├── models.py         # Matching Models (MatchResult, SkillMatchDetail)
│   │   ├── views.py          # Matching API Views
│   │   ├── services.py       # Matching Service Logic
│   │   ├── algorithms.py     # Matching Algorithm Implementation
│   │   └── demo_views.py     # Demo Mode APIs
│   ├── resumes/               # Resume Management App
│   │   ├── models.py         # Resume Models (Resume)
│   │   └── views.py          # Resume APIs
│   ├── requirements.txt       # Python Dependencies
│   ├── create_demo_data.py   # Demo Data Creation Script
│   └── manage.py             # Django Management Script
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── components/       # Reusable React Components
│   │   │   ├── Layout.tsx    # Layout Component
│   │   │   └── auth/         # Authentication Related Components
│   │   ├── pages/           # Page Components
│   │   │   ├── Dashboard.tsx # Dashboard Page
│   │   │   └── JobList.tsx   # Job List Page
│   │   ├── types/           # TypeScript Type Definitions
│   │   │   └── index.ts     # Main Type Interfaces
│   │   ├── utils/           # Utility Functions
│   │   └── App.tsx          # Main Application Component
│   ├── package.json         # Node.js Dependencies Configuration
│   ├── tailwind.config.js   # Tailwind CSS Configuration
│   └── tsconfig.json        # TypeScript Configuration
├── docs/                    # Project Documentation
│   ├── Installation_Guide.md    # Detailed Installation Guide (English)
│   ├── Quick_Start_Guide.md     # Quick Start Guide (English)
│   ├── 安装说明书.md            # Detailed Installation Guide (Chinese)
│   └── 快速启动指南.md          # Quick Start Guide (Chinese)
├── scripts/                 # Automation Scripts
│   ├── setup.bat           # Windows Installation Script (English)
│   ├── start.bat           # Windows Start Script (English)
│   ├── stop.bat            # Windows Stop Script (English)
│   ├── 首次安装.bat         # Windows Installation Script (Chinese)
│   ├── 启动项目.bat         # Windows Start Script (Chinese)
│   └── 停止项目.bat         # Windows Stop Script (Chinese)
├── docker-compose.yml      # Docker Services Configuration
├── .env.example           # Environment Variables Template
└── README.md             # Project Documentation
```

## API Documentation

### Authentication APIs
- `POST /api/users/register/` - User Registration
- `POST /api/users/login/` - User Login
- `POST /api/users/logout/` - User Logout
- `GET /api/users/profile/` - Get User Profile
- `GET /api/users/dashboard/` - Get Dashboard Data

### Job Management APIs
- `GET /api/jobs/` - Get Job List
- `POST /api/jobs/` - Create New Job (Employers Only)
- `GET /api/jobs/{id}/` - Get Job Details
- `PUT /api/jobs/{id}/` - Update Job (Employers Only)
- `DELETE /api/jobs/{id}/` - Delete Job (Employers Only)
- `GET /api/jobs/categories/` - Get Job Categories

### Application Management APIs
- `GET /api/applications/` - Get User Application List
- `POST /api/applications/` - Submit Job Application
- `GET /api/applications/{id}/` - Get Application Details
- `PUT /api/applications/{id}/status/` - Update Application Status
- `GET /api/applications/statistics/` - Get Application Statistics

### Intelligent Matching APIs
- `POST /api/matching/calculate/` - Calculate Job-Candidate Match
- `POST /api/matching/batch-calculate/` - Batch Calculate Matches
- `GET /api/matching/results/` - Get Match Results
- `GET /api/matching/statistics/` - Get Match Statistics
- `GET /api/matching/recommendations/` - Get Personalized Recommendations

### Resume Management APIs
- `GET /api/resumes/` - Get Resume List
- `POST /api/resumes/` - Upload New Resume
- `GET /api/resumes/{id}/` - Get Resume Details
- `POST /api/matching/demo/analyze/` - Demo Mode Match Analysis

## Demo Data

The system includes comprehensive demo data for testing:

```bash
# Create demo data (after initial installation)
cd backend
python create_demo_data.py
```

**Demo Accounts:**
- **Student Account**: demo_student@example.com / password123
- **Employer Account**: demo_employer@example.com / password123
- **Administrator**: admin@example.com / admin123

**Demo Data Includes:**
- 10 student profiles (with skills, education, project experience)
- 5 employer profiles (different industries and company sizes)
- 15 job positions (covering frontend, backend, full-stack, data science, etc.)
- 30 skill tags (programming languages, frameworks, tools, etc.)
- Complete matching relationships and application records

## Matching Algorithm Details

The AI matching system uses a multi-factor algorithm:

### Algorithm Weight Distribution
1. **Skill Matching (40%)**: Exact and related skill matching
2. **Experience Level (25%)**: Work experience matching
3. **Educational Background (20%)**: Degree and field matching
4. **Geographic Location (10%)**: Geographic compatibility
5. **Additional Factors (5%)**: Salary expectations, work type preferences

### Match Score Interpretation
- **90-100%**: Excellent Match - Highly Recommended
- **80-89%**: Very Good Match - Quality Candidate
- **70-79%**: Good Match - Worth Considering
- **60-69%**: Fair Match - Has Potential
- **Below 60%**: Low Match - Not Recommended

### Algorithm Features
- **Real-time Calculation**: Supports real-time match analysis
- **Batch Processing**: Supports large-scale batch matching
- **Configurable Weights**: Supports custom algorithm parameters
- **Cache Optimization**: Smart caching for improved performance

## Development Roadmap

### Phase 1: Core System ✅
- [x] User authentication and profile management
- [x] Job posting and management
- [x] Basic matching algorithms
- [x] Application workflow
- [x] Resume management system

### Phase 2: AI Enhancement 🚧
- [x] Advanced matching algorithms
- [x] Resume parsing and analysis
- [x] Demo mode and data
- [ ] Job description natural language processing
- [ ] Machine learning model training



## Deployment Options

### Development Environment
- Use provided batch scripts for quick setup
- Frontend and backend hot reload functionality
- Debug mode with detailed error information
- SQLite database (no additional configuration required)

### Production Environment
- Docker-based deployment with Nginx reverse proxy
- PostgreSQL database connection pooling
- Redis caching and session management
- SSL/TLS encryption
- Environment-based configuration management

### Cloud Deployment
- AWS/Azure/GCP compatible
- Kubernetes deployment manifests
- CI/CD pipeline integration
- Auto-scaling configuration

## Contributing Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Create a Pull Request

### Development Standards
- Python code follows PEP 8 standards
- Use TypeScript for new frontend code
- Write unit tests for new features
- Update documentation when making API changes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Technical Support

Get support and help:
- Create issues in the GitHub repository
- Email: support@ai-recruitment-system.com
- Documentation: [Project Wiki](wiki-link)

## Acknowledgments

- Django and React communities for excellent frameworks
- scikit-learn for machine learning capabilities
- Tailwind CSS for beautiful UI components
- All contributors who helped build this system