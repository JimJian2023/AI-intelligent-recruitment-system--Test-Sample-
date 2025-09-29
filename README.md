# AI Intelligent Recruitment System

## 项目概述

基于人工智能技术的智能招聘系统，旨在通过自动匹配候选人与合适职位来简化招聘流程。系统使用先进的算法分析简历、职位要求和候选人档案，提供准确的匹配推荐。

## 技术架构

### 后端技术栈
- **框架**: Django 4.2+ (Python Web框架)
- **数据库**: PostgreSQL (主数据库), Redis (缓存)
- **API**: Django REST Framework
- **认证**: JWT Token 认证
- **任务队列**: Celery (异步任务处理)
- **AI/ML**: scikit-learn, pandas, numpy (匹配算法)
- **跨域**: django-cors-headers

### 前端技术栈
- **框架**: React 18+ (JavaScript库)
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **状态管理**: React Context API
- **HTTP客户端**: Axios
- **路由**: React Router DOM
- **构建工具**: Create React App

### 开发运维
- **容器化**: Docker & Docker Compose
- **Web服务器**: Nginx (反向代理)
- **环境管理**: Python venv, Node.js npm
- **开发工具**: 热重载, 自动重启

## 核心功能模块

### 1. 用户管理系统 (users)
- **多角色认证**: 学生和雇主双重身份
- **档案管理**: 完整的用户档案系统
- **技能评估**: 动态技能评估体系
- **经验追踪**: 工作经验和项目作品集
- **仪表板**: 个性化数据统计面板

### 2. 职位管理系统 (jobs)
- **职位发布**: 富文本职位描述编辑器
- **技能要求**: 详细的技能和经验要求设置
- **申请跟踪**: 实时申请状态追踪
- **职位分类**: 有组织的职位分类体系
- **职位提醒**: 个性化职位推送服务

### 3. 智能匹配引擎 (matching)
- **AI驱动匹配**: 先进的候选人-职位匹配算法
- **多维度分析**: 技能、经验、教育背景、地理位置
- **评分系统**: 综合匹配分数计算
- **推荐引擎**: 个性化职位/候选人推荐
- **批量匹配**: 支持大规模批量匹配任务

### 4. 申请管理系统 (applications)
- **申请工作流**: 完整的申请生命周期管理
- **状态跟踪**: 实时申请状态更新
- **面试安排**: 集成面试管理功能
- **反馈系统**: 雇主和候选人反馈收集
- **申请统计**: 详细的申请数据分析

### 5. 简历管理系统 (resumes)
- **简历上传**: 支持多种文件格式
- **简历解析**: 自动信息提取
- **档案集成**: 无缝档案同步
- **版本控制**: 简历历史记录和更新

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+ (可选，默认使用SQLite)
- Redis 6+ (可选，用于缓存)

### 安装选项

#### 选项1: 一键安装 (推荐)
```bash
# 首次安装
首次安装.bat          # 中文版Windows
setup.bat            # 英文版Windows

# 启动应用
启动项目.bat          # 中文版Windows
start.bat            # 英文版Windows

# 停止应用
停止项目.bat          # 中文版Windows
stop.bat             # 英文版Windows
```

#### 选项2: 手动安装
```bash
# 1. 克隆仓库
git clone <repository-url>
cd AI-intelligent-recruitment-system

# 2. 后端设置
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser

# 3. 前端设置
cd ../frontend
npm install

# 4. 环境配置
copy .env.example .env
# 编辑 .env 文件配置数据库和Redis

# 5. 启动服务
# 后端 (终端1)
cd backend
python manage.py runserver

# 前端 (终端2)
cd frontend
npm start
```

#### 选项3: Docker部署
```bash
# 构建并启动所有服务
docker-compose up --build

# 后台运行
docker-compose up -d

# 停止服务
docker-compose down
```

### 访问应用
- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000
- **管理后台**: http://localhost:8000/admin
- **API文档**: http://localhost:8000/api/

## 项目结构

