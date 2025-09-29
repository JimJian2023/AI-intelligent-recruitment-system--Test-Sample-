"""
职位模块序列化器
"""

from rest_framework import serializers
from django.utils import timezone
from .models import Job, JobSkillRequirement, JobSkillPreference, JobCategory, JobAlert
from users.models import Skill, EmployerProfile


class JobCategorySerializer(serializers.ModelSerializer):
    """职位分类序列化器"""
    
    class Meta:
        model = JobCategory
        fields = ['id', 'name', 'description', 'is_active']
        read_only_fields = ['id']


class JobSkillRequirementSerializer(serializers.ModelSerializer):
    """职位技能要求序列化器"""
    skill = serializers.StringRelatedField(read_only=True)
    skill_id = serializers.IntegerField(write_only=True)
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    
    class Meta:
        model = JobSkillRequirement
        fields = [
            'id', 'skill', 'skill_id', 'skill_name',
            'importance', 'min_experience_years', 'weight'
        ]
        read_only_fields = ['id']
    
    def validate_skill_id(self, value):
        """验证技能ID"""
        try:
            Skill.objects.get(id=value, is_active=True)
        except Skill.DoesNotExist:
            raise serializers.ValidationError("技能不存在或已停用")
        return value


class JobSkillPreferenceSerializer(serializers.ModelSerializer):
    """职位技能偏好序列化器"""
    skill = serializers.StringRelatedField(read_only=True)
    skill_id = serializers.IntegerField(write_only=True)
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    
    class Meta:
        model = JobSkillPreference
        fields = [
            'id', 'skill', 'skill_id', 'skill_name', 'bonus_points'
        ]
        read_only_fields = ['id']
    
    def validate_skill_id(self, value):
        """验证技能ID"""
        try:
            Skill.objects.get(id=value, is_active=True)
        except Skill.DoesNotExist:
            raise serializers.ValidationError("技能不存在或已停用")
        return value


