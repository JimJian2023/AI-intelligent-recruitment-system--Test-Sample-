"""
职位模块URL配置
"""

from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # 职位相关
    path('', views.JobListCreateView.as_view(), name='job-list-create'),
    path('<int:pk>/', views.JobDetailView.as_view(), name='job-detail'),
    path('my/', views.my_jobs, name='my-jobs'),
    path('<int:job_id>/apply/', views.apply_job, name='apply-job'),
    path('parse/', views.parse_job_description, name='parse-job-description'),
    path('demo-create/', views.demo_create_job, name='demo-create-job'),
    
    # 职位分类
    path('categories/', views.JobCategoryListView.as_view(), name='job-categories'),
    
    # 职位提醒
    path('alerts/', views.JobAlertListCreateView.as_view(), name='job-alerts'),
    path('alerts/<int:pk>/', views.JobAlertDetailView.as_view(), name='job-alert-detail'),
    
    # 统计和推荐
    path('statistics/', views.job_statistics, name='job-statistics'),
    path('featured/', views.featured_jobs, name='featured-jobs'),
    path('recent/', views.recent_jobs, name='recent-jobs'),
]