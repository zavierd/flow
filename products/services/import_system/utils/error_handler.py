"""
错误处理器
负责统一的错误处理和记录
"""

import logging
from typing import Dict, List, Any
from products.models import ImportError

logger = logging.getLogger(__name__)


class ErrorHandler:
    """错误处理器 - 单一职责：错误处理和记录"""

    def __init__(self, task):
        self.task = task

    def handle_error(self, row_number: int, stage: str, message: str,
                    details: str = '', row_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理错误"""
        error_info = {
            'row_number': row_number,
            'stage': stage,
            'message': message,
            'details': details,
            'row_data': row_data or {}
        }

        # 记录到数据库
        self._save_error_to_db(error_info)

        # 记录到日志
        logger.error(f"行{row_number}[{stage}]: {message}")
        if details:
            logger.debug(f"错误详情: {details}")

        return error_info

    def _save_error_to_db(self, error_info: Dict[str, Any]):
        """保存错误到数据库"""
        try:
            ImportError.objects.create(
                task=self.task,
                row_number=error_info['row_number'],
                field_name=error_info['stage'],
                error_message=error_info['message'],
                raw_data=error_info['row_data'],
                error_type='system'
            )
        except Exception as e:
            logger.error(f"保存错误记录失败: {str(e)}")

    def batch_handle_errors(self, errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量处理错误"""
        handled_errors = []

        for error in errors:
            handled_error = self.handle_error(
                row_number=error.get('row_number', 0),
                stage=error.get('stage', 'unknown'),
                message=error.get('message', '未知错误'),
                details=error.get('details', ''),
                row_data=error.get('row_data', {})
            )
            handled_errors.append(handled_error)

        return handled_errors