class JobListSerializer(serializers.ModelSerializer):
    """职位列表序列化器（简化版）"""
    employer_name = serializers.CharField(source='employer.company_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    required_skills_count = serializers.SerializerMethodField()
    applications_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'employer_name', 'category_name',
            'job_type', 'experience_level', 'location_city',
            'remote_option', 'salary_min', 'salary_max',
            'application_deadline', 'is_active', 'created_at',
            'required_skills_count', 'applications_count'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_required_skills_count(self, obj):
        """获取必需技能数量"""
        return obj.jobskillrequirement_set.count()
    
    def get_applications_count(self, obj):
        """获取申请数量"""
        return obj.applications.count()


class JobDetailSerializer(serializers.ModelSerializer):
    """职位详情序列化器"""
    employer_name = serializers.CharField(source='employer.company_name', read_only=True)
    employer_info = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    required_skills = JobSkillRequirementSerializer(source='jobskillrequirement_set', many=True, read_only=True)
    preferred_skills = JobSkillPreferenceSerializer(source='jobskillpreference_set', many=True, read_only=True)
    applications_count = serializers.SerializerMethodField()
    is_applied = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'description', 'requirements',
            'employer_name', 'employer_info', 'category', 'category_name',
            'job_type', 'experience_level', 'location_city', 'location_state', 'location_country',
            'remote_option', 'salary_min', 'salary_max', 'benefits',
            'application_deadline', 'is_active', 'is_featured', 'created_at', 'updated_at',
            'required_skills', 'preferred_skills', 'applications_count', 'is_applied'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_employer_info(self, obj):
        """获取雇主基本信息"""
        return {
            'id': obj.employer.id,
            'company_name': obj.employer.company_name,
            'industry': obj.employer.industry,
            'company_size': obj.employer.company_size,
            'website_url': obj.employer.website_url,
            'is_verified': obj.employer.is_verified
        }
    
    def get_applications_count(self, obj):
        """获取申请数量"""
        return obj.application_set.count()
    
    def get_is_applied(self, obj):
        """检查当前用户是否已申请"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.user_type == 'student':
            try:
                from users.models import StudentProfile
                student_profile = StudentProfile.objects.get(user=request.user)
                return obj.application_set.filter(student=student_profile).exists()
            except StudentProfile.DoesNotExist:
                pass
        return False


class JobCreateUpdateSerializer(serializers.ModelSerializer):
    """职位创建/更新序列化器"""
    required_skills = JobSkillRequirementSerializer(many=True, required=False)
    preferred_skills = JobSkillPreferenceSerializer(many=True, required=False)
    
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'requirements', 'category',
            'job_type', 'experience_level', 'location_city', 'location_state', 'location_country',
            'remote_option', 'salary_min', 'salary_max', 'benefits',
            'application_deadline', 'is_featured', 'required_skills', 'preferred_skills'
        ]
    
    def validate_application_deadline(self, value):
        """验证申请截止日期"""
        from datetime import date
        
        # 如果value是datetime对象，转换为date
        if hasattr(value, 'date'):
            value = value.date()
        
        # 如果value是字符串，尝试解析为date
        if isinstance(value, str):
            try:
                from datetime import datetime
                value = datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                raise serializers.ValidationError("日期格式必须是YYYY-MM-DD")
        
        # 确保value是date对象
        if not isinstance(value, date):
            raise serializers.ValidationError("无效的日期格式")
        
        # 比较日期
        today = timezone.now().date()
        if value <= today:
            raise serializers.ValidationError("申请截止日期必须是未来的日期")
        return value
    
    def validate(self, data):
        """验证职位数据"""
        salary_min = data.get('salary_min')
        salary_max = data.get('salary_max')
        
        if salary_min and salary_max and salary_min > salary_max:
            raise serializers.ValidationError("最低薪资不能高于最高薪资")
        
        return data
    
    def create(self, validated_data):
        """创建职位"""
        required_skills_data = validated_data.pop('required_skills', [])
        preferred_skills_data = validated_data.pop('preferred_skills', [])
        
        # 从context获取雇主信息
        employer = self.context['employer']
        validated_data['employer'] = employer
        
        job = Job.objects.create(**validated_data)
        
        # 创建技能要求
        self._create_skill_requirements(job, required_skills_data)
        
        # 创建技能偏好
        self._create_skill_preferences(job, preferred_skills_data)
        
        return job
    
    def update(self, instance, validated_data):
        """更新职位"""
        required_skills_data = validated_data.pop('required_skills', None)
        preferred_skills_data = validated_data.pop('preferred_skills', None)
        
        # 更新基本信息
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # 更新技能要求
        if required_skills_data is not None:
            instance.jobskillrequirement_set.all().delete()
            self._create_skill_requirements(instance, required_skills_data)
        
        # 更新技能偏好
        if preferred_skills_data is not None:
            instance.jobskillpreference_set.all().delete()
            self._create_skill_preferences(instance, preferred_skills_data)
        
        return instance
    
    def _create_skill_requirements(self, job, skills_data):
        """创建技能要求"""
        for skill_data in skills_data:
            skill_id = skill_data.pop('skill_id')
            JobSkillRequirement.objects.create(
                job=job,
                skill_id=skill_id,
                **skill_data
            )
    
    def _create_skill_preferences(self, job, skills_data):
        """创建技能偏好"""
        for skill_data in skills_data:
            skill_id = skill_data.pop('skill_id')
            JobSkillPreference.objects.create(
                job=job,
                skill_id=skill_id,
                **skill_data
            )


class JobAlertSerializer(serializers.ModelSerializer):
    """职位提醒序列化器"""
    
    class Meta:
        model = JobAlert
        fields = [
            'id', 'keywords', 'location', 'job_type',
            'salary_min', 'experience_level', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """创建职位提醒"""
        # 从context获取学生信息
        student = self.context['student']
        validated_data['student'] = student
        return super().create(validated_data)


class JobSearchSerializer(serializers.Serializer):
    """职位搜索序列化器"""
    keywords = serializers.CharField(required=False, allow_blank=True)
    category = serializers.IntegerField(required=False)
    job_type = serializers.ChoiceField(choices=Job.JOB_TYPES, required=False)
    experience_level = serializers.ChoiceField(choices=Job.EXPERIENCE_LEVELS, required=False)
    location = serializers.CharField(required=False, allow_blank=True)
    remote_option = serializers.ChoiceField(choices=Job.REMOTE_OPTIONS, required=False)
    salary_min = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    salary_max = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    skills = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    
    def validate(self, data):
        """验证搜索参数"""
        salary_min = data.get('salary_min')
        salary_max = data.get('salary_max')
        
        if salary_min and salary_max and salary_min > salary_max:
            raise serializers.ValidationError("最低薪资不能高于最高薪资")
        
        return data