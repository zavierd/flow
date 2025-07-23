# 数据导入系统配置文件

# 支持的文件格式
SUPPORTED_FILE_FORMATS = ['.xlsx', '.xls', '.csv']

# 文件大小限制（字节）
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# 导入任务配置
IMPORT_TASK_CONFIG = {
    'max_concurrent_tasks': 5,  # 最大并发任务数
    'task_timeout': 3600,  # 任务超时时间（秒）
    'progress_update_interval': 2,  # 进度更新间隔（秒）
    'batch_size': 100,  # 批量处理大小
    'error_limit': 1000,  # 错误记录上限
}

# 数据验证配置
VALIDATION_CONFIG = {
    'required_fields': {
        'royana_products': ['code', 'description'],
    },
    'field_types': {
        'text': str,
        'number': float,
        'boolean': bool,
        'date': 'datetime',
        'enum': list,
    },
    'price_range': {
        'min': 0,
        'max': 999999.99,
    },
    'stock_range': {
        'min': 0,
        'max': 999999,
    }
}

# 模板配置
TEMPLATE_CONFIG = {
    'default_sheet_names': {
        'royana_products': '产品数据',
    },
    'field_descriptions_sheet': '字段说明',
    'enum_sheets': True,  # 是否生成枚举值工作表
    'include_sample_data': True,  # 默认包含示例数据
}

# 错误处理配置
ERROR_HANDLING_CONFIG = {
    'continue_on_error': True,  # 遇到错误时是否继续
    'log_all_errors': True,  # 是否记录所有错误
    'generate_error_report': True,  # 是否生成错误报告
    'error_report_format': 'csv',  # 错误报告格式
}

# 日志配置
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'import_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/import.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'products.services.import_service': {
            'handlers': ['import_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'products.utils.template_generator': {
            'handlers': ['import_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# 性能优化配置
PERFORMANCE_CONFIG = {
    'use_bulk_create': True,  # 使用批量创建
    'use_bulk_update': True,  # 使用批量更新
    'prefetch_related_objects': True,  # 预加载相关对象
    'cache_frequently_used_objects': True,  # 缓存常用对象
    'optimize_database_queries': True,  # 优化数据库查询
}

# 通知配置
NOTIFICATION_CONFIG = {
    'email_notifications': {
        'enabled': False,
        'recipients': [],
        'smtp_settings': {
            'host': 'smtp.example.com',
            'port': 587,
            'username': '',
            'password': '',
            'use_tls': True,
        }
    },
    'webhook_notifications': {
        'enabled': False,
        'url': '',
        'headers': {},
    }
}

# 安全配置
SECURITY_CONFIG = {
    'require_authentication': True,  # 需要认证
    'require_permission': True,  # 需要权限
    'allowed_file_extensions': SUPPORTED_FILE_FORMATS,
    'scan_uploaded_files': False,  # 是否扫描上传的文件
    'max_upload_size': MAX_FILE_SIZE,
    'rate_limiting': {
        'enabled': True,
        'max_requests_per_hour': 100,
    }
}

# 导出配置
EXPORT_CONFIG = {
    'default_format': 'xlsx',
    'include_metadata': True,
    'compress_large_files': True,
    'max_export_rows': 100000,
}