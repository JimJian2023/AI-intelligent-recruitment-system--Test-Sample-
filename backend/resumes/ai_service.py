"""
简历AI解析服务模块
使用Google Generative AI API解析简历文档
"""

import os
import logging
from typing import Dict, Optional, Any
import google.generativeai as genai
from decouple import config
import PyPDF2
import docx
from io import BytesIO

logger = logging.getLogger(__name__)


class ResumeAIService:
    """简历AI解析服务类"""
    
    def __init__(self):
        """初始化简历AI服务"""
        self.api_key = config('GOOGLE_AI_API_KEY', default='')
        
        if not self.api_key or self.api_key == 'your_google_ai_api_key_here':
            logger.warning("Google AI API key not configured properly")
            self.enabled = False
            return
            
        try:
            genai.configure(api_key=self.api_key)
            # 使用稳定的gemini-pro模型
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.enabled = True
            logger.info("Resume AI service initialized with gemini-pro model")
        except Exception as e:
            logger.warning(f"Failed to initialize Resume AI service: {e}")
            self.model = None
            self.enabled = False

    def is_enabled(self) -> bool:
        """检查服务是否可用"""
        return self.enabled

    def extract_text_from_file(self, file_obj, file_extension: str) -> str:
        """从文件中提取文本内容"""
        try:
            if file_extension.lower() == '.pdf':
                return self._extract_text_from_pdf(file_obj)
            elif file_extension.lower() in ['.doc', '.docx']:
                return self._extract_text_from_docx(file_obj)
            elif file_extension.lower() == '.txt':
                return file_obj.read().decode('utf-8')
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
        except Exception as e:
            logger.error(f"Failed to extract text from file: {e}")
            return ""

    def _extract_text_from_pdf(self, file_obj) -> str:
        """从PDF文件中提取文本"""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_obj.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            return ""

    def _extract_text_from_docx(self, file_obj) -> str:
        """从DOCX文件中提取文本"""
        try:
            doc = docx.Document(BytesIO(file_obj.read()))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Failed to extract text from DOCX: {e}")
            return ""

    def parse_resume(self, file_obj, filename: str) -> Dict[str, Any]:
        """
        使用AI解析简历文档
        
        Args:
            file_obj: 文件对象
            filename: 文件名
            
        Returns:
            解析结果字典，包含AI原始响应和结构化数据
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "AI service not available",
                "ai_response": "AI服务未配置或不可用",
                "data": self._get_mock_data()
            }

        try:
            # 提取文件扩展名
            file_extension = os.path.splitext(filename)[1]
            
            # 从文件中提取文本
            resume_text = self.extract_text_from_file(file_obj, file_extension)
            
            if not resume_text.strip():
                return {
                    "success": False,
                    "error": "Failed to extract text from file",
                    "ai_response": "无法从文件中提取文本内容",
                    "data": self._get_mock_data()
                }

            # 构建AI提示词
            prompt = self._build_resume_parsing_prompt(resume_text)
            
            # 调用AI API
            response = self.model.generate_content(prompt)
            ai_response_text = response.text
            
            # 解析AI响应为结构化数据
            parsed_data = self._parse_ai_response(ai_response_text)
            
            logger.info(f"Successfully parsed resume: {filename}")
            
            return {
                "success": True,
                "ai_response": ai_response_text,
                "data": parsed_data,
                "prompt_used": prompt,
                "extracted_text": resume_text[:500] + "..." if len(resume_text) > 500 else resume_text
            }
            
        except Exception as e:
            logger.error(f"AI resume parsing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "ai_response": f"AI解析失败: {str(e)}",
                "data": self._get_mock_data()
            }

    def _build_resume_parsing_prompt(self, resume_text: str) -> str:
        """构建简历解析提示词"""
        return f"""
You are an expert resume parser. Please carefully analyze the following resume content and extract comprehensive information. Pay special attention to all sections and details.

Resume Content:
{resume_text}

Please extract the following information systematically. For each field, provide the most complete and accurate information found in the resume. If information is not available, mark as "Not Provided":

