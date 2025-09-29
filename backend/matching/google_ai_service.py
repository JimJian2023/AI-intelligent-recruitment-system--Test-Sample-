"""
Google AI Service for intelligent matching and analysis
"""
import os
import logging
from typing import Dict, List, Optional, Any
from django.conf import settings
import google.generativeai as genai
from decouple import config

logger = logging.getLogger(__name__)


class GoogleAIService:
    """Google AI service for job-student matching and analysis"""
    
    def __init__(self):
        """Initialize Google AI service"""
        self.api_key = config('GOOGLE_AI_API_KEY', default=None)
        self.model_name = config('GOOGLE_AI_MODEL', default='gemini-2.5-flash')
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                logger.info("Google AI service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Google AI service: {e}")
                self.enabled = False
                self.model = None
        else:
            logger.warning("Google AI service disabled - no API key provided")
            self.model = None

    @property
    def is_enabled(self) -> bool:
        """Check if the service is enabled and ready"""
        return self.enabled and self.model is not None

    def parse_job_description(self, text_content: str) -> str:
        """
        使用AI解析工作描述文档
        
        Args:
            text_content: 文档文本内容
            
        Returns:
            AI解析结果字符串
        """
        if not self.enabled:
            return "AI service not available"
        
        try:
            # 构建AI提示词
            prompt = self._build_job_parsing_prompt(text_content)
            
            # 调用AI API
            response = self.model.generate_content(prompt)
            ai_response_text = response.text
            
            logger.info("Successfully parsed job description with AI")
            return ai_response_text
            
        except Exception as e:
            logger.error(f"AI job description parsing failed: {e}")
            return f"AI解析失败: {str(e)}"

    def _build_job_parsing_prompt(self, job_text: str) -> str:
        """构建工作描述解析提示词"""
        return f"""
You are an expert job description parser. Please carefully analyze the following job posting content and extract comprehensive information. Pay special attention to all sections and details.

Job Posting Content:
{job_text}

Please extract the following information systematically. For each field, provide the most complete and accurate information found in the job posting. If information is not available, mark as "Not Provided":

Job Title: [Extract the job title/position name]
Job Description: [Extract detailed job description, responsibilities, and duties - be comprehensive]
Requirements: [Extract all requirements including education, experience, skills, qualifications - be detailed]
Job Type: [Extract employment type - full-time, part-time, contract, internship, freelance]
Experience Level: [Extract required experience level - entry, junior, mid, senior, executive]
Location: [Extract job location/city]
Remote: [Extract work arrangement - remote, hybrid, on-site]
Salary Min: [Extract minimum salary if mentioned]
Salary Max: [Extract maximum salary if mentioned]
Benefits: [Extract benefits, perks, and compensation details]
Application Deadline: [Extract application deadline or closing date if mentioned]

IMPORTANT INSTRUCTIONS:
1. Be thorough - don't miss any information
2. For multi-line sections like Job Description, Requirements, and Benefits, include all relevant details
3. Extract exact text where possible, don't paraphrase unless necessary
4. If salary is mentioned as a range, extract both minimum and maximum values
5. For job type, use one of: full-time, part-time, contract, internship, freelance
6. For experience level, use one of: entry, junior, mid, senior, executive
7. For remote work, use one of: remote, hybrid, on-site
8. Maintain the exact format shown above with colons after each field name
9. If a section has multiple points, include them all
10. Pay special attention to technical skills, qualifications, and specific requirements

Format your response exactly as shown above, with each field on a separate line.
"""


# 全局服务实例
google_ai_service = GoogleAIService()