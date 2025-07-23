"""
关系构建器
负责创建产品属性关联关系
"""

import logging
from typing import Dict, Any

from .. import ProcessingContext, ProcessingStage, ProcessingStatus
from products.models import Attribute, AttributeValue, SKUAttributeValue, SPUAttribute

logger = logging.getLogger(__name__)


class RelationBuilder:
    """关系构建器 - 单一职责：创建属性关联关系"""

    def build(self, context: ProcessingContext) -> ProcessingContext:
        """构建关系 - 处理多个SKU的属性关联"""
        try:
            context.stage = ProcessingStage.RELATION_BUILDING
            context.status = ProcessingStatus.PROCESSING

            import time
            start_time = time.time()

            # 获取创建的对象（现在是多个SKU）
            skus = context.created_objects.get('skus', [])
            spu = context.created_objects.get('spu')

            if not skus or not spu:
                raise ValueError("缺少必要的产品对象")

            # 为每个SKU创建属性关联
            logger.info(f"🔗 行{context.row_number}: 正在建立产品属性关联关系...")
            total_attributes_created = 0

            for sku in skus:
                attributes_created = self._create_attributes_for_sku(context, sku, spu)
                total_attributes_created += attributes_created
                logger.debug(f"🏷️ SKU {sku.code}: 创建属性 {attributes_created}个")

            # 智能属性处理（处理未定义的属性）
            logger.error(f"🤖 行{context.row_number}: 启动智能属性识别和处理...")  # 临时改为ERROR确保能看到
            try:
                smart_attributes_created = self._process_smart_attributes(context)
                total_attributes_created += smart_attributes_created
                logger.error(f"🤖 行{context.row_number}: 智能属性处理完成，创建 {smart_attributes_created} 个属性")
            except Exception as e:
                logger.error(f"❌ 行{context.row_number}: 智能属性处理异常: {str(e)}")
                import traceback
                logger.error(f"详细错误: {traceback.format_exc()}")

            # 记录处理指标
            processing_time = time.time() - start_time
            context.processing_metrics['stage_durations']['relation_building'] = processing_time

            context.status = ProcessingStatus.SUCCESS
            logger.info(f"✅ 行{context.row_number}: 关系构建完成 (耗时 {processing_time:.3f}s, 创建属性 {total_attributes_created}个)")
            return context

        except Exception as e:
            context.status = ProcessingStatus.FAILED
            context.errors.append({
                'stage': 'relation_building',
                'message': f'关系构建失败: {str(e)}',
                'details': str(e)
            })
            logger.error(f"❌ 行{context.row_number}: 关系构建失败: {str(e)}")
            return context

    def validate_prerequisites(self, context: ProcessingContext) -> bool:
        """验证前置条件"""
        return (
            context.created_objects and
            (context.created_objects.get('skus') or context.created_objects.get('sku')) and  # 支持单个或多个SKU
            context.created_objects.get('spu') and
            context.status != ProcessingStatus.FAILED
        )

    def _create_attributes_for_sku(self, context: ProcessingContext, sku, spu) -> int:
        """为单个SKU创建属性 - 智能处理属性值"""
        data = context.processed_data
        attributes_created = 0

        # 导入配置中定义的所有产品属性字段
        from products.config.ai_data_mapping import PRODUCT_STRUCTURE_MAPPING
        attribute_fields = PRODUCT_STRUCTURE_MAPPING['attribute_fields']

        # 处理所有属性字段
        for attr_name in attribute_fields:
            # 特殊处理等级属性
            if attr_name == '等级':
                # 从SKU编码中提取等级信息
                level = self._extract_level_from_sku(sku)
                if level:
                    success = self._create_intelligent_attribute_relation(sku, spu, attr_name, level, data)
                    if success:
                        attributes_created += 1
                continue

            attr_value = data.get(attr_name)

            # 跳过空值和无效值
            if not attr_value or str(attr_value).strip() in ['', '0', '0.0']:
                continue

            # 使用智能属性处理
            success = self._create_intelligent_attribute_relation(sku, spu, attr_name, str(attr_value), data)
            if success:
                attributes_created += 1
                logger.debug(f"🏷️ 创建属性: {attr_name} = {attr_value}")

        return attributes_created

    def _extract_level_from_sku(self, sku) -> str:
        """从SKU编码中提取等级信息"""
        from products.config.ai_data_mapping import PRICE_LEVEL_PROCESSING

        # 根据SKU编码后缀判断等级
        for level, info in PRICE_LEVEL_PROCESSING['level_mapping'].items():
            if sku.code.endswith(info['suffix']):
                return level

        return None

    def _create_attribute_relation(self, sku, spu, attr_name: str, attr_value: str) -> bool:
        """创建属性关联"""
        try:
            # 生成属性编码
            attr_code = self._generate_attribute_code(attr_name)

            # 创建或获取属性
            attribute, created = Attribute.objects.get_or_create(
                code=attr_code,
                defaults={
                    'name': attr_name,
                    'type': self._determine_attribute_type(attr_value),
                    'is_required': False,
                    'is_filterable': attr_name in ['开门方向', '产品系列']
                }
            )

            # 创建或获取属性值
            attribute_value, created = AttributeValue.objects.get_or_create(
                attribute=attribute,
                value=attr_value,
                defaults={'display_name': attr_value}
            )

            # 创建或更新SKU属性值关联
            sku_attr_value, created = SKUAttributeValue.objects.get_or_create(
                sku=sku,
                attribute=attribute,
                defaults={'attribute_value': attribute_value}
            )

            # 如果已存在但值不同，更新属性值
            if not created and sku_attr_value.attribute_value != attribute_value:
                sku_attr_value.attribute_value = attribute_value
                sku_attr_value.save()
                logger.debug(f"📝 更新SKU属性值: {attr_name} = {attr_value}")

            # 创建SPU属性关联
            SPUAttribute.objects.get_or_create(
                spu=spu,
                attribute=attribute,
                defaults={
                    'is_required': False,
                    'order': self._get_attribute_order(attr_code)
                }
            )

            return True

        except Exception as e:
            logger.warning(f"创建属性关联失败 {attr_name}={attr_value}: {str(e)}")
            return False

    def _process_smart_attributes(self, context: ProcessingContext) -> int:
        """处理智能属性识别和映射"""
        try:
            logger.info(f"🔍 开始智能属性处理，当前数据字段: {list(context.processed_data.keys())}")

            # 导入智能属性处理器
            from ..processors.smart_attribute_processor import get_smart_attribute_processor

            # 获取智能属性处理器实例
            smart_processor = get_smart_attribute_processor()
            logger.info(f"🤖 智能属性处理器状态: 启用={smart_processor.enabled}")

            # 检查是否可以处理
            if not smart_processor.can_process(context):
                logger.warning("智能属性处理器不可用或不适用于当前上下文")
                logger.info(f"处理器状态: enabled={smart_processor.enabled}, data={context.processed_data is not None}, objects={context.created_objects is not None}")
                return 0

            # 处理智能属性
            logger.info("🚀 开始执行智能属性处理...")
            context = smart_processor.process(context)

            # 获取处理结果
            if 'smart_attributes' in context.processing_metrics:
                mapped_count = context.processing_metrics['smart_attributes'].get('mapped_count', 0)
                logger.info(f"🤖 智能属性处理完成: 映射 {mapped_count} 个属性")
                return mapped_count
            else:
                logger.warning("智能属性处理完成，但未找到处理结果")
                return 0

        except Exception as e:
            logger.error(f"智能属性处理失败: {str(e)}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")
            return 0

    def _create_intelligent_attribute_relation(self, sku, spu, attr_name: str, attr_value: str, context_data: dict) -> bool:
        """创建智能属性关联 - AI智能处理字母代码"""
        try:
            from products.config.ai_data_mapping import INTELLIGENT_ATTRIBUTE_MAPPING, PRICE_LEVEL_PROCESSING

            # 获取智能映射配置
            if attr_name in INTELLIGENT_ATTRIBUTE_MAPPING:
                mapping_config = INTELLIGENT_ATTRIBUTE_MAPPING[attr_name]

                # 使用智能映射转换属性名和值
                display_attr_name = mapping_config['display_name']
                display_attr_value = mapping_config['mapping'].get(attr_value, attr_value)

                # 应用上下文规则（如根据系列信息进一步细化）
                if 'context_rules' in mapping_config:
                    series = context_data.get('系列', '')
                    if series in mapping_config['context_rules']:
                        context_rule = mapping_config['context_rules'][series]
                        if 'prefix' in context_rule:
                            display_attr_value = f"{context_rule['prefix']} {display_attr_value}"

                # 创建属性关联
                return self._create_attribute_relation(sku, spu, display_attr_name, display_attr_value)

            # 特殊处理等级属性
            elif attr_name == '等级':
                level_config = PRICE_LEVEL_PROCESSING['attribute_definition']
                display_attr_name = level_config['display_name']

                # 等级值直接使用（如等级Ⅰ、等级Ⅱ等）
                return self._create_attribute_relation(sku, spu, display_attr_name, attr_value)

            # 默认处理（直接使用原始值）
            else:
                return self._create_attribute_relation(sku, spu, attr_name, attr_value)

        except Exception as e:
            logger.warning(f"智能属性处理失败 {attr_name}={attr_value}: {str(e)}")
            # 降级到普通处理
            return self._create_attribute_relation(sku, spu, attr_name, attr_value)

    def _generate_attribute_code(self, attr_name: str) -> str:
        """生成属性编码"""
        code_mapping = {
            '宽度': 'WIDTH',
            '高度': 'HEIGHT',
            '深度': 'DEPTH',
            '开门方向': 'DOOR_DIRECTION',
            '产品系列': 'PRODUCT_SERIES',
            '价格等级1': 'PRICE_LEVEL_1',
            '价格等级2': 'PRICE_LEVEL_2',
            '价格等级3': 'PRICE_LEVEL_3',
            '价格等级4': 'PRICE_LEVEL_4',
            '价格等级5': 'PRICE_LEVEL_5',
        }

        return code_mapping.get(attr_name, attr_name.upper().replace(' ', '_'))

    def _determine_attribute_type(self, value: str) -> str:
        """判断属性类型"""
        if value.replace('.', '').replace('-', '').isdigit():
            return 'number'
        elif len(value) < 20:
            return 'select'
        else:
            return 'text'

    def _get_attribute_order(self, attr_code: str) -> int:
        """获取属性显示顺序"""
        order_mapping = {
            'WIDTH': 1,
            'HEIGHT': 2,
            'DEPTH': 3,
            'DOOR_DIRECTION': 4,
            'PRODUCT_SERIES': 5,
            'PRICE_LEVEL_1': 6,
            'PRICE_LEVEL_2': 7,
            'PRICE_LEVEL_3': 8,
            'PRICE_LEVEL_4': 9,
            'PRICE_LEVEL_5': 10,
        }

        return order_mapping.get(attr_code, 99)