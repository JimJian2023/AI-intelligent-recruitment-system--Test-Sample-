"""
匹配模块序列化器
"""

from rest_framework import serializers
from .models import (
    MatchResult, SkillMatchDetail, MatchingAlgorithmConfig,
    MatchingJob, StudentRecommendation, RecommendationItem
)
from users.models import StudentProfile
from jobs.models import Job
from users.serializers import UserProfileSerializer
from jobs.serializers import JobListSerializer


class SkillMatchDetailSerializer(serializers.ModelSerializer):
    """技能匹配详情序列化器"""
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    
    class Meta:
        model = SkillMatchDetail
        fields = [
            'id', 'skill', 'skill_name', 'required_level', 'student_level',
            'match_score', 'weight', 'is_critical'
        ]


class MatchResultSerializer(serializers.ModelSerializer):
    """匹配结果序列化器"""
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.employer.company_name', read_only=True)
    skill_matches = SkillMatchDetailSerializer(many=True, read_only=True)
    
    class Meta:
        model = MatchResult
        fields = [
            'id', 'student', 'student_name', 'job', 'job_title', 'company_name',
            'overall_score', 'skill_score', 'experience_score', 'education_score',
            'location_score', 'skill_matches', 'match_details', 'recommendation_reasons',
            'improvement_suggestions', 'created_at', 'updated_at'
        ]


class MatchResultDetailSerializer(MatchResultSerializer):
    """匹配结果详情序列化器"""
    student = UserProfileSerializer(read_only=True)
    job = JobListSerializer(read_only=True)
    
    class Meta(MatchResultSerializer.Meta):
        fields = MatchResultSerializer.Meta.fields + ['student', 'job']


class MatchingAlgorithmConfigSerializer(serializers.ModelSerializer):
    """匹配算法配置序列化器"""
    
    class Meta:
        model = MatchingAlgorithmConfig
        fields = [
            'id', 'name', 'skill_weight', 'experience_weight', 'education_weight',
            'location_weight', 'min_match_threshold', 'algorithm_parameters',
            'is_active', 'created_at', 'updated_at'
        ]
    
    def validate(self, data):
        """验证权重总和"""
        weights = [
            data.get('skill_weight', 0),
            data.get('experience_weight', 0),
            data.get('education_weight', 0),
            data.get('location_weight', 0)
        ]
        
        total_weight = sum(weights)
        if abs(total_weight - 1.0) > 0.01:  # 允许小的浮点误差
            raise serializers.ValidationError("所有权重的总和必须等于1.0")
        
        return data


class MatchingJobSerializer(serializers.ModelSerializer):
    """匹配任务序列化器"""
    job_title = serializers.CharField(source='job.title', read_only=True)
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    
    class Meta:
        model = MatchingJob
        fields = [
            'id', 'job', 'job_title', 'student', 'student_name', 'status',
            'priority', 'scheduled_at', 'started_at', 'completed_at',
            'error_message', 'result_count', 'created_at'
        ]


class RecommendationItemSerializer(serializers.ModelSerializer):
    """推荐项目序列化器"""
    
    class Meta:
        model = RecommendationItem
        fields = [
            'id', 'item_type', 'item_id', 'title', 'description',
            'score', 'reasons', 'priority'
        ]


class StudentRecommendationSerializer(serializers.ModelSerializer):
    """学生推荐序列化器"""
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    items = RecommendationItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = StudentRecommendation
        fields = [
            'id', 'student', 'student_name', 'recommendation_type',
            'items', 'career_advice', 'skill_suggestions', 'learning_path',
            'is_active', 'expires_at', 'created_at', 'updated_at'
        ]


class StudentRecommendationCreateSerializer(serializers.ModelSerializer):
    """学生推荐创建序列化器"""
    items = RecommendationItemSerializer(many=True, required=False)
    
    class Meta:
        model = StudentRecommendation
        fields = [
            'student', 'recommendation_type', 'career_advice',
            'skill_suggestions', 'learning_path', 'expires_at', 'items'
        ]
    
    def create(self, validated_data):
        """创建推荐"""
        items_data = validated_data.pop('items', [])
        recommendation = StudentRecommendation.objects.create(**validated_data)
        
        # 创建推荐项目
        for item_data in items_data:
            RecommendationItem.objects.create(
                recommendation=recommendation,
                **item_data
            )
        
        return recommendation


class MatchRequestSerializer(serializers.Serializer):
    """匹配请求序列化器"""
    student_id = serializers.IntegerField(required=False)
    job_id = serializers.IntegerField(required=False)
    limit = serializers.IntegerField(default=10, min_value=1, max_value=100)
    min_score = serializers.FloatField(default=0.0, min_value=0.0, max_value=1.0)
    algorithm_config_id = serializers.IntegerField(required=False)
    
    def validate(self, data):
        """验证请求参数"""
        if not data.get('student_id') and not data.get('job_id'):
            raise serializers.ValidationError("必须提供student_id或job_id中的一个")
        
        if data.get('student_id') and data.get('job_id'):
            raise serializers.ValidationError("不能同时提供student_id和job_id")
        
        return data


class BatchMatchRequestSerializer(serializers.Serializer):
    """批量匹配请求序列化器"""
    student_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=False
    )
    job_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=False
    )
    limit_per_item = serializers.IntegerField(default=5, min_value=1, max_value=50)
    min_score = serializers.FloatField(default=0.0, min_value=0.0, max_value=1.0)
    algorithm_config_id = serializers.IntegerField(required=False)
    priority = serializers.ChoiceField(
        choices=['low', 'normal', 'high'],
        default='normal'
    )
    
    def validate(self, data):
        """验证请求参数"""
        if not data.get('student_ids') and not data.get('job_ids'):
            raise serializers.ValidationError("必须提供student_ids或job_ids中的一个")
        
        if data.get('student_ids') and data.get('job_ids'):
            raise serializers.ValidationError("不能同时提供student_ids和job_ids")
        
        # 限制批量数量
        ids = data.get('student_ids') or data.get('job_ids')
        if len(ids) > 100:
            raise serializers.ValidationError("批量匹配数量不能超过100个")
        
        return data


class MatchStatisticsSerializer(serializers.Serializer):
    """匹配统计序列化器"""
    total_matches = serializers.IntegerField()
    high_quality_matches = serializers.IntegerField()
    medium_quality_matches = serializers.IntegerField()
    low_quality_matches = serializers.IntegerField()
    average_score = serializers.FloatField()
    matches_this_week = serializers.IntegerField()
    matches_this_month = serializers.IntegerField()
    top_skills = serializers.ListField(child=serializers.DictField())
    match_trends = serializers.ListField(child=serializers.DictField())


class RecommendationStatisticsSerializer(serializers.Serializer):
    """推荐统计序列化器"""
    total_recommendations = serializers.IntegerField()
    active_recommendations = serializers.IntegerField()
    job_recommendations = serializers.IntegerField()
    skill_recommendations = serializers.IntegerField()
    career_recommendations = serializers.IntegerField()
    success_rate = serializers.FloatField()
    recommendations_this_month = serializers.IntegerField()