"""
申请模块序列化器
"""

from rest_framework import serializers
from django.utils import timezone
from .models import (
    Application, ApplicationStatusHistory, Interview, 
    Feedback, SavedJob, ApplicationNote
)
from jobs.models import Job
from users.models import StudentProfile, EmployerProfile


class ApplicationListSerializer(serializers.ModelSerializer):
    """申请列表序列化器（简化版）"""
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_company = serializers.CharField(source='job.employer.company_name', read_only=True)
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_email = serializers.CharField(source='student.user.email', read_only=True)
    
    class Meta:
        model = Application
        fields = [
            'id', 'job_title', 'job_company', 'student_name', 'student_email',
            'status', 'ai_match_score', 'applied_at', 'updated_at'
        ]
        read_only_fields = ['id', 'applied_at', 'updated_at']


class ApplicationDetailSerializer(serializers.ModelSerializer):
    """申请详情序列化器"""
    job_info = serializers.SerializerMethodField()
    student_info = serializers.SerializerMethodField()
    skill_match_details = serializers.JSONField(read_only=True)
    status_history = serializers.SerializerMethodField()
    interviews = serializers.SerializerMethodField()
    feedback = serializers.SerializerMethodField()
    
    class Meta:
        model = Application
        fields = [
            'id', 'job_info', 'student_info', 'cover_letter',
            'status', 'ai_match_score', 'skill_match_details',
            'applied_at', 'updated_at', 'status_history',
            'interviews', 'feedback'
        ]
        read_only_fields = ['id', 'applied_at', 'updated_at']
    
    def get_job_info(self, obj):
        """获取职位信息"""
        return {
            'id': obj.job.id,
            'title': obj.job.title,
            'company_name': obj.job.employer.company_name,
            'location_city': obj.job.location_city,
            'job_type': obj.job.job_type,
            'experience_level': obj.job.experience_level,
            'salary_min': obj.job.salary_min,
            'salary_max': obj.job.salary_max
        }
    
    def get_student_info(self, obj):
        """获取学生信息"""
        return {
            'id': obj.student.id,
            'name': obj.student.user.get_full_name(),
            'email': obj.student.user.email,
            'phone': obj.student.user.phone,
            'education_level': obj.student.education_level,
            'major': obj.student.major,
            'university': obj.student.university,
            'graduation_year': obj.student.graduation_year
        }
    
    def get_status_history(self, obj):
        """获取状态历史"""
        history = obj.applicationstatushistory_set.all().order_by('-changed_at')
        return [{
            'status': item.status,
            'changed_at': item.changed_at,
            'changed_by': item.changed_by.get_full_name() if item.changed_by else None,
            'notes': item.notes
        } for item in history]
    
    def get_interviews(self, obj):
        """获取面试信息"""
        interviews = obj.interview_set.all().order_by('-scheduled_at')
        return [{
            'id': interview.id,
            'interview_type': interview.interview_type,
            'scheduled_at': interview.scheduled_at,
            'location': interview.location,
            'interviewer_name': interview.interviewer_name,
            'status': interview.status,
            'evaluation_score': interview.evaluation_score
        } for interview in interviews]
    
    def get_feedback(self, obj):
        """获取反馈信息"""
        feedback = obj.feedback_set.first()
        if feedback:
            return {
                'id': feedback.id,
                'rating': feedback.rating,
                'comment': feedback.comment,
                'technical_skills': feedback.technical_skills,
                'communication': feedback.communication,
                'problem_solving': feedback.problem_solving,
                'cultural_fit': feedback.cultural_fit,
                'created_at': feedback.created_at
            }
        return None


