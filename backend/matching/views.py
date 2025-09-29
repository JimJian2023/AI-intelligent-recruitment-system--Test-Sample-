"""
匹配模块API视图
"""

from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import (
    MatchResult, SkillMatchDetail, MatchingAlgorithmConfig,
    MatchingJob, StudentRecommendation, RecommendationItem
)
from .serializers import (
    MatchResultSerializer, MatchResultDetailSerializer,
    MatchingAlgorithmConfigSerializer, MatchingJobSerializer,
    StudentRecommendationSerializer, StudentRecommendationCreateSerializer,
    MatchRequestSerializer, BatchMatchRequestSerializer,
    MatchStatisticsSerializer, RecommendationStatisticsSerializer
)
from .services import MatchingService
from .algorithms import IntelligentMatcher
from users.models import StudentProfile, EmployerProfile
from jobs.models import Job
import logging

logger = logging.getLogger(__name__)


class MatchResultPagination(PageNumberPagination):
    """匹配结果分页器"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class MatchResultListView(generics.ListAPIView):
    """匹配结果列表视图"""
    serializer_class = MatchResultSerializer
    pagination_class = MatchResultPagination
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """获取匹配结果查询集"""
        user = self.request.user
        
        if user.user_type == 'student':
            try:
                student_profile = StudentProfile.objects.get(user=user)
                queryset = MatchResult.objects.filter(student=student_profile)
            except StudentProfile.DoesNotExist:
                return MatchResult.objects.none()
        
        elif user.user_type == 'employer':
            try:
                employer_profile = EmployerProfile.objects.get(user=user)
                queryset = MatchResult.objects.filter(job__employer=employer_profile)
            except EmployerProfile.DoesNotExist:
                return MatchResult.objects.none()
        
        else:
            return MatchResult.objects.none()
        
        # 过滤参数
        min_score = self.request.query_params.get('min_score')
        if min_score:
            try:
                min_score = float(min_score)
                queryset = queryset.filter(overall_score__gte=min_score)
            except ValueError:
                pass
        
        job_id = self.request.query_params.get('job_id')
        if job_id:
            queryset = queryset.filter(job_id=job_id)
        
        student_id = self.request.query_params.get('student_id')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        # 排序
        ordering = self.request.query_params.get('ordering', '-overall_score')
        if ordering in ['overall_score', '-overall_score', 'created_at', '-created_at']:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-overall_score')
        
        return queryset.select_related('student', 'job', 'job__employer')


class MatchResultDetailView(generics.RetrieveAPIView):
    """匹配结果详情视图"""
    serializer_class = MatchResultDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """获取匹配结果查询集"""
        user = self.request.user
        
        if user.user_type == 'student':
            try:
                student_profile = StudentProfile.objects.get(user=user)
                return MatchResult.objects.filter(student=student_profile)
            except StudentProfile.DoesNotExist:
                return MatchResult.objects.none()
        
        elif user.user_type == 'employer':
            try:
                employer_profile = EmployerProfile.objects.get(user=user)
                return MatchResult.objects.filter(job__employer=employer_profile)
            except EmployerProfile.DoesNotExist:
                return MatchResult.objects.none()
        
        return MatchResult.objects.none()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def calculate_match(request):
    """计算匹配度"""
    serializer = MatchRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    student_id = data.get('student_id')
    job_id = data.get('job_id')
    limit = data.get('limit', 10)
    min_score = data.get('min_score', 0.0)
    algorithm_config_id = data.get('algorithm_config_id')
    
    try:
        matching_service = MatchingService()
        
        if student_id:
            # 为学生查找匹配职位
            if request.user.user_type != 'student':
                return Response(
                    {'error': '只有学生可以查找匹配职位'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            try:
                student_profile = StudentProfile.objects.get(user=request.user, id=student_id)
            except StudentProfile.DoesNotExist:
                return Response(
                    {'error': '学生档案不存在或无权限访问'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            results = matching_service.find_matching_jobs_for_student(
                student_profile,
                limit=limit,
                min_score=min_score,
                algorithm_config_id=algorithm_config_id
            )
        
        elif job_id:
            # 为职位查找匹配学生
            if request.user.user_type != 'employer':
                return Response(
                    {'error': '只有雇主可以查找匹配学生'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            try:
                employer_profile = EmployerProfile.objects.get(user=request.user)
                job = Job.objects.get(id=job_id, employer=employer_profile)
            except (EmployerProfile.DoesNotExist, Job.DoesNotExist):
                return Response(
                    {'error': '职位不存在或无权限访问'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            results = matching_service.find_matching_students_for_job(
                job,
                limit=limit,
                min_score=min_score,
                algorithm_config_id=algorithm_config_id
            )
        
        serializer = MatchResultSerializer(results, many=True)
        return Response({
            'results': serializer.data,
            'count': len(results)
        })
    
    except Exception as e:
        logger.error(f"匹配计算错误: {str(e)}")
        return Response(
            {'error': '匹配计算失败，请稍后重试'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def batch_calculate_match(request):
    """批量计算匹配度"""
    serializer = BatchMatchRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    student_ids = data.get('student_ids')
    job_ids = data.get('job_ids')
    limit_per_item = data.get('limit_per_item', 5)
    min_score = data.get('min_score', 0.0)
    priority = data.get('priority', 'normal')
    algorithm_config_id = data.get('algorithm_config_id')
    
    try:
        matching_service = MatchingService()
        
        if student_ids:
            # 批量为学生查找匹配职位
            if request.user.user_type != 'student':
                return Response(
                    {'error': '只有学生可以批量查找匹配职位'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # 验证学生归属
            try:
                student_profile = StudentProfile.objects.get(user=request.user)
                if student_profile.id not in student_ids:
                    return Response(
                        {'error': '只能为自己查找匹配职位'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except StudentProfile.DoesNotExist:
                return Response(
                    {'error': '学生档案不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 创建批量匹配任务
            matching_jobs = []
            for student_id in student_ids:
                matching_job = MatchingJob.objects.create(
                    student_id=student_id,
                    priority=priority,
                    scheduled_at=timezone.now()
                )
                matching_jobs.append(matching_job)
        
        elif job_ids:
            # 批量为职位查找匹配学生
            if request.user.user_type != 'employer':
                return Response(
                    {'error': '只有雇主可以批量查找匹配学生'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # 验证职位归属
            try:
                employer_profile = EmployerProfile.objects.get(user=request.user)
                jobs = Job.objects.filter(id__in=job_ids, employer=employer_profile)
                if jobs.count() != len(job_ids):
                    return Response(
                        {'error': '部分职位不存在或无权限访问'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except EmployerProfile.DoesNotExist:
                return Response(
                    {'error': '雇主档案不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 创建批量匹配任务
            matching_jobs = []
            for job_id in job_ids:
                matching_job = MatchingJob.objects.create(
                    job_id=job_id,
                    priority=priority,
                    scheduled_at=timezone.now()
                )
                matching_jobs.append(matching_job)
        
        # 启动异步任务
        from .services import batch_calculate_matches
        task_ids = []
        for matching_job in matching_jobs:
            task = batch_calculate_matches.delay(
                matching_job.id,
                limit_per_item,
                min_score,
                algorithm_config_id
            )
            task_ids.append(task.id)
        
        serializer = MatchingJobSerializer(matching_jobs, many=True)
        return Response({
            'matching_jobs': serializer.data,
            'task_ids': task_ids,
            'message': f'已创建 {len(matching_jobs)} 个批量匹配任务'
        })
    
    except Exception as e:
        logger.error(f"批量匹配创建错误: {str(e)}")
        return Response(
            {'error': '批量匹配任务创建失败，请稍后重试'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class StudentRecommendationListView(generics.ListAPIView):
    """学生推荐列表视图"""
    serializer_class = StudentRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """获取学生推荐查询集"""
        if self.request.user.user_type != 'student':
            return StudentRecommendation.objects.none()
        
        try:
            student_profile = StudentProfile.objects.get(user=self.request.user)
            return StudentRecommendation.objects.filter(
                student=student_profile,
                is_active=True,
                expires_at__gt=timezone.now()
            ).order_by('-created_at')
        except StudentProfile.DoesNotExist:
            return StudentRecommendation.objects.none()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_recommendations(request):
    """生成学生推荐"""
    if request.user.user_type != 'student':
        return Response(
            {'error': '只有学生可以生成推荐'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        student_profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        return Response(
            {'error': '请先完善学生档案'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    recommendation_type = request.data.get('type', 'comprehensive')
    
    try:
        matching_service = MatchingService()
        recommendations = matching_service.generate_student_recommendations(
            student_profile,
            recommendation_type=recommendation_type
        )
        
        serializer = StudentRecommendationSerializer(recommendations, many=True)
        return Response({
            'recommendations': serializer.data,
            'count': len(recommendations)
        })
    
    except Exception as e:
        logger.error(f"推荐生成错误: {str(e)}")
        return Response(
            {'error': '推荐生成失败，请稍后重试'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class MatchingAlgorithmConfigListView(generics.ListAPIView):
    """匹配算法配置列表视图"""
    serializer_class = MatchingAlgorithmConfigSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = MatchingAlgorithmConfig.objects.filter(is_active=True)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def match_statistics(request):
    """匹配统计信息"""
    user = request.user
    
    if user.user_type == 'student':
        try:
            student_profile = StudentProfile.objects.get(user=user)
            matches = MatchResult.objects.filter(student=student_profile)
        except StudentProfile.DoesNotExist:
            return Response({'error': '学生档案不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    elif user.user_type == 'employer':
        try:
            employer_profile = EmployerProfile.objects.get(user=user)
            matches = MatchResult.objects.filter(job__employer=employer_profile)
        except EmployerProfile.DoesNotExist:
            return Response({'error': '雇主档案不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    else:
        return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)
    
    # 统计数据
    total_matches = matches.count()
    high_quality_matches = matches.filter(overall_score__gte=0.8).count()
    medium_quality_matches = matches.filter(
        overall_score__gte=0.6, overall_score__lt=0.8
    ).count()
    low_quality_matches = matches.filter(overall_score__lt=0.6).count()
    
    avg_score = matches.aggregate(avg_score=Avg('overall_score'))
    average_score = float(avg_score['avg_score'] or 0)
    
    # 时间统计
    this_week = timezone.now() - timezone.timedelta(days=7)
    this_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    matches_this_week = matches.filter(created_at__gte=this_week).count()
    matches_this_month = matches.filter(created_at__gte=this_month).count()
    
    # 技能统计（简化版）
    top_skills = []
    if user.user_type == 'student':
        # 学生的热门匹配技能
        skill_matches = SkillMatchDetail.objects.filter(
            match_result__student=student_profile
        ).values('skill__name').annotate(
            count=Count('id'),
            avg_score=Avg('match_score')
        ).order_by('-count')[:5]
        
        top_skills = [
            {
                'skill': item['skill__name'],
                'match_count': item['count'],
                'average_score': float(item['avg_score'] or 0)
            }
            for item in skill_matches
        ]
    
    # 匹配趋势（简化版）
    match_trends = []
    for i in range(7):
        date = timezone.now().date() - timezone.timedelta(days=i)
        count = matches.filter(created_at__date=date).count()
        match_trends.append({
            'date': date.isoformat(),
            'count': count
        })
    
    stats = {
        'total_matches': total_matches,
        'high_quality_matches': high_quality_matches,
        'medium_quality_matches': medium_quality_matches,
        'low_quality_matches': low_quality_matches,
        'average_score': average_score,
        'matches_this_week': matches_this_week,
        'matches_this_month': matches_this_month,
        'top_skills': top_skills,
        'match_trends': match_trends
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def recommendation_statistics(request):
    """推荐统计信息"""
    if request.user.user_type != 'student':
        return Response(
            {'error': '只有学生可以查看推荐统计'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        student_profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        return Response({'error': '学生档案不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    recommendations = StudentRecommendation.objects.filter(student=student_profile)
    
    # 统计数据
    total_recommendations = recommendations.count()
    active_recommendations = recommendations.filter(
        is_active=True,
        expires_at__gt=timezone.now()
    ).count()
    
    job_recommendations = recommendations.filter(
        recommendation_type='job'
    ).count()
    skill_recommendations = recommendations.filter(
        recommendation_type='skill'
    ).count()
    career_recommendations = recommendations.filter(
        recommendation_type='career'
    ).count()
    
    # 本月推荐数
    this_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    recommendations_this_month = recommendations.filter(
        created_at__gte=this_month
    ).count()
    
    # 成功率（简化计算）
    success_rate = 0.0
    if total_recommendations > 0:
        # 这里可以根据实际业务逻辑计算成功率
        # 例如：被采纳的推荐数 / 总推荐数
        success_rate = 75.0  # 示例值
    
    stats = {
        'total_recommendations': total_recommendations,
        'active_recommendations': active_recommendations,
        'job_recommendations': job_recommendations,
        'skill_recommendations': skill_recommendations,
        'career_recommendations': career_recommendations,
        'success_rate': success_rate,
        'recommendations_this_month': recommendations_this_month
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def matching_job_status(request, job_id):
    """获取匹配任务状态"""
    try:
        matching_job = MatchingJob.objects.get(id=job_id)
        
        # 检查权限
        if request.user.user_type == 'student':
            try:
                student_profile = StudentProfile.objects.get(user=request.user)
                if matching_job.student != student_profile:
                    return Response(
                        {'error': '无权限访问此匹配任务'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except StudentProfile.DoesNotExist:
                return Response(
                    {'error': '学生档案不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        elif request.user.user_type == 'employer':
            try:
                employer_profile = EmployerProfile.objects.get(user=request.user)
                if not matching_job.job or matching_job.job.employer != employer_profile:
                    return Response(
                        {'error': '无权限访问此匹配任务'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except EmployerProfile.DoesNotExist:
                return Response(
                    {'error': '雇主档案不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        else:
            return Response(
                {'error': '权限不足'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = MatchingJobSerializer(matching_job)
        return Response(serializer.data)
    
    except MatchingJob.DoesNotExist:
        return Response(
            {'error': '匹配任务不存在'},
            status=status.HTTP_404_NOT_FOUND
        )
