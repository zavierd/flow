"""
AI增强服务基类
为所有AI增强服务提供基础功能和接口
"""

import logging
from typing import Dict, List, Any, Optional
from django.conf import settings
from products.utils.ai_feature_flags import AIFeatureFlags, ai_feature_required

logger = logging.getLogger(__name__)


class BaseAIService:
    """AI增强服务基类"""

    def __init__(self):
        """初始化AI服务"""
        self.enabled = self._check_enabled()
        self.config = self._load_config()
        logger.debug(f"{self.__class__.__name__} 初始化完成，启用状态: {self.enabled}")

    def _check_enabled(self) -> bool:
        """检查服务是否启用"""
        # 子类应该覆盖此方法，指定对应的功能标志
        return False

    def _load_config(self) -> Dict[str, Any]:
        """加载服务配置"""
        # 子类可以覆盖此方法，加载特定配置
        return getattr(settings, 'AI_SERVICE_CONFIG', {})

    def process(self, data: Any) -> Optional[Dict[str, Any]]:
        """处理数据（主入口）"""
        if not self.enabled:
            logger.debug(f"{self.__class__.__name__} 服务未启用，跳过处理")
            return None

        try:
            return self._process_impl(data)
        except Exception as e:
            logger.error(f"{self.__class__.__name__} 处理失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'service': self.__class__.__name__
            }

    def _process_impl(self, data: Any) -> Dict[str, Any]:
        """实际处理逻辑（子类必须实现）"""
        raise NotImplementedError("子类必须实现_process_impl方法")

    @classmethod
    def get_service_info(cls) -> Dict[str, Any]:
        """获取服务信息"""
        return {
            'name': cls.__name__,
            'description': cls.__doc__,
            'enabled': cls()._check_enabled()
        }