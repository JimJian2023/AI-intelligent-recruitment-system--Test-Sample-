from django.db import models
from django.utils import timezone


class Resume(models.Model):
    """简历模型"""
    name = models.CharField(max_length=100, verbose_name='姓名')
    email = models.EmailField(verbose_name='邮箱')
    phone = models.CharField(max_length=20, blank=True, verbose_name='电话')
    education = models.TextField(verbose_name='教育背景')
    experience = models.TextField(verbose_name='工作经验')
    skills = models.TextField(verbose_name='技能特长')
    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True, verbose_name='简历文件')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '简历'
        verbose_name_plural = '简历'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.email}"