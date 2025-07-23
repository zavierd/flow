"""
智能属性处理器
集成AI服务，处理未定义属性的智能识别和映射
"""

import logging
from typing import Dict, Any, List
from .. import ProcessingContext, ProcessingStage, ProcessingStatus
from ...ai_services import AttributeAnalyzer, SmartAttributeMapper

logger = logging.getLogger(__name__)


class SmartAttributeProcessor:
    """智能属性处理器 - 处理未定义属性的完整流程"""
    
    def __init__(self):
        self.analyzer = AttributeAnalyzer()
        self.mapper = SmartAttributeMapper()
        self.enabled = True  # 可通过配置控制是否启用
        
    def process(self, context: ProcessingContext) -> ProcessingContext:
        """处理智能属性识别和映射"""
        if not self.enabled:
            logger.debug("智能属性处理器已禁用")
            return context
        
        try:
            import time
            start_time = time.time()
            
            # 1. 识别未定义属性
            logger.info(f"🔍 行{context.row_number}: 开始智能属性识别...")
            unknown_attributes = self.analyzer.identify_unknown_attributes(context.processed_data)
            
            if not unknown_attributes:
                logger.debug(f"行{context.row_number}: 未发现未定义属性")
                return context
            
            # 2. AI分析属性
            logger.info(f"🤖 行{context.row_number}: 启动AI分析 {len(unknown_attributes)} 个未定义属性...")
            analyzed_attributes = self.analyzer.analyze_attributes_batch(unknown_attributes, context.processed_data)
            
            if not analyzed_attributes:
                logger.warning(f"行{context.row_number}: AI分析未返回有效结果")
                return context
            
            # 3. 映射到产品
            logger.info(f"🔗 行{context.row_number}: 开始属性映射...")
            mapped_count = self._map_attributes_to_products(context, analyzed_attributes)
            
            # 4. 记录处理结果
            processing_time = time.time() - start_time
            
            # 更新上下文
            if 'smart_attributes' not in context.processing_metrics:
                context.processing_metrics['smart_attributes'] = {}
            
            context.processing_metrics['smart_attributes'].update({
                'unknown_count': len(unknown_attributes),
                'analyzed_count': len(analyzed_attributes),
                'mapped_count': mapped_count,
                'processing_time': processing_time,
                'analysis_summary': self.analyzer.get_analysis_summary(analyzed_attributes)
            })
            
            logger.info(f"✅ 行{context.row_number}: 智能属性处理完成 (耗时 {processing_time:.3f}s, 映射 {mapped_count} 个属性)")
            
            return context
            
        except Exception as e:
            logger.error(f"❌ 行{context.row_number}: 智能属性处理失败: {str(e)}")
            # 不影响主流程，继续处理
            return context
    
    def _map_attributes_to_products(self, context: ProcessingContext, analyzed_attributes: List[Dict[str, Any]]) -> int:
        """将分析的属性映射到产品"""
        total_mapped = 0
        
        # 获取创建的产品对象
        skus = context.created_objects.get('skus', [])
        spu = context.created_objects.get('spu')
        
        if not skus or not spu:
            logger.warning("缺少产品对象，无法进行属性映射")
            return 0
        
        # 为每个SKU映射属性
        for sku in skus:
            try:
                mapped_count = self.mapper.map_attributes_to_sku(sku, spu, analyzed_attributes)
                total_mapped += mapped_count
                logger.debug(f"🏷️ SKU {sku.code}: 映射 {mapped_count} 个智能属性")
                
            except Exception as e:
                logger.warning(f"SKU {sku.code} 属性映射失败: {str(e)}")
        
        return total_mapped
    
    def can_process(self, context: ProcessingContext) -> bool:
        """判断是否可以处理"""
        return (
            self.enabled and
            context.processed_data is not None and
            context.created_objects is not None and
            context.status != ProcessingStatus.FAILED
        )
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        return {
            'enabled': self.enabled,
            'analyzer_available': self.analyzer.ai_service.is_available(),
            'mapper_stats': self.mapper.get_mapping_statistics()
        }
    
    def enable(self):
        """启用智能属性处理"""
        self.enabled = True
        logger.info("✅ 智能属性处理器已启用")
    
    def disable(self):
        """禁用智能属性处理"""
        self.enabled = False
        logger.info("⚠️ 智能属性处理器已禁用")
    
    def clear_cache(self):
        """清空缓存"""
        self.mapper.clear_cache()
        logger.debug("🧹 清空智能属性处理器缓存")
    
    def optimize_attributes(self, context: ProcessingContext) -> Dict[str, Any]:
        """优化属性（合并相似属性等）"""
        if 'smart_attributes' not in context.processing_metrics:
            return {'message': '没有智能属性数据可优化'}
        
        # 获取分析的属性
        analyzed_attributes = context.processing_metrics['smart_attributes'].get('analyzed_attributes', [])
        
        if not analyzed_attributes:
            return {'message': '没有分析的属性数据'}
        
        # 执行优化
        optimization_result = self.mapper.batch_optimize_attributes(analyzed_attributes)
        
        logger.info(f"🔧 属性优化完成: {optimization_result}")
        return optimization_result


class SmartAttributeConfig:
    """智能属性处理配置"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        'enabled': True,
        'confidence_threshold': 0.7,
        'max_attributes_per_row': 10,
        'enable_optimization': True,
        'cache_results': True,
        'fallback_to_default': True
    }
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """获取配置"""
        from django.conf import settings
        
        # 从Django设置中获取配置
        smart_attr_config = getattr(settings, 'SMART_ATTRIBUTE_CONFIG', {})
        
        # 合并默认配置
        config = cls.DEFAULT_CONFIG.copy()
        config.update(smart_attr_config)
        
        return config
    
    @classmethod
    def is_enabled(cls) -> bool:
        """检查是否启用智能属性处理"""
        return cls.get_config().get('enabled', True)
    
    @classmethod
    def get_confidence_threshold(cls) -> float:
        """获取置信度阈值"""
        return cls.get_config().get('confidence_threshold', 0.7)


# 全局智能属性处理器实例
_smart_processor_instance = None

def get_smart_attribute_processor() -> SmartAttributeProcessor:
    """获取智能属性处理器单例"""
    global _smart_processor_instance
    
    if _smart_processor_instance is None:
        _smart_processor_instance = SmartAttributeProcessor()
        
        # 根据配置设置状态
        if not SmartAttributeConfig.is_enabled():
            _smart_processor_instance.disable()
    
    return _smart_processor_instance
