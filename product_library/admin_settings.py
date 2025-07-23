# Django Admin 优化配置文件

from django.conf import settings

# Admin 性能优化设置
ADMIN_OPTIMIZATION = {
    # 基础性能设置
    'LIST_PER_PAGE': 25,  # 每页显示数量
    'LIST_MAX_SHOW_ALL': 100,  # "显示全部"最大数量
    'SHOW_FULL_RESULT_COUNT': False,  # 禁用完整结果计数
    
    # 大表分页设置
    'LARGE_TABLE_THRESHOLD': 10000,  # 大表阈值
    'USE_LARGE_TABLE_PAGINATOR': True,  # 启用大表分页器
    
    # 缓存设置
    'CACHE_TIMEOUT': 300,  # 缓存超时时间（秒）
    'ENABLE_FILTER_CACHE': True,  # 启用过滤器缓存
    'ENABLE_SEARCH_CACHE': True,  # 启用搜索缓存
    
    # 查询优化
    'AUTO_SELECT_RELATED': True,  # 自动优化select_related
    'AUTO_PREFETCH_RELATED': True,  # 自动优化prefetch_related
    'MAX_RELATED_DEPTH': 2,  # 最大关联深度
    
    # 界面优化
    'ENABLE_BULK_ACTIONS': True,  # 启用批量操作
    'ENABLE_QUICK_FILTERS': True,  # 启用快速过滤器
    'ENABLE_INLINE_EDITING': True,  # 启用内联编辑
    'ENABLE_AJAX_FORMS': True,  # 启用AJAX表单
    
    # 导出功能
    'ENABLE_EXPORT': True,  # 启用数据导出
    'EXPORT_FORMATS': ['csv', 'xlsx', 'json'],  # 支持的导出格式
    'MAX_EXPORT_ROWS': 5000,  # 最大导出行数
    
    # 安全设置
    'REQUIRE_CONFIRMATION_FOR_DELETE': True,  # 删除时需要确认
    'LOG_ADMIN_ACTIONS': True,  # 记录管理员操作
    'ENABLE_AUDIT_TRAIL': True,  # 启用审计跟踪
}

# 模型特定配置
MODEL_CONFIGS = {
    'products.Category': {
        'list_per_page': 50,
        'show_full_result_count': True,  # 分类较少，可以显示完整计数
        'enable_tree_optimization': True,
        'cache_tree_structure': True,
    },
    'products.Brand': {
        'list_per_page': 30,
        'enable_logo_optimization': True,
        'thumbnail_size': (50, 50),
    },
    'products.SPU': {
        'list_per_page': 20,
        'large_table_paginator': True,
        'enable_preview_mode': True,
    },
    'products.SKU': {
        'list_per_page': 15,
        'large_table_paginator': True,
        'enable_bulk_price_update': True,
        'enable_inventory_alerts': True,
    },
    'products.Attribute': {
        'list_per_page': 40,
        'enable_value_preview': True,
    },
    'products.AttributeValue': {
        'list_per_page': 50,
        'enable_color_preview': True,
        'enable_image_preview': True,
    },
}

# 用户权限配置
PERMISSION_CONFIGS = {
    'superuser': {
        'can_delete_all': True,
        'can_bulk_edit': True,
        'can_export_all': True,
        'can_view_analytics': True,
    },
    'manager': {
        'can_delete_own': True,
        'can_bulk_edit': True,
        'can_export_limited': True,
        'can_view_basic_analytics': True,
    },
    'editor': {
        'can_delete_own': False,
        'can_bulk_edit': False,
        'can_export_limited': True,
        'can_view_basic_analytics': False,
    },
    'viewer': {
        'can_delete_own': False,
        'can_bulk_edit': False,
        'can_export_limited': False,
        'can_view_basic_analytics': False,
    },
}

# 界面主题配置
THEME_CONFIGS = {
    'default': {
        'primary_color': '#667eea',
        'secondary_color': '#764ba2',
        'success_color': '#28a745',
        'warning_color': '#ffc107',
        'danger_color': '#dc3545',
        'info_color': '#17a2b8',
    },
    'dark': {
        'primary_color': '#4CAF50',
        'secondary_color': '#2196F3',
        'background_color': '#121212',
        'surface_color': '#1e1e1e',
        'text_color': '#ffffff',
    },
}