Name: [Extract full name]
Email: [Extract email address]
Phone: [Extract phone number]
Address: [Extract location/address]
Degree: [Extract highest degree - look for Bachelor's, Master's, PhD, Diploma, etc.]
Major: [Extract field of study/specialization]
School: [Extract university/institution name]
Graduation Year: [Extract graduation year or expected graduation]
Years of Experience: [Calculate total years of professional experience]
Technical Skills: [Extract all technical skills, programming languages, tools, frameworks - be comprehensive]
Main Work History: [Extract detailed work experience including company names, positions, duration, and key responsibilities]
Main Projects: [Extract project details including names, technologies used, and achievements]
Self Introduction: [Extract summary, objective, or self-introduction section]

IMPORTANT INSTRUCTIONS:
1. Be thorough - don't miss any information
2. For education, look for multiple degrees and include all of them
3. For work experience, include company names, job titles, dates, and key achievements
4. For technical skills, extract ALL mentioned technologies, programming languages, tools, and frameworks
5. For projects, include project names, descriptions, technologies used, and outcomes
6. Maintain original formatting and details where possible
7. If there are multiple entries for the same category, include all of them
8. Pay attention to dates, durations, and chronological information

Please format your response exactly as shown above with clear labels for each field.
"""

    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """解析AI响应为结构化数据"""
        try:
            # 初始化结果字典
            result = {
                'name': 'Not Provided',
                'email': 'Not Provided',
                'phone': 'Not Provided',
                'education': 'Not Provided',
                'major': 'Not Provided',
                'experience_years': 0,
                'skills': 'Not Provided',
                'work_experience': 'Not Provided',
                'project_experience': 'Not Provided',
                'self_introduction': 'Not Provided'
            }
            
            # 改进的文本解析逻辑 - 更准确地提取信息
            lines = ai_response.split('\n')
            
            # 用于收集多行内容的变量
            collecting_work_history = False
            collecting_projects = False
            collecting_skills = False
            collecting_education = False
            collecting_major = False
            work_history_lines = []
            project_lines = []
            skill_lines = []
            education_lines = []
            major_lines = []
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                # 检测各个字段的开始
                if line.startswith('Name:'):
                    result['name'] = self._extract_value_after_colon(line)
                elif line.startswith('Email:'):
                    result['email'] = self._extract_value_after_colon(line)
                elif line.startswith('Phone:'):
                    result['phone'] = self._extract_value_after_colon(line)
                elif line.startswith('Degree:'):
                    # 开始收集教育背景信息
                    collecting_education = True
                    collecting_major = False
                    collecting_work_history = False
                    collecting_projects = False
                    collecting_skills = False
                    initial_education = self._extract_value_after_colon(line)
                    if initial_education != 'Not Provided':
                        education_lines.append(initial_education)
                elif line.startswith('Major:'):
                    # 开始收集专业信息
                    collecting_major = True
                    collecting_education = False
                    collecting_work_history = False
                    collecting_projects = False
                    collecting_skills = False
                    initial_major = self._extract_value_after_colon(line)
                    if initial_major != 'Not Provided':
                        major_lines.append(initial_major)
                elif line.startswith('Years of Experience:'):
                    years_text = self._extract_value_after_colon(line)
                    result['experience_years'] = self._extract_years(years_text)
                    # 停止收集其他内容
                    collecting_education = False
                    collecting_major = False
                elif line.startswith('Technical Skills:'):
                    # 开始收集技能信息
                    collecting_skills = True
                    collecting_work_history = False
                    collecting_projects = False
                    collecting_education = False
                    collecting_major = False
                    initial_skills = self._extract_value_after_colon(line)
                    if initial_skills != 'Not Provided':
                        skill_lines.append(initial_skills)
                elif line.startswith('Main Work History:'):
                    # 开始收集工作经历
                    collecting_work_history = True
                    collecting_projects = False
                    collecting_skills = False
                    collecting_education = False
                    collecting_major = False
                    initial_work = self._extract_value_after_colon(line)
                    if initial_work != 'Not Provided':
                        work_history_lines.append(initial_work)
                elif line.startswith('Main Projects:'):
                    # 开始收集项目经验
                    collecting_projects = True
                    collecting_work_history = False
                    collecting_skills = False
                    collecting_education = False
                    collecting_major = False
                    initial_projects = self._extract_value_after_colon(line)
                    if initial_projects != 'Not Provided':
                        project_lines.append(initial_projects)
                elif line.startswith('Self Introduction:'):
                    result['self_introduction'] = self._extract_value_after_colon(line)
                    # 停止收集其他内容
                    collecting_work_history = False
                    collecting_projects = False
                    collecting_skills = False
                    collecting_education = False
                    collecting_major = False
                else:
                    # 继续收集多行内容
                    if collecting_education and line and not line.startswith(('Name:', 'Email:', 'Phone:', 'Major:', 'Years of Experience:', 'Technical Skills:', 'Main Work History:', 'Main Projects:', 'Self Introduction:')):
                        # 处理以*开头的教育信息
                        if line.startswith('*'):
                            education_lines.append(line[1:].strip())
                        else:
                            education_lines.append(line)
                    elif collecting_major and line and not line.startswith(('Name:', 'Email:', 'Phone:', 'Degree:', 'Years of Experience:', 'Technical Skills:', 'Main Work History:', 'Main Projects:', 'Self Introduction:')):
                        # 处理以*开头的专业信息
                        if line.startswith('*'):
                            major_lines.append(line[1:].strip())
                        else:
                            major_lines.append(line)
                    elif collecting_work_history and line and not line.startswith(('Name:', 'Email:', 'Phone:', 'Degree:', 'Major:', 'Technical Skills:', 'Main Projects:', 'Self Introduction:')):
                        work_history_lines.append(line)
                    elif collecting_projects and line and not line.startswith(('Name:', 'Email:', 'Phone:', 'Degree:', 'Major:', 'Technical Skills:', 'Main Work History:', 'Self Introduction:')):
                        project_lines.append(line)
                    elif collecting_skills and line and not line.startswith(('Name:', 'Email:', 'Phone:', 'Degree:', 'Major:', 'Main Work History:', 'Main Projects:', 'Self Introduction:')):
                        skill_lines.append(line)
            
            # 组合多行内容
            if education_lines:
                result['education'] = ' '.join(education_lines)
            if major_lines:
                result['major'] = ' '.join(major_lines)
            if work_history_lines:
                result['work_experience'] = ' '.join(work_history_lines)
            if project_lines:
                result['project_experience'] = ' '.join(project_lines)
            if skill_lines:
                result['skills'] = ' '.join(skill_lines)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            return self._get_mock_data()

    def _extract_value_after_colon(self, line: str) -> str:
        """从冒号后提取值"""
        if ':' in line:
            value = line.split(':', 1)[1].strip()
            # 移除方括号标记
            if value.startswith('[') and value.endswith(']'):
                value = value[1:-1].strip()
            return value if value and value != 'Not Provided' else 'Not Provided'
        return 'Not Provided'

    def _extract_years(self, text: str) -> int:
        """从文本中提取年数"""
        try:
            import re
            numbers = re.findall(r'\d+', text)
            if numbers:
                return int(numbers[0])
        except:
            pass
        return 0

    def _get_mock_data(self) -> Dict[str, Any]:
        """获取模拟数据"""
        return {
            'name': 'Mock User',
            'email': 'mock@example.com',
            'phone': '123-456-7890',
            'education': 'Bachelor\'s Degree',
            'major': 'Computer Science',
            'experience_years': 3,
            'skills': 'Python, JavaScript, React, Django',
            'work_experience': 'Software Developer at Tech Company (2021-2024)',
            'project_experience': 'E-commerce Platform Development, AI Chatbot Implementation',
            'self_introduction': 'Experienced software developer with expertise in full-stack development and AI technologies.'
        }


# 全局服务实例
resume_ai_service = ResumeAIService()