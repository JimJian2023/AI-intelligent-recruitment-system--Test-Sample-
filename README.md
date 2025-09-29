# AI智能招聘系统 - Summer of Tech 2026

## 🎯 项目概述

基于AI的智能招聘匹配系统，专为Summer of Tech项目设计，解决学生与雇主之间的技能匹配和申请流程优化问题。

## 🏗️ 技术架构

### 前端
- **框架**: React 18 + TypeScript
- **样式**: Tailwind CSS
- **状态管理**: Zustand
- **HTTP客户端**: Axios
- **路由**: React Router

### 后端
- **框架**: Django 4.2 + Django REST Framework
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **认证**: Django内置用户系统 + JWT
- **API文档**: Django REST Framework Browsable API

### AI/ML
- **机器学习**: scikit-learn + pandas
- **数据处理**: NumPy
- **匹配算法**: 余弦相似度 + 权重评分

### 部署
- **容器化**: Docker + Docker Compose
- **前端部署**: Vercel/Netlify
- **后端部署**: Railway/Render

## 📋 核心功能

### 1. 智能匹配系统
- 基于技能标签的相似度计算
- 多维度匹配评分（技能、经验、偏好）
- 双向推荐（学生↔雇主）

### 2. 用户管理
- 学生档案管理（技能、项目、偏好）
- 雇主档案管理（公司信息、职位需求）
- 权限控制和数据安全

### 3. 申请流程
- 智能职位推荐
- 一键申请功能
- 申请状态跟踪

### 4. 数据可视化
- 匹配度仪表板
- 申请统计分析
- 系统使用报告

## 🚀 快速开始

### 环境要求
- Python 3.9+
- Node.js 18+
- Docker (可选)

### 本地开发

1. **克隆项目**
```bash
git clone <repository-url>
cd AI-intelligent-recruitment-system--Test-Sample
```

2. **启动后端**
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

3. **启动前端**
```bash
cd frontend
npm install
npm start
```

4. **使用Docker**
```bash
docker-compose up -d
```

## 📁 项目结构

```
AI-intelligent-recruitment-system--Test-Sample/
├── backend/                 # Django后端
│   ├── config/             # 项目配置
│   ├── apps/               # 应用模块
│   │   ├── users/          # 用户管理
│   │   ├── matching/       # 匹配算法
│   │   ├── jobs/           # 职位管理
│   │   └── applications/   # 申请管理
│   ├── ml_models/          # AI模型
│   └── requirements.txt    # Python依赖
├── frontend/               # React前端
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── pages/          # 页面
│   │   ├── services/       # API服务
│   │   └── utils/          # 工具函数
│   └── package.json        # Node依赖
├── docker-compose.yml      # Docker配置
└── README.md              # 项目说明
```

## 🎨 演示数据

系统包含预设的演示数据：
- 15个虚拟学生档案
- 8个虚拟雇主和职位
- 技能库（Web开发、数据科学、移动开发等）

## 📊 匹配算法

### 核心算法
```python
def calculate_match_score(student_skills, job_requirements):
    # 技能重叠度 (40%)
    skill_overlap = len(set(student_skills) & set(job_requirements))
    skill_score = skill_overlap / len(job_requirements) * 0.4
    
    # 经验匹配度 (30%)
    experience_score = calculate_experience_match() * 0.3
    
    # 学习意愿度 (20%)
    learning_score = calculate_learning_preference() * 0.2
    
    # 地理位置 (10%)
    location_score = calculate_location_match() * 0.1
    
    return (skill_score + experience_score + learning_score + location_score) * 100
```

## 🔧 开发计划

- [x] 项目结构搭建
- [ ] Django后端开发
- [ ] 智能匹配算法实现
- [ ] React前端开发
- [ ] 用户界面实现
- [ ] 集成测试和部署

## 📝 许可证

MIT License

## 👥 贡献者

- 开发团队：AI智能招聘系统开发组
- 项目周期：2024年12月