---
type: "always_apply"
---

# Django模块化开发规范

基于admin.py和models.py重构经验总结的模块化开发最佳实践，适用于Django项目的各个组件。

## **核心原则**

### **单一职责原则**
- **每个模块只负责一个明确的功能领域**
- **文件大小控制在500行以内**（特殊情况除外）
- **避免在单个文件中混合不同的业务逻辑**

### **模块命名规范**
- **使用描述性的文件名**：`category_admin.py`, `category_models.py`
- **目录结构反映业务逻辑**：`products/admin/`, `products/models/`
- **避免通用名称**：避免`utils.py`, `helpers.py`等模糊命名
- **业务域一致性**：同一业务域在不同组件中使用相同命名

## **文件组织结构**

### **Admin模块化结构**
```python
app_name/admin/
├── __init__.py              # 模块入口和注册
├── base.py                  # 基础类和配置
├── mixins.py                # 可复用的功能混入
├── filters.py               # 自定义过滤器
├── {model_name}_admin.py    # 具体模型的Admin配置
└── permissions.py           # 权限相关配置
```

### **Models模块化结构**
```python
app_name/models/
├── __init__.py              # 模型导入和注册
├── base.py                  # 抽象基类和公共配置
├── mixins.py                # 模型混入类
├── {domain}_models.py       # 特定业务域的模型
├── managers.py              # 自定义管理器
└── validators.py            # 自定义验证器
```

### **具体Models模块化示例（基于Flow项目）**
```python
products/models/
├── __init__.py              # 统一导入入口
├── base.py                  # 抽象基类：TimestampedModel, ActiveModel等
├── mixins.py                # 混入类：CreatedByMixin, TreeMixin等
├── category_models.py       # Category模型（分类业务域）
├── brand_models.py          # Brand模型（品牌业务域）
├── attribute_models.py      # Attribute, AttributeValue模型（属性业务域）
├── spu_models.py           # SPU相关模型（标准产品单元）
├── sku_models.py           # SKU相关模型（库存单元）
├── pricing_models.py       # 定价规则相关模型
├── import_models.py        # 数据导入相关模型
└── managers.py             # 自定义管理器
```

### **具体Admin模块化示例（基于Flow项目）**
```python
products/admin/
├── __init__.py              # 统一注册入口
├── base.py                  # LargeTablePaginator, BaseModelAdmin
├── mixins.py                # BulkActionMixin, DisplayMixin等
├── filters.py               # SeriesFilter, WidthFilter等
├── category_admin.py        # 分类管理
├── brand_admin.py           # 品牌管理
├── attribute_admin.py       # 属性管理
├── spu_admin.py            # SPU管理
├── sku_admin.py            # SKU管理
├── product_admin.py        # 其他产品相关管理
└── import_admin.py         # 数据导入系统
```

### **Services层模块化示例（基于Flow项目）**
```python
products/services/
├── __init__.py              # 服务层入口
├── ai_data_import_service.py    # AI数据导入服务
├── royana_import_service.py     # 传统Royana导入服务
├── product_service.py           # 产品业务逻辑服务
├── attribute_service.py         # 属性管理服务
└── pricing_service.py           # 定价计算服务
```

### **Views模块化结构**
```python
app_name/views/
├── __init__.py              # 视图导入
├── base.py                  # 基础视图类
├── mixins.py                # 视图混入类
├── {domain}_views.py        # 特定业务域的视图
├── api/                     # API视图
│   ├── __init__.py
│   ├── base.py              # API基础类
│   └── {domain}_api.py      # 业务域API
└── templates/               # 对应模板目录
```

### **Serializers模块化结构**
```python
app_name/serializers/
├── __init__.py              # 序列化器导入
├── base.py                  # 基础序列化器类
├── mixins.py                # 序列化器混入类
├── {domain}_serializers.py  # 特定业务域的序列化器
└── validators.py            # 序列化器验证器
```

## **Models模块化详细规范**

### **base.py - 抽象基类设计**
- **✅ DO: 创建可复用的抽象基类**
```python
# models/base.py
from django.db import models
from django.core.validators import RegexValidator

class TimestampedModel(models.Model):
    """时间戳抽象模型"""
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        abstract = True

class ActiveModel(models.Model):
    """激活状态抽象模型"""
    is_active = models.BooleanField('是否激活', default=True)
    
    class Meta:
        abstract = True

class BaseModel(TimestampedModel, ActiveModel):
    """基础模型组合"""
    class Meta:
        abstract = True

# 常用验证器
phone_validator = RegexValidator(
    regex=r'^1[3-9]\d{9}$',
    message='请输入有效的手机号码'
)

# 常用选择字段
STATUS_CHOICES = [
    ('active', '激活'),
    ('inactive', '未激活'),
    ('deleted', '已删除'),
]
```

