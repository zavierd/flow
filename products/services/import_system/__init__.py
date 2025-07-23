"""
模块化导入系统

设计原则：
1. 单一职责 - 每个模块只负责一个特定功能
2. 依赖倒置 - 高层模块不依赖低层模块
3. 开闭原则 - 对扩展开放，对修改封闭
4. 接口隔离 - 使用小而专一的接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Protocol
from dataclasses import dataclass
from enum import Enum


class ProcessingStage(Enum):
    """处理阶段枚举"""
    INITIALIZING = "initializing"
    PREPROCESSING = "preprocessing"
    VALIDATION = "validation"
    QUALITY_CHECK = "quality_check"
    AI_ENHANCEMENT = "ai_enhancement"
    ATTRIBUTE_BUILDING = "attribute_building"
    PRODUCT_BUILDING = "product_building"
    RELATION_BUILDING = "relation_building"
    FINALIZING = "finalizing"


class ProcessingStatus(Enum):
    """处理状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StageInfo:
    """阶段信息"""
    stage: ProcessingStage
    name: str
    description: str
    icon: str
    estimated_duration: float = 0.0
    actual_duration: float = 0.0
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


@dataclass
class ProcessingContext:
    """处理上下文 - 在各个模块间传递的数据结构"""
    row_number: int
    original_data: Dict[str, Any]
    processed_data: Dict[str, Any] = None
    quality_issues: List[Dict[str, Any]] = None
    ai_enhancements: Dict[str, Any] = None
    prepared_attributes: Dict[str, Any] = None
    created_objects: Dict[str, Any] = None
    errors: List[Dict[str, Any]] = None
    stage: ProcessingStage = ProcessingStage.PREPROCESSING
    status: ProcessingStatus = ProcessingStatus.PENDING
    stage_info: StageInfo = None
    processing_metrics: Dict[str, Any] = None

    def __post_init__(self):
        if self.processed_data is None:
            self.processed_data = {}
        if self.quality_issues is None:
            self.quality_issues = []
        if self.ai_enhancements is None:
            self.ai_enhancements = {}
        if self.prepared_attributes is None:
            self.prepared_attributes = {}
        if self.created_objects is None:
            self.created_objects = {}
        if self.errors is None:
            self.errors = []
        if self.processing_metrics is None:
            self.processing_metrics = {
                'start_time': None,
                'stage_durations': {},
                'data_size': 0,
                'processed_fields': 0,
                'created_objects_count': 0
            }


@dataclass
class ImportResult:
    """导入结果"""
    success: bool
    total_rows: int
    success_rows: int
    error_rows: int
    errors: List[Dict[str, Any]]
    created_objects: Dict[str, Any] = None

    def __post_init__(self):
        if self.created_objects is None:
            self.created_objects = {}


class Processor(Protocol):
    """处理器接口"""

    def process(self, context: ProcessingContext) -> ProcessingContext:
        """处理数据"""
        ...

    def can_process(self, context: ProcessingContext) -> bool:
        """判断是否可以处理"""
        ...


class Builder(Protocol):
    """构建器接口"""

    def build(self, context: ProcessingContext) -> ProcessingContext:
        """构建对象"""
        ...

    def validate_prerequisites(self, context: ProcessingContext) -> bool:
        """验证前置条件"""
        ...


class Validator(Protocol):
    """验证器接口"""

    def validate(self, context: ProcessingContext) -> List[Dict[str, Any]]:
        """验证数据"""
        ...


# 导出主要类和接口
__all__ = [
    'ProcessingStage',
    'ProcessingStatus',
    'ProcessingContext',
    'ImportResult',
    'Processor',
    'Builder',
    'Validator'
]