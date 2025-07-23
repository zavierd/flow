"""
属性分析器
负责识别和分析未定义的产品属性
"""

import json
import logging
from typing import Dict, Any, List, Optional
from .deepseek_service import DeepSeekService

logger = logging.getLogger(__name__)


class AttributeAnalyzer:
    """属性分析器 - 智能识别和处理未定义属性"""
    
    def __init__(self):
        self.ai_service = DeepSeekService()

        # 从配置获取参数
        from products.config.smart_attribute_config import SMART_ATTRIBUTE_CONFIG
        self.confidence_threshold = SMART_ATTRIBUTE_CONFIG.get('confidence_threshold', 0.6)
        self.use_real_ai = SMART_ATTRIBUTE_CONFIG.get('use_real_ai', True)
        
    def identify_unknown_attributes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """识别未定义的属性"""
        from products.config.ai_data_mapping import PRODUCT_STRUCTURE_MAPPING
        
        # 获取已知字段
        known_fields = set(PRODUCT_STRUCTURE_MAPPING['attribute_fields'])
        
        # 添加基础字段（不应作为属性处理）
        base_fields = {
            '产品描述', '产品编码', '备注',
            '价格等级I', '价格等级II', '价格等级III', '价格等级IV', '价格等级V'
        }
        
        excluded_fields = known_fields.union(base_fields)
        
        # 识别未知属性
        unknown_attributes = {}
        for key, value in data.items():
            if (key not in excluded_fields and 
                value and 
                str(value).strip() and
                str(value).strip() not in ['', '-', 'N/A', '0', '0.0']):
                unknown_attributes[key] = value
        
        logger.info(f"🔍 识别到 {len(unknown_attributes)} 个未定义属性: {list(unknown_attributes.keys())}")
        return unknown_attributes
    
    def analyze_attributes_batch(self, unknown_attributes: Dict[str, Any], context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """批量分析未知属性"""
        analyzed_attributes = []
        
        for attr_name, attr_value in unknown_attributes.items():
            try:
                analysis_result = self.analyze_single_attribute(attr_name, attr_value, context_data)
                if analysis_result:
                    analyzed_attributes.append(analysis_result)
                    logger.info(f"🤖 AI分析属性: {attr_name} → {analysis_result['display_name']}")
                
            except Exception as e:
                logger.warning(f"分析属性失败 {attr_name}: {str(e)}")
                # 使用默认分析
                analyzed_attributes.append(self._create_default_analysis(attr_name, attr_value))
        
        return analyzed_attributes
    
    def analyze_single_attribute(self, attr_name: str, attr_value: str, context_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """分析单个属性"""
        if not self.ai_service.is_available():
            logger.info(f"AI服务不可用，使用默认分析处理属性: {attr_name}")
            return self._create_default_analysis(attr_name, attr_value)
        
        # 构建AI分析提示词
        prompt = self._build_analysis_prompt(attr_name, attr_value, context_data)
        
        # 调用AI服务
        ai_response = self.ai_service.generate_response(prompt)
        
        # 解析AI响应
        analysis_result = self._parse_ai_response(ai_response, attr_name, attr_value)
        
        # 验证分析结果
        if self._validate_analysis_result(analysis_result):
            return analysis_result
        else:
            logger.warning(f"AI分析结果验证失败，使用默认分析: {attr_name}")
            return self._create_default_analysis(attr_name, attr_value)
    
    def _build_analysis_prompt(self, attr_name: str, attr_value: str, context_data: Dict[str, Any]) -> str:
        """构建AI分析提示词"""
        product_desc = context_data.get('产品描述', '')
        series = context_data.get('系列', '')
        type_code = context_data.get('类型代码', '')

        prompt = f"""请分析家具产品属性并返回JSON格式结果。

属性名: {attr_name}
属性值: {attr_value}
产品: {product_desc}

请返回JSON格式的分析结果，包含以下字段：
- display_name: 标准化属性名称
- display_value: 标准化属性值
- attribute_type: 数据类型(text/number/select/boolean/color)
- filterable: 是否可筛选(true/false)
- importance: 重要程度(1-5)
- confidence: 置信度(0.0-1.0)

只返回JSON，不要其他文字："""
        return prompt
    
    def _parse_ai_response(self, ai_response: str, attr_name: str, attr_value: str) -> Dict[str, Any]:
        """解析AI响应"""
        try:
            # 记录原始响应用于调试
            logger.debug(f"AI原始响应: {repr(ai_response)}")

            # 清理响应内容
            cleaned_response = ai_response.strip()

            # 尝试提取JSON部分（如果响应包含其他文本）
            import re
            json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                logger.debug(f"提取的JSON: {json_str}")
            else:
                json_str = cleaned_response

            # 尝试解析JSON
            result = json.loads(json_str)

            # 确保必要字段存在
            required_fields = ['display_name', 'display_value', 'attribute_type', 'filterable', 'importance']
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"缺少必要字段: {field}")

            # 添加原始信息
            result['original_name'] = attr_name
            result['original_value'] = attr_value

            logger.info(f"✅ AI响应解析成功: {attr_name} -> {result['display_name']}")
            return result

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"解析AI响应失败: {str(e)}")
            logger.warning(f"原始响应内容: {repr(ai_response)}")
            return self._create_default_analysis(attr_name, attr_value)
    
    def _validate_analysis_result(self, result: Dict[str, Any]) -> bool:
        """验证分析结果的有效性"""
        try:
            # 检查置信度
            confidence = result.get('confidence', 0)
            if confidence < self.confidence_threshold:
                logger.info(f"AI分析置信度过低: {confidence} < {self.confidence_threshold}")
                return False
            
            # 检查属性类型
            valid_types = ['text', 'number', 'select', 'boolean', 'color']
            if result.get('attribute_type') not in valid_types:
                return False
            
            # 检查重要程度
            importance = result.get('importance', 0)
            if not isinstance(importance, int) or importance < 1 or importance > 5:
                return False
            
            # 检查必要字段
            required_fields = ['display_name', 'display_value']
            for field in required_fields:
                if not result.get(field) or not str(result[field]).strip():
                    return False
            
            return True
            
        except Exception as e:
            logger.warning(f"验证分析结果时出错: {str(e)}")
            return False
    
    def _create_default_analysis(self, attr_name: str, attr_value: str) -> Dict[str, Any]:
        """创建默认分析结果"""
        return {
            'original_name': attr_name,
            'original_value': attr_value,
            'display_name': attr_name,
            'display_value': str(attr_value),
            'attribute_type': 'text',
            'filterable': False,
            'importance': 3,
            'confidence': 0.5,
            'source': 'default'  # 标记为默认处理
        }
    
    def get_analysis_summary(self, analyzed_attributes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """获取分析摘要"""
        if not analyzed_attributes:
            return {'total': 0, 'ai_processed': 0, 'default_processed': 0}
        
        total = len(analyzed_attributes)
        ai_processed = sum(1 for attr in analyzed_attributes if attr.get('source') != 'default')
        default_processed = total - ai_processed
        
        avg_confidence = sum(attr.get('confidence', 0) for attr in analyzed_attributes) / total
        high_importance = sum(1 for attr in analyzed_attributes if attr.get('importance', 0) >= 4)
        filterable_count = sum(1 for attr in analyzed_attributes if attr.get('filterable', False))
        
        return {
            'total': total,
            'ai_processed': ai_processed,
            'default_processed': default_processed,
            'average_confidence': round(avg_confidence, 2),
            'high_importance_count': high_importance,
            'filterable_count': filterable_count,
            'attribute_types': self._count_attribute_types(analyzed_attributes)
        }
    
    def _count_attribute_types(self, analyzed_attributes: List[Dict[str, Any]]) -> Dict[str, int]:
        """统计属性类型分布"""
        type_counts = {}
        for attr in analyzed_attributes:
            attr_type = attr.get('attribute_type', 'unknown')
            type_counts[attr_type] = type_counts.get(attr_type, 0) + 1
        return type_counts
