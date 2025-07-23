"""
进度管理器
负责管理导入过程的进度展示和状态更新
"""

import time
import logging
from typing import Dict, List, Any, Optional
from django.utils import timezone

from .. import ProcessingStage, ProcessingStatus, StageInfo

logger = logging.getLogger(__name__)


class ProgressManager:
    """进度管理器 - 单一职责：管理导入进度和状态展示"""
    
    # 阶段配置
    STAGE_CONFIGS = {
        ProcessingStage.INITIALIZING: {
            'name': '系统初始化',
            'description': '正在初始化导入引擎和验证环境配置...',
            'icon': '🚀',
            'estimated_duration': 0.5
        },
        ProcessingStage.PREPROCESSING: {
            'name': '数据预处理',
            'description': '正在解析CSV格式、清理数据并进行字段映射...',
            'icon': '🔧',
            'estimated_duration': 1.0
        },
        ProcessingStage.VALIDATION: {
            'name': '数据验证',
            'description': '正在执行业务规则验证和数据完整性检查...',
            'icon': '✅',
            'estimated_duration': 0.8
        },
        ProcessingStage.QUALITY_CHECK: {
            'name': 'AI质量检测',
            'description': '正在运行AI算法进行数据质量分析和异常检测...',
            'icon': '🤖',
            'estimated_duration': 2.0
        },
        ProcessingStage.AI_ENHANCEMENT: {
            'name': 'AI智能增强',
            'description': '正在使用深度学习模型提取智能属性和补全数据...',
            'icon': '🧠',
            'estimated_duration': 3.0
        },
        ProcessingStage.ATTRIBUTE_BUILDING: {
            'name': '属性构建',
            'description': '正在创建产品属性定义和属性值映射关系...',
            'icon': '🏗️',
            'estimated_duration': 1.5
        },
        ProcessingStage.PRODUCT_BUILDING: {
            'name': '产品构建',
            'description': '正在创建SPU/SKU产品数据和关联品牌分类...',
            'icon': '📦',
            'estimated_duration': 2.0
        },
        ProcessingStage.RELATION_BUILDING: {
            'name': '关系构建',
            'description': '正在建立产品属性关联和数据库索引优化...',
            'icon': '🔗',
            'estimated_duration': 1.2
        },
        ProcessingStage.FINALIZING: {
            'name': '完成处理',
            'description': '正在生成导入报告和清理临时数据...',
            'icon': '🎉',
            'estimated_duration': 0.5
        }
    }
    
    def __init__(self, task=None):
        self.task = task
        self.current_stage = None
        self.stage_start_time = None
        self.total_start_time = None
        self.stage_history = []
        self.metrics = {
            'total_rows': 0,
            'processed_rows': 0,
            'success_rows': 0,
            'error_rows': 0,
            'current_row': 0,
            'processing_speed': 0.0,
            'estimated_remaining': 0.0
        }
    
    def start_import(self, total_rows: int):
        """开始导入过程"""
        self.total_start_time = time.time()
        self.metrics['total_rows'] = total_rows
        
        # 更新任务状态
        if self.task:
            self.task.status = 'processing'
            self.task.started_at = timezone.now()
            self.task.total_rows = total_rows
            self.task.save()
        
        logger.info(f"开始导入 {total_rows} 行数据")
    
    def start_stage(self, stage: ProcessingStage, row_number: int = None) -> StageInfo:
        """开始新阶段"""
        # 结束上一个阶段
        if self.current_stage:
            self._end_current_stage()
        
        # 开始新阶段
        self.current_stage = stage
        self.stage_start_time = time.time()
        
        config = self.STAGE_CONFIGS.get(stage, {})
        stage_info = StageInfo(
            stage=stage,
            name=config.get('name', stage.value),
            description=config.get('description', f'正在处理 {stage.value}...'),
            icon=config.get('icon', '⚙️'),
            estimated_duration=config.get('estimated_duration', 1.0)
        )
        
        # 更新详细信息
        if row_number:
            stage_info.details['current_row'] = row_number
            stage_info.details['total_rows'] = self.metrics['total_rows']
            stage_info.details['progress_percent'] = (row_number / self.metrics['total_rows']) * 100 if self.metrics['total_rows'] > 0 else 0
        
        # 计算预估剩余时间
        if self.metrics['processed_rows'] > 0:
            elapsed_time = time.time() - self.total_start_time
            avg_time_per_row = elapsed_time / self.metrics['processed_rows']
            remaining_rows = self.metrics['total_rows'] - self.metrics['processed_rows']
            self.metrics['estimated_remaining'] = remaining_rows * avg_time_per_row
            self.metrics['processing_speed'] = self.metrics['processed_rows'] / elapsed_time
        
        stage_info.details['metrics'] = self.metrics.copy()
        
        logger.info(f"开始阶段: {stage_info.name} - {stage_info.description}")
        return stage_info
    
    def update_stage_progress(self, details: Dict[str, Any]):
        """更新当前阶段进度"""
        if self.current_stage and hasattr(self, 'current_stage_info'):
            self.current_stage_info.details.update(details)
    
    def complete_row(self, success: bool, row_number: int):
        """完成一行数据处理"""
        self.metrics['processed_rows'] += 1
        self.metrics['current_row'] = row_number
        
        if success:
            self.metrics['success_rows'] += 1
        else:
            self.metrics['error_rows'] += 1
        
        # 更新任务进度
        if self.task:
            self.task.update_progress(
                self.metrics['processed_rows'],
                self.metrics['success_rows'],
                self.metrics['error_rows']
            )
    
    def complete_import(self, success: bool, errors: List[Dict[str, Any]] = None):
        """完成导入过程"""
        # 结束最后一个阶段
        if self.current_stage:
            self._end_current_stage()
        
        total_duration = time.time() - self.total_start_time if self.total_start_time else 0
        
        # 更新任务状态
        if self.task:
            self.task.status = 'completed' if success else 'failed'
            self.task.completed_at = timezone.now()
            self.task.success_rows = self.metrics['success_rows']
            self.task.error_rows = self.metrics['error_rows']
            
            if not success and errors:
                self.task.error_details = f"导入失败，错误数量: {len(errors)}"
            
            self.task.save()
        
        # 生成最终报告
        final_report = self._generate_final_report(total_duration, success, errors)
        logger.info(f"导入完成: {final_report}")
        
        return final_report
    
    def _end_current_stage(self):
        """结束当前阶段"""
        if self.current_stage and self.stage_start_time:
            duration = time.time() - self.stage_start_time
            
            stage_record = {
                'stage': self.current_stage,
                'duration': duration,
                'completed_at': time.time()
            }
            
            self.stage_history.append(stage_record)
            logger.debug(f"阶段完成: {self.current_stage.value} - 耗时 {duration:.2f}s")
    
    def _generate_final_report(self, total_duration: float, success: bool, errors: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """生成最终报告"""
        return {
            'success': success,
            'total_duration': total_duration,
            'metrics': self.metrics.copy(),
            'stage_history': self.stage_history.copy(),
            'performance': {
                'rows_per_second': self.metrics['processed_rows'] / total_duration if total_duration > 0 else 0,
                'success_rate': (self.metrics['success_rows'] / self.metrics['processed_rows']) * 100 if self.metrics['processed_rows'] > 0 else 0,
                'average_stage_duration': sum(s['duration'] for s in self.stage_history) / len(self.stage_history) if self.stage_history else 0
            },
            'errors': errors or []
        }
    
    def get_current_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        current_time = time.time()
        
        status = {
            'current_stage': self.current_stage.value if self.current_stage else None,
            'metrics': self.metrics.copy(),
            'elapsed_time': current_time - self.total_start_time if self.total_start_time else 0,
            'stage_elapsed_time': current_time - self.stage_start_time if self.stage_start_time else 0
        }
        
        if self.current_stage:
            config = self.STAGE_CONFIGS.get(self.current_stage, {})
            status['stage_info'] = {
                'name': config.get('name', ''),
                'description': config.get('description', ''),
                'icon': config.get('icon', ''),
                'estimated_duration': config.get('estimated_duration', 0)
            }
        
        return status
