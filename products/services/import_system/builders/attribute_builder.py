"""
属性构建器
负责创建和管理产品属性及属性值
"""

import logging
from typing import Dict, List, Any, Optional
from django.db import transaction

from .. import ProcessingContext, ProcessingStage, ProcessingStatus
from products.models import Attribute, AttributeValue

logger = logging.getLogger(__name__)


class AttributeBuilder:
    """属性构建器 - 单一职责：属性和属性值的创建管理"""

    def __init__(self):
        self.attribute_cache = {}  # 属性缓存
        self.attribute_value_cache = {}  # 属性值缓存

    def build(self, context: ProcessingContext) -> ProcessingContext:
        """构建属性和属性值"""
        try:
            context.stage = ProcessingStage.ATTRIBUTE_BUILDING
            context.status = ProcessingStatus.PROCESSING

            # 1. 准备属性数据
            attribute_data = self._prepare_attribute_data(context)

            # 2. 批量创建属性
            with transaction.atomic():
                prepared_attributes = self._batch_create_attributes(attribute_data)

            # 3. 存储到上下文
            context.prepared_attributes = prepared_attributes
            context.status = ProcessingStatus.SUCCESS

            logger.debug(f"行{context.row_number}: 属性构建完成，创建了{len(prepared_attributes.get('attributes', {}))}个属性")
            return context

        except Exception as e:
            context.status = ProcessingStatus.FAILED
            context.errors.append({
                'stage': 'attribute_building',
                'message': f'属性构建失败: {str(e)}',
                'details': str(e)
            })
            logger.error(f"行{context.row_number}: 属性构建失败: {str(e)}")
            return context

    def validate_prerequisites(self, context: ProcessingContext) -> bool:
        """验证前置条件"""
        return (
            context.processed_data is not None and
            context.status != ProcessingStatus.FAILED
        )