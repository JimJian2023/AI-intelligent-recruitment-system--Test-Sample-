#!/usr/bin/env python
"""
创建演示数据脚本
用于生成测试用的学生、雇主、职位和技能数据
"""
import os
import sys
import django
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import StudentProfile, EmployerProfile, Skill, StudentSkill, Project
from jobs.models import Job, JobSkillRequirement, JobSkillPreference, JobCategory

User = get_user_model()

def create_skills():
    """创建技能数据"""
    skills_data = [
        # 编程语言
        {'name': 'Python', 'category': 'programming', 'description': 'Python编程语言'},
        {'name': 'Java', 'category': 'programming', 'description': 'Java编程语言'},
        {'name': 'JavaScript', 'category': 'programming', 'description': 'JavaScript编程语言'},
        {'name': 'C++', 'category': 'programming', 'description': 'C++编程语言'},
        {'name': 'Go', 'category': 'programming', 'description': 'Go编程语言'},
        {'name': 'Rust', 'category': 'programming', 'description': 'Rust编程语言'},
        
        # 前端技术
        {'name': 'React', 'category': 'frontend', 'description': 'React前端框架'},
        {'name': 'Vue.js', 'category': 'frontend', 'description': 'Vue.js前端框架'},
        {'name': 'Angular', 'category': 'frontend', 'description': 'Angular前端框架'},
        {'name': 'HTML/CSS', 'category': 'frontend', 'description': 'HTML和CSS技术'},
        {'name': 'TypeScript', 'category': 'frontend', 'description': 'TypeScript编程语言'},
        
        # 后端技术
        {'name': 'Django', 'category': 'backend', 'description': 'Django Web框架'},
        {'name': 'Spring Boot', 'category': 'backend', 'description': 'Spring Boot框架'},
        {'name': 'Node.js', 'category': 'backend', 'description': 'Node.js运行环境'},
        {'name': 'Express.js', 'category': 'backend', 'description': 'Express.js框架'},
        
        # 数据库
        {'name': 'MySQL', 'category': 'database', 'description': 'MySQL数据库'},
        {'name': 'PostgreSQL', 'category': 'database', 'description': 'PostgreSQL数据库'},
        {'name': 'MongoDB', 'category': 'database', 'description': 'MongoDB数据库'},
        {'name': 'Redis', 'category': 'database', 'description': 'Redis缓存数据库'},
        
        # 云服务和DevOps
        {'name': 'AWS', 'category': 'cloud', 'description': 'Amazon Web Services'},
        {'name': 'Docker', 'category': 'devops', 'description': 'Docker容器技术'},
        {'name': 'Kubernetes', 'category': 'devops', 'description': 'Kubernetes容器编排'},
        {'name': 'Git', 'category': 'tools', 'description': 'Git版本控制'},
        
        # 数据科学和AI
        {'name': '机器学习', 'category': 'ai', 'description': '机器学习技术'},
        {'name': '深度学习', 'category': 'ai', 'description': '深度学习技术'},
        {'name': '数据分析', 'category': 'data', 'description': '数据分析技能'},
        {'name': 'TensorFlow', 'category': 'ai', 'description': 'TensorFlow机器学习框架'},
        {'name': 'PyTorch', 'category': 'ai', 'description': 'PyTorch深度学习框架'},
    ]
    
    created_skills = []
    for skill_data in skills_data:
        skill, created = Skill.objects.get_or_create(
            name=skill_data['name'],
            defaults={
                'category': skill_data['category'],
                'description': skill_data['description']
            }
        )
        created_skills.append(skill)
        if created:
            print(f"创建技能: {skill.name}")
    
    return created_skills

def create_job_categories():
    """创建职位分类"""
    categories_data = [
        {'name': '软件开发', 'description': '软件开发相关职位'},
        {'name': '前端开发', 'description': '前端开发相关职位'},
        {'name': '后端开发', 'description': '后端开发相关职位'},
        {'name': '全栈开发', 'description': '全栈开发相关职位'},
        {'name': '数据科学', 'description': '数据科学相关职位'},
        {'name': '人工智能', 'description': 'AI和机器学习相关职位'},
        {'name': '产品管理', 'description': '产品管理相关职位'},
        {'name': '项目管理', 'description': '项目管理相关职位'},
        {'name': 'UI/UX设计', 'description': 'UI/UX设计相关职位'},
        {'name': 'DevOps', 'description': 'DevOps和运维相关职位'},
    ]
    
    created_categories = []
    for cat_data in categories_data:
        category, created = JobCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        created_categories.append(category)
        if created:
            print(f"创建职位分类: {category.name}")
    
    return created_categories

