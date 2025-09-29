from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from users.models import StudentProfile
from jobs.models import Job
import json


class MatchResult(models.Model):
    """匹配结果模型"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='match_results')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='match_results')
    
    # 匹配分数
    overall_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="总体匹配分数 (0-100)"
    )
    
    # 详细分数
    skill_match_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="技能匹配分数"
    )
    experience_match_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="经验匹配分数"
    )
    education_match_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="教育背景匹配分数"
    )
    location_match_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="地理位置匹配分数"
    )
    
    # 匹配详情（JSON格式存储详细分析）
    match_details = models.JSONField(default=dict, blank=True)
    
    # 推荐理由
    recommendation_reasons = models.JSONField(default=list, blank=True)
    
    # 改进建议
    improvement_suggestions = models.JSONField(default=list, blank=True)
    
    # 匹配状态
    is_active = models.BooleanField(default=True)
    is_viewed_by_student = models.BooleanField(default=False)
    is_viewed_by_employer = models.BooleanField(default=False)
    
    # 时间戳
    calculated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'job']
        ordering = ['-overall_score', '-calculated_at']
        indexes = [
            models.Index(fields=['student', '-overall_score']),
            models.Index(fields=['job', '-overall_score']),
            models.Index(fields=['overall_score']),
        ]

    def __str__(self):
        return f"{self.student.user.get_full_name()} -> {self.job.title} ({self.overall_score:.1f}%)"

    @property
    def match_level(self):
        """根据分数返回匹配等级"""
        if self.overall_score >= 90:
            return 'excellent'
        elif self.overall_score >= 80:
            return 'very_good'
        elif self.overall_score >= 70:
            return 'good'
        elif self.overall_score >= 60:
            return 'fair'
        else:
            return 'poor'

    @property
    def match_level_display(self):
        """匹配等级显示文本"""
        levels = {
            'excellent': '极佳匹配',
            'very_good': '很好匹配',
            'good': '良好匹配',
            'fair': '一般匹配',
            'poor': '匹配度低'
        }
        return levels.get(self.match_level, '未知')


class SkillMatchDetail(models.Model):
    """技能匹配详情模型"""
    match_result = models.ForeignKey(MatchResult, on_delete=models.CASCADE, related_name='skill_details')
    skill_name = models.CharField(max_length=100)
    
    # 学生技能信息
    student_has_skill = models.BooleanField(default=False)
    student_proficiency = models.CharField(max_length=20, blank=True)
    student_experience_years = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    
    # 职位要求信息
    job_requires_skill = models.BooleanField(default=False)
    job_skill_importance = models.CharField(max_length=20, blank=True)
    job_min_experience = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    job_skill_weight = models.FloatField(default=1.0)
    
    # 匹配分析
    match_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    is_missing_skill = models.BooleanField(default=False)
    is_bonus_skill = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-match_score', 'skill_name']

    def __str__(self):
        return f"{self.match_result} - {self.skill_name} ({self.match_score:.1f}%)"


class MatchingAlgorithmConfig(models.Model):
    """匹配算法配置模型"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    # 权重配置
    skill_weight = models.FloatField(default=0.4, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    experience_weight = models.FloatField(default=0.3, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    education_weight = models.FloatField(default=0.2, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    location_weight = models.FloatField(default=0.1, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    # 算法参数
    algorithm_params = models.JSONField(default=dict, blank=True)
    
    # 状态
    is_active = models.BooleanField(default=False)
    version = models.CharField(max_length=20, default='1.0')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} v{self.version}"

    def save(self, *args, **kwargs):
        # 确保权重总和为1.0
        total_weight = self.skill_weight + self.experience_weight + self.education_weight + self.location_weight
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError("权重总和必须等于1.0")
        super().save(*args, **kwargs)


class MatchingJob(models.Model):
    """匹配任务模型（用于批量匹配）"""
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('running', '运行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('cancelled', '已取消'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # 匹配范围
    target_students = models.ManyToManyField(StudentProfile, blank=True)
    target_jobs = models.ManyToManyField(Job, blank=True)
    
    # 匹配条件
    min_match_score = models.FloatField(default=60.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    max_results_per_student = models.IntegerField(default=10, validators=[MinValueValidator(1)])
    
    # 使用的算法配置
    algorithm_config = models.ForeignKey(MatchingAlgorithmConfig, on_delete=models.CASCADE)
    
    # 执行状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress_percentage = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # 执行结果
    total_matches_found = models.IntegerField(default=0)
    execution_time_seconds = models.FloatField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"

    def start_execution(self):
        """开始执行匹配任务"""
        self.status = 'running'
        self.started_at = timezone.now()
        self.save()

    def complete_execution(self, total_matches=0, execution_time=None):
        """完成匹配任务"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.progress_percentage = 100
        self.total_matches_found = total_matches
        if execution_time:
            self.execution_time_seconds = execution_time
        self.save()

    def fail_execution(self, error_message):
        """标记任务失败"""
        self.status = 'failed'
        self.completed_at = timezone.now()
        self.error_message = error_message
        self.save()


class StudentRecommendation(models.Model):
    """学生推荐模型（基于历史数据和行为）"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='recommendations')
    
    # 推荐内容
    recommended_jobs = models.ManyToManyField(Job, through='RecommendationItem')
    recommended_skills = models.JSONField(default=list, blank=True)
    career_suggestions = models.JSONField(default=list, blank=True)
    
    # 推荐基础
    based_on_applications = models.BooleanField(default=False)
    based_on_saved_jobs = models.BooleanField(default=False)
    based_on_profile_similarity = models.BooleanField(default=False)
    based_on_market_trends = models.BooleanField(default=False)
    
    # 推荐质量
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="推荐置信度 (0-1)"
    )
    
    # 状态
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"推荐给 {self.student.user.get_full_name()}"


class RecommendationItem(models.Model):
    """推荐项目详情"""
    recommendation = models.ForeignKey(StudentRecommendation, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    
    # 推荐分数和理由
    recommendation_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    recommendation_reasons = models.JSONField(default=list, blank=True)
    
    # 用户反馈
    is_clicked = models.BooleanField(default=False)
    is_applied = models.BooleanField(default=False)
    is_saved = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    
    # 反馈时间
    clicked_at = models.DateTimeField(null=True, blank=True)
    applied_at = models.DateTimeField(null=True, blank=True)
    saved_at = models.DateTimeField(null=True, blank=True)
    dismissed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['recommendation', 'job']
        ordering = ['-recommendation_score']

    def __str__(self):
        return f"{self.recommendation.student.user.get_full_name()} -> {self.job.title} ({self.recommendation_score:.1f})"
