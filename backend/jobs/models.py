from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import EmployerProfile, Skill


class Job(models.Model):
    """职位模型"""
    JOB_TYPES = [
        ('full_time', '全职'),
        ('part_time', '兼职'),
        ('internship', '实习'),
        ('contract', '合同工'),
        ('freelance', '自由职业'),
    ]
    
    EXPERIENCE_LEVELS = [
        ('entry', '入门级'),
        ('junior', '初级'),
        ('mid', '中级'),
        ('senior', '高级'),
        ('lead', '领导级'),
        ('executive', '管理层'),
    ]
    
    REMOTE_OPTIONS = [
        ('on_site', '现场办公'),
        ('remote', '远程办公'),
        ('hybrid', '混合办公'),
    ]
    
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name='jobs')
    
    # 基本信息
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=3000)
    requirements = models.TextField(max_length=2000)
    responsibilities = models.TextField(max_length=2000)
    
    # 职位详情
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS)
    remote_option = models.CharField(max_length=20, choices=REMOTE_OPTIONS, default='on_site')
    
    # 技能要求
    required_skills = models.ManyToManyField(Skill, through='JobSkillRequirement', related_name='required_for_jobs')
    preferred_skills = models.ManyToManyField(Skill, through='JobSkillPreference', related_name='preferred_for_jobs')
    
    # 薪资和福利
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=10, default='CNY')
    benefits = models.JSONField(default=list, blank=True)
    
    # 地理位置
    location_city = models.CharField(max_length=100)
    location_state = models.CharField(max_length=100, blank=True)
    location_country = models.CharField(max_length=100, default='中国')
    
    # 申请设置
    application_deadline = models.DateTimeField(null=True, blank=True)
    max_applications = models.IntegerField(null=True, blank=True)
    
    # 状态
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', '-created_at']),
            models.Index(fields=['job_type', 'experience_level']),
            models.Index(fields=['location_city']),
        ]

    def __str__(self):
        return f"{self.title} - {self.employer.company_name}"

    @property
    def applications_count(self):
        return self.applications.count()

    @property
    def salary_range_display(self):
        if self.salary_min and self.salary_max:
            return f"{self.salary_min:,.0f} - {self.salary_max:,.0f} {self.salary_currency}"
        elif self.salary_min:
            return f"{self.salary_min:,.0f}+ {self.salary_currency}"
        return "薪资面议"

    def increment_views(self):
        """增加浏览次数"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class JobSkillRequirement(models.Model):
    """职位必需技能模型"""
    IMPORTANCE_LEVELS = [
        ('critical', '关键'),
        ('important', '重要'),
        ('nice_to_have', '加分项'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    importance = models.CharField(max_length=20, choices=IMPORTANCE_LEVELS, default='important')
    min_experience_years = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    weight = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.1), MaxValueValidator(5.0)],
        help_text="匹配算法中的权重 (0.1-5.0)"
    )

    class Meta:
        unique_together = ['job', 'skill']

    def __str__(self):
        return f"{self.job.title} - {self.skill.name} ({self.importance})"


class JobSkillPreference(models.Model):
    """职位偏好技能模型"""
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    bonus_points = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0.1), MaxValueValidator(2.0)],
        help_text="额外加分 (0.1-2.0)"
    )

    class Meta:
        unique_together = ['job', 'skill']

    def __str__(self):
        return f"{self.job.title} - {self.skill.name} (偏好)"


class JobCategory(models.Model):
    """职位分类模型"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name_plural = "Job Categories"

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    @property
    def full_path(self):
        """获取完整分类路径"""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name


class JobAlert(models.Model):
    """职位提醒模型"""
    from users.models import User
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_alerts')
    name = models.CharField(max_length=200)
    
    # 搜索条件
    keywords = models.CharField(max_length=500, blank=True)
    job_types = models.JSONField(default=list, blank=True)
    experience_levels = models.JSONField(default=list, blank=True)
    locations = models.JSONField(default=list, blank=True)
    remote_options = models.JSONField(default=list, blank=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # 通知设置
    is_active = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', '立即'),
            ('daily', '每日'),
            ('weekly', '每周'),
        ],
        default='daily'
    )
    
    last_sent = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"


# 将Job模型与JobCategory关联
Job.add_to_class('category', models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs'))