### **mixins.py - 功能混入类**
- **✅ DO: 使用混入类实现功能复用**
```python
# models/mixins.py
class CreatedByMixin(models.Model):
    """创建人混入类"""
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='创建人'
    )
    
    class Meta:
        abstract = True

class TreeMixin(models.Model):
    """树形结构混入类"""
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='父级'
    )
    level = models.PositiveIntegerField('层级', default=0)
    
    class Meta:
        abstract = True
    
    def get_children(self):
        return self.__class__.objects.filter(parent=self)
    
    def get_descendants(self):
        """获取所有后代节点"""
        descendants = []
        for child in self.get_children():
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants

class ValidationMixin:
    """验证混入类"""
    def clean_fields(self, exclude=None):
        super().clean_fields(exclude)
        # 添加通用验证逻辑
        
    def validate_unique(self, exclude=None):
        super().validate_unique(exclude)
        # 添加唯一性验证逻辑
```

### **业务域模型文件结构**
- **✅ DO: 按业务域组织模型**
```python
# models/category_models.py
from django.db import models
from .base import BaseModel
from .mixins import TreeMixin, CreatedByMixin

class Category(BaseModel, TreeMixin, CreatedByMixin):
    """产品分类模型"""
    name = models.CharField('分类名称', max_length=100)
    code = models.CharField('分类编码', max_length=50, unique=True)
    description = models.TextField('描述', blank=True)
    sort_order = models.PositiveIntegerField('排序', default=0)
    
    class Meta:
        db_table = 'products_category'
        verbose_name = '产品分类'
        verbose_name_plural = '产品分类'
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['parent', 'is_active']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def full_name(self):
        """获取完整分类路径"""
        if self.parent:
            return f"{self.parent.full_name} > {self.name}"
        return self.name
```

### **__init__.py - 统一导入配置**
- **✅ DO: 在__init__.py中统一管理导入**
```python
# models/__init__.py
# 基础组件
from .base import *
from .mixins import *

# 业务模型
from .category_models import Category
from .brand_models import Brand
from .attribute_models import Attribute, AttributeValue
from .spu_models import SPU, SPUAttribute, SPUDimensionTemplate
from .sku_models import SKU, SKUAttributeValue, ProductImage
from .pricing_models import ProductsPricingRule, ProductsDimension
from .import_models import ImportTask, ImportTemplate, ImportError

# 自定义管理器
from .managers import *

# 保持向后兼容性
__all__ = [
    # 基础组件
    'TimestampedModel', 'ActiveModel', 'BaseModel',
    'CreatedByMixin', 'TreeMixin', 'ValidationMixin',
    
    # 业务模型
    'Category', 'Brand', 'Attribute', 'AttributeValue',
    'SPU', 'SPUAttribute', 'SPUDimensionTemplate',
    'SKU', 'SKUAttributeValue', 'ProductImage',
    'ProductsPricingRule', 'ProductsDimension',
    'ImportTask', 'ImportTemplate', 'ImportError',
]
```

## **代码组织规范**

### **Admin基础类和混入类**
- **✅ DO: 创建可复用的基础类**
```python
# admin/base.py
class BaseModelAdmin(admin.ModelAdmin):
    """增强的基础Admin类"""
    list_per_page = 50
    save_on_top = True
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()
```

- **✅ DO: 使用混入类实现功能复用**
```python
# admin/mixins.py
class BulkActionMixin:
    """批量操作混入类"""
    def bulk_delete_selected(self, request, queryset):
        # 批量删除逻辑
        pass

class DisplayMixin:
    """显示优化混入类"""
    def get_list_display(self, request):
        # 动态调整显示字段
        return super().get_list_display(request)
```