def create_demo_users():
    """创建演示用户"""
    # 创建学生用户
    students_data = [
        {'username': 'student1', 'email': 'student1@example.com', 'first_name': '张', 'last_name': '三'},
        {'username': 'student2', 'email': 'student2@example.com', 'first_name': '李', 'last_name': '四'},
        {'username': 'student3', 'email': 'student3@example.com', 'first_name': '王', 'last_name': '五'},
        {'username': 'student4', 'email': 'student4@example.com', 'first_name': '赵', 'last_name': '六'},
        {'username': 'student5', 'email': 'student5@example.com', 'first_name': '陈', 'last_name': '七'},
    ]
    
    # 创建雇主用户
    employers_data = [
        {'username': 'employer1', 'email': 'hr@techcorp.com', 'first_name': '科技', 'last_name': '公司'},
        {'username': 'employer2', 'email': 'hr@innovate.com', 'first_name': '创新', 'last_name': '企业'},
        {'username': 'employer3', 'email': 'hr@startup.com', 'first_name': '初创', 'last_name': '公司'},
    ]
    
    created_students = []
    created_employers = []
    
    # 创建学生用户和档案
    for student_data in students_data:
        user, created = User.objects.get_or_create(
            username=student_data['username'],
            defaults={
                'email': student_data['email'],
                'first_name': student_data['first_name'],
                'last_name': student_data['last_name'],
                'user_type': 'student'
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"创建学生用户: {user.username}")
        
        # 创建学生档案
        profile, profile_created = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                'university': '清华大学',
                'major': '计算机科学与技术',
                'education_level': 'bachelor',
                'graduation_year': timezone.now().year + random.randint(-1, 2),
                'gpa': round(random.uniform(3.0, 4.0), 2),
                'bio': f'我是{user.first_name}{user.last_name}，一名计算机专业的学生。',
                'preferred_locations': ['北京', '上海', '深圳'],
                'preferred_company_sizes': ['medium', 'large'],
                'preferred_industries': ['technology', 'finance']
            }
        )
        created_students.append(profile)
    
    # 创建雇主用户和档案
    for employer_data in employers_data:
        user, created = User.objects.get_or_create(
            username=employer_data['username'],
            defaults={
                'email': employer_data['email'],
                'first_name': employer_data['first_name'],
                'last_name': employer_data['last_name'],
                'user_type': 'employer'
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"创建雇主用户: {user.username}")
        
        # 创建雇主档案
        profile, profile_created = EmployerProfile.objects.get_or_create(
            user=user,
            defaults={
                'company_name': f'{user.first_name}{user.last_name}科技有限公司',
                'company_description': f'{user.first_name}{user.last_name}是一家专注于技术创新的公司。',
                'industry': 'technology',
                'company_size': random.choice(['startup', 'small', 'medium', 'large']),
                'website': f'https://www.{user.username}.com',
                'contact_person': f'{user.first_name}{user.last_name}',
                'contact_title': 'HR经理',
                'office_address': f'{random.choice(["北京", "上海", "深圳", "杭州"])}市科技园区'
            }
        )
        created_employers.append(profile)
    
    return created_students, created_employers

def create_student_skills_and_education(students, skills):
    """为学生添加技能和教育背景"""
    universities = ['清华大学', '北京大学', '上海交通大学', '浙江大学', '华中科技大学']
    majors = ['计算机科学与技术', '软件工程', '数据科学与大数据技术', '人工智能', '信息安全']
    
    for student in students:
        # 更新学生的教育信息（直接在StudentProfile中设置）
        student.university = random.choice(universities)
        student.major = random.choice(majors)
        student.education_level = random.choice(['bachelor', 'master'])
        student.graduation_year = timezone.now().year + random.randint(-2, 2)  # 毕业年份在当前年份前后2年
        student.gpa = round(random.uniform(3.0, 4.0), 2)
        student.save()
        
        # 随机分配技能
        student_skills = random.sample(skills, random.randint(5, 12))
        for skill in student_skills:
            # 使用StudentSkill模型来添加技能和熟练度
            StudentSkill.objects.get_or_create(
                student=student,
                skill=skill,
                defaults={
                    'proficiency_level': random.choice(['beginner', 'intermediate', 'advanced']),
                    'years_of_experience': round(random.uniform(0.5, 5.0), 1)
                }
            )
        
        print(f"为学生 {student.user.username} 添加了 {len(student_skills)} 个技能")

def create_demo_jobs(employers, skills, categories):
    """创建演示职位"""
    jobs_data = [
        {
            'title': 'Python后端开发工程师',
            'description': '负责后端API开发，使用Django框架构建高性能的Web应用。',
            'requirements': '熟练掌握Python、Django、MySQL等技术，有2年以上开发经验。',
            'responsibilities': '参与系统架构设计，编写高质量代码，优化系统性能。',
            'job_type': 'full_time',
            'experience_level': 'mid',
            'required_skills': ['Python', 'Django', 'MySQL'],
            'preferred_skills': ['Redis', 'Docker'],
            'salary_min': 15000,
            'salary_max': 25000,
            'category': '后端开发'
        },
        {
            'title': 'React前端开发工程师',
            'description': '负责前端界面开发，使用React技术栈构建用户友好的Web应用。',
            'requirements': '熟练掌握React、JavaScript、HTML/CSS，有前端开发经验。',
            'responsibilities': '开发响应式用户界面，优化用户体验，与后端API集成。',
            'job_type': 'full_time',
            'experience_level': 'junior',
            'required_skills': ['React', 'JavaScript', 'HTML/CSS'],
            'preferred_skills': ['TypeScript', 'Vue.js'],
            'salary_min': 12000,
            'salary_max': 20000,
            'category': '前端开发'
        },
        {
            'title': '全栈开发工程师',
            'description': '负责前后端全栈开发，参与产品的完整开发周期。',
            'requirements': '熟练掌握前后端技术栈，有全栈开发经验。',
            'responsibilities': '独立完成功能模块开发，参与技术选型和架构设计。',
            'job_type': 'full_time',
            'experience_level': 'senior',
            'required_skills': ['Python', 'React', 'Node.js', 'MySQL'],
            'preferred_skills': ['Docker', 'AWS', 'MongoDB'],
            'salary_min': 20000,
            'salary_max': 35000,
            'category': '全栈开发'
        },
        {
            'title': '数据科学家',
            'description': '负责数据分析和机器学习模型开发，为业务决策提供数据支持。',
            'requirements': '熟练掌握Python、机器学习算法，有数据科学项目经验。',
            'responsibilities': '数据挖掘、模型训练、业务分析报告撰写。',
            'job_type': 'full_time',
            'experience_level': 'mid',
            'required_skills': ['Python', '机器学习', '数据分析'],
            'preferred_skills': ['TensorFlow', 'PyTorch', '深度学习'],
            'salary_min': 18000,
            'salary_max': 30000,
            'category': '数据科学'
        },
        {
            'title': 'DevOps工程师',
            'description': '负责CI/CD流程建设，云基础设施管理和运维自动化。',
            'requirements': '熟练掌握Docker、Kubernetes、云服务，有DevOps经验。',
            'responsibilities': '构建自动化部署流程，监控系统性能，保障服务稳定性。',
            'job_type': 'full_time',
            'experience_level': 'senior',
            'required_skills': ['Docker', 'Kubernetes', 'AWS'],
            'preferred_skills': ['Python', 'Go', 'Git'],
            'salary_min': 22000,
            'salary_max': 40000,
            'category': 'DevOps'
        }
    ]
    
    skill_dict = {skill.name: skill for skill in skills}
    category_dict = {cat.name: cat for cat in categories}
    
    created_jobs = []
    for job_data in jobs_data:
        employer = random.choice(employers)
        
        job, created = Job.objects.get_or_create(
            title=job_data['title'],
            employer=employer,
            defaults={
                'description': job_data['description'],
                'requirements': job_data['requirements'],
                'responsibilities': job_data['responsibilities'],
                'job_type': job_data['job_type'],
                'experience_level': job_data['experience_level'],
                'remote_option': random.choice(['on_site', 'remote', 'hybrid']),
                'salary_min': job_data['salary_min'],
                'salary_max': job_data['salary_max'],
                'location_city': random.choice(['北京', '上海', '深圳', '杭州']),
                'location_country': '中国',
                'application_deadline': timezone.now() + timedelta(days=30),
                'category': category_dict.get(job_data['category'])
            }
        )
        
        if created:
            # 添加必需技能
            for skill_name in job_data['required_skills']:
                if skill_name in skill_dict:
                    JobSkillRequirement.objects.get_or_create(
                        job=job,
                        skill=skill_dict[skill_name],
                        defaults={
                            'importance': 'important',
                            'min_experience_years': random.uniform(1.0, 3.0),
                            'weight': random.uniform(1.0, 2.0)
                        }
                    )
            
            # 添加偏好技能
            for skill_name in job_data['preferred_skills']:
                if skill_name in skill_dict:
                    JobSkillPreference.objects.get_or_create(
                        job=job,
                        skill=skill_dict[skill_name],
                        defaults={
                            'bonus_points': random.uniform(0.5, 1.5)
                        }
                    )
            
            created_jobs.append(job)
            print(f"创建职位: {job.title} - {employer.company_name}")
    
    return created_jobs

def main():
    """主函数"""
    print("开始创建演示数据...")
    
    # 创建技能
    print("\n1. 创建技能数据...")
    skills = create_skills()
    
    # 创建职位分类
    print("\n2. 创建职位分类...")
    categories = create_job_categories()
    
    # 创建用户
    print("\n3. 创建用户和档案...")
    students, employers = create_demo_users()
    
    # 为学生添加技能和教育背景
    print("\n4. 为学生添加技能和教育背景...")
    create_student_skills_and_education(students, skills)
    
    # 创建职位
    print("\n5. 创建演示职位...")
    jobs = create_demo_jobs(employers, skills, categories)
    
    print(f"\n演示数据创建完成!")
    print(f"- 创建了 {len(skills)} 个技能")
    print(f"- 创建了 {len(categories)} 个职位分类")
    print(f"- 创建了 {len(students)} 个学生用户")
    print(f"- 创建了 {len(employers)} 个雇主用户")
    print(f"- 创建了 {len(jobs)} 个职位")
    
    print("\n登录信息:")
    print("学生账号: student1-student5, 密码: password123")
    print("雇主账号: employer1-employer3, 密码: password123")

if __name__ == '__main__':
    main()