from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django.db.models import Q
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import logging
from .models import Resume
from .serializers import ResumeSerializer

logger = logging.getLogger(__name__)


class ResumeViewSet(viewsets.ModelViewSet):
    """简历视图集"""
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    permission_classes = [AllowAny]  # 演示模式允许所有访问

    def get_queryset(self):
        """获取查询集，支持搜索"""
        queryset = Resume.objects.all()
        search = self.request.query_params.get('search', None)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(skills__icontains=search)
            )
        
        return queryset.order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """创建简历"""
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                resume = serializer.save()
                logger.info(f"简历创建成功: {resume.name} - {resume.email}")
                return Response(
                    {
                        'message': '简历上传成功',
                        'data': serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                logger.warning(f"简历创建失败: {serializer.errors}")
                return Response(
                    {
                        'message': '数据验证失败',
                        'errors': serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.error(f"简历创建异常: {str(e)}")
            return Response(
                {
                    'message': '服务器内部错误',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request, *args, **kwargs):
        """获取简历列表"""
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'message': '获取成功',
                'data': serializer.data,
                'count': queryset.count()
            })
        except Exception as e:
            logger.error(f"获取简历列表异常: {str(e)}")
            return Response(
                {
                    'message': '获取简历列表失败',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        """获取单个简历详情"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                'message': '获取成功',
                'data': serializer.data
            })
        except Exception as e:
            logger.error(f"获取简历详情异常: {str(e)}")
            return Response(
                {
                    'message': '获取简历详情失败',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def parse(self, request):
        """AI解析简历文件"""
        try:
            if 'file' not in request.FILES:
                return Response(
                    {'message': '请上传文件'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            uploaded_file = request.FILES['file']
            
            # 验证文件类型
            allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
            file_extension = uploaded_file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                return Response(
                    {'message': '不支持的文件格式，请上传PDF、DOC、DOCX或TXT文件'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 使用真实的AI服务解析简历
            from .ai_service import resume_ai_service
            
            # 调用AI解析服务
            ai_result = resume_ai_service.parse_resume(uploaded_file, uploaded_file.name)
            
            if ai_result['success']:
                logger.info(f"AI解析简历成功: {uploaded_file.name}")
                return Response({
                    'message': 'AI解析成功',
                    'data': ai_result['data'],
                    'ai_response': ai_result['ai_response'],
                    'prompt_used': ai_result.get('prompt_used', ''),
                    'extracted_text': ai_result.get('extracted_text', ''),
                    'ai_enabled': resume_ai_service.is_enabled()
                })
            else:
                logger.warning(f"AI解析简历失败，使用模拟数据: {uploaded_file.name}")
                return Response({
                    'message': 'AI解析完成（使用模拟数据）',
                    'data': ai_result['data'],
                    'ai_response': ai_result['ai_response'],
                    'error': ai_result.get('error', ''),
                    'ai_enabled': resume_ai_service.is_enabled()
                })
            
        except Exception as e:
            logger.error(f"AI解析简历异常: {str(e)}")
            return Response(
                {
                    'message': 'AI解析失败',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取简历统计信息"""
        try:
            total_count = Resume.objects.count()
            return Response({
                'message': '获取统计信息成功',
                'data': {
                    'total_resumes': total_count
                }
            })
        except Exception as e:
            logger.error(f"获取简历统计异常: {str(e)}")
            return Response(
                {
                    'message': '获取统计信息失败',
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )