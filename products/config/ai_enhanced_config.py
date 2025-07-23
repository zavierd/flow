"""
AI增强功能配置
定义AI增强服务的配置参数和规则
"""

# AI功能默认配置
AI_FEATURES_DEFAULT = {
    'ai_quality_detection': False,      # 数据质量检测
    'ai_auto_classification': False,    # 自动分类
    'ai_smart_validation': False,       # 智能验证
    'ai_data_completion': False,        # 数据补全
    'ai_real_time_feedback': False,     # 实时反馈
}

# 数据质量检测配置
QUALITY_DETECTION_CONFIG = {
    # 价格检测配置
    'price_validation': {
        'enable_outlier_detection': True,
        'outlier_method': 'iqr',  # iqr, zscore
        'outlier_threshold': 1.5,
        'enable_logic_check': True,  # 检查价格递增逻辑
        'min_price': 0,
        'max_price': 100000,
    },

    # 尺寸检测配置
    'dimension_validation': {
        'width_range': (10, 300),
        'height_range': (50, 250),
        'depth_range': (30, 100),
        'standard_widths': [30, 40, 50, 60, 80, 90, 120],
        'standard_heights': [72, 90, 120],
        'standard_depths': [56, 60],
    },

    # 编码验证配置
    'code_validation': {
        'pattern': r'^N-[A-Z]+\d+(-\d+)?(-[A-Z/]+)?$',
        'required_prefix': 'N-',
        'enable_consistency_check': True,
    },

    # 质量评分配置
    'scoring': {
        'severity_weights': {
            'critical': 30,
            'high': 20,
            'medium': 10,
            'low': 5
        },
        'min_score': 0,
        'max_score': 100,
    }
}

# 自动分类配置
AUTO_CLASSIFICATION_CONFIG = {
    'enable_code_based': True,      # 基于编码的分类
    'enable_text_based': True,      # 基于文本的分类
    'confidence_threshold': 0.8,    # 置信度阈值
    'fallback_to_manual': True,     # 低置信度时回退到手动
}

# 智能验证配置
SMART_VALIDATION_CONFIG = {
    'enable_real_time': False,      # 实时验证（性能考虑）
    'batch_validation': True,       # 批量验证
    'validation_rules': [
        'required_fields',
        'format_validation',
        'business_rules',
        'consistency_check'
    ]
}

# 数据补全配置
DATA_COMPLETION_CONFIG = {
    'enable_auto_fill': True,       # 自动填充
    'fill_strategies': [
        'historical_data',          # 基于历史数据
        'business_rules',           # 基于业务规则
        'pattern_matching',         # 基于模式匹配
    ],
    'confidence_threshold': 0.9,    # 自动填充置信度阈值
}

# 实时反馈配置
REAL_TIME_FEEDBACK_CONFIG = {
    'enable_paste_validation': True,    # 粘贴时验证
    'enable_suggestions': True,         # 启用建议
    'debounce_delay': 500,             # 防抖延迟(ms)
    'max_suggestions': 5,              # 最大建议数
}

# AI服务配置
AI_SERVICE_CONFIG = {
    'quality_detection': QUALITY_DETECTION_CONFIG,
    'auto_classification': AUTO_CLASSIFICATION_CONFIG,
    'smart_validation': SMART_VALIDATION_CONFIG,
    'data_completion': DATA_COMPLETION_CONFIG,
    'real_time_feedback': REAL_TIME_FEEDBACK_CONFIG,
}

# 日志配置
AI_LOGGING_CONFIG = {
    'enable_performance_logging': True,
    'enable_error_logging': True,
    'log_level': 'INFO',
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}