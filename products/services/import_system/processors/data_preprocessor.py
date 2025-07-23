"""
数据预处理器
负责原始数据的清理、标准化和格式转换
"""

import logging
from typing import Dict, Any
from decimal import Decimal, InvalidOperation

from .. import ProcessingContext, ProcessingStage, ProcessingStatus
from ..utils.field_mapper import FieldMapper
from products.config.ai_data_mapping import AI_DATA_FIELD_MAPPING

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """数据预处理器 - 单一职责：数据清理和标准化"""

    def __init__(self):
        self.field_mapper = FieldMapper(AI_DATA_FIELD_MAPPING)

    def process(self, context: ProcessingContext) -> ProcessingContext:
        """处理数据预处理"""
        try:
            context.stage = ProcessingStage.PREPROCESSING
            context.status = ProcessingStatus.PROCESSING

            # 记录开始时间
            import time
            start_time = time.time()
            context.processing_metrics['start_time'] = start_time

            # 1. 字段映射
            logger.info(f"🔧 行{context.row_number}: 开始字段映射和数据标准化...")
            mapped_data = self.field_mapper.map_fields(context.original_data)

            # 2. 数据清理
            logger.info(f"🧹 行{context.row_number}: 执行数据清理和格式规范化...")
            cleaned_data = self._clean_data(mapped_data)

            # 3. 数据类型转换
            logger.info(f"🔄 行{context.row_number}: 进行数据类型转换和验证...")
            converted_data = self._convert_data_types(cleaned_data)

            # 4. 数据验证
            logger.info(f"✅ 行{context.row_number}: 执行业务规则验证...")
            validated_data = self._validate_basic_data(converted_data)

            context.processed_data = validated_data
            context.status = ProcessingStatus.SUCCESS

            # 记录处理指标
            processing_time = time.time() - start_time
            context.processing_metrics['stage_durations']['preprocessing'] = processing_time
            context.processing_metrics['data_size'] = len(str(context.original_data))
            context.processing_metrics['processed_fields'] = len(validated_data)

            logger.info(f"✅ 行{context.row_number}: 数据预处理完成 (耗时 {processing_time:.3f}s, 处理字段 {len(validated_data)}个)")
            return context

        except Exception as e:
            context.status = ProcessingStatus.FAILED
            context.errors.append({
                'stage': 'preprocessing',
                'message': f'数据预处理失败: {str(e)}',
                'details': str(e)
            })
            logger.error(f"❌ 行{context.row_number}: 数据预处理失败: {str(e)}")
            return context

    def can_process(self, context: ProcessingContext) -> bool:
        """判断是否可以处理"""
        return (
            context.original_data is not None and
            len(context.original_data) > 0 and
            context.status != ProcessingStatus.FAILED
        )

    def _clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """清理数据 - 严格按照原始AI数据处理逻辑"""
        cleaned = {}

        for key, value in data.items():
            if value is None:
                cleaned[key] = ''
            elif isinstance(value, str):
                # 清理字符串：去除首尾空格
                cleaned_value = value.strip()

                # 处理产品描述：分离中英文和规格信息
                if key == '产品描述':
                    cleaned_value = self._process_description(cleaned_value)

                # 处理价格字段：去除逗号，转换数字
                elif key in ['价格等级I', '价格等级II', '价格等级III', '价格等级IV', '价格等级V']:
                    cleaned_value = self._process_price_string(cleaned_value)

                # 处理尺寸字段：确保为数字
                elif key in ['宽度', '高度', '深度']:
                    cleaned_value = self._process_dimension_string(cleaned_value)

                # 处理门板方向：标准化
                elif key == '开门方向':
                    cleaned_value = self._process_door_swing(cleaned_value)

                # 处理备注：保持格式
                elif key == '备注':
                    cleaned_value = self._process_remarks(cleaned_value)

                # 处理空值
                elif cleaned_value in ['-', 'N/A', 'NULL', 'null']:
                    cleaned_value = ''

                cleaned[key] = cleaned_value
            else:
                cleaned[key] = value

        return cleaned

    def _convert_data_types(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """转换数据类型"""
        converted = data.copy()

        # 价格字段转换
        price_fields = ['价格等级I', '价格等级II', '价格等级III', '价格等级IV', '价格等级V']
        for field in price_fields:
            if field in converted:
                converted[field] = self._convert_to_decimal(converted[field])

        # 尺寸字段转换
        dimension_fields = ['宽度', '高度', '深度']
        for field in dimension_fields:
            if field in converted:
                converted[field] = self._convert_to_float(converted[field])

        return converted

    def _convert_to_decimal(self, value) -> Decimal:
        """转换为Decimal类型"""
        if not value or value == '':
            return Decimal('0')

        try:
            # 清理价格字符串
            price_str = str(value).replace(',', '').replace('￥', '').replace('元', '').strip()
            if not price_str or price_str == '-':
                return Decimal('0')
            return Decimal(price_str)
        except (InvalidOperation, ValueError):
            return Decimal('0')

    def _convert_to_float(self, value) -> float:
        """转换为float类型"""
        if not value or value == '':
            return 0.0

        try:
            # 清理尺寸字符串
            dim_str = str(value).replace('cm', '').replace('CM', '').strip()
            if not dim_str or dim_str == '-':
                return 0.0
            return float(dim_str)
        except (ValueError, TypeError):
            return 0.0

    def _validate_basic_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """基础数据验证"""
        validated = data.copy()

        # 必填字段检查
        required_fields = ['产品描述', '产品编码']
        for field in required_fields:
            if not validated.get(field):
                raise ValueError(f"必填字段 {field} 不能为空")

        # 数据合理性检查
        if validated.get('宽度', 0) <= 0:
            raise ValueError("产品宽度必须大于0")

        return validated

    def _process_description(self, description: str) -> str:
        """处理产品描述 - 分离中英文信息"""
        if not description:
            return ''

        # 处理<br>分隔的多行描述
        if '<br>' in description:
            lines = description.split('<br>')
            # 取第一行作为主要描述（通常是中文）
            main_desc = lines[0].strip() if lines else ''
            return main_desc

        return description.strip()

    def _process_price_string(self, price_str: str) -> str:
        """处理价格字符串 - 去除格式化字符"""
        if not price_str or price_str.strip() in ['-', '']:
            return '0'

        # 去除千位分隔符、货币符号等
        cleaned = price_str.replace(',', '').replace('￥', '').replace('元', '').strip()

        # 验证是否为有效数字
        try:
            float(cleaned)
            return cleaned
        except ValueError:
            return '0'

    def _process_dimension_string(self, dim_str: str) -> str:
        """处理尺寸字符串 - 提取数字部分"""
        if not dim_str or dim_str.strip() in ['-', '']:
            return '0'

        # 去除单位标识
        cleaned = dim_str.replace('cm', '').replace('CM', '').replace('mm', '').strip()

        # 验证是否为有效数字
        try:
            float(cleaned)
            return cleaned
        except ValueError:
            return '0'

    def _process_door_swing(self, door_swing: str) -> str:
        """处理门板方向 - 标准化表示"""
        if not door_swing:
            return ''

        # 标准化门板方向映射
        door_mapping = {
            'L/R': '左开/右开',
            'L': '左开',
            'R': '右开',
            '-': '无门板',
            '': '双开',
        }

        return door_mapping.get(door_swing.strip(), door_swing.strip())

    def _process_remarks(self, remarks: str) -> str:
        """处理备注 - 保持原始格式"""
        if not remarks:
            return ''

        # 保持<br>换行符，用于前端显示
        return remarks.strip()