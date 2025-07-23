"""
智能属性映射器
负责将AI分析的属性结果映射到数据库模型
"""

import logging
from typing import Dict, Any, List, Optional
from django.db import transaction
from products.models import Attribute, AttributeValue, SKU, SPU, SKUAttributeValue, SPUAttribute

logger = logging.getLogger(__name__)


class SmartAttributeMapper:
    """智能属性映射器 - 将AI分析结果映射到数据库"""
    
    def __init__(self):
        self.created_attributes = {}  # 缓存已创建的属性
        self.created_values = {}      # 缓存已创建的属性值
        
    def map_attributes_to_sku(self, sku: SKU, spu: SPU, analyzed_attributes: List[Dict[str, Any]]) -> int:
        """将分析的属性映射到SKU"""
        mapped_count = 0
        
        with transaction.atomic():
            for attr_analysis in analyzed_attributes:
                try:
                    success = self._create_attribute_mapping(sku, spu, attr_analysis)
                    if success:
                        mapped_count += 1
                        logger.debug(f"🔗 映射属性: {attr_analysis['display_name']} = {attr_analysis['display_value']}")
                    
                except Exception as e:
                    logger.warning(f"映射属性失败 {attr_analysis.get('display_name', 'unknown')}: {str(e)}")
        
        return mapped_count
    
    def _create_attribute_mapping(self, sku: SKU, spu: SPU, attr_analysis: Dict[str, Any]) -> bool:
        """创建单个属性映射"""
        try:
            # 1. 创建或获取属性定义
            attribute = self._get_or_create_attribute(attr_analysis)
            if not attribute:
                return False
            
            # 2. 创建或获取属性值
            attribute_value = self._get_or_create_attribute_value(attribute, attr_analysis)
            if not attribute_value:
                return False
            
            # 3. 创建SKU属性值关联
            sku_attr_value, created = SKUAttributeValue.objects.get_or_create(
                sku=sku,
                attribute=attribute,
                defaults={'attribute_value': attribute_value}
            )
            
            # 如果已存在但值不同，更新属性值
            if not created and sku_attr_value.attribute_value != attribute_value:
                sku_attr_value.attribute_value = attribute_value
                sku_attr_value.save()
                logger.debug(f"📝 更新SKU属性值: {attribute.name} = {attribute_value.value}")
            
            # 4. 创建SPU属性关联
            spu_attribute, created = SPUAttribute.objects.get_or_create(
                spu=spu,
                attribute=attribute,
                defaults={
                    'is_required': False,
                    'order': self._calculate_attribute_order(attr_analysis)
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"创建属性映射失败: {str(e)}")
            return False
    
    def _get_or_create_attribute(self, attr_analysis: Dict[str, Any]) -> Optional[Attribute]:
        """获取或创建属性定义"""
        try:
            display_name = attr_analysis['display_name']
            attr_type = attr_analysis['attribute_type']
            filterable = attr_analysis.get('filterable', False)
            
            # 生成属性编码
            attr_code = self._generate_attribute_code(display_name)
            
            # 检查缓存
            cache_key = f"{attr_code}_{attr_type}"
            if cache_key in self.created_attributes:
                return self.created_attributes[cache_key]
            
            # 创建或获取属性
            attribute, created = Attribute.objects.get_or_create(
                code=attr_code,
                defaults={
                    'name': display_name,
                    'type': attr_type,
                    'is_required': False,
                    'is_filterable': filterable,
                    'description': f'AI智能识别的属性 (置信度: {attr_analysis.get("confidence", 0):.2f})'
                }
            )
            
            if created:
                logger.info(f"✨ AI创建新属性: {display_name} ({attr_type})")
            
            # 更新现有属性的可筛选性（如果AI建议更改）
            elif not attribute.is_filterable and filterable:
                attribute.is_filterable = True
                attribute.save()
                logger.info(f"📝 更新属性可筛选性: {display_name}")
            
            # 缓存属性
            self.created_attributes[cache_key] = attribute
            return attribute
            
        except Exception as e:
            logger.error(f"创建属性定义失败: {str(e)}")
            return None
    
    def _get_or_create_attribute_value(self, attribute: Attribute, attr_analysis: Dict[str, Any]) -> Optional[AttributeValue]:
        """获取或创建属性值"""
        try:
            display_value = attr_analysis['display_value']
            
            # 检查缓存
            cache_key = f"{attribute.id}_{display_value}"
            if cache_key in self.created_values:
                return self.created_values[cache_key]
            
            # 创建或获取属性值
            attribute_value, created = AttributeValue.objects.get_or_create(
                attribute=attribute,
                value=display_value,
                defaults={
                    'display_name': display_value,
                    'description': f'AI智能识别的属性值'
                }
            )
            
            if created:
                logger.debug(f"✨ 创建新属性值: {attribute.name} = {display_value}")
            
            # 缓存属性值
            self.created_values[cache_key] = attribute_value
            return attribute_value
            
        except Exception as e:
            logger.error(f"创建属性值失败: {str(e)}")
            return None
    
    def _generate_attribute_code(self, display_name: str) -> str:
        """生成属性编码"""
        # 移除特殊字符，转换为大写
        import re
        code = re.sub(r'[^\w\s]', '', display_name)
        code = re.sub(r'\s+', '_', code.strip())
        code = code.upper()
        
        # 如果编码为空，使用默认前缀
        if not code:
            code = 'ATTR'
        
        # 限制长度
        if len(code) > 50:
            code = code[:50]
        
        return code
    
    def _calculate_attribute_order(self, attr_analysis: Dict[str, Any]) -> int:
        """计算属性显示顺序"""
        importance = attr_analysis.get('importance', 3)
        
        # 重要程度越高，排序越靠前
        # 基础排序从100开始，为预定义属性留出空间
        base_order = 100
        
        # 重要程度5: 100-109
        # 重要程度4: 110-119
        # 重要程度3: 120-129
        # 重要程度2: 130-139
        # 重要程度1: 140-149
        order_range_start = base_order + (5 - importance) * 10
        
        # 在范围内随机分配，避免冲突
        import random
        return order_range_start + random.randint(0, 9)
    
    def get_mapping_statistics(self) -> Dict[str, Any]:
        """获取映射统计信息"""
        return {
            'created_attributes_count': len(self.created_attributes),
            'created_values_count': len(self.created_values),
            'attribute_types': self._get_attribute_type_distribution(),
            'filterable_attributes': self._count_filterable_attributes()
        }
    
    def _get_attribute_type_distribution(self) -> Dict[str, int]:
        """获取属性类型分布"""
        type_counts = {}
        for attribute in self.created_attributes.values():
            attr_type = attribute.type
            type_counts[attr_type] = type_counts.get(attr_type, 0) + 1
        return type_counts
    
    def _count_filterable_attributes(self) -> int:
        """统计可筛选属性数量"""
        return sum(1 for attr in self.created_attributes.values() if attr.is_filterable)
    
    def clear_cache(self):
        """清空缓存"""
        self.created_attributes.clear()
        self.created_values.clear()
        logger.debug("🧹 清空属性映射缓存")
    
    def batch_optimize_attributes(self, analyzed_attributes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量优化属性（合并相似属性、标准化等）"""
        optimization_result = {
            'merged_attributes': 0,
            'standardized_values': 0,
            'suggestions': []
        }
        
        # 查找相似属性
        similar_groups = self._find_similar_attributes(analyzed_attributes)
        
        for group in similar_groups:
            if len(group) > 1:
                # 建议合并相似属性
                primary_attr = max(group, key=lambda x: x.get('confidence', 0))
                optimization_result['suggestions'].append({
                    'type': 'merge_attributes',
                    'primary': primary_attr['display_name'],
                    'similar': [attr['display_name'] for attr in group if attr != primary_attr],
                    'confidence': primary_attr.get('confidence', 0)
                })
        
        return optimization_result
    
    def _find_similar_attributes(self, analyzed_attributes: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """查找相似的属性"""
        # 简单的相似性检测（基于名称相似度）
        similar_groups = []
        processed = set()
        
        for i, attr1 in enumerate(analyzed_attributes):
            if i in processed:
                continue
            
            group = [attr1]
            processed.add(i)
            
            for j, attr2 in enumerate(analyzed_attributes[i+1:], i+1):
                if j in processed:
                    continue
                
                # 检查名称相似性
                if self._are_attributes_similar(attr1, attr2):
                    group.append(attr2)
                    processed.add(j)
            
            if len(group) > 1:
                similar_groups.append(group)
        
        return similar_groups
    
    def _are_attributes_similar(self, attr1: Dict[str, Any], attr2: Dict[str, Any]) -> bool:
        """判断两个属性是否相似"""
        name1 = attr1['display_name'].lower()
        name2 = attr2['display_name'].lower()
        
        # 简单的相似性检测
        if name1 == name2:
            return True
        
        # 检查是否包含相同的关键词
        keywords1 = set(name1.split())
        keywords2 = set(name2.split())
        
        # 如果有超过50%的关键词重叠，认为相似
        if keywords1 and keywords2:
            overlap = len(keywords1.intersection(keywords2))
            total = len(keywords1.union(keywords2))
            similarity = overlap / total
            return similarity > 0.5
        
        return False
