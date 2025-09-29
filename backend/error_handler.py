#!/usr/bin/env python
"""
错误处理和异常捕获机制
提供重试逻辑、错误恢复和详细的错误报告
"""

import os
import sys
import logging
import traceback
import time
import json
from datetime import datetime
from pathlib import Path
from functools import wraps
from typing import Callable, Any, Optional, Dict, List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, logger=None):
        """初始化错误处理器"""
        self.logger = logger or logging.getLogger(__name__)
        self.error_counts = {}
        self.error_history = []
        self.max_error_history = 100
        
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """记录错误详情"""
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        
        # 添加到错误历史
        self.error_history.append(error_info)
        if len(self.error_history) > self.max_error_history:
            self.error_history.pop(0)
        
        # 统计错误次数
        error_key = f"{error_info['error_type']}:{error_info['error_message']}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # 记录到日志
        self.logger.error(f"错误发生: {error_info['error_type']} - {error_info['error_message']}")
        self.logger.error(f"错误上下文: {json.dumps(context or {}, ensure_ascii=False)}")
        self.logger.error(f"错误堆栈:\n{error_info['traceback']}")
        
        return error_info
    
    def get_error_summary(self) -> Dict[str, Any]:
        """获取错误汇总"""
        return {
            'total_errors': len(self.error_history),
            'unique_errors': len(self.error_counts),
            'most_common_errors': sorted(
                self.error_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5],
            'recent_errors': self.error_history[-5:] if self.error_history else []
        }