```
AI-intelligent-recruitment-system/
├── backend/                    # Django 后端
│   ├── config/                # Django 配置和设置
│   │   ├── settings.py       # 主要设置文件
│   │   ├── urls.py           # URL路由配置
│   │   └── wsgi.py           # WSGI配置
│   ├── users/                 # 用户管理应用
│   │   ├── models.py         # 用户模型 (User, StudentProfile, EmployerProfile)
│   │   ├── views.py          # 用户视图和API
│   │   └── serializers.py    # 数据序列化器
│   ├── jobs/                  # 职位管理应用
│   │   ├── models.py         # 职位模型 (Job, JobCategory, JobAlert)
│   │   ├── views.py          # 职位API视图
│   │   └── serializers.py    # 职位数据序列化
│   ├── applications/          # 申请管理应用
│   │   ├── models.py         # 申请模型 (Application, Interview, Feedback)
│   │   ├── views.py          # 申请处理API
│   │   └── serializers.py    # 申请数据序列化
│   ├── matching/              # 智能匹配引擎
│   │   ├── models.py         # 匹配模型 (MatchResult, SkillMatchDetail)
│   │   ├── views.py          # 匹配API视图
│   │   ├── services.py       # 匹配服务逻辑
│   │   ├── algorithms.py     # 匹配算法实现
│   │   └── demo_views.py     # 演示模式API
│   ├── resumes/               # 简历管理应用
│   │   ├── models.py         # 简历模型 (Resume)
│   │   └── views.py          # 简历API
│   ├── requirements.txt       # Python依赖包
│   ├── create_demo_data.py   # 演示数据创建脚本
│   └── manage.py             # Django管理脚本
├── frontend/                  # React 前端
│   ├── src/
│   │   ├── components/       # 可复用React组件
│   │   │   ├── Layout.tsx    # 布局组件
│   │   │   └── auth/         # 认证相关组件
│   │   ├── pages/           # 页面组件
│   │   │   ├── Dashboard.tsx # 仪表板页面
│   │   │   └── JobList.tsx   # 职位列表页面
│   │   ├── types/           # TypeScript类型定义
│   │   │   └── index.ts     # 主要类型接口
│   │   ├── utils/           # 工具函数
│   │   └── App.tsx          # 主应用组件
│   ├── package.json         # Node.js依赖配置
│   ├── tailwind.config.js   # Tailwind CSS配置
│   └── tsconfig.json        # TypeScript配置
├── docs/                    # 项目文档
│   ├── Installation_Guide.md    # 详细安装指南 (英文)
│   ├── Quick_Start_Guide.md     # 快速启动指南 (英文)
│   ├── 安装说明书.md            # 详细安装指南 (中文)
│   └── 快速启动指南.md          # 快速启动指南 (中文)
├── scripts/                 # 自动化脚本
│   ├── setup.bat           # Windows安装脚本 (英文)
│   ├── start.bat           # Windows启动脚本 (英文)
│   ├── stop.bat            # Windows停止脚本 (英文)
│   ├── 首次安装.bat         # Windows安装脚本 (中文)
│   ├── 启动项目.bat         # Windows启动脚本 (中文)
│   └── 停止项目.bat         # Windows停止脚本 (中文)
├── docker-compose.yml      # Docker服务配置
├── .env.example           # 环境变量模板
└── README.md             # 项目说明文档
```

## API接口文档

### 认证接口
- `POST /api/users/register/` - 用户注册
- `POST /api/users/login/` - 用户登录
- `POST /api/users/logout/` - 用户登出
- `GET /api/users/profile/` - 获取用户档案
- `GET /api/users/dashboard/` - 获取仪表板数据

### 职位管理接口
- `GET /api/jobs/` - 获取职位列表
- `POST /api/jobs/` - 创建新职位 (仅雇主)
- `GET /api/jobs/{id}/` - 获取职位详情
- `PUT /api/jobs/{id}/` - 更新职位 (仅雇主)
- `DELETE /api/jobs/{id}/` - 删除职位 (仅雇主)
- `GET /api/jobs/categories/` - 获取职位分类

### 申请管理接口
- `GET /api/applications/` - 获取用户申请列表
- `POST /api/applications/` - 提交职位申请
- `GET /api/applications/{id}/` - 获取申请详情
- `PUT /api/applications/{id}/status/` - 更新申请状态
- `GET /api/applications/statistics/` - 获取申请统计

### 智能匹配接口
- `POST /api/matching/calculate/` - 计算职位-候选人匹配度
- `POST /api/matching/batch-calculate/` - 批量计算匹配度
- `GET /api/matching/results/` - 获取匹配结果
- `GET /api/matching/statistics/` - 获取匹配统计
- `GET /api/matching/recommendations/` - 获取个性化推荐

### 简历管理接口
- `GET /api/resumes/` - 获取简历列表
- `POST /api/resumes/` - 上传新简历
- `GET /api/resumes/{id}/` - 获取简历详情
- `POST /api/matching/demo/analyze/` - 演示模式匹配分析

## 演示数据

系统包含完整的演示数据用于测试：

```bash
# 创建演示数据 (初始安装后)
cd backend
python create_demo_data.py
```

**演示账户:**
- **学生账户**: demo_student@example.com / password123
- **雇主账户**: demo_employer@example.com / password123
- **管理员**: admin@example.com / admin123

**演示数据包含:**
- 10个学生档案 (包含技能、教育背景、项目经验)
- 5个雇主档案 (不同行业和公司规模)
- 15个职位 (涵盖前端、后端、全栈、数据科学等)
- 30个技能标签 (编程语言、框架、工具等)
- 完整的匹配关系和申请记录

## 匹配算法详解

AI匹配系统采用多因子算法：

### 算法权重分配
1. **技能匹配 (40%)**: 精确和相关技能匹配
2. **经验水平 (25%)**: 工作年限匹配度
3. **教育背景 (20%)**: 学历和专业领域匹配
4. **地理位置 (10%)**: 地理兼容性
5. **附加因素 (5%)**: 薪资期望、工作类型偏好

### 匹配分数解释
- **90-100%**: 优秀匹配 - 强烈推荐
- **80-89%**: 很好匹配 - 优质候选人
- **70-79%**: 良好匹配 - 值得考虑
- **60-69%**: 一般匹配 - 有发展潜力
- **60%以下**: 匹配度低 - 不推荐

### 算法特性
- **实时计算**: 支持实时匹配分析
- **批量处理**: 支持大规模批量匹配
- **可配置权重**: 支持自定义算法参数
- **缓存优化**: 智能缓存提升性能

## 开发路线图

### 第一阶段: 核心系统 ✅
- [x] 用户认证和档案管理
- [x] 职位发布和管理
- [x] 基础匹配算法
- [x] 申请工作流程
- [x] 简历管理系统

### 第二阶段: AI增强 🚧
- [x] 高级匹配算法
- [x] 简历解析和分析
- [x] 演示模式和数据
- [ ] 职位描述自然语言处理
- [ ] 机器学习模型训练

### 第三阶段: 高级功能 📋
- [ ] 视频面试集成
- [ ] 技能评估测试
- [ ] 分析和报告仪表板
- [ ] 移动应用程序
- [ ] 第三方集成API

### 第四阶段: 企业功能 📋
- [ ] 多租户架构
- [ ] 高级分析和洞察
- [ ] HR系统集成
- [ ] 白标解决方案

## 部署选项

### 开发环境
- 使用提供的批处理脚本快速设置
- 前后端热重载功能
- 调试模式和详细错误信息
- SQLite数据库 (无需额外配置)

### 生产环境
- 基于Docker的部署和Nginx反向代理
- PostgreSQL数据库连接池
- Redis缓存和会话管理
- SSL/TLS加密
- 基于环境的配置管理

### 云部署
- AWS/Azure/GCP兼容
- Kubernetes部署清单
- CI/CD流水线集成
- 自动扩缩容配置

## 贡献指南

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发规范
- Python代码遵循 PEP 8 规范
- 前端新代码使用 TypeScript
- 为新功能编写单元测试
- API更改时更新文档

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 技术支持

获取支持和帮助：
- 在GitHub仓库中创建issue
- 邮箱: support@ai-recruitment-system.com
- 文档: [项目Wiki](wiki-link)

## 致谢

- Django 和 React 社区提供的优秀框架
- scikit-learn 提供的机器学习能力
- Tailwind CSS 提供的美观UI组件
- 所有帮助构建此系统的贡献者