class ApplicationCreateSerializer(serializers.ModelSerializer):
    """申请创建序列化器"""
    
    class Meta:
        model = Application
        fields = ['job', 'cover_letter']
    
    def validate_job(self, value):
        """验证职位"""
        if not value.is_active:
            raise serializers.ValidationError("该职位已关闭")
        
        if value.application_deadline and value.application_deadline < timezone.now().date():
            raise serializers.ValidationError("申请截止日期已过")
        
        return value
    
    def create(self, validated_data):
        """创建申请"""
        student = self.context['student']
        job = validated_data['job']
        
        # 检查是否已申请
        if Application.objects.filter(student=student, job=job).exists():
            raise serializers.ValidationError("您已经申请过这个职位")
        
        validated_data['student'] = student
        validated_data['status'] = 'pending'
        
        return super().create(validated_data)


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    """申请状态更新序列化器"""
    notes = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Application
        fields = ['status', 'notes']
    
    def update(self, instance, validated_data):
        """更新申请状态"""
        notes = validated_data.pop('notes', '')
        old_status = instance.status
        new_status = validated_data.get('status', old_status)
        
        # 更新申请状态
        instance = super().update(instance, validated_data)
        
        # 记录状态变更历史
        if old_status != new_status:
            ApplicationStatusHistory.objects.create(
                application=instance,
                status=new_status,
                changed_by=self.context['request'].user,
                notes=notes
            )
        
        return instance


class InterviewSerializer(serializers.ModelSerializer):
    """面试序列化器"""
    application_info = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Interview
        fields = [
            'id', 'application', 'application_info', 'interview_type',
            'scheduled_at', 'location', 'meeting_link', 'interviewer_name',
            'interviewer_email', 'status', 'evaluation_score', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_application_info(self, obj):
        """获取申请信息"""
        return {
            'id': obj.application.id,
            'job_title': obj.application.job.title,
            'student_name': obj.application.student.user.get_full_name(),
            'student_email': obj.application.student.user.email
        }
    
    def validate_scheduled_at(self, value):
        """验证面试时间"""
        if value <= timezone.now():
            raise serializers.ValidationError("面试时间必须是未来的时间")
        return value


class FeedbackSerializer(serializers.ModelSerializer):
    """反馈序列化器"""
    application_info = serializers.SerializerMethodField(read_only=True)
    given_by_name = serializers.CharField(source='given_by.get_full_name', read_only=True)
    
    class Meta:
        model = Feedback
        fields = [
            'id', 'application', 'application_info', 'feedback_type',
            'rating', 'comment', 'technical_skills', 'communication',
            'problem_solving', 'cultural_fit', 'given_by', 'given_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'given_by', 'created_at', 'updated_at']
    
    def get_application_info(self, obj):
        """获取申请信息"""
        return {
            'id': obj.application.id,
            'job_title': obj.application.job.title,
            'student_name': obj.application.student.user.get_full_name(),
            'company_name': obj.application.job.employer.company_name
        }
    
    def create(self, validated_data):
        """创建反馈"""
        validated_data['given_by'] = self.context['request'].user
        return super().create(validated_data)


class SavedJobSerializer(serializers.ModelSerializer):
    """收藏职位序列化器"""
    job_info = serializers.SerializerMethodField()
    
    class Meta:
        model = SavedJob
        fields = ['id', 'job', 'job_info', 'saved_at', 'notes']
        read_only_fields = ['id', 'saved_at']
    
    def get_job_info(self, obj):
        """获取职位信息"""
        return {
            'id': obj.job.id,
            'title': obj.job.title,
            'company_name': obj.job.employer.company_name,
            'location_city': obj.job.location_city,
            'job_type': obj.job.job_type,
            'salary_min': obj.job.salary_min,
            'salary_max': obj.job.salary_max,
            'is_active': obj.job.is_active
        }
    
    def create(self, validated_data):
        """创建收藏"""
        student = self.context['student']
        job = validated_data['job']
        
        # 检查是否已收藏
        if SavedJob.objects.filter(student=student, job=job).exists():
            raise serializers.ValidationError("您已经收藏过这个职位")
        
        validated_data['student'] = student
        return super().create(validated_data)


class ApplicationNoteSerializer(serializers.ModelSerializer):
    """申请备注序列化器"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ApplicationNote
        fields = [
            'id', 'application', 'note_type', 'content',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """创建备注"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ApplicationStatisticsSerializer(serializers.Serializer):
    """申请统计序列化器"""
    total_applications = serializers.IntegerField()
    pending_applications = serializers.IntegerField()
    reviewed_applications = serializers.IntegerField()
    accepted_applications = serializers.IntegerField()
    rejected_applications = serializers.IntegerField()
    average_match_score = serializers.FloatField()
    applications_this_month = serializers.IntegerField()
    success_rate = serializers.FloatField()