class RetryHandler:
    """重试处理器"""
    
    def __init__(self, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
        """
        初始化重试处理器
        
        Args:
            max_retries: 最大重试次数
            delay: 初始延迟时间（秒）
            backoff: 退避倍数
        """
        self.max_retries = max_retries
        self.delay = delay
        self.backoff = backoff
        self.logger = logging.getLogger(__name__)
    
    def retry_on_exception(self, exceptions: tuple = (Exception,), 
                          max_retries: Optional[int] = None,
                          delay: Optional[float] = None,
                          backoff: Optional[float] = None):
        """
        装饰器：在指定异常时重试
        
        Args:
            exceptions: 需要重试的异常类型
            max_retries: 最大重试次数（覆盖默认值）
            delay: 初始延迟时间（覆盖默认值）
            backoff: 退避倍数（覆盖默认值）
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                _max_retries = max_retries or self.max_retries
                _delay = delay or self.delay
                _backoff = backoff or self.backoff
                
                last_exception = None
                
                for attempt in range(_max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        if attempt == _max_retries:
                            self.logger.error(f"函数 {func.__name__} 重试 {_max_retries} 次后仍然失败")
                            break
                        
                        wait_time = _delay * (_backoff ** attempt)
                        self.logger.warning(
                            f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {str(e)}, "
                            f"{wait_time:.1f}秒后重试"
                        )
                        time.sleep(wait_time)
                
                raise last_exception
            
            return wrapper
        return decorator


class CircuitBreaker:
    """熔断器"""
    
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        """
        初始化熔断器
        
        Args:
            failure_threshold: 失败阈值
            timeout: 熔断超时时间（秒）
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self.logger = logging.getLogger(__name__)
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """调用函数，应用熔断逻辑"""
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time < self.timeout:
                raise Exception(f"熔断器开启，服务不可用，剩余时间: {self.timeout - (time.time() - self.last_failure_time):.1f}秒")
            else:
                self.state = 'HALF_OPEN'
                self.logger.info("熔断器进入半开状态")
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
    
    def on_success(self):
        """成功时的处理"""
        self.failure_count = 0
        if self.state == 'HALF_OPEN':
            self.state = 'CLOSED'
            self.logger.info("熔断器关闭")
    
    def on_failure(self):
        """失败时的处理"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            self.logger.warning(f"熔断器开启，失败次数: {self.failure_count}")


class ErrorRecovery:
    """错误恢复机制"""
    
    def __init__(self, logger=None):
        """初始化错误恢复机制"""
        self.logger = logger or logging.getLogger(__name__)
        self.recovery_strategies = {}
    
    def register_recovery_strategy(self, error_type: type, strategy: Callable):
        """注册错误恢复策略"""
        self.recovery_strategies[error_type] = strategy
        self.logger.info(f"注册错误恢复策略: {error_type.__name__}")
    
    def attempt_recovery(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """尝试错误恢复"""
        error_type = type(error)
        
        if error_type in self.recovery_strategies:
            try:
                self.logger.info(f"尝试恢复错误: {error_type.__name__}")
                strategy = self.recovery_strategies[error_type]
                result = strategy(error, context or {})
                
                if result:
                    self.logger.info(f"错误恢复成功: {error_type.__name__}")
                    return True
                else:
                    self.logger.warning(f"错误恢复失败: {error_type.__name__}")
                    return False
                    
            except Exception as recovery_error:
                self.logger.error(f"错误恢复过程中发生异常: {str(recovery_error)}")
                return False
        else:
            self.logger.warning(f"没有找到错误恢复策略: {error_type.__name__}")
            return False


class ErrorNotifier:
    """错误通知器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化错误通知器"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
    def send_email_notification(self, error_info: Dict[str, Any], recipients: List[str]):
        """发送邮件通知"""
        try:
            if not self.config.get('smtp_enabled', False):
                self.logger.info("SMTP未启用，跳过邮件通知")
                return
            
            smtp_server = self.config.get('smtp_server')
            smtp_port = self.config.get('smtp_port', 587)
            smtp_username = self.config.get('smtp_username')
            smtp_password = self.config.get('smtp_password')
            
            if not all([smtp_server, smtp_username, smtp_password]):
                self.logger.warning("SMTP配置不完整，无法发送邮件")
                return
            
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = f"自动上传程序错误通知 - {error_info['error_type']}"
            
            # 邮件内容
            body = f"""
自动上传程序发生错误：

时间: {error_info['timestamp']}
错误类型: {error_info['error_type']}
错误消息: {error_info['error_message']}
上下文: {json.dumps(error_info.get('context', {}), ensure_ascii=False, indent=2)}

详细堆栈信息:
{error_info['traceback']}
"""
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 发送邮件
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            self.logger.info(f"错误通知邮件已发送给: {', '.join(recipients)}")
            
        except Exception as e:
            self.logger.error(f"发送错误通知邮件失败: {str(e)}")
    
    def log_to_file(self, error_info: Dict[str, Any], error_log_file: str = 'critical_errors.log'):
        """记录到专用错误文件"""
        try:
            log_dir = Path('logs')
            log_dir.mkdir(exist_ok=True)
            
            error_file = log_dir / error_log_file
            
            with open(error_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"时间: {error_info['timestamp']}\n")
                f.write(f"错误类型: {error_info['error_type']}\n")
                f.write(f"错误消息: {error_info['error_message']}\n")
                f.write(f"上下文: {json.dumps(error_info.get('context', {}), ensure_ascii=False, indent=2)}\n")
                f.write(f"堆栈信息:\n{error_info['traceback']}\n")
            
            self.logger.info(f"错误信息已记录到: {error_file}")
            
        except Exception as e:
            self.logger.error(f"记录错误到文件失败: {str(e)}")


class ComprehensiveErrorHandler:
    """综合错误处理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化综合错误处理器"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 初始化各个组件
        self.error_handler = ErrorHandler(self.logger)
        self.retry_handler = RetryHandler(
            max_retries=self.config.get('max_retries', 3),
            delay=self.config.get('retry_delay', 1.0),
            backoff=self.config.get('retry_backoff', 2.0)
        )
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=self.config.get('circuit_breaker_threshold', 5),
            timeout=self.config.get('circuit_breaker_timeout', 60.0)
        )
        self.error_recovery = ErrorRecovery(self.logger)
        self.error_notifier = ErrorNotifier(self.config.get('notification', {}))
        
        # 注册默认恢复策略
        self._register_default_recovery_strategies()
    
    def _register_default_recovery_strategies(self):
        """注册默认错误恢复策略"""
        
        def file_not_found_recovery(error: FileNotFoundError, context: Dict[str, Any]) -> bool:
            """文件未找到错误恢复"""
            file_path = context.get('file_path')
            if file_path:
                # 尝试在常见位置查找文件
                common_paths = [
                    Path(file_path).parent / Path(file_path).name,
                    Path('doc') / Path(file_path).name,
                    Path('.') / Path(file_path).name
                ]
                
                for path in common_paths:
                    if path.exists():
                        self.logger.info(f"在 {path} 找到文件")
                        context['file_path'] = str(path)
                        return True
            return False
        
        def permission_error_recovery(error: PermissionError, context: Dict[str, Any]) -> bool:
            """权限错误恢复"""
            file_path = context.get('file_path')
            if file_path:
                try:
                    # 尝试修改文件权限
                    os.chmod(file_path, 0o644)
                    self.logger.info(f"修改文件权限: {file_path}")
                    return True
                except:
                    pass
            return False
        
        def connection_error_recovery(error: Exception, context: Dict[str, Any]) -> bool:
            """连接错误恢复"""
            # 等待一段时间后重试
            time.sleep(5)
            self.logger.info("等待5秒后重试连接")
            return True
        
        # 注册恢复策略
        self.error_recovery.register_recovery_strategy(FileNotFoundError, file_not_found_recovery)
        self.error_recovery.register_recovery_strategy(PermissionError, permission_error_recovery)
        # 可以添加更多恢复策略
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None, 
                    notify: bool = False, attempt_recovery: bool = True) -> Dict[str, Any]:
        """综合错误处理"""
        # 记录错误
        error_info = self.error_handler.log_error(error, context)
        
        # 尝试错误恢复
        recovery_successful = False
        if attempt_recovery:
            recovery_successful = self.error_recovery.attempt_recovery(error, context)
        
        # 发送通知
        if notify:
            self.error_notifier.log_to_file(error_info)
            
            # 如果是严重错误，发送邮件通知
            if isinstance(error, (SystemError, MemoryError, KeyboardInterrupt)):
                recipients = self.config.get('notification', {}).get('email_recipients', [])
                if recipients:
                    self.error_notifier.send_email_notification(error_info, recipients)
        
        return {
            'error_info': error_info,
            'recovery_successful': recovery_successful,
            'error_summary': self.error_handler.get_error_summary()
        }
    
    def with_error_handling(self, func: Callable, context: Dict[str, Any] = None,
                           retry: bool = True, circuit_breaker: bool = False,
                           notify_on_error: bool = False) -> Any:
        """带错误处理的函数执行"""
        
        def execute():
            if circuit_breaker:
                return self.circuit_breaker.call(func)
            else:
                return func()
        
        try:
            if retry:
                # 使用重试装饰器
                @self.retry_handler.retry_on_exception()
                def retry_execute():
                    return execute()
                
                return retry_execute()
            else:
                return execute()
                
        except Exception as e:
            # 处理错误
            result = self.handle_error(
                e, 
                context=context, 
                notify=notify_on_error, 
                attempt_recovery=True
            )
            
            # 如果恢复成功，再次尝试执行
            if result['recovery_successful']:
                try:
                    return execute()
                except Exception as retry_error:
                    self.logger.error(f"恢复后重试仍然失败: {str(retry_error)}")
            
            # 重新抛出异常
            raise


# 使用示例和配置
DEFAULT_ERROR_CONFIG = {
    'max_retries': 3,
    'retry_delay': 1.0,
    'retry_backoff': 2.0,
    'circuit_breaker_threshold': 5,
    'circuit_breaker_timeout': 60.0,
    'notification': {
        'smtp_enabled': False,
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_username': '',
        'smtp_password': '',
        'email_recipients': []
    }
}


def create_error_handler(config: Dict[str, Any] = None) -> ComprehensiveErrorHandler:
    """创建错误处理器实例"""
    final_config = DEFAULT_ERROR_CONFIG.copy()
    if config:
        final_config.update(config)
    
    return ComprehensiveErrorHandler(final_config)


if __name__ == '__main__':
    # 测试错误处理器
    logging.basicConfig(level=logging.INFO)
    
    error_handler = create_error_handler()
    
    def test_function():
        raise ValueError("测试错误")
    
    try:
        error_handler.with_error_handling(
            test_function,
            context={'test': 'context'},
            retry=True,
            notify_on_error=True
        )
    except Exception as e:
        print(f"最终错误: {e}")
    
    # 输出错误汇总
    summary = error_handler.error_handler.get_error_summary()
    print(f"错误汇总: {json.dumps(summary, ensure_ascii=False, indent=2)}")