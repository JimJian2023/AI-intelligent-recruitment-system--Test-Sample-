from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator


class User(AbstractUser):
    """扩展的用户模型"""
    USER_TYPE_CHOICES = [
        ('student', '学生'),
        ('employer', '雇主'),
        ('admin', '管理员'),
    ]
    
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPE_CHOICES,
        default='student'
    )
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class Skill(models.Model):
    """技能标签模型"""
    SKILL_CATEGORIES = [
        ('programming', '编程语言'),
        ('framework', '框架技术'),
        ('database', '数据库'),
        ('cloud', '云计算'),
        ('design', '设计'),
        ('soft_skill', '软技能'),
        ('other', '其他'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=SKILL_CATEGORIES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class StudentProfile(models.Model):
    """学生档案模型"""
    EDUCATION_LEVELS = [
        ('bachelor', '本科'),
        ('master', '硕士'),
        ('phd', '博士'),
        ('diploma', '专科'),
    ]
    
    EXPERIENCE_LEVELS = [
        ('beginner', '初学者'),
        ('intermediate', '中级'),
        ('advanced', '高级'),
        ('expert', '专家'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    
    # 基本信息
    university = models.CharField(max_length=200)
    major = models.CharField(max_length=200)
    education_level = models.CharField(max_length=20, choices=EDUCATION_LEVELS)
    graduation_year = models.IntegerField()
    gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
    # 技能和经验
    skills = models.ManyToManyField(Skill, through='StudentSkill')
    bio = models.TextField(max_length=1000, blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    
    # 偏好设置
    preferred_locations = models.JSONField(default=list, blank=True)
    preferred_company_sizes = models.JSONField(default=list, blank=True)
    preferred_industries = models.JSONField(default=list, blank=True)
    
    # 简历文件
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    
    # 状态
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.university}"

    @property
    def skill_count(self):
        return self.skills.count()

    @property
    def match_score_cache_key(self):
        return f"student_match_{self.user.id}"


class StudentSkill(models.Model):
    """学生技能关联模型（带熟练度）"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency_level = models.CharField(
        max_length=20, 
        choices=StudentProfile.EXPERIENCE_LEVELS,
        default='beginner'
    )
    years_of_experience = models.DecimalField(
        max_digits=4, 
        decimal_places=1, 
        default=0.0
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'skill']

    def __str__(self):
        return f"{self.student.user.username} - {self.skill.name} ({self.proficiency_level})"


class EmployerProfile(models.Model):
    """雇主档案模型"""
    COMPANY_SIZES = [
        ('startup', '初创公司 (1-10人)'),
        ('small', '小型公司 (11-50人)'),
        ('medium', '中型公司 (51-200人)'),
        ('large', '大型公司 (201-1000人)'),
        ('enterprise', '企业级 (1000+人)'),
    ]
    
    INDUSTRIES = [
        ('technology', '科技'),
        ('finance', '金融'),
        ('healthcare', '医疗'),
        ('education', '教育'),
        ('retail', '零售'),
        ('manufacturing', '制造业'),
        ('consulting', '咨询'),
        ('other', '其他'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    
    # 公司信息
    company_name = models.CharField(max_length=200)
    company_size = models.CharField(max_length=20, choices=COMPANY_SIZES)
    industry = models.CharField(max_length=20, choices=INDUSTRIES)
    company_description = models.TextField(max_length=2000)
    website = models.URLField(blank=True)
    
    # 联系信息
    contact_person = models.CharField(max_length=100)
    contact_title = models.CharField(max_length=100)
    office_address = models.TextField()
    
    # 公司文化和价值观
    company_culture = models.TextField(max_length=1000, blank=True)
    benefits = models.JSONField(default=list, blank=True)
    
    # 验证状态
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name} - {self.contact_person}"

    @property
    def active_jobs_count(self):
        return self.jobs.filter(is_active=True).count()


class Project(models.Model):
    """学生项目经历模型"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    technologies_used = models.ManyToManyField(Skill, blank=True)
    project_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_ongoing = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.student.user.username} - {self.title}"
