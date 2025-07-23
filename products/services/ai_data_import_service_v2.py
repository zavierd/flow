"""
AI数据格式导入服务 V2
使用模块化架构处理AI模型输出的15列标准化数据格式
"""

import logging
from typing import Dict, Any
from django.utils import timezone

from products.models import ImportTask
from .import_system.orchestrator import ImportOrchestrator

logger = logging.getLogger(__name__)


class AIDataImportServiceV2:
    """
    AI数据格式导入服务 V2
    使用模块化架构处理AI模型输出的15列标准化数据格式
    """
    
    def __init__(self, task: ImportTask):
        self.task = task
        self.orchestrator = ImportOrchestrator(task)
        
    def process_ai_data_import(self, csv_content: str) -> Dict[str, Any]:
        """
        处理AI数据格式的CSV导入
        
        Args:
            csv_content: CSV文件内容
            
        Returns:
            Dict: 导入结果统计
        """
        try:
            # 更新任务状态
            self.task.status = 'processing'
            self.task.started_at = timezone.now()
            self.task.save()
            
            # 使用编排器处理导入
            result = self.orchestrator.process_import(csv_content)
            
            # 更新任务状态
            if result.success:
                self.task.status = 'completed'
            else:
                self.task.status = 'failed'
                self.task.error_details = f"导入失败，错误数量: {len(result.errors)}"
            
            self.task.completed_at = timezone.now()
            self.task.total_rows = result.total_rows
            self.task.success_rows = result.success_rows
            self.task.error_rows = result.error_rows
            self.task.save()
            
            return {
                'success': result.success,
                'total_rows': result.total_rows,
                'success_rows': result.success_rows,
                'error_rows': result.error_rows,
                'errors': result.errors
            }
            
        except Exception as e:
            logger.error(f"AI数据导入失败: {str(e)}")
            return self._handle_task_failure(f"导入过程出错: {str(e)}")
    
    def _handle_task_failure(self, error_message: str) -> Dict[str, Any]:
        """处理任务失败"""
        self.task.status = 'failed'
        self.task.completed_at = timezone.now()
        self.task.error_details = error_message
        self.task.save()

        return {
            'success': False,
            'error': error_message,
            'total_rows': getattr(self.task, 'total_rows', 0),
            'success_rows': getattr(self.task, 'success_rows', 0),
            'error_rows': getattr(self.task, 'error_rows', 0),
            'errors': []
        }
