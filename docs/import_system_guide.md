# 产品数据导入系统 - 安装和配置指南

## 系统概述

产品数据导入系统是一个完整的Django应用，为整木定制产品库管理系统提供强大的批量数据导入功能。系统支持产品、分类、品牌、属性等多种数据类型的导入，具有完善的数据验证、错误处理和进度追踪机制。

## 核心功能特性

### 🚀 主要功能
- **多格式支持**: 支持Excel(.xlsx, .xls)和CSV文件导入
- **智能模板**: 自动生成标准化的导入模板，包含字段说明和示例数据
- **数据验证**: 完整的数据验证机制，确保数据质量
- **错误处理**: 详细的错误报告和错误数据导出
- **进度追踪**: 实时导入进度监控和状态更新
- **批量处理**: 支持大批量数据的高效导入
- **Web界面**: 直观的Web管理界面
- **命令行工具**: 支持命令行批量导入

### 🎯 支持的数据类型
- **产品数据**: SKU、SPU、价格、库存、属性、尺寸等
- **分类数据**: 产品分类的树状结构管理
- **品牌数据**: 品牌信息和联系方式
- **属性数据**: 产品属性定义和属性值
- **混合数据**: 多种类型数据的混合导入

## 系统架构

### 📁 文件结构
```
products/
├── models/
│   ├── import_models.py         # 导入相关数据模型
│   └── __init__.py
├── services/
│   ├── import_service.py        # 核心导入服务
│   └── __init__.py
├── serializers/
│   ├── import_serializers.py    # API序列化器
│   └── __init__.py
├── views/
│   ├── import_views.py          # Web视图和API
│   └── __init__.py
├── admin/
│   ├── import_admin.py          # Django管理后台
│   └── __init__.py
├── utils/
│   ├── template_generator.py    # 模板生成器
│   └── __init__.py
├── config/
│   ├── import_config.py         # 系统配置
│   └── __init__.py
├── urls/
│   ├── import_urls.py           # URL路由配置
│   └── __init__.py
├── management/
│   └── commands/
│       ├── import_products.py   # 命令行导入工具
│       └── generate_templates.py # 模板生成命令
├── migrations/
│   └── 0002_import_models.py    # 数据库迁移文件
└── templates/
    └── import/
        └── import_page.html     # 导入页面模板
```

### 🏗️ 核心组件

#### 1. 数据模型 (models/import_models.py)
- **ImportTask**: 导入任务管理
- **ImportError**: 错误记录存储
- **ImportTemplate**: 模板配置管理

#### 2. 服务层 (services/import_service.py)
- **DataImportService**: 核心导入处理服务
- 数据解析、验证、转换和存储
- 错误处理和进度更新

#### 3. 模板生成器 (utils/template_generator.py)
- **ExcelTemplateGenerator**: 动态生成导入模板
- 支持多种数据类型的模板生成
- 包含字段说明和示例数据

## 安装步骤

### 1. 环境要求
- Python 3.8+
- Django 5.0+
- PostgreSQL 12+
- Redis 5.0+

### 2. 安装依赖
```bash
# 安装必要的Python包
pip install pandas openpyxl xlrd django-filter
```

### 3. 更新requirements.txt
在项目的`requirements.txt`文件中添加：
```
# 导入功能依赖
pandas==2.0.3
openpyxl==3.1.2
xlrd==2.0.1
```

### 4. 数据库迁移
```bash
# 创建和应用迁移
python manage.py makemigrations products
python manage.py migrate
```

### 5. 更新Django设置

#### 5.1 更新models/__init__.py
```python
from .import_models import ImportTask, ImportError, ImportTemplate
```

#### 5.2 更新admin/__init__.py
```python
from .import_admin import ImportTaskAdmin, ImportErrorAdmin, ImportTemplateAdmin
```

#### 5.3 更新主URL配置
在`product_library/urls.py`中添加：
```python
from django.urls import path, include

urlpatterns = [
    # ... 其他URL配置
    path('api/', include('products.urls.import_urls')),
    path('import/', TemplateView.as_view(template_name='import/import_page.html'), name='import_page'),
]
```

#### 5.4 更新settings.py
```python
# 文件上传配置
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 导入功能配置
IMPORT_CONFIG = {
    'MAX_FILE_SIZE': 10 * 1024 * 1024,  # 10MB
    'SUPPORTED_FORMATS': ['.xlsx', '.xls', '.csv'],
    'BATCH_SIZE': 100,
}

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/import.log',
        },
    },
    'loggers': {
        'products.services.import_service': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 使用指南

### 1. Web界面使用

#### 1.1 访问导入页面
```
http://localhost:8000/import/
```

#### 1.2 导入流程
1. **下载模板**: 选择对应的数据类型，下载标准模板
2. **准备数据**: 按照模板格式准备要导入的数据
3. **上传文件**: 选择文件并设置任务参数
4. **监控进度**: 实时查看导入进度和状态
5. **查看结果**: 导入完成后查看结果统计和错误报告

### 2. 命令行使用

#### 2.1 批量导入产品数据
```bash
# 导入产品数据
python manage.py import_products /path/to/products.xlsx --type=products --name="产品批量导入"

