"""
用户模块URL配置
"""

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # 认证相关
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    
    # 用户基本信息
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    
    # 学生档案
    path('student/profile/', views.StudentProfileView.as_view(), name='student_profile'),
    path('student/skills/', views.StudentSkillListCreateView.as_view(), name='student_skills'),
    path('student/skills/<int:pk>/', views.StudentSkillDetailView.as_view(), name='student_skill_detail'),
    path('student/projects/', views.ProjectListCreateView.as_view(), name='student_projects'),
    path('student/projects/<int:pk>/', views.ProjectDetailView.as_view(), name='student_project_detail'),
    
    # 雇主档案
    path('employer/profile/', views.EmployerProfileView.as_view(), name='employer_profile'),
    
    # 技能相关
    path('skills/', views.SkillListView.as_view(), name='skills'),
]