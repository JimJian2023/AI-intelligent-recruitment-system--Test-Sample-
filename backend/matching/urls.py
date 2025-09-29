"""
匹配模块URL配置
"""

from django.urls import path
from . import views
from . import demo_views

app_name = 'matching'

urlpatterns = [
    # 匹配结果
    path('results/', views.MatchResultListView.as_view(), name='match-results'),
    path('results/<int:pk>/', views.MatchResultDetailView.as_view(), name='match-result-detail'),
    
    # 匹配计算
    path('calculate/', views.calculate_match, name='calculate-match'),
    path('batch-calculate/', views.batch_calculate_match, name='batch-calculate-match'),
    
    # 学生推荐
    path('recommendations/', views.StudentRecommendationListView.as_view(), name='recommendations'),
    path('recommendations/generate/', views.generate_recommendations, name='generate-recommendations'),
    
    # 算法配置
    path('algorithms/', views.MatchingAlgorithmConfigListView.as_view(), name='algorithm-configs'),
    
    # 统计信息
    path('statistics/', views.match_statistics, name='match-statistics'),
    path('recommendations/statistics/', views.recommendation_statistics, name='recommendation-statistics'),
    
    # 匹配任务状态
    path('jobs/<int:job_id>/status/', views.matching_job_status, name='matching-job-status'),
    
    # 演示模式API
    path('analyze/', demo_views.analyze_match, name='demo-analyze-match'),
]