# 通知配置
NOTIFICATION_CONFIGS = {
    'enable_toast': True,
    'enable_email_notifications': True,
    'enable_browser_notifications': True,
    'notification_timeout': 5000,
    'max_notifications': 5,
}

# 搜索优化配置
SEARCH_CONFIGS = {
    'enable_fuzzy_search': True,
    'enable_autocomplete': True,
    'min_search_length': 2,
    'search_delay': 300,  # 毫秒
    'max_search_results': 100,
    'highlight_search_terms': True,
}

# 分析和报告配置
ANALYTICS_CONFIGS = {
    'enable_performance_monitoring': True,
    'enable_usage_analytics': True,
    'enable_error_tracking': True,
    'report_generation_interval': 'daily',
    'keep_analytics_data_days': 90,
}

# 导入导出配置
IMPORT_EXPORT_CONFIGS = {
    'enable_import': True,
    'enable_export': True,
    'supported_formats': ['csv', 'xlsx', 'json', 'xml'],
    'max_import_rows': 10000,
    'validate_on_import': True,
    'backup_before_import': True,
}

# 移动端优化配置
MOBILE_CONFIGS = {
    'enable_responsive_design': True,
    'enable_touch_gestures': True,
    'mobile_list_per_page': 10,
    'enable_mobile_upload': True,
    'compress_images_for_mobile': True,
}

# 开发和调试配置
DEBUG_CONFIGS = {
    'enable_debug_toolbar': settings.DEBUG,
    'enable_sql_query_logging': settings.DEBUG,
    'enable_performance_profiling': settings.DEBUG,
    'show_template_debug': settings.DEBUG,
    'log_slow_queries': True,
    'slow_query_threshold': 1.0,  # 秒
}

# 备份和恢复配置
BACKUP_CONFIGS = {
    'enable_auto_backup': True,
    'backup_interval': 'daily',
    'backup_retention_days': 30,
    'backup_storage_path': 'backups/',
    'compress_backups': True,
}

# API配置
API_CONFIGS = {
    'enable_rest_api': True,
    'api_version': 'v1',
    'enable_api_documentation': True,
    'api_rate_limiting': True,
    'api_cache_timeout': 300,
}

def get_config(config_name, model_name=None):
    """
    获取配置值
    
    Args:
        config_name: 配置名称
        model_name: 模型名称（可选）
    
    Returns:
        配置值
    """
    if model_name and model_name in MODEL_CONFIGS:
        model_config = MODEL_CONFIGS[model_name]
        if config_name in model_config:
            return model_config[config_name]
    
    # 从全局配置中获取
    all_configs = {
        **ADMIN_OPTIMIZATION,
        **THEME_CONFIGS['default'],
        **NOTIFICATION_CONFIGS,
        **SEARCH_CONFIGS,
        **ANALYTICS_CONFIGS,
        **IMPORT_EXPORT_CONFIGS,
        **MOBILE_CONFIGS,
        **DEBUG_CONFIGS,
        **BACKUP_CONFIGS,
        **API_CONFIGS,
    }
    
    return all_configs.get(config_name)

def get_user_permissions(user):
    """
    根据用户获取权限配置
    
    Args:
        user: Django用户对象
    
    Returns:
        权限配置字典
    """
    if user.is_superuser:
        return PERMISSION_CONFIGS['superuser']
    elif user.groups.filter(name='managers').exists():
        return PERMISSION_CONFIGS['manager']
    elif user.groups.filter(name='editors').exists():
        return PERMISSION_CONFIGS['editor']
    else:
        return PERMISSION_CONFIGS['viewer']

def should_use_large_table_paginator(model_class):
    """
    判断是否应该使用大表分页器
    
    Args:
        model_class: Django模型类
    
    Returns:
        布尔值
    """
    if not get_config('USE_LARGE_TABLE_PAGINATOR'):
        return False
    
    model_name = f"{model_class._meta.app_label}.{model_class._meta.model_name}"
    model_config = MODEL_CONFIGS.get(model_name, {})
    
    if 'large_table_paginator' in model_config:
        return model_config['large_table_paginator']
    
    # 根据表大小自动判断
    try:
        count = model_class.objects.count()
        return count > get_config('LARGE_TABLE_THRESHOLD')
    except:
        return False 