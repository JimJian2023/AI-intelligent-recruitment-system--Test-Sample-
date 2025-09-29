"""
申请模块API视图
"""

from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import (
    Application, ApplicationStatusHistory, Interview, 
    Feedback, SavedJob, ApplicationNote
)
from .serializers import (
    ApplicationListSerializer, ApplicationDetailSerializer,
    ApplicationCreateSerializer, ApplicationStatusUpdateSerializer,
    InterviewSerializer, FeedbackSerializer, SavedJobSerializer,
    ApplicationNoteSerializer, ApplicationStatisticsSerializer
)
from users.models import StudentProfile, EmployerProfile
from jobs.models import Job


class ApplicationPagination(PageNumberPagination):
    """申请分页器"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ApplicationListCreateView(generics.ListCreateAPIView):
    """申请列表和创建视图"""
    pagination_class = ApplicationPagination
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ApplicationCreateSerializer
        return ApplicationListSerializer
    
    def get_queryset(self):
        """获取申请查询集"""
        user = self.request.user
        
        if user.user_type == 'student':
            # 学生查看自己的申请
            try:
                student_profile = StudentProfile.objects.get(user=user)
                queryset = Application.objects.filter(student=student_profile)
            except StudentProfile.DoesNotExist:
                return Application.objects.none()
        
        elif user.user_type == 'employer':
            # 雇主查看自己职位的申请
            try:
                employer_profile = EmployerProfile.objects.get(user=user)
                queryset = Application.objects.filter(job__employer=employer_profile)
            except EmployerProfile.DoesNotExist:
                return Application.objects.none()
        
        else:
            return Application.objects.none()
        
        # 过滤参数
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        job_id = self.request.query_params.get('job_id')
        if job_id:
            queryset = queryset.filter(job_id=job_id)
        
        # 排序
        ordering = self.request.query_params.get('ordering', '-applied_at')
        if ordering in ['applied_at', '-applied_at', 'ai_match_score', '-ai_match_score']:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-applied_at')
        
        return queryset.select_related('job', 'job__employer', 'student', 'student__user')
    
    def perform_create(self, serializer):
        """执行创建"""
        if self.request.user.user_type != 'student':
            raise permissions.PermissionDenied("只有学生可以申请职位")
        
        try:
            student_profile = StudentProfile.objects.get(user=self.request.user)
        except StudentProfile.DoesNotExist:
            raise permissions.PermissionDenied("请先完善学生档案")
        
        serializer.save(student=student_profile)


class ApplicationDetailView(generics.RetrieveUpdateAPIView):
    """申请详情视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ApplicationStatusUpdateSerializer
        return ApplicationDetailSerializer
    
    def get_queryset(self):
        """获取申请查询集"""
        user = self.request.user
        
        if user.user_type == 'student':
            try:
                student_profile = StudentProfile.objects.get(user=user)
                return Application.objects.filter(student=student_profile)
            except StudentProfile.DoesNotExist:
                return Application.objects.none()
        
        elif user.user_type == 'employer':
            try:
                employer_profile = EmployerProfile.objects.get(user=user)
                return Application.objects.filter(job__employer=employer_profile)
            except EmployerProfile.DoesNotExist:
                return Application.objects.none()
        
        return Application.objects.none()
    
    def perform_update(self, serializer):
        """执行更新"""
        # 只有雇主可以更新申请状态
        if self.request.user.user_type != 'employer':
            raise permissions.PermissionDenied("只有雇主可以更新申请状态")
        
        application = self.get_object()
        
        try:
            employer_profile = EmployerProfile.objects.get(user=self.request.user)
            if application.job.employer != employer_profile:
                raise permissions.PermissionDenied("只能更新自己职位的申请")
        except EmployerProfile.DoesNotExist:
            raise permissions.PermissionDenied("雇主档案不存在")
        
        serializer.save()


class InterviewListCreateView(generics.ListCreateAPIView):
    """面试列表和创建视图"""
    serializer_class = InterviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """获取面试查询集"""
        user = self.request.user
        
        if user.user_type == 'student':
            try:
                student_profile = StudentProfile.objects.get(user=user)
                return Interview.objects.filter(application__student=student_profile)
            except StudentProfile.DoesNotExist:
                return Interview.objects.none()
        
        elif user.user_type == 'employer':
            try:
                employer_profile = EmployerProfile.objects.get(user=user)
                return Interview.objects.filter(application__job__employer=employer_profile)
            except EmployerProfile.DoesNotExist:
                return Interview.objects.none()
        
        return Interview.objects.none()
    
    def perform_create(self, serializer):
        """执行创建"""
        if self.request.user.user_type != 'employer':
            raise permissions.PermissionDenied("只有雇主可以安排面试")
        
        application = serializer.validated_data['application']
        
        try:
            employer_profile = EmployerProfile.objects.get(user=self.request.user)
            if application.job.employer != employer_profile:
                raise permissions.PermissionDenied("只能为自己职位的申请安排面试")
        except EmployerProfile.DoesNotExist:
            raise permissions.PermissionDenied("雇主档案不存在")
        
        serializer.save()


class InterviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """面试详情视图"""
    serializer_class = InterviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """获取面试查询集"""
        user = self.request.user
        
        if user.user_type == 'student':
            try:
                student_profile = StudentProfile.objects.get(user=user)
                return Interview.objects.filter(application__student=student_profile)
            except StudentProfile.DoesNotExist:
                return Interview.objects.none()
        
        elif user.user_type == 'employer':
            try:
                employer_profile = EmployerProfile.objects.get(user=user)
                return Interview.objects.filter(application__job__employer=employer_profile)
            except EmployerProfile.DoesNotExist:
                return Interview.objects.none()
        
        return Interview.objects.none()
    
    def perform_update(self, serializer):
        """执行更新"""
        if self.request.user.user_type != 'employer':
            raise permissions.PermissionDenied("只有雇主可以更新面试信息")
        
        interview = self.get_object()
        
        try:
            employer_profile = EmployerProfile.objects.get(user=self.request.user)
            if interview.application.job.employer != employer_profile:
                raise permissions.PermissionDenied("只能更新自己职位的面试")
        except EmployerProfile.DoesNotExist:
            raise permissions.PermissionDenied("雇主档案不存在")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """执行删除"""
        if self.request.user.user_type != 'employer':
            raise permissions.PermissionDenied("只有雇主可以取消面试")
        
        try:
            employer_profile = EmployerProfile.objects.get(user=self.request.user)
            if instance.application.job.employer != employer_profile:
                raise permissions.PermissionDenied("只能取消自己职位的面试")
        except EmployerProfile.DoesNotExist:
            raise permissions.PermissionDenied("雇主档案不存在")
        
        instance.delete()


class FeedbackListCreateView(generics.ListCreateAPIView):
    """反馈列表和创建视图"""
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """获取反馈查询集"""
        user = self.request.user
        
        if user.user_type == 'student':
            try:
                student_profile = StudentProfile.objects.get(user=user)
                return Feedback.objects.filter(application__student=student_profile)
            except StudentProfile.DoesNotExist:
                return Feedback.objects.none()
        
        elif user.user_type == 'employer':
            try:
                employer_profile = EmployerProfile.objects.get(user=user)
                return Feedback.objects.filter(application__job__employer=employer_profile)
            except EmployerProfile.DoesNotExist:
                return Feedback.objects.none()
        
        return Feedback.objects.none()


class SavedJobListCreateView(generics.ListCreateAPIView):
    """收藏职位列表和创建视图"""
    serializer_class = SavedJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """获取收藏职位查询集"""
        if self.request.user.user_type != 'student':
            return SavedJob.objects.none()
        
        try:
            student_profile = StudentProfile.objects.get(user=self.request.user)
            return SavedJob.objects.filter(student=student_profile).select_related(
                'job', 'job__employer'
            )
        except StudentProfile.DoesNotExist:
            return SavedJob.objects.none()
    
    def perform_create(self, serializer):
        """执行创建"""
        if self.request.user.user_type != 'student':
            raise permissions.PermissionDenied("只有学生可以收藏职位")
        
        try:
            student_profile = StudentProfile.objects.get(user=self.request.user)
        except StudentProfile.DoesNotExist:
            raise permissions.PermissionDenied("请先完善学生档案")
        
        serializer.save(student=student_profile)


class SavedJobDetailView(generics.RetrieveUpdateDestroyAPIView):
    """收藏职位详情视图"""
    serializer_class = SavedJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """获取收藏职位查询集"""
        if self.request.user.user_type != 'student':
            return SavedJob.objects.none()
        
        try:
            student_profile = StudentProfile.objects.get(user=self.request.user)
            return SavedJob.objects.filter(student=student_profile)
        except StudentProfile.DoesNotExist:
            return SavedJob.objects.none()


