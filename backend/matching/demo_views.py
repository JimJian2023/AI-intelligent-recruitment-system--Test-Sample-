"""
演示模式的匹配分析视图
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from resumes.models import Resume
from jobs.models import Job
import random
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def analyze_match(request):
    """
    演示模式的匹配分析API
    接收简历ID和职位ID，返回模拟的匹配分析结果
    """
    try:
        resume_id = request.data.get('resume_id')
        job_id = request.data.get('job_id')
        
        if not resume_id or not job_id:
            return Response({
                'error': 'Please provide resume ID and job ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取简历和职位信息
        try:
            resume = get_object_or_404(Resume, id=resume_id)
            job = get_object_or_404(Job, id=job_id)
        except:
            return Response({
                'error': 'Resume or job position not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 生成模拟的匹配分析结果
        overall_score = random.randint(60, 95)
        
        # 根据分数生成不同的分析内容
        if overall_score >= 85:
            detailed_analysis = f"Candidate {resume.name} is highly compatible with the {job.title} position. The candidate's skill background aligns very well with the job requirements, and their educational background and work experience meet the position needs."
            strengths = [
                "Extremely high skill match, core skills fully meet position requirements",
                "Educational background highly matches position requirements",
                "Rich work experience with relevant industry background",
                "Excellent overall quality with great development potential"
            ]
            weaknesses = [
                "Could further improve some auxiliary skills",
                "Recommend adding more relevant project experience"
            ]
            recommendations = [
                "Strongly recommend proceeding to interview stage",
                "Consider offering competitive salary package",
                "Recommend arranging technical interview to verify core skills"
            ]
        elif overall_score >= 70:
            detailed_analysis = f"Candidate {resume.name} is moderately compatible with the {job.title} position. The candidate has basic skill requirements but has room for improvement in some areas."
            strengths = [
                "Solid basic skills, meets basic position requirements",
                "Strong learning ability and good adaptability",
                "Positive work attitude with some experience accumulation"
            ]
            weaknesses = [
                "Some core skills need further strengthening",
                "Relatively limited relevant project experience",
                "Certain professional skills need improvement"
            ]
            recommendations = [
                "Recommend conducting skill assessment interview",
                "Consider providing training opportunities",
                "Suitable as backup candidate"
            ]
        else:
            detailed_analysis = f"Candidate {resume.name} has average compatibility with the {job.title} position. The candidate has some foundation but there is still a significant gap with the position requirements."
            strengths = [
                "Has basic professional qualities",
                "Shows willingness to learn and development potential",
                "Positive attitude and proactive work approach"
            ]
            weaknesses = [
                "Significant gap between core skills and position requirements",
                "Insufficient relevant work experience",
                "Professional skills need substantial improvement",
                "Educational background doesn't match position requirements well"
            ]
            recommendations = [
                "Recommend candidate to improve relevant skills first",
                "Consider entry-level or training positions",
                "Requires longer development period"
            ]
        
        # 构造返回结果
        result = {
            'overall_score': overall_score,
            'detailed_analysis': detailed_analysis,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'recommendations': recommendations,
            'resume_info': {
                'name': resume.name,
                'email': resume.email,
                'skills': resume.skills[:100] + '...' if len(resume.skills) > 100 else resume.skills
            },
            'job_info': {
                'title': job.title,
                'location': job.location_city,
                'type': job.job_type,
                'experience_level': job.experience_level
            }
        }
        
        logger.info(f"Generated demo match analysis: Resume {resume_id} vs Job {job_id}, Score: {overall_score}")
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in analyze_match: {str(e)}")
        return Response({
            'error': 'An error occurred during analysis, please try again later'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)