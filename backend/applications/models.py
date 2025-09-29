from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User, StudentProfile
from jobs.models import Job


class Application(models.Model):
    """求职申请模型"""
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('reviewing', '审核中'),
        ('interview_scheduled', '面试安排'),
        ('interview_completed', '面试完成'),
        ('offer_made', '发出录用'),
        ('accepted', '已接受'),
        ('rejected', '已拒绝'),
        ('withdrawn', '已撤回'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    
    # 申请内容
    cover_letter = models.TextField(max_length=2000, blank=True)
    custom_resume = models.FileField(upload_to='application_resumes/', blank=True, null=True)
    
    # 状态跟踪
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    status_updated_at = models.DateTimeField(auto_now=True)
    status_updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='status_updates')
    
    # 雇主反馈
    employer_notes = models.TextField(max_length=1000, blank=True)
    rejection_reason = models.TextField(max_length=500, blank=True)
    
    # 匹配分数（由AI算法计算）
    match_score = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="AI匹配分数 (0-100)"
    )
    skill_match_details = models.JSONField(default=dict, blank=True)
    
    # 时间戳
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'job']
        ordering = ['-applied_at']
        indexes = [
            models.Index(fields=['status', '-applied_at']),
            models.Index(fields=['job', 'status']),
            models.Index(fields=['student', '-applied_at']),
        ]

    def __str__(self):
        return f"{self.student.user.get_full_name()} -> {self.job.title}"

    @property
    def is_active(self):
        """检查申请是否仍在处理中"""
        return self.status in ['pending', 'reviewing', 'interview_scheduled', 'interview_completed']

    @property
    def days_since_applied(self):
        """计算申请天数"""
        from django.utils import timezone
        return (timezone.now() - self.applied_at).days

    def update_status(self, new_status, updated_by=None, notes=None):
        """更新申请状态"""
        old_status = self.status
        self.status = new_status
        self.status_updated_by = updated_by
        if notes:
            self.employer_notes = notes
        self.save()
        
        # 创建状态变更记录
        ApplicationStatusHistory.objects.create(
            application=self,
            old_status=old_status,
            new_status=new_status,
            changed_by=updated_by,
            notes=notes
        )


class ApplicationStatusHistory(models.Model):
    """申请状态变更历史"""
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20, choices=Application.STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=Application.STATUS_CHOICES)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(max_length=500, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.application} - {self.old_status} -> {self.new_status}"


class Interview(models.Model):
    """面试安排模型"""
    INTERVIEW_TYPES = [
        ('phone', '电话面试'),
        ('video', '视频面试'),
        ('on_site', '现场面试'),
        ('technical', '技术面试'),
        ('hr', 'HR面试'),
        ('final', '终面'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', '已安排'),
        ('confirmed', '已确认'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
        ('rescheduled', '已重新安排'),
    ]
    
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    
    # 面试详情
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPES)
    scheduled_at = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    location = models.CharField(max_length=500, blank=True)
    meeting_link = models.URLField(blank=True)
    
    # 面试官
    interviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conducted_interviews')
    interviewer_notes = models.TextField(max_length=1000, blank=True)
    
    # 状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # 评估
    technical_score = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    communication_score = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    cultural_fit_score = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    overall_rating = models.CharField(
        max_length=20,
        choices=[
            ('excellent', '优秀'),
            ('good', '良好'),
            ('average', '一般'),
            ('poor', '较差'),
        ],
        blank=True
    )
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scheduled_at']

    def __str__(self):
        return f"{self.application} - {self.get_interview_type_display()} ({self.scheduled_at.strftime('%Y-%m-%d %H:%M')})"

    @property
    def average_score(self):
        """计算平均评分"""
        scores = [s for s in [self.technical_score, self.communication_score, self.cultural_fit_score] if s is not None]
        return sum(scores) / len(scores) if scores else None


class Feedback(models.Model):
    """反馈模型（双向反馈）"""
    FEEDBACK_TYPES = [
        ('student_to_employer', '学生对雇主'),
        ('employer_to_student', '雇主对学生'),
        ('interview_feedback', '面试反馈'),
        ('application_feedback', '申请反馈'),
    ]
    
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_type = models.CharField(max_length=30, choices=FEEDBACK_TYPES)
    
    # 反馈内容
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="评分 1-5 星"
    )
    comment = models.TextField(max_length=1000)
    
    # 具体评价维度
    communication_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    professionalism_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    process_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # 是否推荐
    would_recommend = models.BooleanField(null=True, blank=True)
    
    # 提交者
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_feedbacks')
    
    # 可见性
    is_public = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_feedback_type_display()} - {self.rating}星 ({self.application})"


class SavedJob(models.Model):
    """收藏职位模型"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    notes = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'job']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.user.username} 收藏了 {self.job.title}"


class ApplicationNote(models.Model):
    """申请备注模型（雇主内部使用）"""
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='application_notes')
    content = models.TextField(max_length=1000)
    is_private = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"备注 - {self.application} by {self.author.username}"
