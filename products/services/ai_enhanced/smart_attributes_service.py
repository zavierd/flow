"""
智能属性提取服务
结合规则引擎和AI，智能提取产品属性并与数据库现有属性匹配
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from django.conf import settings
from django.db.models import Q
from difflib import SequenceMatcher

from .base_ai_service import BaseAIService
from .deepseek_service import DeepSeekService
from products.utils.ai_feature_flags import AIFeatureFlags
from products.models import Attribute, AttributeValue
import logging

logger = logging.getLogger(__name__)


class SmartAttributesService(BaseAIService):
    """智能属性提取服务"""

    def __init__(self):
        super().__init__()
        self.config = getattr(settings, 'SMART_ATTRIBUTES_CONFIG', {})
        self.deepseek_service = None

        # 初始化DeepSeek服务（如果启用）
        if self.config.get('enable_ai_fallback', True):
            try:
                self.deepseek_service = DeepSeekService()
            except Exception as e:
                logger.warning(f"DeepSeek服务初始化失败: {e}")

    def _check_enabled(self) -> bool:
        """检查服务是否启用"""
        return AIFeatureFlags.is_enabled('ai_smart_attributes')

    def process_for_test(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """专门用于测试的处理方法，忽略启用状态"""
        try:
            return self._process_impl(data)
        except Exception as e:
            logger.error(f"{self.__class__.__name__} 处理失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'service': self.__class__.__name__
            }

    def _process_impl(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """智能属性提取主流程"""
        try:
            # 第一层：规则引擎提取
            rule_attributes = self._extract_by_rules(data)

            # 第二层：AI增强提取（如果启用且需要AI增强）
            ai_attributes = []
            should_use_ai = (
                self.config.get('enable_ai_fallback', True) and
                self.deepseek_service and
                (len(rule_attributes) < 5 or  # 规则提取的属性少于5个
                 self._is_complex_product(data))  # 或者是复杂产品
            )

            if should_use_ai:

                ai_result = self.deepseek_service.extract_attributes(data)
                if ai_result.get('success'):
                    ai_attributes = ai_result.get('attributes', [])

            # 第三层：数据补全（如果启用）
            completion_attributes = []
            if AIFeatureFlags.is_enabled('ai_data_completion'):
                completion_attributes = self._complete_missing_data(
                    rule_attributes + ai_attributes, data
                )

            # 第四层：属性匹配与去重
            all_attributes = rule_attributes + ai_attributes + completion_attributes
            final_attributes = self._match_and_deduplicate(all_attributes, data)

            return {
                'success': True,
                'attributes': final_attributes,
                'rule_count': len(rule_attributes),
                'ai_count': len(ai_attributes),
                'final_count': len(final_attributes),
                'processing_method': 'hybrid' if ai_attributes else 'rules_only'
            }

        except Exception as e:
            logger.error(f"智能属性提取失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _extract_by_rules(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于规则引擎提取属性"""
        attributes = []

        # 从产品编码提取属性
        code = data.get('code', '')
        if code:
            code_attributes = self._extract_from_code(code)
            attributes.extend(code_attributes)

        # 从产品描述提取属性
        description = data.get('description', '')
        if description:
            desc_attributes = self._extract_from_description(description)
            attributes.extend(desc_attributes)

        # 从系列信息提取属性
        series = data.get('series', '')
        if series:
            series_attributes = self._extract_from_series(series)
            attributes.extend(series_attributes)

        return attributes

    def _extract_from_code(self, code: str) -> List[Dict[str, Any]]:
        """从产品编码提取属性"""
        attributes = []

        # 尺寸提取 (例: N-U30-7256-L/R)
        # 先提取类型代码后的数字作为宽度
        width_match = re.search(r'-[A-Z]+(\d+)-', code)
        if width_match:
            width = int(width_match.group(1))
            attributes.append({
                'name': '宽度',
                'value': str(width),
                'unit': 'cm',
                'confidence': 0.95,
                'source': 'code_parsing'
            })

        # 高度提取 (从编码中的数字)
        height_match = re.search(r'-(\d{2})(\d{2})-', code)
        if height_match:
            height = int(height_match.group(1))
            depth = int(height_match.group(2))

            attributes.extend([
                {
                    'name': '高度',
                    'value': str(height),
                    'unit': 'cm',
                    'confidence': 0.90,
                    'source': 'code_parsing'
                },
                {
                    'name': '深度',
                    'value': str(depth),
                    'unit': 'cm',
                    'confidence': 0.90,
                    'source': 'code_parsing'
                }
            ])

        # 门板方向提取
        if 'L/R' in code:
            attributes.append({
                'name': '门板方向',
                'value': '左开/右开',
                'confidence': 0.95,
                'source': 'code_parsing'
            })
        elif code.endswith('-L'):
            attributes.append({
                'name': '门板方向',
                'value': '左开',
                'confidence': 0.95,
                'source': 'code_parsing'
            })
        elif code.endswith('-R'):
            attributes.append({
                'name': '门板方向',
                'value': '右开',
                'confidence': 0.95,
                'source': 'code_parsing'
            })

        return attributes

    def _extract_from_description(self, description: str) -> List[Dict[str, Any]]:
        """从产品描述提取属性"""
        attributes = []

        # 材质关键词匹配
        material_keywords = {
            '实木': '实木',
            '板材': '人造板',
            '多层板': '多层实木板',
            '颗粒板': '刨花板',
            '密度板': '中密度纤维板',
            'MDF': '中密度纤维板'
        }

        for keyword, standard_value in material_keywords.items():
            if keyword in description:
                attributes.append({
                    'name': '材质',
                    'value': standard_value,
                    'confidence': 0.80,
                    'source': 'description_keywords'
                })
                break

        # 功能特征提取
        function_keywords = {
            '抽屉': '带抽屉',
            '拉篮': '带拉篮',
            '转角': '转角柜',
            '吊柜': '吊装式',
            '底柜': '落地式',
            '高柜': '高柜',
            '酒柜': '酒柜功能'
        }

        for keyword, feature in function_keywords.items():
            if keyword in description:
                attributes.append({
                    'name': '功能特征',
                    'value': feature,
                    'confidence': 0.75,
                    'source': 'description_keywords'
                })

        # 颜色提取
        color_keywords = {
            '白色': '白色',
            '黑色': '黑色',
            '原木色': '原木色',
            '胡桃色': '胡桃色',
            '橡木色': '橡木色'
        }

        for keyword, color in color_keywords.items():
            if keyword in description:
                attributes.append({
                    'name': '颜色',
                    'value': color,
                    'confidence': 0.70,
                    'source': 'description_keywords'
                })
                break

        return attributes

    def _extract_from_series(self, series: str) -> List[Dict[str, Any]]:
        """从系列信息提取属性"""
        attributes = []

        # 系列属性
        attributes.append({
            'name': '产品系列',
            'value': series,
            'confidence': 0.95,
            'source': 'series_info'
        })

        # 根据系列推断风格
        style_mapping = {
            'N': '现代简约',
            'C': '古典风格',
            'M': '现代风格',
            'E': '欧式风格'
        }

        if series in style_mapping:
            attributes.append({
                'name': '设计风格',
                'value': style_mapping[series],
                'confidence': 0.80,
                'source': 'series_mapping'
            })

        return attributes

    def _match_and_deduplicate(self, extracted_attributes: List[Dict[str, Any]],
                              product_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """属性匹配与去重"""
        final_attributes = []
        processed_names = set()

        # 获取数据库中现有的属性
        existing_attributes = self._get_existing_attributes()

        for attr in extracted_attributes:
            attr_name = attr.get('name', '')
            attr_value = attr.get('value', '')

            if not attr_name or not attr_value:
                continue

            # 避免重复属性名
            if attr_name in processed_names:
                continue

            # 匹配现有属性
            matched_attr = self._find_matching_attribute(attr_name, existing_attributes)
            if matched_attr:
                # 使用现有属性名
                standardized_name = matched_attr['name']

                # 匹配现有属性值
                matched_value = self._find_matching_attribute_value(
                    matched_attr['id'], attr_value
                )

                if matched_value:
                    # 使用现有属性值
                    final_attributes.append({
                        'attribute_id': matched_attr['id'],
                        'attribute_name': standardized_name,
                        'value_id': matched_value['id'],
                        'value': matched_value['value'],
                        'confidence': attr.get('confidence', 0.5),
                        'source': attr.get('source', 'unknown'),
                        'matched_existing': True
                    })
                else:
                    # 使用现有属性，但创建新属性值
                    final_attributes.append({
                        'attribute_id': matched_attr['id'],
                        'attribute_name': standardized_name,
                        'value_id': None,
                        'value': attr_value,
                        'confidence': attr.get('confidence', 0.5),
                        'source': attr.get('source', 'unknown'),
                        'matched_existing': 'partial'
                    })
            else:
                # 创建新属性和属性值
                final_attributes.append({
                    'attribute_id': None,
                    'attribute_name': attr_name,
                    'value_id': None,
                    'value': attr_value,
                    'confidence': attr.get('confidence', 0.5),
                    'source': attr.get('source', 'unknown'),
                    'matched_existing': False
                })

            processed_names.add(attr_name)

            # 限制属性数量
            max_attrs = self.config.get('max_attributes_per_product', 20)
            if len(final_attributes) >= max_attrs:
                break

        return final_attributes

    def _get_existing_attributes(self) -> List[Dict[str, Any]]:
        """获取数据库中现有的属性"""
        try:
            attributes = Attribute.objects.all().values('id', 'name', 'code', 'type')
            return list(attributes)
        except Exception as e:
            logger.error(f"获取现有属性失败: {e}")
            return []

    def _find_matching_attribute(self, attr_name: str,
                                existing_attributes: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """查找匹配的现有属性"""
        threshold = self.config.get('attribute_similarity_threshold', 0.85)

        best_match = None
        best_score = 0

        for existing_attr in existing_attributes:
            existing_name = existing_attr['name']

            # 精确匹配
            if attr_name == existing_name:
                return existing_attr

            # 相似度匹配
            similarity = SequenceMatcher(None, attr_name, existing_name).ratio()
            if similarity > best_score and similarity >= threshold:
                best_score = similarity
                best_match = existing_attr

        return best_match

    def _find_matching_attribute_value(self, attribute_id: int,
                                     value: str) -> Optional[Dict[str, Any]]:
        """查找匹配的现有属性值"""
        try:
            # 精确匹配
            exact_match = AttributeValue.objects.filter(
                attribute_id=attribute_id,
                value=value
            ).values('id', 'value').first()

            if exact_match:
                return exact_match

            # 相似度匹配
            threshold = self.config.get('attribute_similarity_threshold', 0.85)
            existing_values = AttributeValue.objects.filter(
                attribute_id=attribute_id
            ).values('id', 'value')

            best_match = None
            best_score = 0

            for existing_value in existing_values:
                similarity = SequenceMatcher(
                    None, value, existing_value['value']
                ).ratio()

                if similarity > best_score and similarity >= threshold:
                    best_score = similarity
                    best_match = existing_value

            return best_match

        except Exception as e:
            logger.error(f"查找匹配属性值失败: {e}")
            return None

    def _is_complex_product(self, data: Dict[str, Any]) -> bool:
        """判断是否为复杂产品，需要AI增强处理"""
        description = data.get('description', '').lower()
        code = data.get('code', '')

        # 复杂产品特征
        complex_keywords = [
            '古典', '欧式', '美式', '中式',  # 风格词汇
            'led', '灯带', '恒温', '智能',   # 高科技功能
            '雕花', '手工', '定制',         # 工艺特征
            '酒柜', '书柜', '衣帽间',       # 特殊功能
            '玻璃', '皮革', '大理石',       # 特殊材质
        ]

        # 非标准编码格式
        non_standard_code = not re.match(r'^N-[A-Z]+\d+(-\d+)?(-[A-Z/]+)?$', code)

        # 描述包含复杂关键词
        has_complex_keywords = any(keyword in description for keyword in complex_keywords)

        # 描述很长（超过50字符）
        long_description = len(description) > 50

        return non_standard_code or has_complex_keywords or long_description

    def _complete_missing_data(self, existing_attributes: List[Dict[str, Any]],
                              data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """智能数据补全"""
        completion_attributes = []

        try:
            # 检查缺失的关键属性
            existing_attr_names = {attr.get('name', '') for attr in existing_attributes}
            missing_attrs = self._identify_missing_attributes(existing_attr_names, data)

            if not missing_attrs:
                return completion_attributes

            # 使用AI补全缺失数据
            if self.deepseek_service and len(missing_attrs) > 0:
                completion_result = self._ai_complete_missing_data(missing_attrs, data)
                if completion_result:
                    completion_attributes.extend(completion_result)

            # 使用规则补全缺失数据
            rule_completion = self._rule_complete_missing_data(missing_attrs, data)
            completion_attributes.extend(rule_completion)

        except Exception as e:
            logger.error(f"数据补全失败: {e}")

        return completion_attributes

    def _identify_missing_attributes(self, existing_attr_names: set,
                                   data: Dict[str, Any]) -> List[str]:
        """识别缺失的关键属性"""
        # 定义关键属性
        essential_attributes = [
            '材质', '颜色', '设计风格', '功能特征',
            '表面处理', '安装方式', '适用空间'
        ]

        missing_attrs = []
        for attr in essential_attributes:
            if attr not in existing_attr_names:
                missing_attrs.append(attr)

        return missing_attrs

    def _ai_complete_missing_data(self, missing_attrs: List[str],
                                 data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """使用AI补全缺失数据"""
        try:
            completion_prompt = f"""基于以下产品信息，请补全缺失的属性：

产品描述：{data.get('description', '')}
产品编码：{data.get('code', '')}
系列：{data.get('series', '')}

需要补全的属性：{', '.join(missing_attrs)}

请根据产品描述推断这些属性的合理值。返回JSON格式：
{{
  "completed_attributes": [
    {{"name": "材质", "value": "推断的材质", "confidence": 0.8}},
    {{"name": "颜色", "value": "推断的颜色", "confidence": 0.7}}
  ]
}}

只补全有把握的属性，不确定的请不要包含。"""

            completion_data = {
                'task_type': 'data_completion',
                'prompt': completion_prompt
            }

            result = self.deepseek_service.process(completion_data)

            if result and result.get('success'):
                return self._parse_completion_result(result)

        except Exception as e:
            logger.error(f"AI数据补全失败: {e}")

        return []

    def _parse_completion_result(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析AI补全结果"""
        attributes = []

        try:
            api_response = result.get('response', {})
            choices = api_response.get('choices', [])

            if choices:
                content = choices[0].get('message', {}).get('content', '')

                # 清理JSON格式
                clean_content = content.strip()
                if clean_content.startswith('```json'):
                    clean_content = clean_content[7:]
                if clean_content.endswith('```'):
                    clean_content = clean_content[:-3]
                clean_content = clean_content.strip()

                completion_result = json.loads(clean_content)
                completed_attrs = completion_result.get('completed_attributes', [])

                for attr in completed_attrs:
                    attributes.append({
                        'name': attr.get('name', ''),
                        'value': attr.get('value', ''),
                        'confidence': attr.get('confidence', 0.5),
                        'source': 'ai_completion'
                    })

        except Exception as e:
            logger.error(f"解析AI补全结果失败: {e}")

        return attributes

    def _rule_complete_missing_data(self, missing_attrs: List[str],
                                   data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """使用规则补全缺失数据"""
        attributes = []

        description = data.get('description', '').lower()
        series = data.get('series', '')

        # 规则补全逻辑
        for attr_name in missing_attrs:
            if attr_name == '安装方式':
                if '吊柜' in description or 'wall' in description.lower():
                    attributes.append({
                        'name': '安装方式',
                        'value': '壁挂式',
                        'confidence': 0.9,
                        'source': 'rule_completion'
                    })
                elif '底柜' in description or 'base' in description.lower():
                    attributes.append({
                        'name': '安装方式',
                        'value': '落地式',
                        'confidence': 0.9,
                        'source': 'rule_completion'
                    })

            elif attr_name == '适用空间':
                if '厨房' in description or 'kitchen' in description.lower():
                    attributes.append({
                        'name': '适用空间',
                        'value': '厨房',
                        'confidence': 0.8,
                        'source': 'rule_completion'
                    })
                elif '书房' in description or '书柜' in description:
                    attributes.append({
                        'name': '适用空间',
                        'value': '书房',
                        'confidence': 0.8,
                        'source': 'rule_completion'
                    })
                elif '酒柜' in description:
                    attributes.append({
                        'name': '适用空间',
                        'value': '客厅/餐厅',
                        'confidence': 0.8,
                        'source': 'rule_completion'
                    })

        return attributes