# 试运行模式
python manage.py import_products /path/to/products.xlsx --dry-run

# 详细输出
python manage.py import_products /path/to/products.xlsx --verbose
```

#### 2.2 生成导入模板
```bash
# 生成产品导入模板
python manage.py generate_templates --type=products --output=./templates/ --sample

# 生成所有类型的模板
python manage.py generate_templates --type=all --output=./templates/
```

### 3. API使用

#### 3.1 创建导入任务
```python
POST /api/import-tasks/
Content-Type: multipart/form-data

{
    "name": "产品数据导入",
    "task_type": "products",
    "file_path": <file>
}
```

#### 3.2 查询导入进度
```python
GET /api/import-tasks/{task_id}/progress/
```

#### 3.3 下载模板
```python
GET /api/import-templates/download_template/?type=products&sample=true
```

## 数据格式说明

### 1. 产品数据格式
| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| SKU编码 | 文本 | 是 | 产品的唯一标识 |
| SKU名称 | 文本 | 是 | 产品名称 |
| 分类编码 | 文本 | 是 | 产品分类编码 |
| 品牌编码 | 文本 | 是 | 品牌编码 |
| 价格 | 数字 | 是 | 销售价格 |
| 库存数量 | 数字 | 否 | 库存数量 |
| 属性_颜色 | 文本 | 否 | 产品颜色 |
| 尺寸_高度 | 数字 | 否 | 产品高度(mm) |

### 2. 分类数据格式
| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| 分类编码 | 文本 | 是 | 分类的唯一标识 |
| 分类名称 | 文本 | 是 | 分类名称 |
| 父分类编码 | 文本 | 否 | 上级分类编码 |
| 排序 | 数字 | 否 | 显示顺序 |

## 故障排除

### 1. 常见问题

#### Q1: 导入失败，提示"文件格式不支持"
**解决方案**:
- 确保文件格式为.xlsx、.xls或.csv
- 检查文件是否损坏
- 确认文件大小不超过10MB

#### Q2: 导入过程中出现编码错误
**解决方案**:
- 确保CSV文件使用UTF-8编码
- 对于Excel文件，使用较新版本的Excel保存

#### Q3: 导入速度较慢
**解决方案**:
- 检查数据量是否过大，可以分批导入
- 优化数据库索引
- 增加系统内存配置

#### Q4: 属性值导入失败
**解决方案**:
- 确保属性名称格式正确（如：属性_颜色）
- 检查属性值是否符合预定义的格式
- 查看错误报告获取详细信息

### 2. 日志查看
```bash
# 查看导入日志
tail -f logs/import.log

# 查看Django日志
tail -f logs/django.log
```

### 3. 数据库维护
```bash
# 清理失败的导入任务
python manage.py shell
>>> from products.models.import_models import ImportTask
>>> ImportTask.objects.filter(status='failed').delete()

# 重建索引
python manage.py dbshell
>>> REINDEX TABLE products_importtask;
```

## 性能优化

### 1. 数据库优化
```python
# settings.py
DATABASES = {
    'default': {
        # ... 其他配置
        'OPTIONS': {
            'MAX_CONNS': 20,
            'conn_max_age': 600,
        }
    }
}
```

### 2. 缓存配置
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### 3. 批量处理优化
```python
# 在import_config.py中调整批量大小
IMPORT_TASK_CONFIG = {
    'batch_size': 500,  # 增加批量大小
    'max_concurrent_tasks': 3,  # 减少并发任务数
}
```

## 安全考虑

### 1. 文件上传安全
- 限制文件大小和类型
- 扫描恶意文件
- 隔离上传文件存储

### 2. 权限控制
- 限制导入功能的访问权限
- 记录导入操作日志
- 定期清理敏感数据

### 3. 数据验证
- 严格的数据格式验证
- 防止SQL注入
- 限制批量操作的规模

## 扩展开发

### 1. 添加新的数据类型
1. 在`template_generator.py`中添加新的模板配置
2. 在`import_service.py`中添加对应的处理逻辑
3. 更新配置文件和URL路由

### 2. 自定义验证规则
```python
# 在import_service.py中添加自定义验证
def _validate_custom_field(self, value):
    # 自定义验证逻辑
    if not self._is_valid_custom_format(value):
        raise ValidationError("自定义字段格式不正确")
```

### 3. 集成外部API
```python
# 在import_service.py中添加外部API调用
def _sync_with_external_system(self, data):
    # 调用外部API同步数据
    response = requests.post(EXTERNAL_API_URL, json=data)
    return response.json()
```

## 技术支持

如需技术支持或有问题反馈，请联系开发团队或查看项目文档。

---

*最后更新时间: 2025年7月18日*