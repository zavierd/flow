#!/usr/bin/env python3
"""
Django自动模块化重构工具

基于.cursor/rules/django_modular_development.mdc规范
自动执行Django文件的模块化重构
"""

import os
import re
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict


class AutoModularizer:
    """自动模块化重构器"""
    
    def __init__(self, project_root: str, dry_run: bool = False):
        self.project_root = Path(project_root)
        self.dry_run = dry_run
        self.backup_dir = self.project_root / '.modularization_backup'
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """加载代码模板"""
        return {
            'models_init': '''"""
统一模型导入入口
基于django_modular_development.mdc规范自动生成
"""

# 基础组件
from .base import *
from .mixins import *

# 业务模型
{model_imports}

# 自定义管理器
try:
    from .managers import *
except ImportError:
    pass

# 保持向后兼容性
__all__ = [
    # 基础组件
    'TimestampedModel', 'ActiveModel', 'BaseModel',
    'CreatedByMixin', 'TreeMixin', 'ValidationMixin',
    
    # 业务模型
{model_all_list}
]
''',
            
            'models_base': '''"""
模型基础类和公共配置
基于django_modular_development.mdc规范自动生成
"""

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


class OrderedModel(models.Model):
    """排序抽象模型"""
    sort_order = models.PositiveIntegerField('排序', default=0)
    
    class Meta:
        abstract = True


class DescribedModel(models.Model):
    """描述抽象模型"""
    description = models.TextField('描述', blank=True)
    
    class Meta:
        abstract = True


class CodedModel(models.Model):
    """编码抽象模型"""
    code = models.CharField('编码', max_length=50, unique=True)
    
    class Meta:
        abstract = True


class BaseModel(TimestampedModel, ActiveModel):
    """基础模型组合"""
    class Meta:
        abstract = True


class StandardModel(BaseModel, OrderedModel, DescribedModel):
    """标准模型组合"""
    name = models.CharField('名称', max_length=100)
    
    class Meta:
        abstract = True
    
    def __str__(self):
        return self.name


# 常用验证器
phone_validator = RegexValidator(
    regex=r'^1[3-9]\\d{9}$',
    message='请输入有效的手机号码'
)

email_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$',
    message='请输入有效的邮箱地址'
)

# 常用选择字段
STATUS_CHOICES = [
    ('active', '激活'),
    ('inactive', '未激活'),
    ('deleted', '已删除'),
]

GENDER_CHOICES = [
    ('M', '男'),
    ('F', '女'),
    ('U', '未知'),
]
''',

            'models_mixins': '''"""
模型混入类
基于django_modular_development.mdc规范自动生成
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class CreatedByMixin(models.Model):
    """创建人混入类"""
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='创建人',
        related_name='%(app_label)s_%(class)s_created'
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
        """获取直接子节点"""
        return self.__class__.objects.filter(parent=self)
    
    def get_descendants(self):
        """获取所有后代节点"""
        descendants = []
        for child in self.get_children():
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants
    
    def get_ancestors(self):
        """获取所有祖先节点"""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors
    
    @property
    def full_path(self):
        """获取完整路径"""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return getattr(self, 'name', str(self))


class PriceMixin(models.Model):
    """价格相关混入类"""
    price = models.DecimalField('价格', max_digits=10, decimal_places=2, default=0)
    original_price = models.DecimalField('原价', max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField('成本价', max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        abstract = True
    
    @property
    def discount_rate(self):
        """折扣率"""
        if self.original_price and self.original_price > 0:
            return (self.original_price - self.price) / self.original_price * 100
        return 0
    
    @property
    def profit_margin(self):
        """利润率"""
        if self.cost_price and self.cost_price > 0:
            return (self.price - self.cost_price) / self.price * 100
        return 0


class StockMixin(models.Model):
    """库存相关混入类"""
    stock_quantity = models.PositiveIntegerField('库存数量', default=0)
    reserved_quantity = models.PositiveIntegerField('预留数量', default=0)
    sold_quantity = models.PositiveIntegerField('已售数量', default=0)
    
    class Meta:
        abstract = True
    
    @property
    def available_quantity(self):
        """可用数量"""
        return self.stock_quantity - self.reserved_quantity
    
    @property
    def is_in_stock(self):
        """是否有库存"""
        return self.available_quantity > 0


class AttributeConfigMixin(models.Model):
    """属性配置混入类"""
    is_required = models.BooleanField('是否必填', default=False)
    is_filterable = models.BooleanField('是否可筛选', default=True)
    is_variant = models.BooleanField('是否规格属性', default=False)
    
    class Meta:
        abstract = True


class ValidationMixin:
    """验证混入类"""
    
    def clean_fields(self, exclude=None):
        """字段验证"""
        super().clean_fields(exclude)
        # 添加通用验证逻辑
        
    def validate_unique(self, exclude=None):
        """唯一性验证"""
        super().validate_unique(exclude)
        # 添加唯一性验证逻辑
    
    def full_clean(self, exclude=None, validate_unique=True):
        """完整验证"""
        super().full_clean(exclude, validate_unique)
        # 添加完整验证逻辑
''',

            'admin_init': '''"""
统一Admin注册入口
基于django_modular_development.mdc规范自动生成
"""

from django.contrib import admin

# 导入模型
from ..models import (
{model_imports}
)

# 导入Admin类
{admin_imports}

# 统一注册
{admin_registers}
''',

            'admin_base': '''"""
Admin基础类和配置
基于django_modular_development.mdc规范自动生成
"""

from django.contrib import admin
from django.core.paginator import Paginator
from django.db import connection


class LargeTablePaginator(Paginator):
    """PostgreSQL优化分页器"""
    
    def count(self):
        if not hasattr(self, '_count'):
            # 使用估算计数优化大表性能
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT reltuples::bigint FROM pg_class WHERE relname = %s",
                        [self.object_list.model._meta.db_table]
                    )
                    result = cursor.fetchone()
                    self._count = result[0] if result and result[0] else 0
            except Exception:
                # 降级为普通计数
                self._count = super().count()
        return self._count


class BaseModelAdmin(admin.ModelAdmin):
    """增强的基础Admin类"""
    
    list_per_page = 50
    save_on_top = True
    paginator = LargeTablePaginator
    
    def get_queryset(self, request):
        """优化查询性能"""
        qs = super().get_queryset(request)
        # 子类可以覆盖此方法添加select_related和prefetch_related
        return qs
    
    def get_readonly_fields(self, request, obj=None):
        """动态只读字段"""
        readonly_fields = list(super().get_readonly_fields(request, obj))
        
        # 添加时间戳字段为只读
        if hasattr(self.model, 'created_at'):
            readonly_fields.append('created_at')
        if hasattr(self.model, 'updated_at'):
            readonly_fields.append('updated_at')
            
        return readonly_fields
    
    def save_model(self, request, obj, form, change):
        """保存时自动设置创建人"""
        if hasattr(obj, 'created_by') and not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class TreeModelAdmin(BaseModelAdmin):
    """树形模型Admin基类"""
    
    list_display = ['name', 'parent', 'level', 'is_active']
    list_filter = ['level', 'is_active']
    search_fields = ['name']
    ordering = ['level', 'sort_order', 'name']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')


class ReadOnlyModelAdmin(BaseModelAdmin):
    """只读模型Admin基类"""
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
''',

            'admin_mixins': '''"""
Admin功能混入类
基于django_modular_development.mdc规范自动生成
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect


class BulkActionMixin:
    """批量操作混入类"""
    
    actions = ['bulk_activate', 'bulk_deactivate']
    
    @admin.action(description='批量激活选中项')
    def bulk_activate(self, request, queryset):
        """批量激活"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'成功激活 {updated} 个项目')
    
    @admin.action(description='批量停用选中项')
    def bulk_deactivate(self, request, queryset):
        """批量停用"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'成功停用 {updated} 个项目')


class DisplayMixin:
    """显示优化混入类"""
    
    def colored_status(self, obj):
        """彩色状态显示"""
        if hasattr(obj, 'is_active'):
            if obj.is_active:
                return format_html('<span style="color: green;">●</span> 激活')
            else:
                return format_html('<span style="color: red;">●</span> 停用')
        return '-'
    colored_status.short_description = '状态'
    
    def created_time(self, obj):
        """格式化创建时间"""
        if hasattr(obj, 'created_at') and obj.created_at:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')
        return '-'
    created_time.short_description = '创建时间'
    
    def updated_time(self, obj):
        """格式化更新时间"""
        if hasattr(obj, 'updated_at') and obj.updated_at:
            return obj.updated_at.strftime('%Y-%m-%d %H:%M')
        return '-'
    updated_time.short_description = '更新时间'


class ExportMixin:
    """导出功能混入类"""
    
    actions = ['export_csv']
    
    def export_csv(self, request, queryset):
        """导出CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.model._meta.verbose_name}.csv"'
        
        writer = csv.writer(response)
        
        # 写入表头
        headers = []
        for field in self.list_display:
            if hasattr(self.model, field):
                headers.append(self.model._meta.get_field(field).verbose_name)
            else:
                headers.append(field)
        writer.writerow(headers)
        
        # 写入数据
        for obj in queryset:
            row = []
            for field in self.list_display:
                if hasattr(obj, field):
                    value = getattr(obj, field)
                    if callable(value):
                        value = value()
                    row.append(str(value))
                else:
                    row.append('')
            writer.writerow(row)
        
        return response
    
    export_csv.short_description = '导出CSV文件'


class SearchMixin:
    """搜索优化混入类"""
    
    def get_search_results(self, request, queryset, search_term):
        """优化搜索性能"""
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        
        # 如果搜索词是数字，尝试按ID搜索
        if search_term.isdigit():
            queryset |= self.model.objects.filter(id=search_term)
            use_distinct = True
        
        return queryset, use_distinct


class LinkMixin:
    """关联链接混入类"""
    
    def get_related_link(self, obj, field_name, display_field='__str__'):
        """生成关联对象的链接"""
        related_obj = getattr(obj, field_name, None)
        if related_obj:
            opts = related_obj._meta
            url = reverse(f'admin:{opts.app_label}_{opts.model_name}_change', 
                         args=[related_obj.pk])
            display_text = getattr(related_obj, display_field)
            if callable(display_text):
                display_text = display_text()
            return format_html('<a href="{}">{}</a>', url, display_text)
        return '-'
''',

            'compatibility_import': '''"""
兼容性导入文件
原始{original_file}已备份为{backup_file}
基于django_modular_development.mdc规范自动生成

此文件确保从原始文件导入的代码继续工作
"""

# 从新的模块化结构导入所有内容
from .{module_dir} import *

# 如果有其他模块直接导入原文件中的类，在下面提供兼容性导入
{compatibility_imports}
''',
        }
    
    def create_backup(self, file_path: Path) -> Path:
        """创建文件备份"""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
        
        if not self.dry_run:
            shutil.copy2(file_path, backup_file)
            print(f"✅ 备份文件: {file_path} -> {backup_file}")
        else:
            print(f"[DRY RUN] 将备份: {file_path} -> {backup_file}")
        
        return backup_file
    
    def analyze_models_file(self, file_path: Path) -> Dict:
        """分析models.py文件结构"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analysis = {
            'imports': [],
            'models': {},
            'business_domains': defaultdict(list),
            'base_classes': [],
            'mixins': [],
            'constants': [],
            'functions': [],
        }
        
        # 解析导入语句
        import_pattern = r'^(from .+ import .+|import .+)$'
        for match in re.finditer(import_pattern, content, re.MULTILINE):
            analysis['imports'].append(match.group(1))
        
        # 解析模型类
        class_pattern = r'class\s+(\w+)\s*\([^)]*\):\s*\n(.*?)(?=\nclass|\n\n\w|\Z)'
        for match in re.finditer(class_pattern, content, re.DOTALL):
            class_name = match.group(1)
            class_body = match.group(2)
            
            # 判断是否是模型类
            if 'models.Model' in class_body or 'Model' in class_body:
                # 提取字段和方法
                fields = self._extract_model_fields(class_body)
                methods = self._extract_model_methods(class_body)
                meta = self._extract_model_meta(class_body)
                
                analysis['models'][class_name] = {
                    'fields': fields,
                    'methods': methods,
                    'meta': meta,
                    'full_definition': match.group(0)
                }
                
                # 识别业务域
                domain = self._extract_business_domain(class_name)
                if domain:
                    analysis['business_domains'][domain].append(class_name)
                else:
                    analysis['business_domains']['misc'].append(class_name)
        
        return analysis
    
    def analyze_admin_file(self, file_path: Path) -> Dict:
        """分析admin.py文件结构"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analysis = {
            'imports': [],
            'admin_classes': {},
            'registrations': [],
            'business_domains': defaultdict(list),
        }
        
        # 解析导入语句
        import_pattern = r'^(from .+ import .+|import .+)$'
        for match in re.finditer(import_pattern, content, re.MULTILINE):
            analysis['imports'].append(match.group(1))
        
        # 解析Admin类
        class_pattern = r'class\s+(\w+Admin)\s*\([^)]*\):\s*\n(.*?)(?=\nclass|\n\n\w|\Z)'
        for match in re.finditer(class_pattern, content, re.DOTALL):
            class_name = match.group(1)
            class_body = match.group(2)
            
            analysis['admin_classes'][class_name] = {
                'full_definition': match.group(0)
            }
            
            # 识别对应的模型
            model_name = class_name.replace('Admin', '')
            domain = self._extract_business_domain(model_name)
            if domain:
                analysis['business_domains'][domain].append(class_name)
            else:
                analysis['business_domains']['misc'].append(class_name)
        
        # 解析注册语句
        register_pattern = r'admin\.site\.register\s*\([^)]+\)'
        for match in re.finditer(register_pattern, content):
            analysis['registrations'].append(match.group(0))
        
        return analysis
    
    def _extract_model_fields(self, class_body: str) -> List[str]:
        """提取模型字段"""
        field_pattern = r'(\w+)\s*=\s*models\.\w+Field'
        return re.findall(field_pattern, class_body)
    
    def _extract_model_methods(self, class_body: str) -> List[str]:
        """提取模型方法"""
        method_pattern = r'def\s+(\w+)\s*\('
        return re.findall(method_pattern, class_body)
    
    def _extract_model_meta(self, class_body: str) -> Optional[str]:
        """提取Meta类"""
        meta_pattern = r'class Meta:\s*\n(.*?)(?=\n    def|\n    \w+\s*=|\n\n|\Z)'
        match = re.search(meta_pattern, class_body, re.DOTALL)
        return match.group(0) if match else None
    
    def _extract_business_domain(self, class_name: str) -> Optional[str]:
        """从类名提取业务域"""
        domains = {
            'category': 'category',
            'brand': 'brand',
            'product': 'product',
            'sku': 'sku', 
            'spu': 'spu',
            'attribute': 'attribute',
            'price': 'pricing',
            'pricing': 'pricing',
            'dimension': 'pricing',
            'import': 'import',
            'export': 'import',
            'user': 'user',
            'order': 'order',
            'payment': 'payment',
            'inventory': 'stock',
            'stock': 'stock',
        }
        
        class_lower = class_name.lower()
        for keyword, domain in domains.items():
            if keyword in class_lower:
                return domain
        
        return None
    
    def create_modular_structure(self, app_path: Path, file_type: str, analysis: Dict) -> Dict[str, str]:
        """创建模块化目录结构"""
        if file_type == 'models':
            return self._create_models_structure(app_path, analysis)
        elif file_type == 'admin':
            return self._create_admin_structure(app_path, analysis)
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")
    
    def _create_models_structure(self, app_path: Path, analysis: Dict) -> Dict[str, str]:
        """创建models模块化结构"""
        models_dir = app_path / 'models'
        
        if not self.dry_run:
            models_dir.mkdir(exist_ok=True)
        
        files_created = {}
        
        # 创建__init__.py
        model_imports = []
        model_all_list = []
        
        for domain, model_names in analysis['business_domains'].items():
            if domain != 'misc' and model_names:
                # 为每个业务域创建文件
                domain_file = f"{domain}_models.py"
                file_path = models_dir / domain_file
                
                # 收集该域的模型定义
                domain_models = []
                for model_name in model_names:
                    if model_name in analysis['models']:
                        domain_models.append(analysis['models'][model_name]['full_definition'])
                        model_imports.append(f"from .{domain}_models import {model_name}")
                        model_all_list.append(f"    '{model_name}',")
                
                if domain_models:
                    file_content = self._generate_domain_models_file(domain, domain_models, analysis['imports'])
                    files_created[str(file_path)] = file_content
        
        # 处理misc模型
        if analysis['business_domains']['misc']:
            misc_models = []
            for model_name in analysis['business_domains']['misc']:
                if model_name in analysis['models']:
                    misc_models.append(analysis['models'][model_name]['full_definition'])
                    model_imports.append(f"from .misc_models import {model_name}")
                    model_all_list.append(f"    '{model_name}',")
            
            if misc_models:
                file_path = models_dir / 'misc_models.py'
                file_content = self._generate_domain_models_file('misc', misc_models, analysis['imports'])
                files_created[str(file_path)] = file_content
        
        # 创建base.py
        base_file = models_dir / 'base.py'
        files_created[str(base_file)] = self.templates['models_base']
        
        # 创建mixins.py
        mixins_file = models_dir / 'mixins.py'
        files_created[str(mixins_file)] = self.templates['models_mixins']
        
        # 创建__init__.py
        init_file = models_dir / '__init__.py'
        init_content = self.templates['models_init'].format(
            model_imports='\\n'.join(model_imports),
            model_all_list='\\n'.join(model_all_list)
        )
        files_created[str(init_file)] = init_content
        
        return files_created
    
    def _create_admin_structure(self, app_path: Path, analysis: Dict) -> Dict[str, str]:
        """创建admin模块化结构"""
        admin_dir = app_path / 'admin'
        
        if not self.dry_run:
            admin_dir.mkdir(exist_ok=True)
        
        files_created = {}
        
        # 创建业务域文件
        model_imports = []
        admin_imports = []
        admin_registers = []
        
        for domain, admin_names in analysis['business_domains'].items():
            if domain != 'misc' and admin_names:
                domain_file = f"{domain}_admin.py"
                file_path = admin_dir / domain_file
                
                # 收集该域的Admin定义
                domain_admins = []
                for admin_name in admin_names:
                    if admin_name in analysis['admin_classes']:
                        domain_admins.append(analysis['admin_classes'][admin_name]['full_definition'])
                        admin_imports.append(f"from .{domain}_admin import {admin_name}")
                        
                        # 生成注册语句
                        model_name = admin_name.replace('Admin', '')
                        model_imports.append(model_name)
                        admin_registers.append(f"admin.site.register({model_name}, {admin_name})")
                
                if domain_admins:
                    file_content = self._generate_domain_admin_file(domain, domain_admins, analysis['imports'])
                    files_created[str(file_path)] = file_content
        
        # 处理misc admin
        if analysis['business_domains']['misc']:
            misc_admins = []
            for admin_name in analysis['business_domains']['misc']:
                if admin_name in analysis['admin_classes']:
                    misc_admins.append(analysis['admin_classes'][admin_name]['full_definition'])
                    admin_imports.append(f"from .misc_admin import {admin_name}")
                    
                    model_name = admin_name.replace('Admin', '')
                    model_imports.append(model_name)
                    admin_registers.append(f"admin.site.register({model_name}, {admin_name})")
            
            if misc_admins:
                file_path = admin_dir / 'misc_admin.py'
                file_content = self._generate_domain_admin_file('misc', misc_admins, analysis['imports'])
                files_created[str(file_path)] = file_content
        
        # 创建base.py
        base_file = admin_dir / 'base.py'
        files_created[str(base_file)] = self.templates['admin_base']
        
        # 创建mixins.py
        mixins_file = admin_dir / 'mixins.py'
        files_created[str(mixins_file)] = self.templates['admin_mixins']
        
        # 创建__init__.py
        init_file = admin_dir / '__init__.py'
        init_content = self.templates['admin_init'].format(
            model_imports=',\\n    '.join(set(model_imports)),
            admin_imports='\\n'.join(admin_imports),
            admin_registers='\\n'.join(admin_registers)
        )
        files_created[str(init_file)] = init_content
        
        return files_created
    
    def _generate_domain_models_file(self, domain: str, model_definitions: List[str], imports: List[str]) -> str:
        """生成业务域模型文件"""
        # 过滤相关导入
        relevant_imports = []
        for imp in imports:
            if 'django.db' in imp or 'models' in imp:
                relevant_imports.append(imp)
        
        content = f'''"""
{domain}业务域模型
基于django_modular_development.mdc规范自动生成
"""

{chr(10).join(relevant_imports)}
from .base import BaseModel, StandardModel
from .mixins import CreatedByMixin, TreeMixin, PriceMixin, StockMixin


{chr(10).join(model_definitions)}
'''
        return content
    
    def _generate_domain_admin_file(self, domain: str, admin_definitions: List[str], imports: List[str]) -> str:
        """生成业务域Admin文件"""
        # 过滤相关导入
        relevant_imports = []
        for imp in imports:
            if 'django.contrib.admin' in imp or 'admin' in imp:
                relevant_imports.append(imp)
        
        content = f'''"""
{domain}业务域Admin
基于django_modular_development.mdc规范自动生成
"""

from django.contrib import admin
{chr(10).join(relevant_imports)}
from .base import BaseModelAdmin, TreeModelAdmin
from .mixins import BulkActionMixin, DisplayMixin, ExportMixin
from ..models import *


{chr(10).join(admin_definitions)}
'''
        return content
    
    def write_files(self, files_to_create: Dict[str, str]):
        """写入文件"""
        for file_path, content in files_to_create.items():
            path_obj = Path(file_path)
            
            if self.dry_run:
                print(f"[DRY RUN] 将创建文件: {file_path}")
                print(f"文件大小: {len(content)} 字符")
            else:
                path_obj.parent.mkdir(parents=True, exist_ok=True)
                with open(path_obj, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 创建文件: {file_path}")
    
    def create_compatibility_file(self, original_file: Path, module_dir: str, backup_file: Path):
        """创建兼容性文件"""
        compatibility_content = self.templates['compatibility_import'].format(
            original_file=original_file.name,
            backup_file=backup_file.name,
            module_dir=module_dir,
            compatibility_imports="# 根据需要添加具体的兼容性导入"
        )
        
        if self.dry_run:
            print(f"[DRY RUN] 将替换 {original_file} 为兼容性导入文件")
        else:
            with open(original_file, 'w', encoding='utf-8') as f:
                f.write(compatibility_content)
            print(f"✅ 替换 {original_file} 为兼容性导入文件")
    
    def modularize_file(self, file_path: Path, file_type: str):
        """模块化单个文件"""
        print(f"\\n开始模块化: {file_path}")
        
        # 1. 创建备份
        backup_file = self.create_backup(file_path)
        
        # 2. 分析文件结构
        if file_type == 'models':
            analysis = self.analyze_models_file(file_path)
        elif file_type == 'admin':
            analysis = self.analyze_admin_file(file_path)
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")
        
        print(f"分析结果: 发现 {len(analysis.get('models', analysis.get('admin_classes', {})))} 个类")
        print(f"业务域: {list(analysis['business_domains'].keys())}")
        
        # 3. 创建模块化结构
        app_path = file_path.parent
        files_to_create = self.create_modular_structure(app_path, file_type, analysis)
        
        # 4. 写入文件
        self.write_files(files_to_create)
        
        # 5. 创建兼容性文件
        self.create_compatibility_file(file_path, file_type, backup_file)
        
        print(f"✅ 完成模块化: {file_path}")
        print(f"创建了 {len(files_to_create)} 个新文件")
    
    def modularize_project(self, target_files: Optional[List[str]] = None):
        """模块化整个项目"""
        print(f"开始模块化Django项目: {self.project_root}")
        if self.dry_run:
            print("🔍 DRY RUN 模式 - 仅预览，不会实际修改文件")
        print()
        
        files_processed = 0
        
        # 查找需要处理的文件
        for app_dir in self.project_root.iterdir():
            if not app_dir.is_dir() or app_dir.name.startswith('.'):
                continue
            
            # 检查models.py
            models_file = app_dir / 'models.py'
            if models_file.exists() and (not target_files or str(models_file) in target_files):
                try:
                    self.modularize_file(models_file, 'models')
                    files_processed += 1
                except Exception as e:
                    print(f"❌ 处理 {models_file} 时出错: {e}")
            
            # 检查admin.py
            admin_file = app_dir / 'admin.py'
            if admin_file.exists() and (not target_files or str(admin_file) in target_files):
                try:
                    self.modularize_file(admin_file, 'admin')
                    files_processed += 1
                except Exception as e:
                    print(f"❌ 处理 {admin_file} 时出错: {e}")
        
        print(f"\\n🎉 模块化完成！")
        print(f"处理了 {files_processed} 个文件")
        if self.backup_dir.exists():
            print(f"备份目录: {self.backup_dir}")


def main():
    parser = argparse.ArgumentParser(description='Django自动模块化重构工具')
    parser.add_argument('project_path', nargs='?', default='.', 
                       help='Django项目根目录路径 (默认: 当前目录)')
    parser.add_argument('-f', '--files', nargs='+',
                       help='指定要处理的文件路径')
    parser.add_argument('--dry-run', action='store_true',
                       help='预览模式，不实际修改文件')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='显示详细信息')
    
    args = parser.parse_args()
    
    project_path = Path(args.project_path).resolve()
    
    if not project_path.exists():
        print(f"错误: 项目路径不存在: {project_path}")
        sys.exit(1)
    
    print("Django自动模块化重构工具")
    print("基于规范: .cursor/rules/django_modular_development.mdc")
    print("=" * 60)
    
    modularizer = AutoModularizer(project_path, dry_run=args.dry_run)
    
    try:
        modularizer.modularize_project(target_files=args.files)
    except KeyboardInterrupt:
        print("\\n操作被用户中断")
    except Exception as e:
        print(f"\\n❌ 发生错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main() 