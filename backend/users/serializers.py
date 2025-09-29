"""
用户模块序列化器
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, StudentProfile, EmployerProfile, Skill, StudentSkill, Project


class SkillSerializer(serializers.ModelSerializer):
    """技能序列化器"""
    
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'description', 'is_active']
        read_only_fields = ['id']


class StudentSkillSerializer(serializers.ModelSerializer):
    """学生技能序列化器"""
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.IntegerField(write_only=True)
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    
    class Meta:
        model = StudentSkill
        fields = [
            'id', 'skill', 'skill_id', 'skill_name', 
            'proficiency_level', 'years_of_experience', 'is_certified'
        ]
        read_only_fields = ['id']
    
    def validate_skill_id(self, value):
        """验证技能ID"""
        try:
            Skill.objects.get(id=value, is_active=True)
        except Skill.DoesNotExist:
            raise serializers.ValidationError("技能不存在或已停用")
        return value


class ProjectSerializer(serializers.ModelSerializer):
    """项目序列化器"""
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'technologies_used',
            'start_date', 'end_date', 'project_url', 'github_url',
            'role', 'achievements', 'is_featured'
        ]
        read_only_fields = ['id']
    
    def validate(self, data):
        """验证项目数据"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("开始日期不能晚于结束日期")
        
        return data


class StudentProfileSerializer(serializers.ModelSerializer):
    """学生档案序列化器"""
    skills = StudentSkillSerializer(source='studentskill_set', many=True, read_only=True)
    projects = ProjectSerializer(source='project_set', many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = [
            'id', 'username', 'email', 'full_name',
            'education_level', 'major', 'university', 'graduation_year',
            'gpa', 'bio', 'resume_url', 'portfolio_url', 'linkedin_url',
            'github_url', 'preferred_job_types', 'preferred_locations',
            'expected_salary_min', 'expected_salary_max', 'availability_date',
            'is_seeking_job', 'skills', 'projects', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'username', 'email', 'full_name', 'created_at', 'updated_at']
    
    def validate_graduation_year(self, value):
        """验证毕业年份"""
        from datetime import datetime
        current_year = datetime.now().year
        
        if value < 1950 or value > current_year + 10:
            raise serializers.ValidationError("毕业年份不合理")
        
        return value
    
    def validate(self, data):
        """验证学生档案数据"""
        expected_salary_min = data.get('expected_salary_min')
        expected_salary_max = data.get('expected_salary_max')
        
        if expected_salary_min and expected_salary_max:
            if expected_salary_min > expected_salary_max:
                raise serializers.ValidationError("最低期望薪资不能高于最高期望薪资")
        
        return data


class EmployerProfileSerializer(serializers.ModelSerializer):
    """雇主档案序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = EmployerProfile
        fields = [
            'id', 'username', 'email', 'company_name', 'company_description',
            'industry', 'company_size', 'website_url', 'company_logo_url',
            'contact_person', 'contact_phone', 'contact_email',
            'company_address', 'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'username', 'email', 'is_verified', 'created_at', 'updated_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'user_type', 'phone'
        ]
    
    def validate(self, data):
        """验证注册数据"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("两次输入的密码不一致")
        
        return data
    
    def create(self, validated_data):
        """创建用户"""
        validated_data.pop('password_confirm')
        user_type = validated_data.pop('user_type')
        
        user = User.objects.create_user(**validated_data)
        user.user_type = user_type
        user.save()
        
        # 根据用户类型创建对应的档案
        if user_type == 'student':
            StudentProfile.objects.create(user=user)
        elif user_type == 'employer':
            EmployerProfile.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """验证登录数据"""
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            # 先通过邮箱查找用户
            try:
                user = User.objects.get(email=email)
                # 使用用户名进行认证（Django默认认证方式）
                user = authenticate(username=user.username, password=password)
                if not user:
                    raise serializers.ValidationError("邮箱或密码错误")
            except User.DoesNotExist:
                raise serializers.ValidationError("邮箱或密码错误")
            
            if not user.is_active:
                raise serializers.ValidationError("用户账户已被禁用")
            
            data['user'] = user
        else:
            raise serializers.ValidationError("必须提供邮箱和密码")
        
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """用户基本信息序列化器"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'user_type', 'phone', 'avatar', 'is_active',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'username', 'user_type', 'date_joined', 'last_login']


class PasswordChangeSerializer(serializers.Serializer):
    """密码修改序列化器"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_old_password(self, value):
        """验证旧密码"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("旧密码错误")
        return value
    
    def validate(self, data):
        """验证密码修改数据"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("两次输入的新密码不一致")
        return data
    
    def save(self):
        """保存新密码"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class StudentSkillCreateSerializer(serializers.ModelSerializer):
    """创建学生技能序列化器"""
    
    class Meta:
        model = StudentSkill
        fields = ['skill_id', 'proficiency_level', 'years_of_experience', 'is_certified']
    
    def validate_skill_id(self, value):
        """验证技能ID"""
        try:
            Skill.objects.get(id=value, is_active=True)
        except Skill.DoesNotExist:
            raise serializers.ValidationError("技能不存在或已停用")
        return value
    
    def create(self, validated_data):
        """创建学生技能"""
        student = self.context['student']
        skill_id = validated_data['skill_id']
        
        # 检查是否已存在该技能
        if StudentSkill.objects.filter(student=student, skill_id=skill_id).exists():
            raise serializers.ValidationError("该技能已存在")
        
        validated_data['student'] = student
        return super().create(validated_data)