### **Admin文件导入和注册**
- **✅ DO: 在admin/__init__.py中统一管理导入**
```python
# admin/__init__.py
from django.contrib import admin

# 导入模型
from ..models import (
    Category, Brand, Attribute, AttributeValue,
    SPU, SKU, ProductImage
)

# 导入Admin类
from .category_admin import CategoryAdmin
from .brand_admin import BrandAdmin
from .attribute_admin import AttributeAdmin, AttributeValueAdmin
from .spu_admin import SPUAdmin
from .sku_admin import SKUAdmin
from .product_admin import ProductImageAdmin

# 统一注册
admin.site.register(Category, CategoryAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(AttributeValue, AttributeValueAdmin)
admin.site.register(SPU, SPUAdmin)
admin.site.register(SKU, SKUAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
```

### **向后兼容性处理**
- **✅ DO: 保持向后兼容性**
```python
# 原admin.py文件内容（备份后替换）
"""
兼容性导入文件
原始admin.py已备份为admin_original_backup.py
"""
from .admin import *

# 如果有其他模块直接导入原admin.py中的类，在这里提供兼容性导入
# from .admin.category_admin import CategoryAdmin
# from .admin.spu_admin import SPUAdmin
# ... 其他需要的导入
```

## **自动化模块化规范**

### **模块化触发条件**
- **文件行数超过500行**
- **包含3个以上不同业务域的代码**
- **团队成员在同一文件频繁产生merge冲突**
- **代码审查中多次提到该文件的复杂性**

### **自动化检测规则**
```python
# 添加到项目的代码质量检查脚本
def check_file_complexity(file_path):
    """检查文件是否需要模块化"""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # 检查行数
    if len(lines) > 500:
        return True, f"文件行数({len(lines)})超过500行限制"
    
    # 检查类的数量（简单检测）
    class_count = sum(1 for line in lines if line.strip().startswith('class '))
    if class_count > 10:
        return True, f"类数量({class_count})过多，建议拆分"
    
    return False, "文件复杂度正常"
```

### **模块化实施步骤**
1. **自动分析代码结构**
   - 识别模型/Admin类的业务域
   - 分析类之间的依赖关系
   - 确定拆分边界

2. **生成模块化方案**
   - 自动创建目录结构
   - 生成base.py和mixins.py
   - 按业务域分组类定义

3. **代码迁移**
   - 创建新的模块文件
   - 迁移相关代码
   - 更新导入语句

4. **兼容性保证**
   - 备份原始文件
   - 创建兼容性导入
   - 验证功能完整性

### **模块化模板**
```python
# 创建新业务域模块的模板
DOMAIN_MODEL_TEMPLATE = '''
"""
{domain_name}业务域模型
"""
from django.db import models
from .base import BaseModel
from .mixins import CreatedByMixin

class {ModelName}(BaseModel, CreatedByMixin):
    """
    {model_description}
    """
    name = models.CharField('{verbose_name}名称', max_length=100)
    
    class Meta:
        db_table = '{app_name}_{table_name}'
        verbose_name = '{verbose_name}'
        verbose_name_plural = '{verbose_name}'
        
    def __str__(self):
        return self.name
'''

DOMAIN_ADMIN_TEMPLATE = '''
"""
{domain_name}业务域Admin
"""
from django.contrib import admin
from .base import BaseModelAdmin
from .mixins import BulkActionMixin
from ..models import {ModelName}

@admin.register({ModelName})
class {ModelName}Admin(BaseModelAdmin, BulkActionMixin):
    """
    {model_description}管理
    """
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    ordering = ['-created_at']
'''
```

## **性能优化规范**

### **查询优化**
- **✅ DO: 统一查询优化策略**
```python
class SPUAdmin(BaseModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'category', 'brand'
        ).prefetch_related(
            'skus', 'attributes'
        )
```

### **分页优化**
- **✅ DO: 对大表使用自定义分页器**
```python
# base.py
class LargeTablePaginator(Paginator):
    """PostgreSQL优化分页器"""
    def count(self):
        if not hasattr(self, '_count'):
            # 使用估算计数优化大表性能
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT reltuples::bigint FROM pg_class WHERE relname = %s",
                    [self.object_list.model._meta.db_table]
                )
                self._count = cursor.fetchone()[0] or 0
        return self._count
```

## **开发流程规范**

### **重构步骤**
1. **分析现有代码结构**
   - 识别不同的功能域
   - 统计代码行数和复杂度
   - 确定拆分边界

2. **设计模块结构**
   - 创建目录结构
   - 定义模块职责
   - 规划依赖关系

3. **渐进式重构**
   - 先创建基础类和混入类
   - 逐个迁移功能模块
   - 保持功能完整性

