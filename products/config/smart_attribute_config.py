"""
智能属性处理配置
管理AI智能属性识别和处理的各种配置选项
"""

# 智能属性处理全局配置
SMART_ATTRIBUTE_CONFIG = {
    # 基础配置
    'enabled': True,                    # 是否启用智能属性处理
    'use_real_ai': True,                # 是否使用真实AI服务（而非模拟）
    'confidence_threshold': 0.6,        # AI分析的最低置信度阈值（降低以接受更多结果）
    'max_attributes_per_row': 15,       # 每行数据最大处理的未知属性数量（增加以处理更多属性）
    'enable_optimization': True,        # 是否启用属性优化（合并相似属性等）
    'cache_results': True,              # 是否缓存处理结果
    'fallback_to_default': True,        # AI失败时是否降级到默认处理
    
    # AI服务配置
    'ai_service': {
        'provider': 'deepseek',         # AI服务提供商
        'timeout': 30,                  # API调用超时时间（秒）
        'max_retries': 3,               # 最大重试次数
        'retry_delay': 1,               # 重试延迟（秒）
    },
    
    # 属性分析配置
    'analysis': {
        'batch_size': 5,                # 批量分析的属性数量
        'enable_context_analysis': True, # 是否启用上下文分析
        'min_value_length': 1,          # 属性值的最小长度
        'max_value_length': 200,        # 属性值的最大长度
        'exclude_patterns': [           # 排除的属性名模式
            r'^temp_.*',                # 临时字段
            r'^_.*',                    # 私有字段
            r'.*_id$',                  # ID字段
        ]
    },
    
    # 属性映射配置
    'mapping': {
        'auto_create_attributes': True,  # 是否自动创建新属性
        'auto_create_values': True,      # 是否自动创建新属性值
        'merge_similar_attributes': True, # 是否合并相似属性
        'similarity_threshold': 0.8,     # 属性相似度阈值
        'default_attribute_order': 100,  # 默认属性排序起始值
    },
    
    # 性能配置
    'performance': {
        'enable_parallel_processing': False, # 是否启用并行处理
        'max_workers': 3,                   # 最大工作线程数
        'memory_limit_mb': 100,             # 内存使用限制（MB）
        'processing_timeout': 60,           # 单行处理超时时间（秒）
    },
    
    # 日志配置
    'logging': {
        'log_level': 'INFO',            # 日志级别
        'log_ai_requests': True,        # 是否记录AI请求
        'log_analysis_results': True,   # 是否记录分析结果
        'log_mapping_details': False,   # 是否记录映射详情
    }
}

# 属性类型优先级配置
ATTRIBUTE_TYPE_PRIORITY = {
    'color': 5,      # 颜色类型优先级最高
    'select': 4,     # 选择类型
    'number': 3,     # 数字类型
    'boolean': 2,    # 布尔类型
    'text': 1        # 文本类型优先级最低
}

# 重要属性关键词配置
IMPORTANT_ATTRIBUTE_KEYWORDS = {
    # 高重要性（5分）
    'high': [
        '材质', '颜色', '风格', '等级', '品质',
        'material', 'color', 'style', 'grade', 'quality'
    ],
    
    # 中高重要性（4分）
    'medium_high': [
        '品牌', '系列', '型号', '规格', '尺寸',
        'brand', 'series', 'model', 'spec', 'size'
    ],
    
    # 中等重要性（3分）
    'medium': [
        '厚度', '重量', '产地', '工艺', '配置',
        'thickness', 'weight', 'origin', 'craft', 'config'
    ],
    
    # 低重要性（2分）
    'low': [
        '包装', '备注', '说明', '附件', '配件',
        'package', 'remark', 'note', 'accessory', 'component'
    ]
}

# 可筛选属性关键词配置
FILTERABLE_ATTRIBUTE_KEYWORDS = [
    '材质', '颜色', '风格', '等级', '品牌', '系列', '类型', '规格',
    'material', 'color', 'style', 'grade', 'brand', 'series', 'type', 'spec'
]

# 属性值标准化规则
ATTRIBUTE_VALUE_NORMALIZATION_RULES = {
    # 材质标准化
    'material': {
        '实木': '实木材质',
        '颗粒板': '实木颗粒板',
        '密度板': '中密度纤维板',
        'MDF': '中密度纤维板',
        'OSB': '定向刨花板',
        '胶合板': '多层胶合板',
        '刨花板': '刨花板材',
    },
    
    # 颜色标准化
    'color': {
        '白': '纯白色',
        '黑': '经典黑',
        '灰': '高级灰',
        '木色': '原木色',
        '胡桃': '胡桃木色',
        '樱桃': '樱桃木色',
        '橡木': '橡木色',
    },
    
    # 风格标准化
    'style': {
        '现代': '现代简约',
        '简约': '现代简约',
        '欧式': '欧式古典',
        '中式': '新中式',
        '美式': '美式乡村',
        '北欧': '北欧风格',
        '工业': '工业风格',
    },
    
    # 等级标准化
    'grade': {
        'E0': 'E0级环保',
        'E1': 'E1级环保',
        'E2': 'E2级环保',
        'F4星': 'F4星级',
        'CARB': 'CARB认证',
    }
}

# AI提示词模板配置
AI_PROMPT_TEMPLATES = {
    # 基础属性分析模板
    'basic_analysis': """
作为产品属性专家，请分析以下产品属性信息：

属性名: {attr_name}
属性值: {attr_value}

产品上下文信息:
- 产品描述: {product_desc}
- 产品系列: {series}
- 类型代码: {type_code}

请提供以下分析结果：
1. 标准化的属性显示名称（更专业和规范的名称）
2. 标准化的属性值（统一格式和术语）
3. 属性类型（text/number/select/boolean/color）
4. 是否应该作为可筛选属性（true/false）
5. 属性的重要程度（1-5，5最高）
6. 分析置信度（0-1）

请以JSON格式返回，包含字段：display_name, display_value, attribute_type, filterable, importance, confidence
""",
    
    # 批量属性分析模板
    'batch_analysis': """
作为产品属性专家，请批量分析以下产品属性信息：

产品上下文: {product_context}

属性列表:
{attributes_list}

请为每个属性提供标准化的分析结果，以JSON数组格式返回。
""",
    
    # 属性优化模板
    'optimization': """
请分析以下属性列表，识别可以合并的相似属性：

{attributes_data}

请提供优化建议，包括：
1. 可以合并的相似属性组
2. 建议的标准属性名称
3. 属性值的标准化建议

以JSON格式返回优化建议。
"""
}

# 错误处理配置
ERROR_HANDLING_CONFIG = {
    'max_errors_per_row': 5,        # 每行最大错误数
    'continue_on_error': True,      # 出错时是否继续处理
    'log_all_errors': True,         # 是否记录所有错误
    'fallback_strategies': [        # 降级策略
        'use_default_analysis',
        'skip_attribute',
        'use_original_value'
    ]
}

# 缓存配置
CACHE_CONFIG = {
    'enable_attribute_cache': True,     # 启用属性缓存
    'enable_value_cache': True,         # 启用属性值缓存
    'cache_ttl': 3600,                  # 缓存过期时间（秒）
    'max_cache_size': 1000,             # 最大缓存条目数
    'cache_key_prefix': 'smart_attr_',  # 缓存键前缀
}
