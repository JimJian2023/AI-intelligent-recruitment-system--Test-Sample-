from rest_framework import serializers
from .models import Resume


class ResumeSerializer(serializers.ModelSerializer):
    """简历序列化器"""
    
    class Meta:
        model = Resume
        fields = [
            'id', 'name', 'email', 'phone', 'education', 
            'experience', 'skills', 'resume_file', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_email(self, value):
        """验证邮箱格式"""
        if not value:
            raise serializers.ValidationError("邮箱不能为空")
        return value

    def validate_name(self, value):
        """验证姓名"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("姓名至少需要2个字符")
        return value.strip()

    def validate_resume_file(self, value):
        """验证简历文件"""
        if value:
            # 检查文件大小 (10MB)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("文件大小不能超过10MB")
            
            # 检查文件类型
            allowed_types = ['application/pdf', 'application/msword', 
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError("只支持PDF、DOC、DOCX格式的文件")
        
        return value