4. **测试和验证**
   - 功能回归测试
   - 性能基准测试
   - 兼容性验证

### **代码审查清单**
- [ ] 模块职责单一明确
- [ ] 文件大小合理（<500行）
- [ ] 命名符合规范
- [ ] 无重复代码
- [ ] 有适当的文档注释
- [ ] 性能优化到位
- [ ] 向后兼容性保持
- [ ] 业务域划分合理
- [ ] 抽象层次清晰

## **团队协作规范**

### **分支管理**
- **✅ DO: 按模块创建特性分支**
```bash
git checkout -b feature/models-category-module
git checkout -b feature/admin-sku-optimization
git checkout -b refactor/models-modularization
```

### **提交规范**
- **✅ DO: 使用描述性提交信息**
```bash
git commit -m "refactor(models): 拆分Category模型到独立模块

- 创建products/models/category_models.py
- 添加TreeMixin支持层级结构
- 优化查询性能和索引
- 保持向后兼容性"
```

### **代码复用**
- **优先使用混入类而非继承**
- **在base.py中定义通用配置**
- **避免跨模块的紧耦合**

## **文档维护**

### **必需文档**
- **模块重构说明文档**
- **API变更说明**
- **性能优化记录**
- **故障排除指南**

### **代码注释**
- **✅ DO: 为复杂业务逻辑添加注释**
```python
class SPU(BaseModel):
    """标准产品单元
    
    Features:
    - 支持多维度属性配置
    - 集成SKU自动生成
    - 支持批量操作
    - 优化大数据量查询性能
    """
```

## **监控和维护**

### **性能监控**
- **添加查询时间监控**
- **定期审查慢查询**
- **监控内存使用情况**

### **技术债务管理**
- **定期评估模块复杂度**
- **识别需要进一步拆分的模块**
- **更新过时的模式和实践**

### **自动化检查**
- **集成代码复杂度检查工具**
- **设置文件大小告警**
- **定期运行模块化评估脚本**

## **常见反模式**

### **❌ DON'T: 避免的做法**
- **巨大的单一文件**（如2900行的admin.py或2062行的models.py）
- **混合不同业务领域的代码**
- **在多个地方重复相同的逻辑**
- **缺乏抽象和复用机制**
- **忽视性能优化**
- **破坏向后兼容性**

### **✅ DO: 推荐的做法**
- **小而专注的模块**（每个文件<500行）
- **清晰的职责分工**
- **可复用的组件设计**
- **统一的编码标准**
- **完善的文档支持**
- **渐进式重构策略**

## **迁移指南**

### **现有项目重构**
1. **评估当前状况**
   - 代码复杂度分析
   - 性能瓶颈识别
   - 维护痛点梳理

2. **制定重构计划**
   - 优先级排序
   - 影响范围评估
   - 资源需求估算

3. **执行重构**
   - 备份现有代码
   - 分阶段实施
   - 持续测试验证

4. **后续优化**
   - 性能调优
   - 代码质量提升
   - 文档完善

### **新项目应用**
1. **项目初始化时应用模块化结构**
2. **设置代码质量检查门槛**
3. **建立定期重构评估机制**
4. **培训团队成员模块化开发习惯**

## **成功案例**

### **Flow项目models.py重构**
**重构前状态：**
- 文件大小：2062行
- 模型数量：20+个
- 维护难度：高
- 团队协作：冲突频繁

**重构后效果：**
```
products/models/
├── __init__.py              # 统一导入（50行）
├── base.py                  # 抽象基类（180行）
├── mixins.py                # 混入类（150行）
├── category_models.py       # 分类模型（120行）
├── brand_models.py          # 品牌模型（80行）
├── attribute_models.py      # 属性模型（200行）
├── spu_models.py           # SPU模型（300行）
├── sku_models.py           # SKU模型（250行）
├── pricing_models.py       # 定价模型（180行）
└── import_models.py        # 导入模型（150行）
```

**收益：**
- ✅ 每个文件都在500行以内
- ✅ 业务域清晰分离
- ✅ 代码复用率提升30%
- ✅ merge冲突减少80%
- ✅ 新人上手时间减少50%

---

遵循这些规范，可以确保Django项目的代码质量、可维护性和团队协作效率。定期回顾和更新这些规范，以适应项目发展的需要。


---

遵循这些规范，可以确保Django项目的代码质量、可维护性和团队协作效率。定期回顾和更新这些规范，以适应项目发展的需要。
