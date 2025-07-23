import pandas as pd
import json
from typing import Dict, List, Any, Optional, Tuple
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal, InvalidOperation
import logging
from products.models import (
    Category, Brand, Attribute, AttributeValue, SPU, SKU,
    SPUAttribute, SKUAttributeValue, ProductsDimension, ProductsPricingRule
)
from products.models import ImportTask, ImportError, ImportTemplate
from products.utils.royana_code_parser import royana_parser


logger = logging.getLogger(__name__)


class DataImportService:
    """
    数据导入服务类
    
    负责处理Excel文件的解析、验证和导入
    """
    
    def __init__(self, task: ImportTask):
        self.task = task
        self.errors = []
        self.success_count = 0
        self.error_count = 0
        
    def process_import(self) -> Dict[str, Any]:
        """
        处理导入任务
        
        Returns:
            Dict: 导入结果统计
        """
        try:
            # 更新任务状态
            self.task.status = 'processing'
            self.task.started_at = timezone.now()
            self.task.save()
            
            # 读取Excel文件
            df = self._read_excel_file()
            if df is None:
                return self._handle_task_failure("文件读取失败")
            
            self.task.total_rows = len(df)
            self.task.save()
            
            # 根据任务类型处理数据
            if self.task.task_type == 'products':
                self._process_products_data(df)
            elif self.task.task_type == 'categories':
                self._process_categories_data(df)
            elif self.task.task_type == 'brands':
                self._process_brands_data(df)
            elif self.task.task_type == 'attributes':
                self._process_attributes_data(df)
            elif self.task.task_type == 'mixed':
                self._process_mixed_data(df)
            
            # 完成任务
            self._complete_task()
            
            return {
                'success': True,
                'total_rows': self.task.total_rows,
                'success_rows': self.success_count,
                'error_rows': self.error_count,
                'errors': self.errors
            }
            
        except Exception as e:
            logger.error(f"导入任务失败: {str(e)}")
            return self._handle_task_failure(str(e))
    
    def _read_excel_file(self) -> Optional[pd.DataFrame]:
        """读取Excel文件"""
        try:
            # 支持多种Excel格式
            file_path = self.task.file_path.path
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path, engine='openpyxl')
            elif file_path.endswith('.xls'):
                df = pd.read_excel(file_path, engine='xlrd')
            else:
                df = pd.read_csv(file_path, encoding='utf-8')
            
            # 清理数据
            df = df.dropna(how='all')  # 删除完全空白的行
            df = df.fillna('')  # 填充空值
            
            return df
            
        except Exception as e:
            logger.error(f"文件读取失败: {str(e)}")
            return None
    
    def _process_products_data(self, df: pd.DataFrame):
        """处理产品数据导入"""
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    # 检查是否是Royana产品编码格式
                    code = str(row.get('code', '')).strip()
                    if code.startswith('N-'):
                        self._import_royana_product_row(row, index + 2)
                    else:
                        self._import_product_row(row, index + 2)  # 原有逻辑
                    self.success_count += 1

            except Exception as e:
                self._add_error(index + 2, 'system', '', str(e), row.to_dict())
                self.error_count += 1

            # 更新进度
            self.task.update_progress(
                index + 1,
                self.success_count,
                self.error_count
            )
    




    
    def _map_dimension_type(self, dim_type: str) -> str:
        """映射尺寸类型"""
        mapping = {
            '高度': 'height',
            '宽度': 'width',
            '厚度': 'depth',
            '深度': 'depth',
            '长度': 'length',
            '直径': 'diameter',
            '重量': 'weight',
            'height': 'height',
            'width': 'width',
            'depth': 'depth',
            'length': 'length',
            'diameter': 'diameter',
            'weight': 'weight',
        }
        return mapping.get(dim_type, 'custom')
    
    def _safe_decimal(self, value: Any) -> Optional[Decimal]:
        """安全转换为Decimal"""
        if not value or str(value).strip() == '':
            return None
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError):
            return None
    
    def _safe_bool(self, value: Any) -> bool:
        """安全转换为布尔值"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', '是', '1', 'yes']
        return bool(value)
    
    def _add_error(self, row_num: int, error_type: str, field: str, message: str, data: Dict):
        """添加错误记录"""
        error = ImportError.objects.create(
            task=self.task,
            row_number=row_num,
            error_type=error_type,
            field_name=field,
            error_message=message,
            raw_data=data
        )
        self.errors.append({
            'row': row_num,
            'field': field,
            'message': message,
            'data': data
        })
    
    def _complete_task(self):
        """完成任务"""
        self.task.status = 'completed' if self.error_count == 0 else 'partial'
        self.task.completed_at = timezone.now()
        self.task.success_rows = self.success_count
        self.task.error_rows = self.error_count
        self.task.result_summary = {
            'total_rows': self.task.total_rows,
            'success_rows': self.success_count,
            'error_rows': self.error_count,
            'success_rate': (self.success_count / self.task.total_rows) * 100 if self.task.total_rows > 0 else 0
        }
        self.task.save()
    
    def _handle_task_failure(self, error_message: str) -> Dict[str, Any]:
        """处理任务失败"""
        self.task.status = 'failed'
        self.task.completed_at = timezone.now()
        self.task.error_details = error_message
        self.task.save()
        
        return {
            'success': False,
            'error': error_message,
            'total_rows': self.task.total_rows,
            'success_rows': self.success_count,
            'error_rows': self.error_count
        }
    


    def _import_royana_product_row(self, row: pd.Series, row_number: int):
        """
        导入Royana产品行数据
        基于产品编码智能解析并创建完整的产品信息
        """
        # 获取基础数据
        code = str(row.get('code', '')).strip()
        description = str(row.get('description', '')).strip()
        name = str(row.get('name', '')).strip()

        # 验证必填字段
        if not code:
            raise ValidationError("产品编码不能为空")
        if not description:
            raise ValidationError("产品描述不能为空")

        # 处理价格信息（多级价格体系）
        price_level_2 = self._parse_decimal(row.get('price_level_2', 0))
        price_level_3 = self._parse_decimal(row.get('price_level_3', 0))
        price_level_4 = self._parse_decimal(row.get('price_level_4', 0))
        price_level_5 = self._parse_decimal(row.get('price_level_5', 0))
        default_price = self._parse_decimal(row.get('price', 0))

        # 确定销售价格（优先级：默认价格 > 价格等级III > 价格等级II）
        if default_price > 0:
            price = default_price
        elif price_level_3 > 0:
            price = price_level_3
        elif price_level_2 > 0:
            price = price_level_2
        else:
            raise ValidationError("必须提供至少一个有效的价格")

        # 尝试解析产品编码（如果解析失败，使用手动填写的信息）
        parsed_info = None
        if code.startswith('N-'):
            # 处理编码中的 L/R 后缀
            clean_code = code.replace('/R', '').replace('-L/R', '-L')
            parsed_info = royana_parser.parse_code(clean_code)

        # 获取产品信息（优先使用手动填写，其次使用解析结果）
        brand_code = str(row.get('brand_code', '')).strip() or (parsed_info.brand_code if parsed_info else 'ROYANA')
        series = str(row.get('series', '')).strip() or (parsed_info.series if parsed_info else 'NOVO')
        cabinet_type = str(row.get('cabinet_type', '')).strip() or (parsed_info.cabinet_type if parsed_info else '底柜')

        # 尺寸信息
        width = int(row.get('width', 0)) or (parsed_info.width if parsed_info else 0)
        height = int(row.get('height', 0)) or (parsed_info.height if parsed_info else 72)
        depth = int(row.get('depth', 0)) or (parsed_info.depth if parsed_info else 56)

        # 门板和抽屉信息
        door_count = int(row.get('door_count', 0)) or 1
        drawer_count = int(row.get('drawer_count', 0)) or 0
        drawer_type = str(row.get('drawer_type', '')).strip() or '无'
        door_direction = str(row.get('door_direction', '')).strip() or ''

        # 分类信息
        main_category = str(row.get('main_category', '')).strip() or '底柜'
        sub_category = str(row.get('sub_category', '')).strip() or '单门'

        # 生成产品名称（如果未提供）
        if not name:
            name = self._generate_product_name(cabinet_type, width, door_direction)

        # 创建或获取品牌
        brand = self._get_or_create_brand(
            code=brand_code,
            name=brand_code,
            description=f"{brand_code}品牌产品"
        )

        # 创建或获取分类
        category_code = f"{main_category}_{sub_category}".upper()
        category = self._get_or_create_category(
            code=category_code,
            name=f"{main_category}-{sub_category}",
            description=f"{main_category}类产品，{sub_category}配置"
        )

        # 创建或获取SPU
        spu_code = f"{series}_{cabinet_type}_{width}CM"
        spu = self._get_or_create_spu(
            code=spu_code,
            name=f"{series}系列{cabinet_type}{width}cm",
            category=category,
            brand=brand,
            description=description
        )

        # 创建SKU
        sku_data = {
            'code': code,
            'name': name,
            'spu': spu,
            'brand': brand,
            'price': price,
            'cost_price': self._parse_decimal(row.get('cost_price')),
            'market_price': self._parse_decimal(row.get('market_price')),
            'stock_quantity': int(row.get('stock_quantity', 0)),
            'min_stock': int(row.get('min_stock', 10)),
            'description': description,
            'specifications': str(row.get('specifications', '')),
            'usage_scenario': str(row.get('usage_scenario', '')),
            'status': str(row.get('status', 'active')),
            'remarks': str(row.get('remarks', '')),
        }

        sku = self._create_sku(sku_data)

        # 创建SKU属性值
        self._create_sku_attributes_enhanced(sku, {
            'width': width,
            'height': height,
            'depth': depth,
            'cabinet_type': cabinet_type,
            'door_count': door_count,
            'drawer_count': drawer_count,
            'drawer_type': drawer_type,
            'door_direction': door_direction,
            'price_level_2': price_level_2,
            'price_level_3': price_level_3,
            'price_level_4': price_level_4,
            'price_level_5': price_level_5,
            'english_name': str(row.get('english_name', '')),
            'accessories': str(row.get('accessories', '')),
            'installation_notes': str(row.get('installation_notes', '')),
            'features': str(row.get('features', '')),
        })

        logger.info(f"成功导入Royana产品: {code} - {name}")

    def _get_or_create_brand(self, code: str, name: str, description: str = '') -> Brand:
        """获取或创建品牌"""
        brand, created = Brand.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'description': description,
                'order': 0
            }
        )
        if created:
            logger.info(f"创建新品牌: {code} - {name}")
        return brand

    def _get_or_create_category(self, code: str, name: str, description: str = '') -> Category:
        """获取或创建分类"""
        category, created = Category.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'description': description,
                'level': 1,
                'parent': None
            }
        )
        if created:
            logger.info(f"创建新分类: {code} - {name}")
        return category

    def _generate_product_name(self, cabinet_type: str, width: int, door_direction: str = '') -> str:
        """生成产品名称"""
        name_parts = ['NOVO系列', cabinet_type, f'{width}cm']
        if door_direction and door_direction not in ['无门板', '双开']:
            name_parts.append(door_direction)
        return ''.join(name_parts)

    def _get_or_create_spu(self, code: str, name: str, category: Category,
                          brand: Brand, description: str = '') -> SPU:
        """获取或创建SPU"""
        spu, created = SPU.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'category': category,
                'brand': brand,
                'description': description or f"NOVO系列产品",
                'specifications': f"整木定制产品",
                'usage_scenario': f"适用于家居储物需求",
                'order': 0
            }
        )
        if created:
            logger.info(f"创建新SPU: {code} - {name}")
            # 为SPU创建标准属性
            self._create_spu_attributes_enhanced(spu)
        return spu

    def _create_sku(self, sku_data: Dict[str, Any]) -> SKU:
        """创建SKU"""
        sku = SKU.objects.create(**sku_data)
        logger.info(f"创建新SKU: {sku.code} - {sku.name}")
        return sku

    def _create_spu_attributes_enhanced(self, spu: SPU):
        """为SPU创建增强的标准属性"""
        # 创建或获取标准属性
        attributes_data = [
            ('WIDTH', '宽度', 'number', 'cm'),
            ('HEIGHT', '高度', 'number', 'cm'),
            ('DEPTH', '深度', 'number', 'cm'),
            ('CABINET_TYPE', '柜体类型', 'select', ''),
            ('DOOR_COUNT', '门板数量', 'number', '个'),
            ('DRAWER_COUNT', '抽屉数量', 'number', '个'),
            ('DRAWER_TYPE', '抽屉类型', 'select', ''),
            ('DOOR_DIRECTION', '门板方向', 'select', ''),
            ('PRICE_LEVEL_2', '价格等级II', 'number', '元'),
            ('PRICE_LEVEL_3', '价格等级III', 'number', '元'),
            ('PRICE_LEVEL_4', '价格等级IV', 'number', '元'),
            ('PRICE_LEVEL_5', '价格等级V', 'number', '元'),
        ]

        for attr_code, attr_name, attr_type, unit in attributes_data:
            attribute, created = Attribute.objects.get_or_create(
                code=attr_code,
                defaults={
                    'name': attr_name,
                    'type': attr_type,
                    'unit': unit,
                    'description': f"{attr_name}属性",
                    'order': 0
                }
            )

            # 创建SPU属性关联
            SPUAttribute.objects.get_or_create(
                spu=spu,
                attribute=attribute,
                defaults={
                    'is_required': attr_code in ['WIDTH', 'HEIGHT', 'DEPTH', 'CABINET_TYPE'],
                    'order': 0
                }
            )

    def _create_spu_attributes(self, spu: SPU, parsed_info):
        """为SPU创建标准属性"""
        # 创建或获取标准属性
        attributes_data = [
            ('WIDTH', '宽度', 'number', 'cm'),
            ('HEIGHT', '高度', 'number', 'cm'),
            ('DEPTH', '深度', 'number', 'cm'),
            ('CABINET_TYPE', '柜体类型', 'select', ''),
            ('DRAWER_CONFIG', '抽屉配置', 'select', ''),
        ]

        if parsed_info.door_direction:
            attributes_data.append(('DOOR_DIRECTION', '门板方向', 'select', ''))

        for attr_code, attr_name, attr_type, unit in attributes_data:
            attribute, created = Attribute.objects.get_or_create(
                code=attr_code,
                defaults={
                    'name': attr_name,
                    'type': attr_type,
                    'unit': unit,
                    'description': f"{attr_name}属性",
                    'order': 0
                }
            )

            # 创建SPU属性关联
            SPUAttribute.objects.get_or_create(
                spu=spu,
                attribute=attribute,
                defaults={
                    'is_required': True,
                    'order': 0
                }
            )

    def _create_sku_attributes(self, sku: SKU, parsed_info, row: pd.Series):
        """创建SKU属性值"""
        # 基础尺寸属性
        attribute_values = [
            ('WIDTH', str(parsed_info.width)),
            ('HEIGHT', str(parsed_info.height)),
            ('DEPTH', str(parsed_info.depth)),
            ('CABINET_TYPE', parsed_info.cabinet_type),
            ('DRAWER_CONFIG', parsed_info.drawer_config),
        ]

        if parsed_info.door_direction:
            attribute_values.append(('DOOR_DIRECTION', parsed_info.door_direction))

        for attr_code, value in attribute_values:
            try:
                attribute = Attribute.objects.get(code=attr_code)

                # 创建或获取属性值
                if attribute.type in ['select', 'multiselect']:
                    attr_value, created = AttributeValue.objects.get_or_create(
                        attribute=attribute,
                        value=value,
                        defaults={'display_name': value}
                    )

                    # 创建SKU属性值关联
                    SKUAttributeValue.objects.get_or_create(
                        sku=sku,
                        attribute=attribute,
                        defaults={'attribute_value': attr_value}
                    )
                else:
                    # 直接存储自定义值
                    SKUAttributeValue.objects.get_or_create(
                        sku=sku,
                        attribute=attribute,
                        defaults={'custom_value': value}
                    )

            except Attribute.DoesNotExist:
                logger.warning(f"属性 {attr_code} 不存在，跳过")
                continue

    def _create_sku_attributes_enhanced(self, sku: SKU, attributes_data: dict):
        """创建增强的SKU属性值"""
        # 属性映射
        attribute_mapping = {
            'width': ('WIDTH', 'width'),
            'height': ('HEIGHT', 'height'),
            'depth': ('DEPTH', 'depth'),
            'cabinet_type': ('CABINET_TYPE', 'cabinet_type'),
            'door_count': ('DOOR_COUNT', 'door_count'),
            'drawer_count': ('DRAWER_COUNT', 'drawer_count'),
            'drawer_type': ('DRAWER_TYPE', 'drawer_type'),
            'door_direction': ('DOOR_DIRECTION', 'door_direction'),
            'price_level_2': ('PRICE_LEVEL_2', 'price_level_2'),
            'price_level_3': ('PRICE_LEVEL_3', 'price_level_3'),
            'price_level_4': ('PRICE_LEVEL_4', 'price_level_4'),
            'price_level_5': ('PRICE_LEVEL_5', 'price_level_5'),
        }

        for data_key, (attr_code, _) in attribute_mapping.items():
            value = attributes_data.get(data_key)
            if value is None or value == '':
                continue

            try:
                attribute = Attribute.objects.get(code=attr_code)

                # 创建或获取属性值
                if attribute.type in ['select', 'multiselect'] and str(value).strip():
                    attr_value, created = AttributeValue.objects.get_or_create(
                        attribute=attribute,
                        value=str(value),
                        defaults={'display_name': str(value)}
                    )

                    # 创建SKU属性值关联
                    SKUAttributeValue.objects.get_or_create(
                        sku=sku,
                        attribute=attribute,
                        defaults={'attribute_value': attr_value}
                    )
                elif str(value).strip():
                    # 直接存储自定义值
                    SKUAttributeValue.objects.get_or_create(
                        sku=sku,
                        attribute=attribute,
                        defaults={'custom_value': str(value)}
                    )

            except Attribute.DoesNotExist:
                logger.warning(f"属性 {attr_code} 不存在，跳过")
                continue

    def _parse_decimal(self, value) -> Decimal:
        """解析十进制数值"""
        if value is None or value == '':
            return Decimal('0.00')

        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return Decimal('0.00')