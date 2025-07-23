"""
AI功能开关管理
提供动态启用/禁用AI功能的机制，确保系统稳定性
"""

from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class AIFeatureFlags:
    """AI功能开关管理器"""

    # 功能开关键名
    QUALITY_DETECTION = 'ai_quality_detection'
    AUTO_CLASSIFICATION = 'ai_auto_classification'
    SMART_VALIDATION = 'ai_smart_validation'
    DATA_COMPLETION = 'ai_data_completion'
    REAL_TIME_FEEDBACK = 'ai_real_time_feedback'
    DEEPSEEK_INTEGRATION = 'ai_deepseek_integration'
    SMART_ATTRIBUTES = 'ai_smart_attributes'

    # 默认配置
    DEFAULT_FLAGS = {
        QUALITY_DETECTION: False,      # 数据质量检测
        AUTO_CLASSIFICATION: False,    # 自动分类
        SMART_VALIDATION: False,       # 智能验证
        DATA_COMPLETION: False,        # 数据补全
        REAL_TIME_FEEDBACK: False,     # 实时反馈
        DEEPSEEK_INTEGRATION: False,   # DeepSeek API集成
        SMART_ATTRIBUTES: False,       # 智能属性提取
    }

    @classmethod
    def is_enabled(cls, feature_name: str) -> bool:
        """检查功能是否启用"""
        try:
            # 优先从缓存获取
            cache_key = f'ai_feature_{feature_name}'
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"从缓存获取AI功能状态 {feature_name}: {cached_value}")
                return cached_value

            # 从设置获取
            ai_features = getattr(settings, 'AI_FEATURES', {})
            enabled = ai_features.get(feature_name, cls.DEFAULT_FLAGS.get(feature_name, False))

            logger.debug(f"从设置获取AI功能状态 {feature_name}: {enabled}")

            # 缓存结果（5分钟）
            cache.set(cache_key, enabled, 300)
            return enabled

        except Exception as e:
            logger.warning(f"获取AI功能开关失败 {feature_name}: {e}")
            return False

    @classmethod
    def enable_feature(cls, feature_name: str):
        """启用功能"""
        cache_key = f'ai_feature_{feature_name}'
        cache.set(cache_key, True, 300)
        logger.info(f"AI功能已启用: {feature_name}")

    @classmethod
    def disable_feature(cls, feature_name: str):
        """禁用功能"""
        cache_key = f'ai_feature_{feature_name}'
        cache.set(cache_key, False, 300)
        logger.info(f"AI功能已禁用: {feature_name}")

    @classmethod
    def get_all_flags(cls) -> dict:
        """获取所有功能开关状态"""
        return {
            flag: cls.is_enabled(flag)
            for flag in cls.DEFAULT_FLAGS.keys()
        }

    @classmethod
    def clear_cache(cls):
        """清除所有AI功能的缓存"""
        for flag_name in cls.DEFAULT_FLAGS.keys():
            cache_key = f'ai_feature_{flag_name}'
            cache.delete(cache_key)
        logger.info("AI功能缓存已清除")


def ai_feature_required(feature_name: str):
    """装饰器：检查AI功能是否启用"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if AIFeatureFlags.is_enabled(feature_name):
                return func(*args, **kwargs)
            else:
                logger.debug(f"AI功能未启用，跳过: {feature_name}")
                return None
        return wrapper
    return decorator


# 便捷函数
def is_quality_detection_enabled() -> bool:
    """数据质量检测是否启用"""
    return AIFeatureFlags.is_enabled(AIFeatureFlags.QUALITY_DETECTION)


def is_auto_classification_enabled() -> bool:
    """自动分类是否启用"""
    return AIFeatureFlags.is_enabled(AIFeatureFlags.AUTO_CLASSIFICATION)


def is_smart_validation_enabled() -> bool:
    """智能验证是否启用"""
    return AIFeatureFlags.is_enabled(AIFeatureFlags.SMART_VALIDATION)


def is_deepseek_integration_enabled() -> bool:
    """DeepSeek API集成是否启用"""
    return AIFeatureFlags.is_enabled(AIFeatureFlags.DEEPSEEK_INTEGRATION)


def is_smart_attributes_enabled() -> bool:
    """智能属性提取是否启用"""
    return AIFeatureFlags.is_enabled(AIFeatureFlags.SMART_ATTRIBUTES)