"""
申请模块URL配置
"""

from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    # 申请相关
    path('', views.ApplicationListCreateView.as_view(), name='application-list-create'),
    path('<int:pk>/', views.ApplicationDetailView.as_view(), name='application-detail'),
    path('statistics/', views.application_statistics, name='application-statistics'),
    path('bulk-update/', views.bulk_update_applications, name='bulk-update-applications'),
    
    # 面试相关
    path('interviews/', views.InterviewListCreateView.as_view(), name='interview-list-create'),
    path('interviews/<int:pk>/', views.InterviewDetailView.as_view(), name='interview-detail'),
    path('interviews/upcoming/', views.upcoming_interviews, name='upcoming-interviews'),
    
    # 反馈相关
    path('feedback/', views.FeedbackListCreateView.as_view(), name='feedback-list-create'),
    
    # 收藏职位相关
    path('saved-jobs/', views.SavedJobListCreateView.as_view(), name='saved-job-list-create'),
    path('saved-jobs/<int:pk>/', views.SavedJobDetailView.as_view(), name='saved-job-detail'),
    
    # 申请备注相关
    path('<int:application_id>/notes/', views.ApplicationNoteListCreateView.as_view(), name='application-note-list-create'),
]