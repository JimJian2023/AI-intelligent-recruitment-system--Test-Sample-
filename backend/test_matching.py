#!/usr/bin/env python
"""
测试Google AI增强的匹配算法功能
"""
import os
import sys
import django
from django.contrib.auth import get_user_model

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import StudentProfile
from jobs.models import Job
from matching.algorithms import IntelligentMatcher

User = get_user_model()

def test_ai_matching():
    """测试AI增强的匹配功能"""
    print("开始测试Google AI增强的匹配算法...")
    
    # 获取第一个学生
    try:
        student = StudentProfile.objects.first()
        if not student:
            print("错误: 没有找到学生数据，请先运行create_demo_data.py")
            return
        
        print(f"测试学生: {student.user.username} ({student.user.get_full_name()})")
        print(f"学生专业: {student.major}")
        print(f"学生技能数量: {student.skill_count}")
        
        # 获取第一个职位
        job = Job.objects.first()
        if not job:
            print("错误: 没有找到职位数据，请先运行create_demo_data.py")
            return
            
        print(f"\n测试职位: {job.title}")
        print(f"职位公司: {job.employer.company_name}")
        print(f"职位要求: {job.requirements[:100]}...")
        
        # 创建匹配器并计算匹配度
        matcher = IntelligentMatcher()
        print("\n开始计算匹配度...")
        
        match_result = matcher.calculate_match(student, job)
        
        print(f"\n匹配结果:")
        print(f"总体匹配度: {match_result.overall_score:.2f}%")
        print(f"技能匹配度: {match_result.skill_match_score:.2f}%")
        print(f"经验匹配度: {match_result.experience_match_score:.2f}%")
        print(f"教育匹配度: {match_result.education_match_score:.2f}%")
        print(f"地理位置匹配度: {match_result.location_match_score:.2f}%")
        print(f"匹配等级: {match_result.match_level_display}")
        
        # 显示匹配详情
        if match_result.match_details:
            details = match_result.match_details
            print(f"\n匹配详情:")
            print(f"必需技能总数: {details.get('total_required_skills', 0)}")
            print(f"匹配的必需技能: {details.get('matched_required_skills', 0)}")
            print(f"加分技能数量: {details.get('bonus_skills_count', 0)}")
            
            # 显示缺失技能
            missing_skills = details.get('missing_skills', [])
            if missing_skills:
                # 处理缺失技能可能是字典列表的情况
                if isinstance(missing_skills[0], dict):
                    skill_names = [skill.get('skill_name', str(skill)) for skill in missing_skills]
                    print(f"缺失技能：{', '.join(skill_names[:5])}")  # 只显示前5个
                else:
                    print(f"缺失技能：{', '.join(missing_skills[:5])}")  # 只显示前5个
            
            # 显示加分技能
            bonus_skills = details.get('bonus_skills', [])
            if bonus_skills:
                # 处理加分技能可能是字典列表的情况
                if isinstance(bonus_skills[0], dict):
                    skill_names = [skill.get('skill_name', str(skill)) for skill in bonus_skills]
                    print(f"加分技能：{', '.join(skill_names[:5])}")  # 只显示前5个
                else:
                    print(f"加分技能：{', '.join(bonus_skills[:5])}")  # 只显示前5个
        
        # 显示推荐理由
        if match_result.recommendation_reasons:
            print(f"\n推荐理由:")
            for reason in match_result.recommendation_reasons[:3]:  # 只显示前3个
                print(f"- {reason}")
        
        # 显示改进建议
        if match_result.improvement_suggestions:
            print(f"\n改进建议:")
            for suggestion in match_result.improvement_suggestions[:3]:  # 只显示前3个
                print(f"- {suggestion}")
        
        # 检查是否有AI增强分析
        if match_result.match_details and 'ai_analysis' in match_result.match_details:
            ai_analysis = match_result.match_details['ai_analysis']
            print(f"\nGoogle AI分析结果:")
            if isinstance(ai_analysis, dict):
                print(f"兼容性分析: {ai_analysis.get('compatibility_analysis', 'N/A')}")
                print(f"优势: {', '.join(ai_analysis.get('strengths', []))}")
                print(f"顾虑: {', '.join(ai_analysis.get('concerns', []))}")
                print(f"技能推荐: {', '.join(ai_analysis.get('skill_recommendations', []))}")
                print(f"职业建议: {ai_analysis.get('career_advice', 'N/A')}")
                print(f"置信度: {ai_analysis.get('confidence_score', 'N/A')}")
                if ai_analysis.get('success'):
                    print("AI分析状态: 成功")
                else:
                    print("AI分析状态: 失败")
            else:
                print(ai_analysis)
        else:
            print("\n注意: 没有找到Google AI分析结果，可能是API配置问题")
        
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_ai_matching()