class ApplicationNoteListCreateView(generics.ListCreateAPIView):
    """申请备注列表和创建视图"""
    serializer_class = ApplicationNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """获取申请备注查询集"""
        application_id = self.kwargs.get('application_id')
        
        # 检查用户权限
        try:
            application = Application.objects.get(id=application_id)
            
            if self.request.user.user_type == 'student':
                student_profile = StudentProfile.objects.get(user=self.request.user)
                if application.student != student_profile:
                    return ApplicationNote.objects.none()
            
            elif self.request.user.user_type == 'employer':
                employer_profile = EmployerProfile.objects.get(user=self.request.user)
                if application.job.employer != employer_profile:
                    return ApplicationNote.objects.none()
            
            else:
                return ApplicationNote.objects.none()
            
            return ApplicationNote.objects.filter(application=application)
        
        except (Application.DoesNotExist, StudentProfile.DoesNotExist, EmployerProfile.DoesNotExist):
            return ApplicationNote.objects.none()
    
    def perform_create(self, serializer):
        """执行创建"""
        application_id = self.kwargs.get('application_id')
        application = get_object_or_404(Application, id=application_id)
        
        # 检查权限
        if self.request.user.user_type == 'student':
            try:
                student_profile = StudentProfile.objects.get(user=self.request.user)
                if application.student != student_profile:
                    raise permissions.PermissionDenied("只能为自己的申请添加备注")
            except StudentProfile.DoesNotExist:
                raise permissions.PermissionDenied("学生档案不存在")
        
        elif self.request.user.user_type == 'employer':
            try:
                employer_profile = EmployerProfile.objects.get(user=self.request.user)
                if application.job.employer != employer_profile:
                    raise permissions.PermissionDenied("只能为自己职位的申请添加备注")
            except EmployerProfile.DoesNotExist:
                raise permissions.PermissionDenied("雇主档案不存在")
        
        else:
            raise permissions.PermissionDenied("权限不足")
        
        serializer.save(application=application)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def application_statistics(request):
    """申请统计信息"""
    user = request.user
    
    if user.user_type == 'student':
        try:
            student_profile = StudentProfile.objects.get(user=user)
            applications = Application.objects.filter(student=student_profile)
        except StudentProfile.DoesNotExist:
            return Response({'error': '学生档案不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    elif user.user_type == 'employer':
        try:
            employer_profile = EmployerProfile.objects.get(user=user)
            applications = Application.objects.filter(job__employer=employer_profile)
        except EmployerProfile.DoesNotExist:
            return Response({'error': '雇主档案不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    else:
        return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)
    
    # 统计数据
    total_applications = applications.count()
    status_counts = applications.values('status').annotate(count=Count('id'))
    
    stats = {
        'total_applications': total_applications,
        'pending_applications': 0,
        'reviewed_applications': 0,
        'accepted_applications': 0,
        'rejected_applications': 0,
        'average_match_score': 0,
        'applications_this_month': 0,
        'success_rate': 0
    }
    
    # 按状态统计
    for item in status_counts:
        if item['status'] == 'pending':
            stats['pending_applications'] = item['count']
        elif item['status'] == 'reviewed':
            stats['reviewed_applications'] = item['count']
        elif item['status'] == 'accepted':
            stats['accepted_applications'] = item['count']
        elif item['status'] == 'rejected':
            stats['rejected_applications'] = item['count']
    
    # 平均匹配分数
    avg_score = applications.aggregate(avg_score=Avg('ai_match_score'))
    stats['average_match_score'] = float(avg_score['avg_score'] or 0)
    
    # 本月申请数
    this_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    stats['applications_this_month'] = applications.filter(applied_at__gte=this_month).count()
    
    # 成功率
    if total_applications > 0:
        stats['success_rate'] = (stats['accepted_applications'] / total_applications) * 100
    
    return Response(stats)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_update_applications(request):
    """批量更新申请状态"""
    if request.user.user_type != 'employer':
        return Response(
            {'error': '只有雇主可以批量更新申请状态'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        employer_profile = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        return Response(
            {'error': '雇主档案不存在'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    application_ids = request.data.get('application_ids', [])
    new_status = request.data.get('status')
    notes = request.data.get('notes', '')
    
    if not application_ids or not new_status:
        return Response(
            {'error': '请提供申请ID列表和新状态'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 验证申请归属
    applications = Application.objects.filter(
        id__in=application_ids,
        job__employer=employer_profile
    )
    
    if applications.count() != len(application_ids):
        return Response(
            {'error': '部分申请不存在或无权限操作'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 批量更新
    updated_count = 0
    for application in applications:
        old_status = application.status
        application.status = new_status
        application.save()
        
        # 记录状态变更历史
        ApplicationStatusHistory.objects.create(
            application=application,
            status=new_status,
            changed_by=request.user,
            notes=notes
        )
        
        updated_count += 1
    
    return Response({
        'message': f'成功更新 {updated_count} 个申请状态',
        'updated_count': updated_count
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def upcoming_interviews(request):
    """即将到来的面试"""
    user = request.user
    
    if user.user_type == 'student':
        try:
            student_profile = StudentProfile.objects.get(user=user)
            interviews = Interview.objects.filter(
                application__student=student_profile,
                scheduled_at__gte=timezone.now(),
                status='scheduled'
            ).order_by('scheduled_at')
        except StudentProfile.DoesNotExist:
            return Response({'error': '学生档案不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    elif user.user_type == 'employer':
        try:
            employer_profile = EmployerProfile.objects.get(user=user)
            interviews = Interview.objects.filter(
                application__job__employer=employer_profile,
                scheduled_at__gte=timezone.now(),
                status='scheduled'
            ).order_by('scheduled_at')
        except EmployerProfile.DoesNotExist:
            return Response({'error': '雇主档案不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    else:
        return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = InterviewSerializer(interviews, many=True, context={'request': request})
    return Response(serializer.data)
