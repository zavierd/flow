"""
数据清理服务
负责安全地清空产品数据库
"""

import logging
from typing import Dict, Any, List
from django.db import transaction
from django.core.exceptions import ValidationError

from products.models import (
    SKU, SPU, SKUAttributeValue, SPUAttribute, 
    AttributeValue, Attribute, Brand, Category,
    ImportTask, ImportError, ProductsDimension, ProductsPricingRule
)

logger = logging.getLogger(__name__)


class DataCleaner:
    """数据清理器 - 单一职责：安全清理产品数据"""
    
    def __init__(self):
        self.deletion_stats = {}
        self.errors = []
    
    def clear_product_data(self, confirm: bool = False) -> Dict[str, Any]:
        """
        清空产品数据
        
        Args:
            confirm: 是否确认删除操作
            
        Returns:
            Dict: 清理结果统计
        """
        if not confirm:
            return {
                'success': False,
                'error': '危险操作：需要确认参数才能执行清理',
                'stats': {}
            }
        
        try:
            # 1. 统计当前数据
            current_stats = self._get_current_stats()
            logger.info(f"开始清理产品数据，当前统计: {current_stats}")
            
            # 2. 执行清理
            with transaction.atomic():
                deletion_stats = self._execute_cleanup()
            
            # 3. 验证清理结果
            final_stats = self._get_current_stats()
            
            result = {
                'success': True,
                'message': '产品数据清理完成',
                'before_stats': current_stats,
                'deletion_stats': deletion_stats,
                'after_stats': final_stats,
                'errors': self.errors
            }
            
            logger.info(f"产品数据清理完成: {deletion_stats}")
            return result
            
        except Exception as e:
            logger.error(f"产品数据清理失败: {str(e)}")
            return {
                'success': False,
                'error': f'清理失败: {str(e)}',
                'stats': self.deletion_stats,
                'errors': self.errors
            }
    
    def _get_current_stats(self) -> Dict[str, int]:
        """获取当前数据统计"""
        return {
            'sku_count': SKU.objects.count(),
            'spu_count': SPU.objects.count(),
            'attribute_count': Attribute.objects.count(),
            'attribute_value_count': AttributeValue.objects.count(),
            'sku_attribute_value_count': SKUAttributeValue.objects.count(),
            'spu_attribute_count': SPUAttribute.objects.count(),
            'brand_count': Brand.objects.count(),
            'category_count': Category.objects.count(),
            'import_task_count': ImportTask.objects.count(),
            'import_error_count': ImportError.objects.count(),
            'dimension_count': ProductsDimension.objects.count(),
            'pricing_rule_count': ProductsPricingRule.objects.count(),
        }
    
    def _execute_cleanup(self) -> Dict[str, int]:
        """执行清理操作"""
        deletion_stats = {}
        
        # 按依赖关系顺序删除数据
        cleanup_order = [
            ('SKU属性值关联', SKUAttributeValue),
            ('SPU属性关联', SPUAttribute),
            ('产品尺寸', ProductsDimension),
            ('产品定价规则', ProductsPricingRule),
            ('SKU产品', SKU),
            ('SPU产品', SPU),
            ('属性值', AttributeValue),
            ('属性', Attribute),
            ('品牌', Brand),
            ('产品分类', Category),
            ('导入错误', ImportError),
            ('导入任务', ImportTask),
        ]
        
        for name, model in cleanup_order:
            try:
                count = model.objects.count()
                if count > 0:
                    deleted_count = model.objects.all().delete()[0]
                    deletion_stats[name] = deleted_count
                    logger.info(f"删除{name}: {deleted_count}条记录")
                else:
                    deletion_stats[name] = 0
                    
            except Exception as e:
                error_msg = f"删除{name}失败: {str(e)}"
                self.errors.append(error_msg)
                logger.error(error_msg)
                deletion_stats[name] = 0
        
        return deletion_stats
    
    def clear_specific_data(self, data_types: List[str], confirm: bool = False) -> Dict[str, Any]:
        """
        清空特定类型的数据
        
        Args:
            data_types: 要清理的数据类型列表
            confirm: 是否确认删除操作
            
        Returns:
            Dict: 清理结果统计
        """
        if not confirm:
            return {
                'success': False,
                'error': '危险操作：需要确认参数才能执行清理',
                'stats': {}
            }
        
        # 数据类型映射
        type_mapping = {
            'sku': SKU,
            'spu': SPU,
            'attributes': Attribute,
            'attribute_values': AttributeValue,
            'brands': Brand,
            'categories': Category,
            'import_tasks': ImportTask,
            'import_errors': ImportError,
        }
        
        try:
            deletion_stats = {}
            
            with transaction.atomic():
                for data_type in data_types:
                    if data_type in type_mapping:
                        model = type_mapping[data_type]
                        count = model.objects.count()
                        if count > 0:
                            deleted_count = model.objects.all().delete()[0]
                            deletion_stats[data_type] = deleted_count
                            logger.info(f"删除{data_type}: {deleted_count}条记录")
                        else:
                            deletion_stats[data_type] = 0
                    else:
                        self.errors.append(f"未知的数据类型: {data_type}")
            
            return {
                'success': True,
                'message': f'指定数据清理完成: {", ".join(data_types)}',
                'deletion_stats': deletion_stats,
                'errors': self.errors
            }
            
        except Exception as e:
            logger.error(f"指定数据清理失败: {str(e)}")
            return {
                'success': False,
                'error': f'清理失败: {str(e)}',
                'stats': deletion_stats,
                'errors': self.errors
            }
    
    def get_data_summary(self) -> Dict[str, Any]:
        """获取数据摘要"""
        stats = self._get_current_stats()
        
        # 计算总数据量
        total_records = sum(stats.values())
        
        # 分类统计
        product_records = stats['sku_count'] + stats['spu_count']
        attribute_records = (stats['attribute_count'] + stats['attribute_value_count'] + 
                           stats['sku_attribute_value_count'] + stats['spu_attribute_count'])
        meta_records = stats['brand_count'] + stats['category_count']
        import_records = stats['import_task_count'] + stats['import_error_count']
        
        return {
            'total_records': total_records,
            'categories': {
                'products': {
                    'count': product_records,
                    'details': {
                        'sku': stats['sku_count'],
                        'spu': stats['spu_count']
                    }
                },
                'attributes': {
                    'count': attribute_records,
                    'details': {
                        'attributes': stats['attribute_count'],
                        'attribute_values': stats['attribute_value_count'],
                        'sku_relations': stats['sku_attribute_value_count'],
                        'spu_relations': stats['spu_attribute_count']
                    }
                },
                'metadata': {
                    'count': meta_records,
                    'details': {
                        'brands': stats['brand_count'],
                        'categories': stats['category_count']
                    }
                },
                'import_history': {
                    'count': import_records,
                    'details': {
                        'tasks': stats['import_task_count'],
                        'errors': stats['import_error_count']
                    }
                }
            },
            'raw_stats': stats
        }
