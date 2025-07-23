"""
AI数据格式导入服务
使用模块化架构处理AI模型输出的15列标准化数据格式
"""

import logging
from typing import Dict, Any, Optional, List

from products.models import ImportTask

logger = logging.getLogger(__name__)


class AIDataImportService:
    """
    AI数据格式导入服务
    专门处理AI模型输出的15列标准化数据格式
    """
    
    def __init__(self, task: ImportTask):
        self.task = task
        self.errors = []
        self.success_count = 0
        self.error_count = 0
        self.ai_quality_service = None
        self.smart_attributes_service = None

        # 初始化AI增强服务（如果启用）
        if is_quality_detection_enabled():
            try:
                from products.services.ai_enhanced.ai_quality_service import AIQualityService
                self.ai_quality_service = AIQualityService()
                logger.info("AI质量检测服务已启用")
            except ImportError as e:
                logger.warning(f"AI质量检测服务导入失败: {e}")

        if is_smart_attributes_enabled():
            try:
                from products.services.ai_enhanced.smart_attributes_service import SmartAttributesService
                self.smart_attributes_service = SmartAttributesService()
                logger.info("智能属性提取服务已启用")
            except ImportError as e:
                logger.warning(f"智能属性提取服务导入失败: {e}")
        
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
            
            # 解析CSV数据
            rows = self._parse_ai_csv_data(csv_content)
            if rows is None:
                return self._handle_task_failure("CSV数据解析失败")

            self.task.total_rows = len(rows)
            self.task.save()

            # 处理每一行数据
            for index, row in enumerate(rows):
                try:
                    with transaction.atomic():
                        # 1. 数据预处理和验证
                        processed_data = self._preprocess_row_data(row, index + 2)

                        # 2. AI质量检测（如果启用）
                        quality_result = self._run_ai_quality_check(processed_data, index + 2)

                        # 3. 智能属性提取（如果启用）
                        smart_attributes_result = self._run_smart_attributes_extraction(processed_data, index + 2)

                        # 4. 属性预创建
                        prepared_attributes = self._prepare_attributes(processed_data, smart_attributes_result, index + 2)

                        # 5. 创建产品
                        self._create_product_with_prepared_data(processed_data, prepared_attributes, index + 2)
                        self.success_count += 1

                except Exception as e:
                    self._add_error(index + 2, 'system', '', str(e), row)
                    self.error_count += 1

                # 更新进度
                self.task.update_progress(
                    index + 1,
                    self.success_count,
                    self.error_count
                )
            
            # 完成任务
            self.task.status = 'completed'
            self.task.completed_at = timezone.now()
            self.task.save()
            
            return {
                'success': True,
                'total_rows': self.task.total_rows,
                'success_rows': self.success_count,
                'error_rows': self.error_count,
                'errors': self.errors
            }
            
        except Exception as e:
            logger.error(f"AI数据导入失败: {str(e)}")
            return self._handle_task_failure(f"导入过程出错: {str(e)}")
    
    def _parse_ai_csv_data(self, csv_content: str) -> Optional[List[Dict[str, Any]]]:
        """解析AI输出的CSV数据"""
        try:
            # 使用csv模块读取CSV内容
            csv_reader = csv.DictReader(StringIO(csv_content))

            # 验证列结构
            expected_columns = [
                '产品描述 (Description)', '产品编码 (Code)', '系列 (Series)',
                '类型代码 (Type_Code)', '宽度 (Width_cm)', '高度 (Height_cm)',
                '深度 (Depth_cm)', '配置代码 (Config_Code)', '开门方向 (Door_Swing)',
                '等级Ⅰ', '等级Ⅱ', '等级Ⅲ', '等级Ⅳ', '等级Ⅴ', '备注 (Remarks)'
            ]

            # 检查列是否匹配
            if not all(col in csv_reader.fieldnames for col in expected_columns):
                missing_cols = [col for col in expected_columns if col not in csv_reader.fieldnames]
                logger.error(f"CSV缺少必要列: {missing_cols}")
                return None

            # 读取所有行并预处理数据
            rows = []
            for row in csv_reader:
                processed_row = self._preprocess_ai_data_row(row)
                rows.append(processed_row)

            return rows

        except Exception as e:
            logger.error(f"CSV解析失败: {str(e)}")
            return None
    
    def _preprocess_ai_data_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """预处理单行AI数据"""
        processed_row = row.copy()

        # 处理产品描述：提取中文部分
        processed_row['产品描述_处理'] = self._extract_chinese_description(row.get('产品描述 (Description)', ''))
        processed_row['英文名称'] = self._extract_english_name(row.get('产品描述 (Description)', ''))

        # 处理价格数据：去除逗号，转换为数字
        price_columns = ['等级Ⅰ', '等级Ⅱ', '等级Ⅲ', '等级Ⅳ', '等级Ⅴ']
        for col in price_columns:
            processed_row[col] = self._clean_price_data(row.get(col, ''))

        # 处理尺寸数据
        dimension_columns = ['宽度 (Width_cm)', '高度 (Height_cm)', '深度 (Depth_cm)']
        for col in dimension_columns:
            processed_row[col] = self._clean_dimension_data(row.get(col, ''))

        # 处理门板方向
        processed_row['门板方向_处理'] = self._map_door_swing(row.get('开门方向 (Door_Swing)', ''))

        # 处理柜体类型
        processed_row['柜体类型_处理'] = self._map_cabinet_type(row.get('类型代码 (Type_Code)', ''))

        return processed_row
    
    def _extract_chinese_description(self, description: str) -> str:
        """提取产品描述中的中文部分"""
        if not description or description == '':
            return ''

        lines = str(description).replace('<br>', '\n').split('\n')
        return lines[0].strip() if lines else ''

    def _extract_english_name(self, description: str) -> str:
        """提取产品描述中的英文名称"""
        if not description or description == '':
            return ''

        lines = str(description).replace('<br>', '\n').split('\n')
        return lines[1].strip() if len(lines) > 1 else ''

    def _clean_price_data(self, price_value) -> float:
        """清理价格数据"""
        if not price_value or price_value == '-' or price_value == '':
            return 0.0

        try:
            # 去除逗号和空格
            clean_price = str(price_value).replace(',', '').replace(' ', '')
            return float(clean_price)
        except (ValueError, TypeError):
            return 0.0

    def _clean_dimension_data(self, dimension_value) -> Optional[int]:
        """清理尺寸数据"""
        if not dimension_value or dimension_value == '-' or dimension_value == '':
            return None

        try:
            return int(float(dimension_value))
        except (ValueError, TypeError):
            return None

    def _map_door_swing(self, door_swing: str) -> str:
        """映射门板方向"""
        if not door_swing or door_swing == '-':
            return '双开'

        return DOOR_SWING_MAPPING.get(str(door_swing), '双开')

    def _map_cabinet_type(self, type_code: str) -> str:
        """映射柜体类型"""
        if not type_code:
            return '底柜'

        return CABINET_TYPE_MAPPING.get(str(type_code), '底柜')

    def _preprocess_row_data(self, row: Dict[str, Any], row_number: int) -> Dict[str, Any]:
        """预处理行数据，标准化字段名和值"""
        try:
            # 标准化字段映射
            processed_data = {}
            for original_field, standard_field in AI_DATA_FIELD_MAPPING.items():
                value = row.get(original_field, '')
                processed_data[standard_field] = value

            # 数据清理和转换
            processed_data = self._clean_and_convert_data(processed_data)

            # 添加行号用于错误追踪
            processed_data['_row_number'] = row_number
            processed_data['_original_data'] = row

            return processed_data

        except Exception as e:
            logger.error(f"行{row_number}数据预处理失败: {str(e)}")
            raise

    def _clean_and_convert_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """清理和转换数据"""
        # 清理价格数据
        for level in ['价格等级I', '价格等级II', '价格等级III', '价格等级IV', '价格等级V']:
            if level in data:
                price_str = str(data[level]).replace(',', '').replace('-', '0').strip()
                try:
                    data[level] = float(price_str) if price_str and price_str != '0' else 0
                except (ValueError, TypeError):
                    data[level] = 0

        # 清理尺寸数据
        for dimension in ['宽度', '高度', '深度']:
            if dimension in data:
                dim_str = str(data[dimension]).strip()
                try:
                    data[dimension] = float(dim_str) if dim_str and dim_str != '-' else 0
                except (ValueError, TypeError):
                    data[dimension] = 0

        # 清理文本数据
        for field in ['产品描述', '产品编码', '系列', '开门方向', '备注']:
            if field in data:
                data[field] = str(data[field]).strip()

        return data

    def _run_ai_quality_check(self, processed_data: Dict[str, Any], row_number: int) -> Optional[Dict[str, Any]]:
        """运行AI质量检测"""
        if not self.ai_quality_service:
            return None

        try:
            # 调用AI质量检测服务
            quality_result = self.ai_quality_service.process(row)

            # 记录质量检测结果
            if quality_result and quality_result.get('success'):
                # 记录质量问题
                issues = quality_result.get('issues', [])
                if issues:
                    for issue in issues:
                        self._add_quality_issue(
                            row_number=row_number,
                            field=issue.get('field', ''),
                            value=issue.get('value', ''),
                            message=issue.get('message', ''),
                            severity=issue.get('severity', 'low'),
                            row_data=row
                        )

                # 返回质量检测结果
                return quality_result

        except Exception as e:
            logger.warning(f"AI质量检测失败: {str(e)}")

        return None

    def _add_quality_issue(self, row_number: int, field: str, value: Any,
                          message: str, severity: str, row_data: Dict) -> None:
        """添加质量问题记录"""
        # 记录到导入错误表
        ImportError.objects.create(
            task=self.task,
            row_number=row_number,
            field_name=field,
            error_message=f"[{severity.upper()}] {message}",
            raw_data=row_data,
            error_type='quality_check'
        )

        # 如果不是critical，不计入错误统计
        if severity != 'critical':
            return

        # 添加到错误列表
        error = {
            'row_number': row_number,
            'field': field,
            'value': value,
            'message': message,
            'row_data': row_data,
            'severity': severity
        }
        self.errors.append(error)

    def _run_smart_attributes_extraction(self, row: Dict[str, Any], row_number: int) -> Optional[Dict[str, Any]]:
        """运行智能属性提取"""
        if not self.smart_attributes_service:
            return None

        try:
            # 准备属性提取数据
            extraction_data = {
                'brand': 'ROYANA',  # 从任务名称或配置获取
                'description': row.get('产品描述 (Description)', ''),
                'code': row.get('产品编码 (Code)', ''),
                'series': row.get('系列 (Series)', '')
            }

            # 调用智能属性提取服务
            attributes_result = self.smart_attributes_service.process(extraction_data)

            if attributes_result and attributes_result.get('success'):
                logger.info(f"行{row_number}: 智能属性提取成功，提取了{attributes_result.get('final_count', 0)}个属性")
                return attributes_result
            else:
                logger.warning(f"行{row_number}: 智能属性提取失败")

        except Exception as e:
            logger.warning(f"行{row_number}: 智能属性提取异常: {str(e)}")

        return None

    def _prepare_attributes(self, processed_data: Dict[str, Any],
                           smart_attributes_result: Optional[Dict[str, Any]],
                           row_number: int) -> Dict[str, Any]:
        """预创建所有需要的属性和属性值"""
        try:
            prepared_attributes = {
                'basic_attributes': [],
                'smart_attributes': [],
                'attribute_objects': {},
                'attribute_value_objects': {}
            }

            # 1. 准备基础属性
            basic_attrs = self._prepare_basic_attributes(processed_data)
            prepared_attributes['basic_attributes'] = basic_attrs

            # 2. 准备智能属性
            if smart_attributes_result and smart_attributes_result.get('success'):
                smart_attrs = self._prepare_smart_attributes(smart_attributes_result)
                prepared_attributes['smart_attributes'] = smart_attrs

            # 3. 批量创建属性和属性值
            self._batch_create_attributes(prepared_attributes)

            return prepared_attributes

        except Exception as e:
            logger.error(f"行{row_number}属性准备失败: {str(e)}")
            raise

    def _prepare_basic_attributes(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """准备基础属性"""
        attributes = []

        # 基础属性映射
        basic_attr_mapping = {
            '宽度': data.get('宽度', 0),
            '高度': data.get('高度', 0),
            '深度': data.get('深度', 0),
            '开门方向': data.get('开门方向', ''),
            '配置代码': data.get('配置代码', ''),
            '备注说明': data.get('备注', ''),
            '产品系列': data.get('系列', ''),
        }

        # 价格属性
        for i, level in enumerate(['价格等级I', '价格等级II', '价格等级III', '价格等级IV', '价格等级V'], 1):
            price = data.get(level, 0)
            if price > 0:
                basic_attr_mapping[f'价格等级{i}'] = price

        # 转换为属性对象格式
        for attr_name, attr_value in basic_attr_mapping.items():
            if attr_value and str(attr_value).strip():
                attributes.append({
                    'name': attr_name,
                    'value': str(attr_value),
                    'type': self._determine_attribute_type_for_value(attr_value),
                    'source': 'basic_mapping'
                })

        return attributes

    def _prepare_smart_attributes(self, smart_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """准备智能属性"""
        attributes = []
        smart_attrs = smart_result.get('attributes', [])

        for attr in smart_attrs:
            attributes.append({
                'name': attr.get('attribute_name', ''),
                'value': attr.get('value', ''),
                'type': 'select' if len(str(attr.get('value', ''))) < 50 else 'text',
                'source': 'ai_extraction',
                'confidence': attr.get('confidence', 0.5),
                'existing_attr_id': attr.get('attribute_id'),
                'existing_value_id': attr.get('value_id')
            })

        return attributes

    def _determine_attribute_type_for_value(self, value) -> str:
        """智能判断属性类型"""
        if isinstance(value, (int, float)) or str(value).replace('.', '').isdigit():
            return 'number'
        elif len(str(value)) < 20:
            return 'select'
        else:
            return 'text'

    def _batch_create_attributes(self, prepared_attributes: Dict[str, Any]):
        """批量创建属性和属性值"""
        all_attributes = prepared_attributes['basic_attributes'] + prepared_attributes['smart_attributes']

        for attr_data in all_attributes:
            attr_name = attr_data['name']
            attr_value = attr_data['value']

            if not attr_name or not attr_value:
                continue

            # 创建或获取属性
            if attr_data.get('existing_attr_id'):
                # 使用现有属性
                attribute = Attribute.objects.get(id=attr_data['existing_attr_id'])
            else:
                # 创建新属性
                attr_code = self._generate_attribute_code(attr_name)
                attribute, created = Attribute.objects.get_or_create(
                    code=attr_code,
                    defaults={
                        'name': attr_name,
                        'type': attr_data.get('type', 'text'),
                        'is_required': False,
                        'is_filterable': attr_name in ['材质', '颜色', '风格', '系列']
                    }
                )

            # 创建或获取属性值
            if attr_data.get('existing_value_id'):
                # 使用现有属性值
                attribute_value = AttributeValue.objects.get(id=attr_data['existing_value_id'])
            else:
                # 创建新属性值
                attribute_value, created = AttributeValue.objects.get_or_create(
                    attribute=attribute,
                    value=attr_value,
                    defaults={'display_name': attr_value}
                )

            # 存储到准备好的对象中
            prepared_attributes['attribute_objects'][attr_name] = attribute
            prepared_attributes['attribute_value_objects'][attr_name] = attribute_value

    def _create_product_with_prepared_data(self, processed_data: Dict[str, Any],
                                          prepared_attributes: Dict[str, Any],
                                          row_number: int):
        """使用预准备的数据创建产品"""
        try:
            # 提取基础产品信息
            product_info = self._extract_product_info(processed_data)

            # 创建产品（SPU/SKU）
            sku = self._create_product_structure(product_info)

            # 建立属性关联
            self._create_attribute_associations(sku, prepared_attributes)

            logger.info(f"行{row_number}产品创建成功: {sku.code}")

        except Exception as e:
            logger.error(f"行{row_number}产品创建失败: {str(e)}")
            raise

    def _process_ai_data_row(self, row: Dict[str, Any], row_number: int,
                            quality_result: Optional[Dict[str, Any]] = None,
                            smart_attributes_result: Optional[Dict[str, Any]] = None):
        """处理单行AI数据"""
        # 获取基础数据
        code = str(row.get('产品编码 (Code)', '')).strip()
        description = row.get('产品描述_处理', '')
        english_name = row.get('英文名称', '')

        # 验证必填字段
        if not code:
            raise ValidationError("产品编码不能为空")
        if not description:
            raise ValidationError("产品描述不能为空")

        # 获取价格信息
        price_level_1 = row.get('等级Ⅰ', 0.0)
        price_level_2 = row.get('等级Ⅱ', 0.0)
        price_level_3 = row.get('等级Ⅲ', 0.0)
        price_level_4 = row.get('等级Ⅳ', 0.0)
        price_level_5 = row.get('等级Ⅴ', 0.0)

        # 确定销售价格
        price = self._determine_sales_price([price_level_1, price_level_2, price_level_3, price_level_4, price_level_5])

        # 获取产品信息
        series = str(row.get('系列 (Series)', 'N')).strip()
        cabinet_type = row.get('柜体类型_处理', '底柜')
        width = row.get('宽度 (Width_cm)')
        height = row.get('高度 (Height_cm)', 72)
        depth = row.get('深度 (Depth_cm)', 56)
        door_direction = row.get('门板方向_处理', '双开')
        config_code = str(row.get('配置代码 (Config_Code)', '-')).strip()
        remarks = str(row.get('备注 (Remarks)', '')).strip()

        # 创建产品
        self._create_ai_product(
            code=code,
            description=description,
            english_name=english_name,
            series=series,
            cabinet_type=cabinet_type,
            width=width,
            height=height,
            depth=depth,
            door_direction=door_direction,
            config_code=config_code,
            remarks=remarks,
            price_level_1=price_level_1,
            price_level_2=price_level_2,
            price_level_3=price_level_3,
            price_level_4=price_level_4,
            price_level_5=price_level_5,
            price=price,
            smart_attributes_result=smart_attributes_result  # 传递智能属性结果
        )

        logger.info(f"成功导入AI数据产品: {code} - {description}")
    
    def _determine_sales_price(self, prices: List[float]) -> float:
        """确定销售价格"""
        # 过滤掉0值
        valid_prices = [p for p in prices if p > 0]
        
        if not valid_prices:
            raise ValidationError("必须提供至少一个有效的价格")
        
        # 使用价格等级III作为默认销售价格，如果没有则使用第一个有效价格
        if len(prices) >= 3 and prices[2] > 0:
            return prices[2]  # 等级III
        
        return valid_prices[0]

    def _create_ai_product(self, **kwargs):
        """创建AI数据产品"""
        # 获取或创建品牌
        brand = self._get_or_create_brand(
            code='ROYANA',
            name='ROYANA整木定制',
            description='ROYANA整木定制品牌'
        )

        # 生成分类信息
        main_category = self._determine_main_category(kwargs['cabinet_type'])
        sub_category = self._determine_sub_category(kwargs['cabinet_type'], kwargs['door_direction'])

        # 创建或获取分类
        category_code = f"{main_category}_{sub_category}".upper()
        category = self._get_or_create_category(
            code=category_code,
            name=f"{main_category}-{sub_category}",
            description=f"{main_category}类产品，{sub_category}配置"
        )

        # 创建或获取SPU
        spu_code = f"{kwargs['series']}_{kwargs['cabinet_type']}_{kwargs['width']}CM"
        spu = self._get_or_create_spu(
            code=spu_code,
            name=f"{kwargs['series']}系列{kwargs['cabinet_type']}{kwargs['width']}cm",
            category=category,
            brand=brand,
            description=kwargs['description']
        )

        # 生成SKU数据
        sku_code = kwargs['code']
        sku_name = self._generate_product_name(kwargs['description'], kwargs['width'], kwargs['cabinet_type'])

        sku_data = {
            'code': sku_code,
            'name': sku_name,
            'spu': spu,
            'brand': brand,
            'price': Decimal(str(kwargs['price'])),
            'stock_quantity': 0,
            'min_stock': 10,
            'status': 'active',
            'description': kwargs['description']
        }

        sku = self._create_sku(sku_data)

        # 创建SKU属性值
        self._create_ai_sku_attributes(sku, kwargs)

        # 创建智能属性（如果有）
        smart_attributes_result = kwargs.get('smart_attributes_result')
        if smart_attributes_result and smart_attributes_result.get('success'):
            self._create_smart_attributes(sku, smart_attributes_result)

        return sku

    def _create_smart_attributes(self, sku: SKU, smart_attributes_result: Dict[str, Any]):
        """创建智能提取的属性"""
        try:
            attributes = smart_attributes_result.get('attributes', [])
            created_count = 0

            for attr_data in attributes:
                try:
                    # 获取属性信息
                    attr_name = attr_data.get('attribute_name', '')
                    attr_value = attr_data.get('value', '')
                    confidence = attr_data.get('confidence', 0.5)

                    if not attr_name or not attr_value:
                        continue

                    # 如果已经匹配到现有属性
                    if attr_data.get('attribute_id'):
                        attribute_id = attr_data['attribute_id']
                        attribute = Attribute.objects.get(id=attribute_id)

                        # 创建或获取属性值
                        if attr_data.get('value_id'):
                            # 使用现有属性值
                            attribute_value = AttributeValue.objects.get(id=attr_data['value_id'])
                        else:
                            # 创建新属性值
                            attribute_value, created = AttributeValue.objects.get_or_create(
                                attribute=attribute,
                                value=attr_value,
                                defaults={'display_name': attr_value}
                            )
                    else:
                        # 创建新属性
                        attr_code = self._generate_attribute_code(attr_name)
                        attribute, created = Attribute.objects.get_or_create(
                            code=attr_code,
                            defaults={
                                'name': attr_name,
                                'type': self._determine_attribute_type(attr_value),
                                'is_required': False,
                                'is_filterable': attr_name in ['材质', '颜色', '风格', '功能']
                            }
                        )

                        # 创建属性值
                        attribute_value, created = AttributeValue.objects.get_or_create(
                            attribute=attribute,
                            value=attr_value,
                            defaults={'display_name': attr_value}
                        )

                    # 创建SKU属性值关联
                    sku_attr_value, created = SKUAttributeValue.objects.get_or_create(
                        sku=sku,
                        attribute=attribute,
                        defaults={'attribute_value': attribute_value}
                    )

                    if created:
                        created_count += 1

                        # 确保SPU属性关联
                        self._ensure_spu_attribute(sku.spu, attribute)

                        logger.debug(f"创建智能属性: {attr_name} = {attr_value} (置信度: {confidence:.2f})")

                except Exception as e:
                    logger.error(f"创建智能属性失败 {attr_name}: {str(e)}")
                    continue

            logger.info(f"为SKU {sku.code} 创建了 {created_count} 个智能属性")

        except Exception as e:
            logger.error(f"智能属性创建过程失败: {str(e)}")

    def _determine_attribute_type(self, value: str) -> str:
        """智能判断属性类型"""
        if isinstance(value, (int, float)) or value.isdigit():
            return 'number'
        elif len(value) < 20:
            return 'select'
        else:
            return 'text'

    def _determine_main_category(self, cabinet_type: str) -> str:
        """确定主分类"""
        if '底柜' in cabinet_type:
            return '底柜'
        elif '吊柜' in cabinet_type:
            return '吊柜'
        elif '高柜' in cabinet_type:
            return '高柜'
        else:
            return '底柜'

    def _determine_sub_category(self, cabinet_type: str, door_direction: str) -> str:
        """确定子分类"""
        if '单门' in cabinet_type:
            return '单门'
        elif '双门' in cabinet_type:
            return '双门'
        elif '抽屉' in cabinet_type:
            return '抽屉柜'
        else:
            return '单门'

    def _generate_product_name(self, description: str, width: int, cabinet_type: str) -> str:
        """生成产品名称"""
        if width:
            return f"{cabinet_type}{width}cm"
        else:
            return description[:20] if description else cabinet_type

    def _create_ai_sku_attributes(self, sku: SKU, data: Dict[str, Any]):
        """创建AI数据的SKU属性"""
        attributes_data = {
            '宽度': data.get('width'),
            '高度': data.get('height', 72),
            '深度': data.get('depth', 56),
            '柜体类型': data.get('cabinet_type'),
            '门板方向': data.get('door_direction'),
            '配置代码': data.get('config_code'),
            '备注说明': data.get('remarks'),
            '英文名称': data.get('english_name'),
            '价格等级I': data.get('price_level_1', 0),
            '价格等级II': data.get('price_level_2', 0),
            '价格等级III': data.get('price_level_3', 0),
            '价格等级IV': data.get('price_level_4', 0),
            '价格等级V': data.get('price_level_5', 0),
        }

        for attr_name, attr_value in attributes_data.items():
            if attr_value is not None and attr_value != '' and attr_value != '-':
                self._create_sku_attribute_value(sku, attr_name, attr_value)

    def _create_sku_attribute_value(self, sku: SKU, attr_name: str, attr_value):
        """创建SKU属性值"""
        try:
            # 生成属性编码
            attr_code = self._generate_attribute_code(attr_name)

            # 获取或创建属性
            attribute, created = Attribute.objects.get_or_create(
                code=attr_code,
                defaults={
                    'name': attr_name,
                    'type': self._determine_attribute_type(attr_value),
                    'is_required': False,
                    'is_filterable': attr_name in ['宽度', '高度', '深度', '门板方向', '柜体类型']
                }
            )

            # 创建或获取属性值
            if isinstance(attr_value, (int, float)):
                attr_value_str = str(int(attr_value)) if isinstance(attr_value, float) and attr_value.is_integer() else str(attr_value)
            else:
                attr_value_str = str(attr_value)

            attribute_value, created = AttributeValue.objects.get_or_create(
                attribute=attribute,
                value=attr_value_str,
                defaults={'display_name': attr_value_str}
            )

            # 创建SKU属性值关联
            SKUAttributeValue.objects.get_or_create(
                sku=sku,
                attribute=attribute,
                defaults={'attribute_value': attribute_value}
            )

            # 确保SPU也关联了这个属性
            self._ensure_spu_attribute(sku.spu, attribute)

        except Exception as e:
            logger.warning(f"创建属性值失败 {attr_name}={attr_value}: {str(e)}")

    def _generate_attribute_code(self, attr_name: str) -> str:
        """生成属性编码"""
        code_mapping = {
            '宽度': 'WIDTH',
            '高度': 'HEIGHT',
            '深度': 'DEPTH',
            '柜体类型': 'CABINET_TYPE',
            '门板方向': 'DOOR_DIRECTION',
            '配置代码': 'CONFIG_CODE',
            '备注说明': 'REMARKS',
            '英文名称': 'ENGLISH_NAME',
            '价格等级I': 'PRICE_LEVEL_1',
            '价格等级II': 'PRICE_LEVEL_2',
            '价格等级III': 'PRICE_LEVEL_3',
            '价格等级IV': 'PRICE_LEVEL_4',
            '价格等级V': 'PRICE_LEVEL_5',
        }
        return code_mapping.get(attr_name, attr_name.upper().replace(' ', '_'))

    def _ensure_spu_attribute(self, spu: SPU, attribute: Attribute):
        """确保SPU关联了指定属性"""
        try:
            SPUAttribute.objects.get_or_create(
                spu=spu,
                attribute=attribute,
                defaults={
                    'is_required': attribute.code in ['WIDTH', 'CABINET_TYPE'],
                    'order': self._get_attribute_order(attribute.code)
                }
            )
        except Exception as e:
            logger.warning(f"创建SPU属性关联失败 {spu.code}-{attribute.name}: {str(e)}")

    def _get_attribute_order(self, attr_code: str) -> int:
        """获取属性显示顺序"""
        order_mapping = {
            'WIDTH': 1,
            'HEIGHT': 2,
            'DEPTH': 3,
            'CABINET_TYPE': 4,
            'DOOR_DIRECTION': 5,
            'CONFIG_CODE': 6,
            'ENGLISH_NAME': 7,
            'PRICE_LEVEL_1': 8,
            'PRICE_LEVEL_2': 9,
            'PRICE_LEVEL_3': 10,
            'PRICE_LEVEL_4': 11,
            'PRICE_LEVEL_5': 12,
            'REMARKS': 13,
        }
        return order_mapping.get(attr_code, 99)

    def _determine_attribute_type(self, value) -> str:
        """确定属性类型"""
        if isinstance(value, (int, float)):
            return 'number'
        elif isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, str):
            # 根据值的内容判断类型
            if value in ['左开', '右开', '左开/右开', '双开', '-']:
                return 'select'
            elif len(value) < 50:
                return 'select'
            else:
                return 'text'
        else:
            return 'text'

    # 辅助方法（复用现有的方法）
    def _get_or_create_brand(self, code: str, name: str, description: str) -> Brand:
        """获取或创建品牌"""
        brand, created = Brand.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'description': description
            }
        )
        return brand

    def _get_or_create_category(self, code: str, name: str, description: str) -> Category:
        """获取或创建分类"""
        category, created = Category.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'description': description,
                'is_active': True
            }
        )
        return category

    def _get_or_create_spu(self, code: str, name: str, category: Category, brand: Brand, description: str) -> SPU:
        """获取或创建SPU"""
        spu, created = SPU.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'category': category,
                'brand': brand,
                'description': description,
                'is_active': True
            }
        )
        return spu

    def _create_sku(self, sku_data: Dict[str, Any]) -> SKU:
        """创建SKU"""
        sku, created = SKU.objects.get_or_create(
            code=sku_data['code'],
            defaults=sku_data
        )

        if not created:
            # 更新现有SKU
            for key, value in sku_data.items():
                if key != 'code':
                    setattr(sku, key, value)
            sku.save()

        return sku

    def _add_error(self, row_number: int, field: str, value: str, message: str, row_data: Dict):
        """添加错误记录"""
        error = {
            'row_number': row_number,
            'field': field,
            'value': value,
            'message': message,
            'row_data': row_data
        }
        self.errors.append(error)

        # 保存到数据库
        ImportError.objects.create(
            task=self.task,
            row_number=row_number,
            field_name=field,
            error_message=message,
            raw_data=row_data,
            error_type='validation'
        )

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
