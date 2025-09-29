"""
匹配服务模块
提供高级匹配功能和业务逻辑
"""

from typing import List, Dict, Optional, Tuple
from django.db.models import Q, Count, Avg, Prefetch
from django.utils import timezone
from django.core.cache import cache
from celery import shared_task
import logging

from users.models import StudentProfile, User
from jobs.models import Job
from applications.models import Application
from .models import MatchResult, MatchingJob, StudentRecommendation, RecommendationItem
from .algorithms import IntelligentMatcher

logger = logging.getLogger(__name__)


class MatchingService:
    """匹配服务类"""
    
    def __init__(self):
        self.matcher = IntelligentMatcher()
    
    def find_matches_for_student(self, student_id: int, limit: int = 20, 
                                min_score: float = 60.0) -> List[MatchResult]:
        """为学生查找匹配的职位"""
        try:
            student = StudentProfile.objects.select_related('user').get(id=student_id)
            
            # 获取活跃的职位，排除已申请的
            applied_jobs = Application.objects.filter(
                student=student
            ).values_list('job_id', flat=True)
            
            active_jobs = Job.objects.filter(
                is_active=True,
                application_deadline__gte=timezone.now().date()
            ).exclude(
                id__in=applied_jobs
            ).select_related('employer').prefetch_related(
                'jobskillrequirement_set__skill',
                'jobskillpreference_set__skill'
            )
            
            # 检查缓存
            cache_key = f"student_matches_{student_id}_{min_score}_{limit}"
            cached_results = cache.get(cache_key)
            if cached_results:
                logger.info(f"从缓存获取学生匹配结果: {student.user.username}")
                return cached_results
            
            # 计算匹配
            matches = []
            for job in active_jobs:
                match_result = self.matcher.calculate_match(student, job)
                if match_result.overall_score >= min_score:
                    matches.append(match_result)
            
            # 按分数排序
            matches.sort(key=lambda x: x.overall_score, reverse=True)
            top_matches = matches[:limit]
            
            # 缓存结果（1小时）
            cache.set(cache_key, top_matches, 3600)
            
            logger.info(f"为学生 {student.user.username} 找到 {len(top_matches)} 个匹配职位")
            return top_matches
            
        except StudentProfile.DoesNotExist:
            logger.error(f"学生档案不存在: {student_id}")
            return []
        except Exception as e:
            logger.error(f"查找学生匹配失败: {student_id}, 错误: {str(e)}")
            return []
    
    def find_matches_for_job(self, job_id: int, limit: int = 20, 
                            min_score: float = 60.0) -> List[MatchResult]:
        """为职位查找匹配的学生"""
        try:
            job = Job.objects.select_related('employer').prefetch_related(
                'jobskillrequirement_set__skill',
                'jobskillpreference_set__skill'
            ).get(id=job_id)
            
            # 获取活跃的学生档案，排除已申请的
            applied_students = Application.objects.filter(
                job=job
            ).values_list('student_id', flat=True)
            
            active_students = StudentProfile.objects.filter(
                user__is_active=True,
                is_seeking_job=True
            ).exclude(
                id__in=applied_students
            ).select_related('user').prefetch_related(
                'studentskill_set__skill'
            )
            
            # 检查缓存
            cache_key = f"job_matches_{job_id}_{min_score}_{limit}"
            cached_results = cache.get(cache_key)
            if cached_results:
                logger.info(f"从缓存获取职位匹配结果: {job.title}")
                return cached_results
            
            # 计算匹配
            matches = []
            for student in active_students:
                match_result = self.matcher.calculate_match(student, job)
                if match_result.overall_score >= min_score:
                    matches.append(match_result)
            
            # 按分数排序
            matches.sort(key=lambda x: x.overall_score, reverse=True)
            top_matches = matches[:limit]
            
            # 缓存结果（1小时）
            cache.set(cache_key, top_matches, 3600)
            
            logger.info(f"为职位 {job.title} 找到 {len(top_matches)} 个匹配学生")
            return top_matches
            
        except Job.DoesNotExist:
            logger.error(f"职位不存在: {job_id}")
            return []
        except Exception as e:
            logger.error(f"查找职位匹配失败: {job_id}, 错误: {str(e)}")
            return []
    
    def generate_student_recommendations(self, student_id: int) -> Optional[StudentRecommendation]:
        """生成学生个性化推荐"""
        try:
            student = StudentProfile.objects.select_related('user').get(id=student_id)
            
            # 获取匹配结果
            matches = self.find_matches_for_student(student_id, limit=10, min_score=70.0)
            
            if not matches:
                logger.info(f"学生 {student.user.username} 暂无高质量匹配")
                return None
            
            # 分析匹配结果，生成推荐
            job_recommendations = []
            skill_recommendations = []
            career_advice = []
            
            # 职位推荐
            for match in matches[:5]:
                job_recommendations.append({
                    'job_id': match.job.id,
                    'job_title': match.job.title,
                    'company_name': match.job.employer.company_name,
                    'match_score': match.overall_score,
                    'recommendation_reason': ', '.join(match.recommendation_reasons[:2])
                })
            
            # 技能推荐（基于缺失的关键技能）
            skill_gaps = {}
            for match in matches:
                for missing_skill in match.match_details.get('missing_skills', []):
                    skill_name = missing_skill['skill_name']
                    importance = missing_skill['importance']
                    
                    if skill_name not in skill_gaps:
                        skill_gaps[skill_name] = {'count': 0, 'importance': importance}
                    skill_gaps[skill_name]['count'] += 1
            
            # 按出现频率和重要性排序
            sorted_skills = sorted(
                skill_gaps.items(),
                key=lambda x: (x[1]['count'], {'critical': 3, 'important': 2, 'nice_to_have': 1}[x[1]['importance']]),
                reverse=True
            )
            
            for skill_name, info in sorted_skills[:5]:
                skill_recommendations.append({
                    'skill_name': skill_name,
                    'importance': info['importance'],
                    'demand_count': info['count'],
                    'learning_priority': 'high' if info['importance'] == 'critical' else 'medium'
                })
            
            # 职业建议
            avg_score = sum(match.overall_score for match in matches) / len(matches)
            
            if avg_score >= 85:
                career_advice.append("您的技能匹配度很高，建议积极申请心仪职位")
            elif avg_score >= 70:
                career_advice.append("您具备良好的基础，建议针对性提升关键技能")
            else:
                career_advice.append("建议重点学习市场需求技能，提升竞争力")
            
            if skill_recommendations:
                top_skill = skill_recommendations[0]['skill_name']
                career_advice.append(f"建议优先学习 {top_skill}，这是当前市场的热门技能")
            
            # 创建或更新推荐记录
            recommendation, created = StudentRecommendation.objects.update_or_create(
                student=student,
                defaults={
                    'recommendation_type': 'comprehensive',
                    'confidence_score': min(avg_score, 95.0),
                    'generated_at': timezone.now()
                }
            )
            
            # 清除旧的推荐项目
            recommendation.items.all().delete()
            
            # 创建新的推荐项目
            recommendation_items = []
            
            # 添加职位推荐
            for job_rec in job_recommendations:
                recommendation_items.append(
                    RecommendationItem(
                        recommendation=recommendation,
                        item_type='job',
                        item_id=job_rec['job_id'],
                        title=job_rec['job_title'],
                        description=job_rec['recommendation_reason'],
                        score=job_rec['match_score'],
                        metadata=job_rec
                    )
                )
            
            # 添加技能推荐
            for skill_rec in skill_recommendations:
                recommendation_items.append(
                    RecommendationItem(
                        recommendation=recommendation,
                        item_type='skill',
                        title=f"学习 {skill_rec['skill_name']}",
                        description=f"重要性: {skill_rec['importance']}, 需求度: {skill_rec['demand_count']} 个职位",
                        score=skill_rec['demand_count'] * 10,
                        metadata=skill_rec
                    )
                )
            
            # 添加职业建议
            for i, advice in enumerate(career_advice):
                recommendation_items.append(
                    RecommendationItem(
                        recommendation=recommendation,
                        item_type='advice',
                        title=f"职业建议 {i+1}",
                        description=advice,
                        score=90 - i * 5,
                        metadata={'advice': advice}
                    )
                )
            
            RecommendationItem.objects.bulk_create(recommendation_items)
            
            logger.info(f"为学生 {student.user.username} 生成个性化推荐")
            return recommendation
            
        except StudentProfile.DoesNotExist:
            logger.error(f"学生档案不存在: {student_id}")
            return None
        except Exception as e:
            logger.error(f"生成学生推荐失败: {student_id}, 错误: {str(e)}")
            return None
    
    def get_matching_statistics(self, student_id: Optional[int] = None, 
                              job_id: Optional[int] = None) -> Dict:
        """获取匹配统计信息"""
        try:
            stats = {}
            
            if student_id:
                # 学生匹配统计
                student_matches = MatchResult.objects.filter(
                    student_id=student_id,
                    is_active=True
                )
                
                stats['student_stats'] = {
                    'total_matches': student_matches.count(),
                    'high_quality_matches': student_matches.filter(overall_score__gte=80).count(),
                    'medium_quality_matches': student_matches.filter(
                        overall_score__gte=60, overall_score__lt=80
                    ).count(),
                    'average_score': student_matches.aggregate(Avg('overall_score'))['overall_score__avg'] or 0,
                    'top_score': student_matches.aggregate(models.Max('overall_score'))['overall_score__max'] or 0
                }
            
            if job_id:
                # 职位匹配统计
                job_matches = MatchResult.objects.filter(
                    job_id=job_id,
                    is_active=True
                )
                
                stats['job_stats'] = {
                    'total_matches': job_matches.count(),
                    'high_quality_matches': job_matches.filter(overall_score__gte=80).count(),
                    'medium_quality_matches': job_matches.filter(
                        overall_score__gte=60, overall_score__lt=80
                    ).count(),
                    'average_score': job_matches.aggregate(Avg('overall_score'))['overall_score__avg'] or 0,
                    'top_score': job_matches.aggregate(models.Max('overall_score'))['overall_score__max'] or 0
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取匹配统计失败, 错误: {str(e)}")
            return {}
    
    def refresh_matches(self, student_id: Optional[int] = None, job_id: Optional[int] = None):
        """刷新匹配结果（清除缓存）"""
        try:
            if student_id:
                # 清除学生相关缓存
                cache_pattern = f"student_matches_{student_id}_*"
                # 注意：这里需要根据实际缓存后端实现清除模式匹配的缓存
                logger.info(f"清除学生 {student_id} 的匹配缓存")
            
            if job_id:
                # 清除职位相关缓存
                cache_pattern = f"job_matches_{job_id}_*"
                logger.info(f"清除职位 {job_id} 的匹配缓存")
            
            if not student_id and not job_id:
                # 清除所有匹配缓存
                cache.clear()
                logger.info("清除所有匹配缓存")
                
        except Exception as e:
            logger.error(f"刷新匹配缓存失败, 错误: {str(e)}")


# Celery异步任务
@shared_task
def batch_calculate_matches(student_ids: List[int] = None, job_ids: List[int] = None, 
                           min_score: float = 60.0):
    """批量计算匹配结果的异步任务"""
    try:
        matcher = IntelligentMatcher()
        
        # 获取学生和职位
        if student_ids:
            students = StudentProfile.objects.filter(id__in=student_ids).select_related('user')
        else:
            students = StudentProfile.objects.filter(
                user__is_active=True,
                is_seeking_job=True
            ).select_related('user')
        
        if job_ids:
            jobs = Job.objects.filter(id__in=job_ids).select_related('employer')
        else:
            jobs = Job.objects.filter(
                is_active=True,
                application_deadline__gte=timezone.now().date()
            ).select_related('employer')
        
        # 批量匹配
        results = matcher.batch_match(list(students), list(jobs), min_score)
        
        # 创建匹配任务记录
        matching_job = MatchingJob.objects.create(
            job_name=f"批量匹配_{timezone.now().strftime('%Y%m%d_%H%M%S')}",
            status='completed',
            total_students=len(students),
            total_jobs=len(jobs),
            total_matches=len(results),
            completed_at=timezone.now()
        )
        
        logger.info(f"批量匹配任务完成: {matching_job.job_name}, 生成 {len(results)} 个匹配结果")
        return {
            'job_id': matching_job.id,
            'total_matches': len(results),
            'students_count': len(students),
            'jobs_count': len(jobs)
        }
        
    except Exception as e:
        logger.error(f"批量匹配任务失败: {str(e)}")
        # 创建失败记录
        MatchingJob.objects.create(
            job_name=f"批量匹配_失败_{timezone.now().strftime('%Y%m%d_%H%M%S')}",
            status='failed',
            error_message=str(e)
        )
        raise


@shared_task
def generate_daily_recommendations():
    """生成每日推荐的异步任务"""
    try:
        service = MatchingService()
        
        # 获取活跃的求职学生
        active_students = StudentProfile.objects.filter(
            user__is_active=True,
            is_seeking_job=True
        ).values_list('id', flat=True)
        
        success_count = 0
        for student_id in active_students:
            try:
                recommendation = service.generate_student_recommendations(student_id)
                if recommendation:
                    success_count += 1
            except Exception as e:
                logger.error(f"为学生 {student_id} 生成推荐失败: {str(e)}")
                continue
        
        logger.info(f"每日推荐任务完成: 为 {success_count}/{len(active_students)} 名学生生成推荐")
        return {
            'total_students': len(active_students),
            'success_count': success_count
        }
        
    except Exception as e:
        logger.error(f"每日推荐任务失败: {str(e)}")
        raise