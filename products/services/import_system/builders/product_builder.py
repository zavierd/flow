"""
产品构建器
负责创建SPU和SKU产品数据
"""

import logging
from typing import Dict, Any
from django.db import transaction
from decimal import Decimal

from .. import ProcessingContext, ProcessingStage, ProcessingStatus
from products.models import Brand, Category, SPU, SKU

logger = logging.getLogger(__name__)


class ProductBuilder:
    """产品构建器 - 单一职责：创建产品数据"""

    def build(self, context: ProcessingContext) -> ProcessingContext:
        """构建产品 - 正确的SPU/SKU关系（一个SPU对应多个SKU）"""
        try:
            context.stage = ProcessingStage.PRODUCT_BUILDING
            context.status = ProcessingStatus.PROCESSING

            import time
            start_time = time.time()

            # 1. 创建或获取品牌
            logger.info(f"📦 行{context.row_number}: 正在创建/获取品牌信息...")
            brand = self._get_or_create_brand()

            # 2. 创建或获取分类
            logger.info(f"📂 行{context.row_number}: 正在创建/获取产品分类...")
            category = self._get_or_create_category(context.processed_data)

            # 3. 创建或获取SPU（按系列和类型分组，不包含具体规格）
            logger.info(f"🏷️ 行{context.row_number}: 正在创建标准产品单元(SPU)...")
            spu = self._get_or_create_spu(context.processed_data, brand, category)

            # 4. 创建多个SKU（根据价格等级创建多个SKU）
            logger.info(f"📋 行{context.row_number}: 正在创建库存单元(SKU)...")
            skus = self._create_skus_for_price_levels(context.processed_data, spu, brand)

            # 5. 存储创建的对象
            context.created_objects = {
                'brand': brand,
                'category': category,
                'spu': spu,
                'skus': skus,  # 注意：现在是多个SKU
                'primary_sku': skus[0] if skus else None  # 主要SKU（用于兼容性）
            }

            # 记录处理指标
            processing_time = time.time() - start_time
            context.processing_metrics['stage_durations']['product_building'] = processing_time
            context.processing_metrics['created_objects_count'] = len(context.created_objects)

            context.status = ProcessingStatus.SUCCESS
            sku_codes = [sku.code for sku in skus]
            logger.info(f"✅ 行{context.row_number}: 产品创建成功 - {len(skus)}个SKU (耗时 {processing_time:.3f}s)")
            logger.info(f"📊 创建对象: 品牌({brand.name}) → 分类({category.name}) → SPU({spu.code}) → SKUs({', '.join(sku_codes)})")
            return context

        except Exception as e:
            context.status = ProcessingStatus.FAILED
            context.errors.append({
                'stage': 'product_building',
                'message': f'产品创建失败: {str(e)}',
                'details': str(e)
            })
            logger.error(f"❌ 行{context.row_number}: 产品创建失败: {str(e)}")
            return context

    def validate_prerequisites(self, context: ProcessingContext) -> bool:
        """验证前置条件"""
        return (
            context.processed_data is not None and
            context.processed_data.get('产品编码') and
            context.processed_data.get('产品描述') and
            context.status != ProcessingStatus.FAILED
        )

    def _get_or_create_brand(self) -> Brand:
        """获取或创建品牌"""
        brand, created = Brand.objects.get_or_create(
            code='ROYANA',
            defaults={
                'name': 'ROYANA整木定制',
                'description': 'ROYANA整木定制品牌'
            }
        )
        return brand

    def _get_or_create_category(self, data: Dict[str, Any]) -> Category:
        """获取或创建分类"""
        # 简化的分类逻辑
        category_name = "整木定制产品"
        category, created = Category.objects.get_or_create(
            code='CUSTOM_WOOD',
            defaults={
                'name': category_name,
                'description': '整木定制产品分类'
            }
        )
        return category

    def _get_or_create_spu(self, data: Dict[str, Any], brand: Brand, category: Category) -> SPU:
        """获取或创建SPU - 正确的分组逻辑（一个SPU对应多个SKU）"""
        # SPU应该按系列和类型分组，不包含具体的尺寸规格
        description = data.get('产品描述', '')
        series = data.get('系列', 'DEFAULT')
        type_code = data.get('类型代码', '')

        # 生成SPU编码：系列_类型（不包含尺寸）
        spu_code = f"{series}_{type_code}"

        # 从产品描述提取SPU名称（去除具体规格信息）
        spu_name = self._extract_spu_name_from_description(description, series, type_code)

        try:
            spu = SPU.objects.get(code=spu_code)
            # 更新现有SPU的基本信息
            spu.name = spu_name
            spu.brand = brand
            spu.category = category
            spu.description = f"{series}系列 {type_code}类型产品"
            spu.is_active = True
            spu.save()

            logger.debug(f"📝 更新现有SPU: {spu_code}")
            return spu

        except SPU.DoesNotExist:
            # 创建新SPU
            spu = SPU.objects.create(
                code=spu_code,
                name=spu_name,
                brand=brand,
                category=category,
                description=f"{series}系列 {type_code}类型产品",
                is_active=True
            )

            logger.debug(f"✨ 创建新SPU: {spu_code}")
            return spu

    def _create_skus_for_price_levels(self, data: Dict[str, Any], spu: SPU, brand: Brand) -> list:
        """根据价格等级创建多个SKU - 正确逻辑：一个等级对应一个SKU"""
        from products.config.ai_data_mapping import PRICE_LEVEL_PROCESSING

        base_sku_code = data.get('产品编码', '')
        base_description = data.get('产品描述', '')
        base_remarks = data.get('备注', '')

        created_skus = []

        # 遍历所有价格等级，为每个有价格的等级创建SKU
        for level_key in PRICE_LEVEL_PROCESSING['levels']:
            # 正确的价格字段映射
            price_field_mapping = {
                '等级Ⅰ': '价格等级I',
                '等级Ⅱ': '价格等级II',
                '等级Ⅲ': '价格等级III',
                '等级Ⅳ': '价格等级IV',
                '等级Ⅴ': '价格等级V',
            }

            price_field = price_field_mapping.get(level_key)
            if not price_field:
                continue

            price_value = data.get(price_field, 0)

            if not price_value or price_value <= 0:
                continue  # 跳过没有价格的等级

            # 生成SKU编码：基础编码 + 等级后缀
            level_info = PRICE_LEVEL_PROCESSING['level_mapping'][level_key]
            sku_code = f"{base_sku_code}{level_info['suffix']}"

            # 生成SKU名称：基础名称 + 等级显示名
            sku_name = f"{base_description} ({level_info['display_name']})"

            # 创建或更新SKU
            sku = self._create_single_sku(
                sku_code=sku_code,
                sku_name=sku_name,
                price=price_value,
                level=level_key,
                spu=spu,
                brand=brand,
                description=base_remarks
            )

            if sku:
                created_skus.append(sku)
                logger.info(f"✨ 创建{level_key}SKU: {sku_code} (价格: {price_value})")

        return created_skus

    def _create_single_sku(self, sku_code: str, sku_name: str, price: float, level: str,
                          spu: SPU, brand: Brand, description: str) -> SKU:
        """创建单个SKU"""
        try:
            sku = SKU.objects.get(code=sku_code)
            # 更新现有SKU
            sku.name = sku_name
            sku.spu = spu
            sku.brand = brand
            sku.price = Decimal(str(price))
            sku.description = description
            sku.save()

            logger.debug(f"📝 更新现有SKU: {sku_code}")
            return sku

        except SKU.DoesNotExist:
            # 创建新SKU
            sku = SKU.objects.create(
                code=sku_code,
                name=sku_name,
                spu=spu,
                brand=brand,
                price=Decimal(str(price)),
                stock_quantity=0,
                min_stock=10,
                is_active=True,
                description=description
            )

            logger.debug(f"✨ 创建新SKU: {sku_code}")
            return sku

    def _extract_spu_name_from_description(self, description: str, series: str, type_code: str) -> str:
        """从产品描述提取SPU名称（去除具体规格信息）"""
        from products.config.ai_data_mapping import INTELLIGENT_ATTRIBUTE_MAPPING

        if not description:
            # 使用智能映射生成默认名称
            series_display = INTELLIGENT_ATTRIBUTE_MAPPING['系列']['mapping'].get(series, series)
            type_display = INTELLIGENT_ATTRIBUTE_MAPPING['类型代码']['mapping'].get(type_code, type_code)
            return f"{series_display} {type_display}"

        # 如果描述包含<br>，取第一行作为主要名称
        if '<br>' in description:
            main_desc = description.split('<br>')[0].strip()
        else:
            main_desc = description.strip()

        # 提取通用部分作为SPU名称（去除具体的尺寸、编码等SKU级别信息）
        if main_desc:
            # 去除常见的SKU级别信息（如具体尺寸、编码等）
            import re
            # 去除尺寸信息（如80cm、90cm等）
            cleaned_desc = re.sub(r'\d+cm', '', main_desc)
            # 去除编码信息（如N-NOVO80-1-L等）
            cleaned_desc = re.sub(r'N-[A-Z0-9-]+', '', cleaned_desc)
            # 去除多余空格
            cleaned_desc = re.sub(r'\s+', ' ', cleaned_desc).strip()

            if cleaned_desc and len(cleaned_desc) > 5:
                # 如果清理后的描述太长，截取前面部分
                if len(cleaned_desc) > 30:
                    return cleaned_desc[:30] + "..."
                return cleaned_desc

        # 默认生成SPU名称（使用智能映射）
        series_display = INTELLIGENT_ATTRIBUTE_MAPPING['系列']['mapping'].get(series, series)
        type_display = INTELLIGENT_ATTRIBUTE_MAPPING['类型代码']['mapping'].get(type_code, type_code)
        return f"{series_display} {type_display}"