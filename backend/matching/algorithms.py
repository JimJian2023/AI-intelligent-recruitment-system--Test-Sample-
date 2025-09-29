"""
智能匹配算法模块
实现学生与职位的智能匹配逻辑
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from django.db.models import Q, Prefetch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

from users.models import StudentProfile, StudentSkill, Skill
from jobs.models import Job, JobSkillRequirement, JobSkillPreference
from .models import MatchResult, SkillMatchDetail, MatchingAlgorithmConfig
from .google_ai_service import google_ai_service

logger = logging.getLogger(__name__)


class SkillMatcher:
    """技能匹配器"""
    
    def __init__(self):
        self.proficiency_weights = {
            'beginner': 0.3,
            'intermediate': 0.6,
            'advanced': 0.8,
            'expert': 1.0
        }
        
        self.importance_weights = {
            'critical': 3.0,
            'important': 2.0,
            'nice_to_have': 1.0
        }
    
    def calculate_skill_match(self, student: StudentProfile, job: Job) -> Dict:
        """计算技能匹配度"""
        # 获取学生技能
        student_skills = {
            skill.skill.name: {
                'proficiency': skill.proficiency_level,
                'experience': float(skill.years_of_experience)
            }
            for skill in student.studentskill_set.select_related('skill').all()
        }
        
        # 获取职位必需技能
        required_skills = {
            req.skill.name: {
                'importance': req.importance,
                'min_experience': float(req.min_experience_years),
                'weight': req.weight
            }
            for req in job.jobskillrequirement_set.select_related('skill').all()
        }
        
        # 获取职位偏好技能
        preferred_skills = {
            pref.skill.name: {
                'bonus_points': pref.bonus_points
            }
            for pref in job.jobskillpreference_set.select_related('skill').all()
        }
        
        # 计算匹配分数
        total_score = 0.0
        max_possible_score = 0.0
        skill_details = []
        missing_skills = []
        bonus_skills = []
        
        # 处理必需技能
        for skill_name, req_info in required_skills.items():
            importance_weight = self.importance_weights[req_info['importance']]
            skill_weight = req_info['weight']
            max_possible_score += importance_weight * skill_weight * 100
            
            if skill_name in student_skills:
                student_skill = student_skills[skill_name]
                
                # 计算熟练度分数
                proficiency_score = self.proficiency_weights[student_skill['proficiency']] * 100
                
                # 计算经验分数
                experience_score = min(student_skill['experience'] / max(req_info['min_experience'], 1), 1.0) * 100
                
                # 综合分数
                skill_score = (proficiency_score * 0.6 + experience_score * 0.4) * importance_weight * skill_weight
                total_score += skill_score
                
                skill_details.append({
                    'skill_name': skill_name,
                    'student_has_skill': True,
                    'student_proficiency': student_skill['proficiency'],
                    'student_experience_years': student_skill['experience'],
                    'job_requires_skill': True,
                    'job_skill_importance': req_info['importance'],
                    'job_min_experience': req_info['min_experience'],
                    'job_skill_weight': skill_weight,
                    'match_score': (proficiency_score * 0.6 + experience_score * 0.4),
                    'is_missing_skill': False,
                    'is_bonus_skill': False
                })
            else:
                # 缺失必需技能
                missing_skills.append({
                    'skill_name': skill_name,
                    'importance': req_info['importance'],
                    'min_experience': req_info['min_experience']
                })
                
                skill_details.append({
                    'skill_name': skill_name,
                    'student_has_skill': False,
                    'student_proficiency': '',
                    'student_experience_years': 0.0,
                    'job_requires_skill': True,
                    'job_skill_importance': req_info['importance'],
                    'job_min_experience': req_info['min_experience'],
                    'job_skill_weight': skill_weight,
                    'match_score': 0.0,
                    'is_missing_skill': True,
                    'is_bonus_skill': False
                })
        
        # 处理偏好技能（加分项）
        for skill_name, pref_info in preferred_skills.items():
            if skill_name in student_skills and skill_name not in required_skills:
                student_skill = student_skills[skill_name]
                proficiency_score = self.proficiency_weights[student_skill['proficiency']] * 100
                bonus_score = proficiency_score * pref_info['bonus_points']
                total_score += bonus_score
                
                bonus_skills.append({
                    'skill_name': skill_name,
                    'proficiency': student_skill['proficiency'],
                    'bonus_points': pref_info['bonus_points']
                })
                
                skill_details.append({
                    'skill_name': skill_name,
                    'student_has_skill': True,
                    'student_proficiency': student_skill['proficiency'],
                    'student_experience_years': student_skill['experience'],
                    'job_requires_skill': False,
                    'job_skill_importance': '',
                    'job_min_experience': 0.0,
                    'job_skill_weight': 1.0,
                    'match_score': proficiency_score,
                    'is_missing_skill': False,
                    'is_bonus_skill': True
                })
        
        # 计算最终匹配分数
        if max_possible_score > 0:
            skill_match_score = min((total_score / max_possible_score) * 100, 100.0)
        else:
            skill_match_score = 0.0
        
        return {
            'skill_match_score': skill_match_score,
            'skill_details': skill_details,
            'missing_skills': missing_skills,
            'bonus_skills': bonus_skills,
            'total_required_skills': len(required_skills),
            'matched_required_skills': len(required_skills) - len(missing_skills),
            'bonus_skills_count': len(bonus_skills)
        }


class ExperienceMatcher:
    """经验匹配器"""
    
    def calculate_experience_match(self, student: StudentProfile, job: Job) -> float:
        """计算经验匹配度"""
        # 经验等级映射
        experience_levels = {
            'entry': 0,
            'junior': 1,
            'mid': 3,
            'senior': 5,
            'lead': 8,
            'executive': 10
        }
        
        # 学生总经验年数（基于技能经验的平均值）
        student_skills = student.studentskill_set.all()
        if student_skills:
            avg_experience = sum(float(skill.years_of_experience) for skill in student_skills) / len(student_skills)
        else:
            avg_experience = 0.0
        
        # 职位要求的经验等级
        job_experience_level = experience_levels.get(job.experience_level, 0)
        
        # 计算匹配分数
        if avg_experience >= job_experience_level:
            # 经验充足或超出要求
            if job_experience_level == 0:
                return 100.0
            else:
                # 避免过度惩罚经验丰富的候选人
                excess_ratio = avg_experience / job_experience_level
                if excess_ratio <= 2.0:
                    return 100.0
                else:
                    # 经验过多时轻微降分
                    return max(85.0, 100.0 - (excess_ratio - 2.0) * 5)
        else:
            # 经验不足
            if job_experience_level == 0:
                return 100.0
            else:
                ratio = avg_experience / job_experience_level
                return max(0.0, ratio * 100.0)


class EducationMatcher:
    """教育背景匹配器"""
    
    def __init__(self):
        self.education_levels = {
            'diploma': 1,
            'bachelor': 2,
            'master': 3,
            'phd': 4
        }
    
    def calculate_education_match(self, student: StudentProfile, job: Job) -> float:
        """计算教育背景匹配度"""
        # 基础教育等级匹配
        student_level = self.education_levels.get(student.education_level, 0)
        
        # 由于Job模型中没有直接的教育要求字段，我们基于职位等级推断
        job_level_requirements = {
            'entry': 1,      # 专科及以上
            'junior': 2,     # 本科及以上
            'mid': 2,        # 本科及以上
            'senior': 2,     # 本科及以上
            'lead': 3,       # 硕士优先
            'executive': 3   # 硕士优先
        }
        
        required_level = job_level_requirements.get(job.experience_level, 2)
        
        if student_level >= required_level:
            return 100.0
        else:
            # 教育水平不足时的分数计算
            return max(0.0, (student_level / required_level) * 100.0)


class LocationMatcher:
    """地理位置匹配器"""
    
    def calculate_location_match(self, student: StudentProfile, job: Job) -> float:
        """计算地理位置匹配度"""
        # 检查学生偏好位置
        preferred_locations = student.preferred_locations or []
        job_location = job.location_city
        
        # 远程工作选项
        if job.remote_option in ['remote', 'hybrid']:
            return 100.0
        
        # 精确匹配
        if job_location in preferred_locations:
            return 100.0
        
        # 如果学生没有设置偏好位置，给予中等分数
        if not preferred_locations:
            return 60.0
        
        # 位置不匹配
        return 20.0


class IntelligentMatcher:
    """智能匹配引擎"""
    
    def __init__(self, config: Optional[MatchingAlgorithmConfig] = None):
        self.config = config or self._get_default_config()
        self.skill_matcher = SkillMatcher()
        self.experience_matcher = ExperienceMatcher()
        self.education_matcher = EducationMatcher()
        self.location_matcher = LocationMatcher()
    
    def _get_default_config(self) -> MatchingAlgorithmConfig:
        """获取默认配置"""
        config, created = MatchingAlgorithmConfig.objects.get_or_create(
            name='default',
            defaults={
                'description': '默认匹配算法配置',
                'skill_weight': 0.4,
                'experience_weight': 0.3,
                'education_weight': 0.2,
                'location_weight': 0.1,
                'is_active': True
            }
        )
        return config
    
    def calculate_match(self, student: StudentProfile, job: Job) -> MatchResult:
        """计算学生与职位的匹配度"""
        try:
            # 计算各维度分数
            skill_result = self.skill_matcher.calculate_skill_match(student, job)
            experience_score = self.experience_matcher.calculate_experience_match(student, job)
            education_score = self.education_matcher.calculate_education_match(student, job)
            location_score = self.location_matcher.calculate_location_match(student, job)
            
            # 计算加权总分
            overall_score = (
                skill_result['skill_match_score'] * self.config.skill_weight +
                experience_score * self.config.experience_weight +
                education_score * self.config.education_weight +
                location_score * self.config.location_weight
            )
            
            # 生成推荐理由
            recommendation_reasons = self._generate_recommendation_reasons(
                skill_result, experience_score, education_score, location_score
            )
            
            # 生成改进建议
            improvement_suggestions = self._generate_improvement_suggestions(skill_result)
            
            # 创建或更新匹配结果
            match_result, created = MatchResult.objects.update_or_create(
                student=student,
                job=job,
                defaults={
                    'overall_score': round(overall_score, 2),
                    'skill_match_score': round(skill_result['skill_match_score'], 2),
                    'experience_match_score': round(experience_score, 2),
                    'education_match_score': round(education_score, 2),
                    'location_match_score': round(location_score, 2),
                    'match_details': {
                        'total_required_skills': skill_result['total_required_skills'],
                        'matched_required_skills': skill_result['matched_required_skills'],
                        'bonus_skills_count': skill_result['bonus_skills_count'],
                        'missing_skills': skill_result['missing_skills'],
                        'bonus_skills': skill_result['bonus_skills']
                    },
                    'recommendation_reasons': recommendation_reasons,
                    'improvement_suggestions': improvement_suggestions
                }
            )
            
            # 使用Google AI增强匹配分析（在创建match_result之后）
            ai_analysis = self._get_ai_enhanced_analysis(student, job, overall_score, skill_result, match_result)
            
            # 更新match_result的AI分析结果
            match_result.match_details['ai_analysis'] = ai_analysis
            match_result.save()
            
            # 创建技能匹配详情
            if created or not match_result.skill_details.exists():
                self._create_skill_details(match_result, skill_result['skill_details'])
            
            logger.info(f"匹配计算完成: {student.user.username} -> {job.title} = {overall_score:.2f}%")
            return match_result
            
        except Exception as e:
            logger.error(f"匹配计算失败: {student.user.username} -> {job.title}, 错误: {str(e)}")
            raise
    
    def _create_skill_details(self, match_result: MatchResult, skill_details: List[Dict]):
        """创建技能匹配详情记录"""
        # 删除旧的详情记录
        match_result.skill_details.all().delete()
        
        # 创建新的详情记录
        skill_detail_objects = []
        for detail in skill_details:
            skill_detail_objects.append(
                SkillMatchDetail(
                    match_result=match_result,
                    **detail
                )
            )
        
        SkillMatchDetail.objects.bulk_create(skill_detail_objects)
    
    def _generate_recommendation_reasons(self, skill_result: Dict, experience_score: float, 
                                       education_score: float, location_score: float) -> List[str]:
        """生成推荐理由"""
        reasons = []
        
        # 技能匹配理由
        if skill_result['skill_match_score'] >= 80:
            reasons.append(f"技能匹配度高达 {skill_result['skill_match_score']:.1f}%")
        
        matched_ratio = skill_result['matched_required_skills'] / max(skill_result['total_required_skills'], 1)
        if matched_ratio >= 0.8:
            reasons.append(f"满足 {skill_result['matched_required_skills']}/{skill_result['total_required_skills']} 项必需技能")
        
        if skill_result['bonus_skills_count'] > 0:
            reasons.append(f"拥有 {skill_result['bonus_skills_count']} 项加分技能")
        
        # 经验匹配理由
        if experience_score >= 90:
            reasons.append("工作经验完全符合要求")
        elif experience_score >= 70:
            reasons.append("工作经验基本符合要求")
        
        # 教育背景理由
        if education_score >= 90:
            reasons.append("教育背景完全匹配")
        
        # 地理位置理由
        if location_score >= 90:
            reasons.append("地理位置匹配度高")
        
        return reasons
    
    def _generate_improvement_suggestions(self, skill_result: Dict) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 基于缺失技能的建议
        missing_skills = skill_result['missing_skills']
        if missing_skills:
            critical_missing = [s for s in missing_skills if s['importance'] == 'critical']
            important_missing = [s for s in missing_skills if s['importance'] == 'important']
            
            if critical_missing:
                skills_list = ', '.join([s['skill_name'] for s in critical_missing[:3]])
                suggestions.append(f"建议重点学习关键技能: {skills_list}")
            
            if important_missing:
                skills_list = ', '.join([s['skill_name'] for s in important_missing[:3]])
                suggestions.append(f"建议补充重要技能: {skills_list}")
        
        # 基于匹配分数的建议
        if skill_result['skill_match_score'] < 60:
            suggestions.append("建议提升相关技能熟练度，增加项目经验")
        
        return suggestions
    
    def batch_match(self, students: List[StudentProfile], jobs: List[Job], 
                   min_score: float = 60.0) -> List[MatchResult]:
        """批量匹配"""
        results = []
        total_combinations = len(students) * len(jobs)
        processed = 0
        
        logger.info(f"开始批量匹配: {len(students)} 名学生 × {len(jobs)} 个职位")
        
        for student in students:
            for job in jobs:
                try:
                    match_result = self.calculate_match(student, job)
                    if match_result.overall_score >= min_score:
                        results.append(match_result)
                    
                    processed += 1
                    if processed % 100 == 0:
                        logger.info(f"批量匹配进度: {processed}/{total_combinations}")
                        
                except Exception as e:
                    logger.error(f"批量匹配失败: {student.user.username} -> {job.title}, 错误: {str(e)}")
                    continue
        
        logger.info(f"批量匹配完成: 生成 {len(results)} 个有效匹配结果")
        return results
    
    def _get_ai_enhanced_analysis(self, student: StudentProfile, job: Job, overall_score: float, skill_result: dict, match_result: MatchResult = None) -> dict:
        """使用Google AI增强匹配分析"""
        try:
            from .google_ai_service import GoogleAIService
            ai_service = GoogleAIService()
            
            # 如果没有传入match_result，创建一个临时的用于AI分析
            if match_result is None:
                match_result = MatchResult(
                    student=student,
                    job=job,
                    overall_score=overall_score
                )
            
            # 获取AI分析
            ai_analysis = ai_service.analyze_match_compatibility(student, job, match_result)
            
            return {
                'compatibility_analysis': ai_analysis.get('compatibility_analysis', ''),
                'strengths': ai_analysis.get('strengths', []),
                'concerns': ai_analysis.get('concerns', []),
                'skill_recommendations': ai_analysis.get('skill_recommendations', []),
                'career_advice': ai_analysis.get('career_advice', ''),
                'confidence_score': ai_analysis.get('confidence_score', 0.8)
            }
        except Exception as e:
            logger.warning(f"AI分析失败: {str(e)}")
            return {
                'compatibility_analysis': '暂时无法获取AI分析',
                'strengths': [],
                'concerns': [],
                'skill_recommendations': [],
                'career_advice': '',
                'confidence_score': 0.0
            }
    
    def get_top_matches_for_student(self, student: StudentProfile, limit: int = 10) -> List[MatchResult]:
        """获取学生的最佳职位匹配"""
        return MatchResult.objects.filter(
            student=student,
            is_active=True
        ).select_related('job', 'job__employer').order_by('-overall_score')[:limit]
    
    def get_top_matches_for_job(self, job: Job, limit: int = 10) -> List[MatchResult]:
        """获取职位的最佳学生匹配"""
        return MatchResult.objects.filter(
            job=job,
            is_active=True
        ).select_related('student', 'student__user').order_by('-overall_score')[:limit]