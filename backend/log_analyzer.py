#!/usr/bin/env python
"""
日志分析工具
分析自动上传程序的日志输出，识别问题、性能瓶颈和处理统计
"""

import os
import re
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional, Tuple
import statistics

# 移除可视化依赖，使用文本报告
HAS_VISUALIZATION = False

try:
    import matplotlib.pyplot as plt
    HAS_VISUALIZATION = True
except ImportError:
    pass


class LogAnalyzer:
    """日志分析器"""
    
    def __init__(self, log_dir='logs'):
        """初始化日志分析器"""
        self.log_dir = Path(log_dir)
        self.log_pattern = re.compile(
            r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - '
            r'(?P<logger>\S+) - '
            r'(?P<level>\w+) - '
            r'(?P<function>\w+):(?P<line>\d+) - '
            r'(?P<message>.*)'
        )
        
    def parse_log_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """解析日志文件"""
        entries = []
        current_entry = None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:  # 跳过空行
                        continue
                    
                    # 尝试解析为新的日志条目
                    entry = self.parse_log_line(line)
                    if entry:
                        # 如果有当前条目，先保存它
                        if current_entry:
                            current_entry['file'] = file_path.name
                            entries.append(current_entry)
                        
                        # 开始新的条目
                        current_entry = entry
                        current_entry['line_number'] = line_num
                    else:
                        # 这是多行消息的延续
                        if current_entry:
                            current_entry['message'] += '\n' + line
                        else:
                            # 调试：打印无法解析的行
                            print(f"无法解析第{line_num}行: {line[:100]}")
                
                # 保存最后一个条目
                if current_entry:
                    current_entry['file'] = file_path.name
                    entries.append(current_entry)
                    
        except Exception as e:
            print(f"解析文件 {file_path} 时出错: {e}")
        
        return entries
    
    def parse_log_line(self, line: str) -> Optional[Dict[str, Any]]:
        """解析单行日志"""
        # 匹配日志格式: 2025-09-30 01:26:11,112 - __main__ - INFO - 消息
        log_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\S+) - (\w+) - (.+)'
        match = re.match(log_pattern, line.strip())
        
        if not match:
            return None
        
        timestamp_str, logger_name, level, message = match.groups()
        
        try:
            # 解析时间戳，将逗号替换为点号以匹配Python的微秒格式
            timestamp_str_fixed = timestamp_str.replace(',', '.')
            timestamp = datetime.strptime(timestamp_str_fixed, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            return None
        
        return {
            'timestamp': timestamp,
            'logger': logger_name,
            'level': level,
            'message': message,
            'raw_line': line.strip()
        }
    
    def analyze_processing_performance(self, entries):
        """分析处理性能"""
        print("\n" + "="*60)
        print("📊 处理性能分析")
        print("="*60)
        
        # 统计各个步骤的耗时
        step_times = defaultdict(list)
        current_process = {}
        
        for entry in entries:
            message = entry['message']
            timestamp = entry['timestamp']
            
            if '开始处理文件:' in message:
                current_process['start'] = timestamp
            elif '步骤1: 提取文档内容' in message:
                current_process['extract_start'] = timestamp
            elif '成功提取文本内容' in message:
                if 'extract_start' in current_process:
                    duration = (timestamp - current_process['extract_start']).total_seconds()
                    step_times['文档提取'].append(duration)
            elif '步骤2: AI解析职位描述' in message:
                current_process['ai_start'] = timestamp
            elif 'AI解析完成' in message:
                if 'ai_start' in current_process:
                    duration = (timestamp - current_process['ai_start']).total_seconds()
                    step_times['AI解析'].append(duration)
            elif '步骤3: 保存到数据库' in message:
                current_process['db_start'] = timestamp
            elif '成功保存职位到数据库' in message:
                if 'db_start' in current_process:
                    duration = (timestamp - current_process['db_start']).total_seconds()
                    step_times['数据库保存'].append(duration)
            elif '文件处理完成' in message:
                if 'start' in current_process:
                    duration = (timestamp - current_process['start']).total_seconds()
                    step_times['总处理时间'].append(duration)
                current_process = {}
        
        # 输出性能统计
        for step, times in step_times.items():
            if times:
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                print(f"\n{step}:")
                print(f"  平均耗时: {avg_time:.2f}秒")
                print(f"  最短耗时: {min_time:.2f}秒")
                print(f"  最长耗时: {max_time:.2f}秒")
                print(f"  处理次数: {len(times)}")
    
    def analyze_error_patterns(self, entries):
        """分析错误模式"""
        print("\n" + "="*60)
        print("🚨 错误模式分析")
        print("="*60)
        
        error_entries = [e for e in entries if e['level'] == 'ERROR']
        
        if not error_entries:
            print("没有发现错误日志")
            return
        
        # 错误类型统计
        error_types = {}
        for entry in error_entries:
            message = entry['message']
            # 提取错误类型
            if ':' in message:
                error_type = message.split(':')[0].strip()
            else:
                error_type = "未知错误"
            
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        print(f"错误类型分布:")
        for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {error_type}: {count}")
        
        # 显示最近的错误
        print(f"\n最近的错误 (最多显示5条):")
        recent_errors = sorted(error_entries, key=lambda x: x['timestamp'], reverse=True)[:5]
        for i, entry in enumerate(recent_errors, 1):
            print(f"{i}. [{entry['timestamp']}] {entry['message']}")
        
        # 错误时间分布
        error_hours = {}
        for entry in error_entries:
            hour = entry['timestamp'].hour
            error_hours[hour] = error_hours.get(hour, 0) + 1
        
        if error_hours:
            print(f"\n错误时间分布:")
            for hour in sorted(error_hours.keys()):
                print(f"  {hour:02d}:00-{hour:02d}:59: {error_hours[hour]} 个错误")
    
    def analyze_ai_performance(self, entries):
        """分析AI性能"""
        print("\n" + "="*60)
        print("🤖 AI解析性能分析")
        print("="*60)
        
        ai_success = 0
        ai_failure = 0
        ai_response_lengths = []
        
        for entry in entries:
            message = entry['message']
            
            if 'AI解析完成' in message:
                ai_success += 1
            elif 'AI解析失败' in message:
                ai_failure += 1
            elif 'AI原始响应:' in message:
                # 提取响应长度
                response_text = message.split('AI原始响应:')[1].strip()
                ai_response_lengths.append(len(response_text))
        
        total_ai_calls = ai_success + ai_failure
        
        if total_ai_calls > 0:
            success_rate = (ai_success / total_ai_calls) * 100
            print(f"\nAI解析成功率: {success_rate:.1f}% ({ai_success}/{total_ai_calls})")
            print(f"AI解析失败次数: {ai_failure}")
            
            if ai_response_lengths:
                avg_response_length = sum(ai_response_lengths) / len(ai_response_lengths)
                print(f"平均响应长度: {avg_response_length:.0f}字符")
        else:
            print("没有发现AI解析记录")
    
    def analyze_database_operations(self, entries):
        """分析数据库操作"""
        print("\n" + "="*60)
        print("💾 数据库操作分析")
        print("="*60)
        
        db_saves = 0
        created_jobs = []
        
        for entry in entries:
            message = entry['message']
            
            if '成功保存职位到数据库' in message:
                db_saves += 1
                # 提取职位ID
                if 'ID:' in message:
                    job_id = message.split('ID:')[1].strip().split()[0]
                    created_jobs.append(job_id)
            elif '职位详情:' in message:
                # 提取职位详情
                details = message.split('职位详情:')[1].strip()
                print(f"  创建职位: {details}")
        
        print(f"\n成功保存到数据库: {db_saves}次")
        print(f"创建的职位ID: {', '.join(created_jobs) if created_jobs else '无'}")
    
    def generate_summary_report(self, entries):
        """生成汇总报告"""
        print("\n" + "="*60)
        print("📋 处理汇总报告")
        print("="*60)
        
        if not entries:
            print("没有找到日志条目")
            return
        
        # 时间范围
        start_time = min(e['timestamp'] for e in entries)
        end_time = max(e['timestamp'] for e in entries)
        duration = end_time - start_time
        
        # 日志级别统计
        level_counts = Counter(e['level'] for e in entries)
        
        # 处理的文件数量
        processed_files = len([e for e in entries if '开始处理文件:' in e['message']])
        completed_files = len([e for e in entries if '文件处理完成' in e['message']])
        failed_files = len([e for e in entries if '文件处理失败:' in e['message']])
        
        print(f"\n时间范围: {start_time.strftime('%Y-%m-%d %H:%M:%S')} - {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总持续时间: {duration}")
        print(f"总日志条目: {len(entries)}")
        
        print(f"\n日志级别分布:")
        for level, count in level_counts.most_common():
            print(f"  {level}: {count}")
        
        print(f"\n文件处理统计:")
        print(f"  开始处理: {processed_files}")
        print(f"  成功完成: {completed_files}")
        print(f"  处理失败: {failed_files}")
        
        if processed_files > 0:
            success_rate = (completed_files / processed_files) * 100
            print(f"  成功率: {success_rate:.1f}%")
    
    def analyze_logs(self, date_filter=None):
        """分析日志"""
        print("🔍 开始分析日志...")
        
        # 查找日志文件
        log_files = []
        if date_filter:
            pattern = f"auto_upload_{date_filter}*.log"
        else:
            pattern = "auto_upload_*.log"
        
        for log_file in self.log_dir.glob(pattern):
            if not log_file.name.endswith('_errors.log'):  # 排除错误专用日志
                log_files.append(log_file)
        
        if not log_files:
            print(f"没有找到匹配的日志文件: {pattern}")
            return
        
        print(f"找到 {len(log_files)} 个日志文件")
        
        # 解析所有日志文件
        all_entries = []
        for log_file in sorted(log_files):
            print(f"解析日志文件: {log_file}")
            entries = self.parse_log_file(log_file)
            all_entries.extend(entries)
        
        if not all_entries:
            print("没有找到有效的日志条目")
            return
        
        print(f"总共解析了 {len(all_entries)} 条日志")
        
        # 执行各种分析
        self.generate_summary_report(all_entries)
        self.analyze_processing_performance(all_entries)
        self.analyze_error_patterns(all_entries)
        self.analyze_ai_performance(all_entries)
        self.analyze_database_operations(all_entries)
        
        print("\n" + "="*60)
        print("✅ 日志分析完成")
        print("="*60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='分析自动上传程序日志')
    parser.add_argument('--date', help='分析指定日期的日志 (格式: YYYYMMDD)')
    parser.add_argument('--log-dir', default='logs', help='日志目录路径')
    
    args = parser.parse_args()
    
    analyzer = LogAnalyzer(args.log_dir)
    analyzer.analyze_logs(args.date)


if __name__ == '__main__':
    main()