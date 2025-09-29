"""
用户模块API视图
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404
from django.db import transaction
import logging

from .models import User, StudentProfile, EmployerProfile, Skill, StudentSkill, Project
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    StudentProfileSerializer, EmployerProfileSerializer, SkillSerializer,
    StudentSkillSerializer, StudentSkillCreateSerializer, ProjectSerializer,
    PasswordChangeSerializer
)

logger = logging.getLogger(__name__)


class UserRegistrationView(generics.CreateAPIView):
    """用户注册视图"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """创建用户"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            
            logger.info(f"新用户注册: {user.username} ({user.user_type})")
            
            return Response({
                'message': '注册成功',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'user_type': user.user_type,
                    'full_name': user.get_full_name()
                },
                'token': token.key
            }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """用户登录视图"""
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = serializer.validated_data['user']
    login(request, user)
    
    token, created = Token.objects.get_or_create(user=user)
    
    logger.info(f"用户登录: {user.username}")
    
    return Response({
        'message': '登录成功',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_type': user.user_type,
            'is_active': user.is_active,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None
        },
        'tokens': {
            'access': token.key,
            'refresh': token.key  # 使用同一个token作为access和refresh
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """用户登出视图"""
    try:
        # 删除用户的token
        request.user.auth_token.delete()
    except:
        pass
    
    logout(request)
    logger.info(f"用户登出: {request.user.username}")
    
    return Response({'message': '登出成功'})


class UserProfileView(generics.RetrieveUpdateAPIView):
    """用户基本信息视图"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class PasswordChangeView(generics.GenericAPIView):
    """密码修改视图"""
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        logger.info(f"用户修改密码: {request.user.username}")
        
        return Response({'message': '密码修改成功'})


class StudentProfileView(generics.RetrieveUpdateAPIView):
    """学生档案视图"""
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        if self.request.user.user_type != 'student':
            raise permissions.PermissionDenied("只有学生用户可以访问学生档案")
        
        profile, created = StudentProfile.objects.get_or_create(user=self.request.user)
        return profile


class EmployerProfileView(generics.RetrieveUpdateAPIView):
    """雇主档案视图"""
    serializer_class = EmployerProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        if self.request.user.user_type != 'employer':
            raise permissions.PermissionDenied("只有雇主用户可以访问雇主档案")
        
        profile, created = EmployerProfile.objects.get_or_create(user=self.request.user)
        return profile


class SkillListView(generics.ListAPIView):
    """技能列表视图"""
    queryset = Skill.objects.filter(is_active=True)
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        
        if category:
            queryset = queryset.filter(category=category)
        
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset.order_by('category', 'name')


class StudentSkillListCreateView(generics.ListCreateAPIView):
    """学生技能列表和创建视图"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return StudentSkillCreateSerializer
        return StudentSkillSerializer
    
    def get_queryset(self):
        if self.request.user.user_type != 'student':
            return StudentSkill.objects.none()
        
        try:
            student_profile = StudentProfile.objects.get(user=self.request.user)
            return StudentSkill.objects.filter(student=student_profile).select_related('skill')
        except StudentProfile.DoesNotExist:
            return StudentSkill.objects.none()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.user.user_type == 'student':
            try:
                context['student'] = StudentProfile.objects.get(user=self.request.user)
            except StudentProfile.DoesNotExist:
                pass
        return context
    
    def create(self, request, *args, **kwargs):
        if request.user.user_type != 'student':
            return Response(
                {'error': '只有学生用户可以添加技能'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().create(request, *args, **kwargs)


class StudentSkillDetailView(generics.RetrieveUpdateDestroyAPIView):
    """学生技能详情视图"""
    serializer_class = StudentSkillSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.user_type != 'student':
            return StudentSkill.objects.none()
        
        try:
            student_profile = StudentProfile.objects.get(user=self.request.user)
            return StudentSkill.objects.filter(student=student_profile)
        except StudentProfile.DoesNotExist:
            return StudentSkill.objects.none()


class ProjectListCreateView(generics.ListCreateAPIView):
    """项目列表和创建视图"""
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.user_type != 'student':
            return Project.objects.none()
        
        try:
            student_profile = StudentProfile.objects.get(user=self.request.user)
            return Project.objects.filter(student=student_profile).order_by('-start_date')
        except StudentProfile.DoesNotExist:
            return Project.objects.none()
    
    def perform_create(self, serializer):
        if self.request.user.user_type != 'student':
            raise permissions.PermissionDenied("只有学生用户可以创建项目")
        
        try:
            student_profile = StudentProfile.objects.get(user=self.request.user)
            serializer.save(student=student_profile)
        except StudentProfile.DoesNotExist:
            raise permissions.PermissionDenied("学生档案不存在")


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """项目详情视图"""
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.user_type != 'student':
            return Project.objects.none()
        
        try:
            student_profile = StudentProfile.objects.get(user=self.request.user)
            return Project.objects.filter(student=student_profile)
        except StudentProfile.DoesNotExist:
            return Project.objects.none()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_dashboard(request):
    """用户仪表板数据"""
    user = request.user
    
    if user.user_type == 'student':
        try:
            student_profile = StudentProfile.objects.get(user=user)
            skills_count = StudentSkill.objects.filter(student=student_profile).count()
            projects_count = Project.objects.filter(student=student_profile).count()
            
            # 获取申请统计
            from applications.models import Application
            applications = Application.objects.filter(student=student_profile)
            applications_count = applications.count()
            pending_applications = applications.filter(status='pending').count()
            
            # 获取匹配统计
            from matching.models import MatchResult
            matches = MatchResult.objects.filter(student=student_profile, is_active=True)
            high_matches = matches.filter(overall_score__gte=80).count()
            
            return Response({
                'user_type': 'student',
                'profile_completion': _calculate_student_profile_completion(student_profile),
                'stats': {
                    'skills_count': skills_count,
                    'projects_count': projects_count,
                    'applications_count': applications_count,
                    'pending_applications': pending_applications,
                    'high_quality_matches': high_matches
                }
            })
            
        except StudentProfile.DoesNotExist:
            return Response({'error': '学生档案不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    elif user.user_type == 'employer':
        try:
            employer_profile = EmployerProfile.objects.get(user=user)
            
            # 获取职位统计
            from jobs.models import Job
            jobs = Job.objects.filter(employer=employer_profile)
            active_jobs = jobs.filter(is_active=True).count()
            total_jobs = jobs.count()
            
            # 获取申请统计
            from applications.models import Application
            applications = Application.objects.filter(job__employer=employer_profile)
            total_applications = applications.count()
            pending_applications = applications.filter(status='pending').count()
            
            return Response({
                'user_type': 'employer',
                'profile_completion': _calculate_employer_profile_completion(employer_profile),
                'stats': {
                    'active_jobs': active_jobs,
                    'total_jobs': total_jobs,
                    'total_applications': total_applications,
                    'pending_applications': pending_applications
                }
            })
            
        except EmployerProfile.DoesNotExist:
            return Response({'error': '雇主档案不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    else:
        return Response({'error': '未知用户类型'}, status=status.HTTP_400_BAD_REQUEST)


def _calculate_student_profile_completion(profile):
    """计算学生档案完成度"""
    total_fields = 12
    completed_fields = 0
    
    # 检查必填字段
    if profile.education_level:
        completed_fields += 1
    if profile.major:
        completed_fields += 1
    if profile.university:
        completed_fields += 1
    if profile.graduation_year:
        completed_fields += 1
    if profile.bio:
        completed_fields += 1
    if profile.preferred_job_types:
        completed_fields += 1
    if profile.preferred_locations:
        completed_fields += 1
    if profile.expected_salary_min:
        completed_fields += 1
    if profile.availability_date:
        completed_fields += 1
    
    # 检查技能
    if StudentSkill.objects.filter(student=profile).exists():
        completed_fields += 1
    
    # 检查项目
    if Project.objects.filter(student=profile).exists():
        completed_fields += 1
    
    # 检查链接
    links = [profile.resume_url, profile.portfolio_url, profile.linkedin_url, profile.github_url]
    if any(links):
        completed_fields += 1
    
    return round((completed_fields / total_fields) * 100, 1)


def _calculate_employer_profile_completion(profile):
    """计算雇主档案完成度"""
    total_fields = 8
    completed_fields = 0
    
    # 检查必填字段
    if profile.company_name:
        completed_fields += 1
    if profile.company_description:
        completed_fields += 1
    if profile.industry:
        completed_fields += 1
    if profile.company_size:
        completed_fields += 1
    if profile.contact_person:
        completed_fields += 1
    if profile.contact_phone:
        completed_fields += 1
    if profile.contact_email:
        completed_fields += 1
    if profile.company_address:
        completed_fields += 1
    
    return round((completed_fields / total_fields) * 100, 1)
