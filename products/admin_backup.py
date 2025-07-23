import os
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.db import models, connection
from django.db.models import Q, Count, Prefetch
from django.conf import settings
from django import forms
from django.forms import TextInput, Textarea, ModelChoiceField, Select, ModelForm
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from mptt.admin import DraggableMPTTAdmin
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.cache import cache
from django.contrib.admin.filters import SimpleListFilter
from django.contrib.admin.views.main import ChangeList
from .models import Category, Brand, Attribute, AttributeValue, SPU, SPUAttribute, SKU, SKUAttributeValue, ProductImage, ProductsPricingRule, ProductsDimension, SPUDimensionTemplate, ImportTask, ImportError, ImportTemplate


from django.contrib.admin.filters import SimpleListFilter


class SeriesFilter(SimpleListFilter):
    """自定义系列过滤器"""
    title = '产品系列'
    parameter_name = 'series'
    
    def lookups(self, request, model_admin):
        """返回过滤选项"""
        return [
            ('NOVO', 'NOVO系列'),
            ('TALOS', 'TALOS系列'),
            ('LUNA', 'LUNA系列'),
            ('HERA', 'HERA系列'),
            ('INTERCHANGEABLE', '通用件'),
        ]
    
    def queryset(self, request, queryset):
        """过滤查询集"""
        if self.value():
            return queryset.filter(
                sku_attribute_values__attribute__code='SERIES',
                sku_attribute_values__custom_value=self.value()
            ).distinct()
        return queryset


class WidthFilter(SimpleListFilter):
    """自定义宽度过滤器"""
    title = '产品宽度'
    parameter_name = 'width'
    
    def lookups(self, request, model_admin):
        """返回过滤选项"""
        return [
            ('30', '30cm'),
            ('45', '45cm'),
            ('50', '50cm'),
            ('60', '60cm'),
            ('90', '90cm'),
            ('100', '100cm'),
            ('110', '110cm'),
            ('120', '120cm'),
        ]
    
    def queryset(self, request, queryset):
        """过滤查询集"""
        if self.value():
            return queryset.filter(
                sku_attribute_values__attribute__code='WIDTH',
                sku_attribute_values__custom_value=self.value()
            ).distinct()
        return queryset


# 优化的大数据表分页器
class LargeTablePaginator(Paginator):
    """
    优化大数据表的分页器
    使用PostgreSQL的reltuples进行估算，避免大表COUNT查询超时
    """
    
    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True):
        super().__init__(object_list, per_page, orphans, allow_empty_first_page)
        self._count = None
    
    @property
    def count(self):
        """
        对于大表使用估算计数，避免性能问题
        """
        if self._count is None:
            try:
                # 检查是否有WHERE条件
                if not self.object_list.query.where:
                    # 尝试使用PostgreSQL的reltuples进行估算
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "SELECT reltuples FROM pg_class WHERE relname = %s",
                            [self.object_list.query.model._meta.db_table]
                        )
                        result = cursor.fetchone()
                        if result:
                            self._count = int(result[0])
                            return self._count
            except Exception:
                # 如果失败，回退到默认行为
                pass
            
            # 默认计数
            self._count = super().count
        return self._count


# 自定义 Admin 基类 - 增强版
class BaseModelAdmin(admin.ModelAdmin):
    """增强版基础 Admin 配置"""
    
    # 基本配置
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '40', 'class': 'vTextField'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 60, 'class': 'vLargeTextField'})},
    }
    
    # 性能优化配置
    list_per_page = 25  # 减少每页显示数量提升性能
    list_max_show_all = 100  # 限制"显示全部"的最大数量
    show_full_result_count = False  # 禁用完整结果计数
    
    # 默认排序字段
    sortable_by = ('id', 'created_at', 'updated_at')
    
    # 大表标识
    large_table_paginator = False
    
    def get_paginator(self, request, queryset, per_page, orphans=0, allow_empty_first_page=True):
        """根据表大小选择分页器"""
        if self.large_table_paginator and not settings.DEBUG:
            return LargeTablePaginator(queryset, per_page, orphans, allow_empty_first_page)
        return self.paginator(queryset, per_page, orphans, allow_empty_first_page)
    
    def get_readonly_fields(self, request, obj=None):
        """设置只读字段"""
        readonly_fields = list(self.readonly_fields)
        if obj:  # 编辑时
            readonly_fields.extend(['created_at', 'updated_at'])
        return readonly_fields
    
    def get_queryset(self, request):
        """优化查询性能"""
        queryset = super().get_queryset(request)
        
        # 根据模型自动优化查询
        model = self.model
        
        # 自动添加 select_related 优化外键查询
        fk_fields = [f.name for f in model._meta.fields if f.is_relation and not f.many_to_many]
        if fk_fields:
            queryset = queryset.select_related(*fk_fields)
        
        # 自动添加 prefetch_related 优化多对多查询
        m2m_fields = [f.name for f in model._meta.many_to_many]
        if m2m_fields:
            queryset = queryset.prefetch_related(*m2m_fields)
        
        return queryset
    
    def has_add_permission(self, request):
        """检查添加权限"""
        return request.user.is_superuser or super().has_add_permission(request)
    
    def has_change_permission(self, request, obj=None):
        """检查修改权限"""
        return request.user.is_superuser or super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """检查删除权限"""
        return request.user.is_superuser or super().has_delete_permission(request, obj)
    
    def has_view_permission(self, request, obj=None):
        """检查查看权限"""
        return request.user.is_authenticated and super().has_view_permission(request, obj)


# 自定义过滤器
class ActiveFilter(SimpleListFilter):
    """通用激活状态过滤器"""
    title = '状态'
    parameter_name = 'is_active'
    
    def lookups(self, request, model_admin):
        return (
            ('1', '已启用'),
            ('0', '已禁用'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(is_active=True)
        if self.value() == '0':
            return queryset.filter(is_active=False)
        return queryset


class DateRangeFilter(SimpleListFilter):
    """日期范围过滤器"""
    title = '创建时间'
    parameter_name = 'date_range'
    
    def lookups(self, request, model_admin):
        return (
            ('today', '今天'),
            ('week', '本周'),
            ('month', '本月'),
            ('year', '今年'),
        )
    
    def queryset(self, request, queryset):
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        now = timezone.now()
        
        if self.value() == 'today':
            return queryset.filter(created_at__date=now.date())
        elif self.value() == 'week':
            start_week = now - timedelta(days=now.weekday())
            return queryset.filter(created_at__gte=start_week)
        elif self.value() == 'month':
            start_month = now.replace(day=1)
            return queryset.filter(created_at__gte=start_month)
        elif self.value() == 'year':
            start_year = now.replace(month=1, day=1)
            return queryset.filter(created_at__gte=start_year)
        
        return queryset


# Category Admin 配置 - 增强版
@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin, BaseModelAdmin):
    """分类管理 - 支持树状结构和拖拽排序"""
    
    list_display = [
        'tree_actions',
        'indented_title',
        'code',
        'get_level_display',
        'order',
        'is_active',
        'get_children_count',
        'get_spu_count',
        'created_at'
    ]
    list_display_links = ('indented_title',)
    list_filter = [ActiveFilter, DateRangeFilter, 'level']
    search_fields = ['name', 'code', 'description']
    list_editable = ['order', 'is_active']
    actions = ['sort_alphabetically', 'sort_by_order', 'reset_order', 'bulk_activate', 'bulk_deactivate']
    
    # MPTT 相关设置
    mptt_level_indent = 20
    mptt_indent_field = 'name'
    expand_tree_by_default = True
    
    # 性能优化
    list_per_page = 50
    show_full_result_count = False
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'code', 'parent', 'order'),
            'classes': ('wide',)
        }),
        ('详细信息', {
            'fields': ('description', 'is_active'),
            'classes': ('collapse', 'wide')
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('parent').annotate(
            children_count=Count('children'),
            spu_count=Count('spus')
        )
    
    def indented_title(self, obj):
        """带缩进的标题显示"""
        return format_html(
            '<div style="margin-left: {}px">{}</div>',
            obj.level * self.mptt_level_indent,
            obj.name
        )
    indented_title.short_description = '分类名称'
    indented_title.admin_order_field = 'name'
    
    def get_level_display(self, obj):
        """显示层级"""
        level_colors = {
            0: '#e74c3c',  # 红色 - 一级
            1: '#3498db',  # 蓝色 - 二级
            2: '#2ecc71',  # 绿色 - 三级
            3: '#f39c12',  # 橙色 - 四级
        }
        color = level_colors.get(obj.level, '#95a5a6')
        return format_html(
            '<span style="color: {}; font-weight: bold;">第{}级</span>',
            color, obj.level + 1
        )
    get_level_display.short_description = '层级'
    get_level_display.admin_order_field = 'level'
    
    def get_children_count(self, obj):
        """显示子分类数量"""
        count = getattr(obj, 'children_count', obj.get_children().count())
        if count > 0:
            return format_html(
                '<a href="{}?parent__id={}" style="color: #0066cc; font-weight: bold;">{} 个</a>',
                reverse('admin:products_category_changelist'), obj.id, count
            )
        return format_html('<span style="color: #999;">无</span>')
    get_children_count.short_description = '子分类'
    get_children_count.admin_order_field = 'children_count'
    
    def get_spu_count(self, obj):
        """显示SPU数量"""
        count = getattr(obj, 'spu_count', obj.spus.count())
        if count > 0:
            return format_html(
                '<a href="{}?category__id={}" style="color: #27ae60; font-weight: bold;">{} 个产品</a>',
                reverse('admin:products_spu_changelist'), obj.id, count
            )
        return format_html('<span style="color: #999;">无产品</span>')
    get_spu_count.short_description = 'SPU数量'
    get_spu_count.admin_order_field = 'spu_count'
    
    # 批量操作
    def bulk_activate(self, request, queryset):
        """批量激活"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'成功激活 {updated} 个分类。', messages.SUCCESS)
    bulk_activate.short_description = "激活选中的分类"
    
    def bulk_deactivate(self, request, queryset):
        """批量停用"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'成功停用 {updated} 个分类。', messages.SUCCESS)
    bulk_deactivate.short_description = "停用选中的分类"
    
    def sort_alphabetically(self, request, queryset):
        """按字母顺序排序"""
        # 按层级分组排序
        levels = {}
        for obj in queryset:
            if obj.level not in levels:
                levels[obj.level] = []
            levels[obj.level].append(obj)
        
        updated_count = 0
        for level, categories in levels.items():
            # 按名称排序
            categories.sort(key=lambda x: x.name)
            for i, category in enumerate(categories):
                category.order = i + 1
                category.save(update_fields=['order'])
                updated_count += 1
        
        # 重建树结构
        Category.objects.rebuild()
        
        self.message_user(
            request,
            f'成功对 {updated_count} 个分类进行了字母排序'
        )
    sort_alphabetically.short_description = "按字母顺序排序"
    
    def sort_by_order(self, request, queryset):
        """按 order 字段排序"""
        # 按层级分组排序
        levels = {}
        for obj in queryset:
            if obj.level not in levels:
                levels[obj.level] = []
            levels[obj.level].append(obj)
        
        updated_count = 0
        for level, categories in levels.items():
            # 按 order 字段排序
            categories.sort(key=lambda x: (x.order, x.name))
            for i, category in enumerate(categories):
                if category.order != i + 1:
                    category.order = i + 1
                    category.save(update_fields=['order'])
                    updated_count += 1
        
        # 重建树结构
        Category.objects.rebuild()
        
        self.message_user(
            request,
            f'成功对 {updated_count} 个分类按 order 字段进行了排序'
        )
    sort_by_order.short_description = "按 order 字段排序"
    
    def reset_order(self, request, queryset):
        """重置排序（按ID顺序）"""
        # 按层级分组排序
        levels = {}
        for obj in queryset:
            if obj.level not in levels:
                levels[obj.level] = []
            levels[obj.level].append(obj)
        
        updated_count = 0
        for level, categories in levels.items():
            # 按ID排序
            categories.sort(key=lambda x: x.id)
            for i, category in enumerate(categories):
                category.order = i + 1
                category.save(update_fields=['order'])
                updated_count += 1
        
        # 重建树结构
        Category.objects.rebuild()
        
        self.message_user(
            request,
            f'成功重置了 {updated_count} 个分类的排序'
        )
    reset_order.short_description = "重置排序（按创建顺序）"
    
    def has_delete_permission(self, request, obj=None):
        """分类删除权限控制"""
        # 只有超级用户可以删除分类
        if not request.user.is_superuser:
            return False
        
        # 检查是否有子分类
        if obj and obj.get_children().exists():
            return False
        
        # 检查是否有关联的 SPU
        if obj and obj.spus.exists():
            return False
            
        return True
    
    # 自定义表单字段验证
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """自定义父分类字段"""
        if db_field.name == "parent":
            # 排除当前节点及其子节点，避免循环引用
            if request.resolver_match.kwargs.get('object_id'):
                try:
                    current_id = int(request.resolver_match.kwargs['object_id'])
                    current_category = Category.objects.get(id=current_id)
                    # 排除自己和所有子节点
                    exclude_ids = [current_id] + list(
                        current_category.get_descendants().values_list('id', flat=True)
                    )
                    kwargs["queryset"] = Category.objects.exclude(id__in=exclude_ids)
                except (ValueError, Category.DoesNotExist):
                    pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Brand Admin 配置 - 增强版
@admin.register(Brand)
class BrandAdmin(BaseModelAdmin):
    """品牌管理"""
    
    list_display = [
        'name', 'code', 'get_logo_display', 'get_contact_info', 
        'get_spu_count', 'get_sku_count', 'is_active', 'created_at'
    ]
    list_filter = [ActiveFilter, DateRangeFilter, 'created_at']
    search_fields = ['name', 'code', 'description', 'contact_person', 'contact_email']
    list_editable = ['is_active']
    ordering = ['name']
    actions = ['activate_brands', 'deactivate_brands', 'export_brands']
    
    # 性能优化
    list_per_page = 30
    list_select_related = []  # 无外键需要预加载
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'code'),
            'description': '品牌的基本标识信息，编码必须唯一',
            'classes': ('wide',)
        }),
        ('Logo 管理', {
            'fields': ('logo', 'get_logo_preview'),
            'description': '品牌Logo图片管理，支持JPG、PNG格式，建议尺寸200x200像素',
            'classes': ('wide',)
        }),
        ('详细信息', {
            'fields': ('description', 'website'),
            'classes': ('collapse', 'wide')
        }),
        ('联系人信息', {
            'fields': ('contact_person', 'contact_phone', 'contact_email'),
            'classes': ('collapse', 'wide'),
            'description': '品牌联系人相关信息'
        }),
        ('状态', {
            'fields': ('is_active',)
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['get_logo_preview', 'created_at', 'updated_at']
    
    class Media:
        css = {
            'all': ('admin/css/brand_admin.css',)
        }
        js = ('admin/js/brand_admin.js',)
    
    def get_queryset(self, request):
        """优化查询，添加统计信息"""
        return super().get_queryset(request).annotate(
            spu_count=Count('spus'),
            sku_count=Count('skus')
        )
    
    def get_logo_display(self, obj):
        """列表页显示Logo"""
        if obj.logo:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 4px; object-fit: cover; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" title="{}" />',
                obj.logo.url, obj.name
            )
        return format_html('<span style="color: #999; font-style: italic;">无Logo</span>')
    get_logo_display.short_description = 'Logo'
    
    def get_logo_preview(self, obj):
        """详情页显示Logo预览"""
        if obj.logo:
            return format_html(
                '''
                <div class="logo-preview-container">
                    <img src="{}" style="max-width: 200px; max-height: 200px; border: 1px solid #ddd; border-radius: 8px; object-fit: cover;" />
                    <div style="margin-top: 10px;">
                        <p><strong>文件名:</strong> {}</p>
                        <p><strong>大小:</strong> {}</p>
                        <button type="button" class="button" onclick="deleteLogo({})">删除Logo</button>
                    </div>
                </div>
                ''',
                obj.logo.url,
                os.path.basename(obj.logo.name),
                self._get_file_size(obj.logo) if obj.logo else '未知',
                obj.pk
            )
        return format_html(
            '<p style="color: #999; font-style: italic;">暂无Logo，请点击上方"选择文件"上传Logo</p>'
        )
    get_logo_preview.short_description = 'Logo预览'
    
    def _get_file_size(self, file_field):
        """获取文件大小"""
        try:
            size = file_field.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        except:
            return "未知"
    
    def get_urls(self):
        """添加自定义URL"""
        urls = super().get_urls()
        custom_urls = [
            path('delete-logo/<int:brand_id>/', self.admin_site.admin_view(self.delete_logo_view), name='brand_delete_logo'),
        ]
        return custom_urls + urls
    
    @method_decorator(csrf_exempt)
    def delete_logo_view(self, request, brand_id):
        """删除Logo的AJAX视图"""
        if request.method == 'POST':
            try:
                brand = Brand.objects.get(pk=brand_id)
                if brand.logo:
                    # 删除文件
                    logo_path = brand.logo.path
                    brand.logo.delete(save=False)
                    brand.save()
                    
                    # 尝试删除物理文件
                    try:
                        if os.path.exists(logo_path):
                            os.remove(logo_path)
                    except:
                        pass
                    
                    return JsonResponse({'success': True, 'message': 'Logo删除成功'})
                else:
                    return JsonResponse({'success': False, 'message': '该品牌没有Logo'})
            except Brand.DoesNotExist:
                return JsonResponse({'success': False, 'message': '品牌不存在'})
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'删除失败: {str(e)}'})
        
        return JsonResponse({'success': False, 'message': '无效请求'})
    
    def get_contact_info(self, obj):
        """显示联系人信息"""
        info_parts = []
        if obj.contact_person:
            info_parts.append(f"联系人: {obj.contact_person}")
        if obj.contact_phone:
            info_parts.append(f"电话: {obj.contact_phone}")
        if obj.contact_email:
            info_parts.append(f"邮箱: {obj.contact_email}")
        
        if info_parts:
            return format_html('<br>'.join(info_parts))
        return format_html('<span style="color: #999;">无联系信息</span>')
    get_contact_info.short_description = '联系信息'
    
    def get_spu_count(self, obj):
        """显示SPU数量"""
        count = getattr(obj, 'spu_count', obj.spus.count())
        if count > 0:
            return format_html(
                '<a href="{}?brand__id={}" style="color: #27ae60; font-weight: bold;">{} 个</a>',
                reverse('admin:products_spu_changelist'), obj.id, count
            )
        return format_html('<span style="color: #999;">无</span>')
    get_spu_count.short_description = 'SPU数量'
    get_spu_count.admin_order_field = 'spu_count'
    
    def get_sku_count(self, obj):
        """显示SKU数量"""
        count = getattr(obj, 'sku_count', obj.skus.count())
        if count > 0:
            return format_html(
                '<a href="{}?brand__id={}" style="color: #3498db; font-weight: bold;">{} 个</a>',
                reverse('admin:products_sku_changelist'), obj.id, count
            )
        return format_html('<span style="color: #999;">无</span>')
    get_sku_count.short_description = 'SKU数量'
    get_sku_count.admin_order_field = 'sku_count'
    
    def activate_brands(self, request, queryset):
        """批量激活品牌"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'成功激活 {updated} 个品牌。', messages.SUCCESS)
    activate_brands.short_description = "激活选中的品牌"
    
    def deactivate_brands(self, request, queryset):
        """批量停用品牌"""
        # 检查是否有关联的活跃SKU
        brands_with_active_skus = []
        for brand in queryset:
            if brand.skus.filter(status='active').exists():
                brands_with_active_skus.append(brand.name)
        
        if brands_with_active_skus:
            self.message_user(
                request, 
                f'以下品牌有活跃产品，无法停用: {", ".join(brands_with_active_skus)}',
                messages.ERROR
            )
            return
        
        updated = queryset.update(is_active=False)
        self.message_user(request, f'成功停用 {updated} 个品牌。', messages.SUCCESS)
    deactivate_brands.short_description = "停用选中的品牌"
    
    def clean(self):
        """数据验证"""
        super().clean()
        
        # 验证联系邮箱格式
        if self.contact_email:
            from django.core.validators import validate_email
            try:
                validate_email(self.contact_email)
            except ValidationError:
                raise ValidationError({'contact_email': '请输入有效的邮箱地址'})
        
        # 验证联系电话格式（简单验证）
        if self.contact_phone:
            import re
            if not re.match(r'^[\d\-\+\(\)\s]+$', self.contact_phone):
                raise ValidationError({'contact_phone': '请输入有效的电话号码'})
    
    def has_delete_permission(self, request, obj=None):
        """品牌删除权限控制"""
        # 只有超级用户可以删除品牌
        if not request.user.is_superuser:
            return False
        
        # 检查是否有关联的 SKU
        if obj and obj.skus.exists():
            return False
            
        return True
    
    def delete_model(self, request, obj):
        """删除前检查"""
        if obj.skus.exists():
            messages.error(request, f'品牌 "{obj.name}" 有关联产品，无法删除。')
            return False
        super().delete_model(request, obj)
        messages.success(request, f'品牌 "{obj.name}" 已成功删除。')


class AttributeValueInline(admin.TabularInline):
    """属性值内联编辑"""
    model = AttributeValue
    extra = 3
    fields = ['value', 'display_name', 'color_code', 'order', 'is_active']
    
    def get_formset(self, request, obj=None, **kwargs):
        """根据属性类型调整字段"""
        formset = super().get_formset(request, obj, **kwargs)
        if obj and obj.type == 'color':
            self.fields = ['value', 'display_name', 'color_code', 'order', 'is_active']
        elif obj and obj.type == 'image':
            self.fields = ['value', 'display_name', 'image', 'order', 'is_active']
        else:
            self.fields = ['value', 'display_name', 'order', 'is_active']
        return formset


# Attribute Admin 配置
@admin.register(Attribute)
class AttributeAdmin(BaseModelAdmin):
    """属性管理"""
    
    list_display = ['name', 'code', 'get_type_display', 'unit', 'get_values_count', 'is_required', 'is_filterable', 'order', 'is_active']
    list_filter = ['type', 'is_required', 'is_filterable', 'is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'name']
    actions = ['standardize_values', 'activate_attributes', 'deactivate_attributes']
    inlines = [AttributeValueInline]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'code', 'type', 'unit', 'order'),
            'description': '属性的基本定义信息'
        }),
        ('配置选项', {
            'fields': ('is_required', 'is_filterable', 'is_active'),
            'description': '属性的行为配置'
        }),
        ('描述信息', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )
    
    def get_type_display(self, obj):
        """显示属性类型"""
        type_colors = {
            'text': '#17a2b8',
            'number': '#28a745',
            'select': '#fd7e14',
            'multiselect': '#e83e8c',
            'boolean': '#6f42c1',
            'date': '#dc3545',
            'color': '#20c997',
            'image': '#6c757d',
        }
        color = type_colors.get(obj.type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_type_display()
        )
    get_type_display.short_description = '类型'
    
    def get_values_count(self, obj):
        """显示属性值数量"""
        count = obj.values.count()
        if count > 0:
            return format_html(
                '<a href="/admin/products/attributevalue/?attribute__id={}" target="_blank">{} 个值</a>',
                obj.id, count
            )
        return format_html('<span style="color: #999;">无属性值</span>')
    get_values_count.short_description = '属性值'
    
    def standardize_values(self, request, queryset):
        """批量标准化属性值"""
        standardized_count = 0
        for attribute in queryset:
            if attribute.type in ['text', 'select', 'multiselect']:
                # 对文本类型属性值进行标准化
                values = attribute.values.all()
                for value in values:
                    original_value = value.value
                    standardized_value = self._standardize_text_value(original_value)
                    if standardized_value != original_value:
                        value.value = standardized_value
                        value.save()
                        standardized_count += 1
        
        if standardized_count > 0:
            self.message_user(request, f'成功标准化 {standardized_count} 个属性值。', messages.SUCCESS)
        else:
            self.message_user(request, '没有需要标准化的属性值。', messages.INFO)
    standardize_values.short_description = "标准化选中属性的值"
    
    def activate_attributes(self, request, queryset):
        """批量激活属性"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'成功激活 {updated} 个属性。', messages.SUCCESS)
    activate_attributes.short_description = "激活选中的属性"
    
    def deactivate_attributes(self, request, queryset):
        """批量停用属性"""
        # 检查是否有关联的SPU
        attributes_with_spus = []
        for attribute in queryset:
            if attribute.spus.filter(is_active=True).exists():
                attributes_with_spus.append(attribute.name)
        
        if attributes_with_spus:
            self.message_user(
                request, 
                f'以下属性有关联的活跃SPU，无法停用: {", ".join(attributes_with_spus)}',
                messages.ERROR
            )
            return
        
        updated = queryset.update(is_active=False)
        self.message_user(request, f'成功停用 {updated} 个属性。', messages.SUCCESS)
    deactivate_attributes.short_description = "停用选中的属性"
    
    def _standardize_text_value(self, value):
        """标准化文本值"""
        if not value:
            return value
        
        # 去除首尾空格
        standardized = value.strip()
        
        # 统一大小写（根据需要调整）
        # standardized = standardized.title()  # 首字母大写
        
        # 移除多余空格
        import re
        standardized = re.sub(r'\s+', ' ', standardized)
        
        # 统一常见单位
        unit_mappings = {
            '毫米': 'mm',
            '厘米': 'cm',
            '米': 'm',
            '千克': 'kg',
            '克': 'g',
            '升': 'L',
            '毫升': 'ml',
        }
        
        for old_unit, new_unit in unit_mappings.items():
            standardized = standardized.replace(old_unit, new_unit)
        
        return standardized
    
    def save_model(self, request, obj, form, change):
        """保存时进行数据验证"""
        # 验证属性编码格式
        import re
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', obj.code):
            messages.error(request, '属性编码必须以字母开头，只能包含字母、数字和下划线')
            return
        
        # 根据属性类型设置默认配置
        if obj.type in ['select', 'multiselect'] and not change:
            obj.is_filterable = True
        elif obj.type in ['text', 'image'] and not change:
            obj.is_filterable = False
            
        super().save_model(request, obj, form, change)
        
        # 如果是新创建的select或multiselect类型，提示添加属性值
        if not change and obj.type in ['select', 'multiselect']:
            messages.info(request, f'属性 "{obj.name}" 创建成功！请在下方添加可选的属性值。')
    
    def has_delete_permission(self, request, obj=None):
        """属性删除权限控制"""
        if not request.user.is_superuser:
            return False
        
        # 检查是否有关联的SPU
        if obj and obj.spus.exists():
            return False
            
        # 检查是否有属性值
        if obj and obj.values.exists():
            return False
            
        return True
    
    def delete_model(self, request, obj):
        """删除前检查"""
        if obj.spus.exists():
            messages.error(request, f'属性 "{obj.name}" 有关联SPU，无法删除。')
            return False
        
        if obj.values.exists():
            messages.error(request, f'属性 "{obj.name}" 有属性值，请先删除所有属性值。')
            return False
            
        super().delete_model(request, obj)
        messages.success(request, f'属性 "{obj.name}" 已成功删除。')


# AttributeValue Admin 配置
@admin.register(AttributeValue)
class AttributeValueAdmin(BaseModelAdmin):
    """属性值管理"""
    
    list_display = ['get_value_display', 'attribute', 'get_display_name', 'get_color_preview', 'order', 'is_active', 'created_at']
    list_filter = ['attribute', 'is_active', 'created_at', 'attribute__type']
    search_fields = ['value', 'display_name', 'attribute__name']
    list_editable = ['order', 'is_active']
    ordering = ['attribute', 'order', 'value']
    actions = ['standardize_selected_values', 'activate_values', 'deactivate_values']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('attribute', 'value', 'display_name', 'order'),
            'description': '属性值的基本定义'
        }),
        ('扩展信息', {
            'fields': ('color_code', 'image'),
            'classes': ('collapse',),
            'description': '颜色代码用于颜色类型属性，图片用于图片类型属性'
        }),
        ('状态', {
            'fields': ('is_active',)
        }),
    )

    def get_value_display(self, obj):
        """显示属性值"""
        if obj.attribute.type == 'color' and obj.color_code:
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; margin-right: 5px;">{}</span>{}',
                obj.color_code, '●', obj.value
            )
        elif obj.attribute.type == 'image' and obj.image:
            return format_html(
                '<img src="{}" width="30" height="30" style="border-radius: 3px; margin-right: 5px; object-fit: cover;" /><span>{}</span>',
                obj.image.url, obj.value
            )
        return obj.value
    get_value_display.short_description = '属性值'
    
    def get_display_name(self, obj):
        """显示展示名称"""
        if obj.display_name and obj.display_name != obj.value:
            return format_html(
                '<span style="color: #666; font-style: italic;">{}</span>',
                obj.display_name
            )
        return format_html('<span style="color: #999;">-</span>')
    get_display_name.short_description = '显示名称'
    
    def get_color_preview(self, obj):
        """显示颜色预览"""
        if obj.attribute.type == 'color' and obj.color_code:
            return format_html(
                '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ddd; border-radius: 3px; display: inline-block;"></div>',
                obj.color_code
            )
        return format_html('<span style="color: #999;">-</span>')
    get_color_preview.short_description = '颜色'
    
    def standardize_selected_values(self, request, queryset):
        """标准化选中的属性值"""
        standardized_count = 0
        for value in queryset:
            original_value = value.value
            standardized_value = self._standardize_value(value)
            if standardized_value != original_value:
                value.value = standardized_value
                value.save()
                standardized_count += 1
        
        if standardized_count > 0:
            self.message_user(request, f'成功标准化 {standardized_count} 个属性值。', messages.SUCCESS)
        else:
            self.message_user(request, '没有需要标准化的属性值。', messages.INFO)
    standardize_selected_values.short_description = "标准化选中的属性值"
    
    def activate_values(self, request, queryset):
        """批量激活属性值"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'成功激活 {updated} 个属性值。', messages.SUCCESS)
    activate_values.short_description = "激活选中的属性值"
    
    def deactivate_values(self, request, queryset):
        """批量停用属性值"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'成功停用 {updated} 个属性值。', messages.SUCCESS)
    deactivate_values.short_description = "停用选中的属性值"
    
    def _standardize_value(self, value_obj):
        """标准化单个属性值"""
        value = value_obj.value
        if not value:
            return value
        
        # 基本清理
        standardized = value.strip()
        
        # 移除多余空格
        import re
        standardized = re.sub(r'\s+', ' ', standardized)
        
        # 根据属性类型进行特定标准化
        if value_obj.attribute.type == 'color':
            # 颜色值标准化
            if standardized.startswith('#'):
                standardized = standardized.upper()
            else:
                # 常见颜色名称标准化
                color_mappings = {
                    '红色': '红',
                    '蓝色': '蓝',
                    '绿色': '绿',
                    '黄色': '黄',
                    '黑色': '黑',
                    '白色': '白',
                    '灰色': '灰',
                    '棕色': '棕',
                    '紫色': '紫',
                    '橙色': '橙',
                }
                for old_color, new_color in color_mappings.items():
                    standardized = standardized.replace(old_color, new_color)
        
        elif value_obj.attribute.type == 'number':
            # 数字值标准化
            standardized = re.sub(r'[^\d\.\-\+]', '', standardized)
        
        # 统一单位
        unit_mappings = {
            '毫米': 'mm',
            '厘米': 'cm',
            '米': 'm',
            '千克': 'kg',
            '克': 'g',
            '升': 'L',
            '毫升': 'ml',
        }
        
        for old_unit, new_unit in unit_mappings.items():
            standardized = standardized.replace(old_unit, new_unit)
        
        return standardized
    
    def save_model(self, request, obj, form, change):
        """保存时自动标准化"""
        obj.value = self._standardize_value(obj)
        
        # 如果没有显示名称，使用属性值作为显示名称
        if not obj.display_name:
            obj.display_name = obj.value
            
        # 验证颜色代码格式
        import re
        if obj.color_code and not re.match(r'^#[0-9A-Fa-f]{6}$', obj.color_code):
            messages.error(request, '颜色代码格式不正确，应为 #RRGGBB 格式（如 #FF0000）')
            return
            
        super().save_model(request, obj, form, change)


class SPUAttributeInline(admin.TabularInline):
    """SPU属性内联编辑 - 优化版"""
    model = SPUAttribute
    extra = 1
    min_num = 0
    max_num = 20  # 限制最大属性数量
    
    fields = ['attribute', 'get_attribute_info', 'is_required', 'default_value', 'get_values_preview', 'order']
    readonly_fields = ['get_attribute_info', 'get_values_preview']
    
    # 添加自定义 CSS 和 JavaScript
    class Media:
        css = {
            'all': ('admin/css/spu_attribute_inline.css',)
        }
        js = ('admin/js/spu_attribute_inline.js',)
    
    class SPUAttributeForm(ModelForm):
        """自定义SPU属性表单"""
        class Meta:
            model = SPUAttribute
            fields = '__all__'
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
            # 如果已经选择了属性，则为default_value字段设置选择器
            if self.instance and self.instance.attribute_id:
                attribute = self.instance.attribute
                choices = self.get_attribute_value_choices(attribute)
                
                if choices:
                    self.fields['default_value'].widget = Select(choices=choices)
                    self.fields['default_value'].help_text = f"从{attribute.name}的可用值中选择默认值"
        
        def get_attribute_value_choices(self, attribute):
            """获取属性值选择项"""
            if not attribute:
                return []
            
            choices = [('', '--- 请选择 ---')]
            
            # 获取该属性的所有活跃值
            values = attribute.values.filter(is_active=True).order_by('order', 'value')
            
            for value in values:
                display_name = value.display_name or value.value
                choices.append((value.value, display_name))
            
            return choices
    
    form = SPUAttributeForm
    
    def get_attribute_info(self, obj):
        """显示属性信息"""
        if obj and obj.attribute:
            attr = obj.attribute
            type_colors = {
                'text': '#007cba',      # 蓝色
                'number': '#28a745',    # 绿色
                'select': '#ffc107',    # 黄色
                'multiselect': '#fd7e14', # 橙色
                'boolean': '#6c757d',   # 灰色
                'date': '#17a2b8',      # 青色
                'color': '#e83e8c',     # 粉色
                'image': '#6f42c1',     # 紫色
            }
            
            color = type_colors.get(attr.type, '#6c757d')
            type_display = dict(attr.ATTRIBUTE_TYPES).get(attr.type, attr.type)
            
            info_html = f'''
            <div style="font-size: 12px; line-height: 1.4;">
                <div style="margin-bottom: 3px;">
                    <span style="background-color: {color}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">
                        {type_display}
                    </span>
                </div>
                <div style="color: #666;">
                    编码: <strong>{attr.code}</strong>
                </div>
                {f'<div style="color: #666;">单位: {attr.unit}</div>' if attr.unit else ''}
                {f'<div style="color: #999; font-size: 11px;">{attr.description[:50]}...</div>' if attr.description else ''}
            </div>
            '''
            return format_html(info_html)
        return '-'
    
    get_attribute_info.short_description = '属性信息'
    
    def get_values_preview(self, obj):
        """显示属性值预览"""
        if obj and obj.attribute:
            attr = obj.attribute
            values = attr.values.filter(is_active=True)[:5]  # 只显示前5个值
            
            if not values.exists():
                return format_html('<span style="color: #999; font-size: 11px;">无可用值</span>')
            
            preview_html = '<div style="font-size: 11px; max-width: 200px;">'
            
            for value in values:
                if attr.type == 'color' and value.color_code:
                    preview_html += f'''
                    <span style="display: inline-block; width: 12px; height: 12px; 
                         background-color: {value.color_code}; border: 1px solid #ddd; 
                         border-radius: 2px; margin-right: 3px; vertical-align: middle;" 
                         title="{value.value}"></span>
                    '''
                elif attr.type == 'image' and value.image:
                    preview_html += f'''
                    <img src="{value.image.url}" style="width: 16px; height: 16px; 
                         margin-right: 3px; border-radius: 2px;" title="{value.value}">
                    '''
                else:
                    display_value = value.display_name or value.value
                    if len(display_value) > 8:
                        display_value = display_value[:8] + '...'
                    preview_html += f'<span style="background: #f8f9fa; padding: 1px 4px; margin-right: 2px; border-radius: 2px; border: 1px solid #e9ecef;" title="{value.value}">{display_value}</span>'
            
            total_count = attr.values.filter(is_active=True).count()
            if total_count > 5:
                preview_html += f'<span style="color: #999;">... +{total_count - 5}个</span>'
            
            preview_html += '</div>'
            return format_html(preview_html)
        
        return '-'
    
    get_values_preview.short_description = '可选值预览'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """定制属性选择框"""
        if db_field.name == "attribute":
            # 只显示启用的属性
            kwargs["queryset"] = Attribute.objects.filter(is_active=True).order_by('order', 'name')
            
            # 自定义属性显示格式
            class AttributeChoiceField(ModelChoiceField):
                def label_from_instance(self, obj):
                    type_display = dict(obj.ATTRIBUTE_TYPES).get(obj.type, obj.type)
                    unit_info = f" ({obj.unit})" if obj.unit else ""
                    return f"{obj.name} [{type_display}]{unit_info} - {obj.code}"
            
            kwargs["form_class"] = AttributeChoiceField
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_formset(self, request, obj=None, **kwargs):
        """定制表单集"""
        formset = super().get_formset(request, obj, **kwargs)
        
        # 添加自定义验证
        original_clean = formset.clean
        
        def clean(self):
            if hasattr(original_clean, '__call__'):
                original_clean(self)
            
            # 检查是否有重复的属性
            attributes = []
            for form in self.forms:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    attribute = form.cleaned_data.get('attribute')
                    if attribute:
                        if attribute in attributes:
                            raise ValidationError(f'属性 "{attribute.name}" 不能重复关联到同一个SPU')
                        attributes.append(attribute)
        
        formset.clean = clean
        return formset


# ===================== 内联编辑器类定义 =====================

class SPUDimensionTemplateInline(admin.TabularInline):
    """SPU尺寸模板内联编辑器"""
    model = SPUDimensionTemplate
    extra = 1
    min_num = 0
    max_num = 8
    
    fields = [
        'dimension_type', 'default_value', 'unit', 
        'min_value', 'max_value', 'is_required', 'is_key_dimension', 'order'
    ]
    
    verbose_name = "SPU尺寸模板"
    verbose_name_plural = "SPU尺寸模板"
    
    # 默认展开
    classes = []
    
    def get_formset(self, request, obj=None, **kwargs):
        """获取表单集，自动设置SPU"""
        FormSetClass = super().get_formset(request, obj, **kwargs)
        
        class CustomFormSet(FormSetClass):
            def save(self, commit=True):
                instances = super().save(commit=False)
                for instance in instances:
                    if obj:  # obj是当前编辑的SPU
                        instance.spu = obj
                    if not instance.pk and hasattr(request, 'user'):
                        instance.created_by = request.user
                    if commit:
                        instance.save()
                if commit:
                    self.save_m2m()
                return instances
        
        return CustomFormSet


class ProductsPricingRuleInline(admin.TabularInline):
    """SPU产品加价规则内联编辑器"""
    model = ProductsPricingRule
    extra = 1
    min_num = 0
    max_num = 5
    
    # 使用简洁的字段布局，控制列宽
    fields = ['name', 'rule_type', 'threshold_value', 'price_increment', 'is_active']
    
    verbose_name = "加价规则"
    verbose_name_plural = "加价规则"
    
    # 添加自定义样式，默认展开
    classes = []
    
    def get_queryset(self, request):
        """只显示SPU级别的规则（sku为空的规则）"""
        return super().get_queryset(request).filter(sku__isnull=True)
    
    def get_formset(self, request, obj=None, **kwargs):
        """获取表单集，自动设置SPU"""
        FormSetClass = super().get_formset(request, obj, **kwargs)
        
        class CustomFormSet(FormSetClass):
            def save(self, commit=True):
                instances = super().save(commit=False)
                for instance in instances:
                    if obj:  # obj是当前编辑的SPU
                        instance.spu = obj
                        instance.sku = None  # 确保这是SPU级别的规则
                    if not instance.pk and hasattr(request, 'user'):
                        instance.created_by = request.user
                    if commit:
                        instance.save()
                if commit:
                    self.save_m2m()
                return instances
        
        return CustomFormSet


class ProductsDimensionInline(admin.TabularInline):
    """SKU产品尺寸内联编辑器"""
    model = ProductsDimension
    extra = 1
    min_num = 0
    max_num = 8
    
    # 使用简洁的字段布局，重点字段优先
    fields = [
        'dimension_type', 'standard_value', 'unit', 
        'min_value', 'max_value', 'is_key_dimension'
    ]
    
    verbose_name = "产品尺寸"
    verbose_name_plural = "产品尺寸"
    
    # 添加自定义样式，默认展开
    classes = []
    
    def get_formset(self, request, obj=None, **kwargs):
        """获取表单集，自动设置SKU"""
        FormSetClass = super().get_formset(request, obj, **kwargs)
        
        class CustomFormSet(FormSetClass):
            def save(self, commit=True):
                instances = super().save(commit=False)
                for instance in instances:
                    if obj:  # obj是当前编辑的SKU
                        instance.sku = obj
                    if not instance.pk and hasattr(request, 'user'):
                        instance.created_by = request.user
                    if commit:
                        instance.save()
                if commit:
                    self.save_m2m()
                return instances
        
        return CustomFormSet


class SKUPricingRuleInline(admin.TabularInline):
    """SKU专属加价规则内联编辑器"""
    model = ProductsPricingRule
    extra = 1
    min_num = 0
    max_num = 3
    
    # 使用简洁的字段布局，控制列宽  
    fields = ['name', 'rule_type', 'threshold_value', 'unit_increment', 'price_increment', 'is_active']
    
    # 隐藏SPU字段，自动设置
    exclude = ['spu']
    
    verbose_name = "SKU专属加价规则"
    verbose_name_plural = "SKU专属加价规则"
    
    # 默认展开，不折叠
    classes = []
    
    def get_queryset(self, request):
        """只显示当前SKU的专属规则"""
        queryset = super().get_queryset(request)
        # 过滤出有SKU且有SPU的规则
        return queryset.filter(
            sku__isnull=False,
            spu__isnull=False
        ).select_related('spu', 'sku')
    
    def get_formset(self, request, obj=None, **kwargs):
        """获取表单集，自动设置SPU和SKU"""
        FormSetClass = super().get_formset(request, obj, **kwargs)
        
        class CustomFormSet(FormSetClass):
            def save(self, commit=True):
                instances = super().save(commit=False)
                for instance in instances:
                    if obj:  # obj是当前编辑的SKU
                        instance.sku = obj
                        # 确保SPU被正确设置
                        if hasattr(obj, 'spu') and obj.spu:
                            instance.spu = obj.spu
                        else:
                            # 如果由于某种原因SKU没有SPU，跳过这个实例
                            continue
                    # 设置创建人
                    if not instance.pk and hasattr(request, 'user'):
                        instance.created_by = request.user
                    if commit:
                        instance.save()
                if commit:
                    self.save_m2m()
                return instances
        
        return CustomFormSet


@admin.register(SPU)
class SPUAdmin(BaseModelAdmin):
    """SPU管理 - ROYANA品牌优化版"""
    
    list_display = ['name', 'code', 'category', 'brand', 'get_attribute_count', 'get_sku_count', 'get_price_range', 'is_active', 'created_at']
    list_filter = ['category', 'brand', 'is_active', 'created_at', 'attributes__type']
    search_fields = ['name', 'code', 'description', 'attributes__name', 'attributes__code']
    list_editable = ['is_active']
    ordering = ['brand', 'category', 'name']
    filter_horizontal = []  # 移除默认的多选框，使用内联编辑
    inlines = [SPUAttributeInline, SPUDimensionTemplateInline, ProductsPricingRuleInline]
    actions = ['duplicate_spu', 'copy_attributes', 'activate_spu', 'deactivate_spu', 'create_standard_skus']
    
    # 添加自定义 CSS 和 JavaScript
    class Media:
        css = {
            'all': ('admin/css/spu_admin.css',)
        }
        js = ('admin/js/spu_admin.js', 'admin/js/spu_dimension_template.js')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'code', 'category', 'brand'),
            'description': 'SPU的基本标识信息，编码在系统中必须唯一。品牌信息关联到具体制造商。'
        }),
        ('详细信息', {
            'fields': ('description', 'specifications', 'usage_scenario'),
            'classes': ('collapse',),
            'description': '产品的详细描述和规格说明，用于指导SKU创建'
        }),
        ('状态', {
            'fields': ('is_active',)
        }),
        ('配置说明', {
            'fields': (),
            'description': '<strong>配置指南：</strong><br/>'
                          '• <strong>属性配置</strong>：定义此SPU支持的所有属性维度，如尺寸、材质、风格等<br/>'
                          '• <strong>尺寸模板</strong>：设置标准尺寸模板，创建SKU时自动继承这些尺寸配置<br/>'
                          '• <strong>加价规则</strong>：设置SPU级别的通用加价规则，应用于基于此SPU创建的所有SKU<br/>'
                          '• 保存后可在下方的内联编辑区域进行详细配置',
            'classes': ('collapse',)
        }),
    )
    
    def get_attribute_count(self, obj):
        """显示关联的属性数量"""
        count = obj.spuattribute_set.count()
        if count > 0:
            # 使用Django Admin的正确URL格式
            url = reverse('admin:products_spuattribute_changelist') + f'?spu__id__exact={obj.id}'
            return format_html(
                '<a href="{}" style="color: #007cba; text-decoration: none;">{} 个属性</a>',
                url, count
            )
        return f'{count} 个属性'
    
    get_attribute_count.short_description = '配置属性'
    get_attribute_count.admin_order_field = 'spuattribute_count'
    
    def get_sku_count(self, obj):
        """显示 SKU 数量"""
        count = obj.skus.count()
        if count > 0:
            # 使用Django Admin的正确URL格式
            url = reverse('admin:products_sku_changelist') + f'?spu__id__exact={obj.id}'
            return format_html(
                '<a href="{}" style="color: #28a745; text-decoration: none;">{} 个产品</a>',
                url, count
            )
        return f'{count} 个产品'
    
    get_sku_count.short_description = 'SKU产品'
    get_sku_count.admin_order_field = 'sku_count'
    
    def get_price_range(self, obj):
        """显示基于此SPU的SKU价格范围"""
        skus = obj.skus.filter(status='active')
        if not skus.exists():
            return '-'
        
        prices = skus.values_list('price', flat=True)
        min_price = min(prices)
        max_price = max(prices)
        
        if min_price == max_price:
            return f'¥{min_price}'
        else:
            return format_html(
                '<span style="color: #dc3545;">¥{}</span> - <span style="color: #28a745;">¥{}</span>',
                min_price, max_price
            )
    
    get_price_range.short_description = '价格范围'
    
    get_sku_count.short_description = 'SKU数量'
    get_sku_count.admin_order_field = 'sku_count'
    
    def get_queryset(self, request):
        """优化查询，避免N+1问题"""
        return super().get_queryset(request).select_related('category').prefetch_related(
            'spuattribute_set__attribute',
            'skus'
        ).annotate(
            spuattribute_count=Count('spuattribute'),
            sku_count=Count('skus')
        )
    
    # 自定义批量操作
    def duplicate_spu(self, request, queryset):
        """复制SPU"""
        duplicated_count = 0
        for spu in queryset:
            # 创建新的SPU副本
            new_spu = SPU.objects.create(
                name=f"{spu.name} (副本)",
                code=f"{spu.code}_copy_{duplicated_count + 1}",
                category=spu.category,
                description=spu.description,
                specifications=spu.specifications,
                usage_scenario=spu.usage_scenario,
                is_active=False,  # 默认设为未启用
                created_by=request.user
            )
            
            # 复制属性关联
            for spu_attr in spu.spuattribute_set.all():
                SPUAttribute.objects.create(
                    spu=new_spu,
                    attribute=spu_attr.attribute,
                    is_required=spu_attr.is_required,
                    default_value=spu_attr.default_value,
                    order=spu_attr.order
                )
            
            duplicated_count += 1
        
        self.message_user(request, f'成功复制了 {duplicated_count} 个SPU')
    
    duplicate_spu.short_description = '复制选中的SPU'
    
    def copy_attributes(self, request, queryset):
        """复制属性配置到其他SPU"""
        if queryset.count() != 1:
            self.message_user(request, '请选择一个SPU作为属性配置源', level=messages.WARNING)
            return
        
        source_spu = queryset.first()
        # 这里可以添加更复杂的逻辑，比如弹出选择目标SPU的对话框
        # 暂时只显示提示信息
        self.message_user(
            request, 
            f'已选择 "{source_spu.name}" 作为属性配置源。请在下次更新中实现目标SPU选择功能。',
            level=messages.INFO
        )
    
    copy_attributes.short_description = '复制属性配置'
    
    def activate_spu(self, request, queryset):
        """激活SPU"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'成功激活了 {updated} 个SPU')
    
    activate_spu.short_description = '激活选中的SPU'
    
    def deactivate_spu(self, request, queryset):
        """停用SPU"""
        # 检查是否有关联的活跃SKU
        has_active_skus = False
        for spu in queryset:
            if spu.skus.filter(status='active').exists():
                has_active_skus = True
                break
        
        if has_active_skus:
            self.message_user(
                request,
                '无法停用SPU：存在状态为"上架"的SKU。请先下架相关SKU。',
                level=messages.ERROR
            )
            return
        
        updated = queryset.update(is_active=False)
        self.message_user(request, f'成功停用了 {updated} 个SPU')
    
    deactivate_spu.short_description = '停用选中的SPU'

    def get_urls(self):
        """添加自定义URL"""
        urls = super().get_urls()
        custom_urls = [
            path('attribute-api/', self.admin_site.admin_view(self.attribute_api_view), name='products_spu_attribute_api'),
            path('category-attributes/<int:category_id>/', self.admin_site.admin_view(self.category_attributes_view), name='products_spu_category_attributes'),
            path('attribute-values/<int:attribute_id>/', self.admin_site.admin_view(self.attribute_values_view), name='products_spu_attribute_values'),
            path('clear-cache/', self.admin_site.admin_view(self.clear_cache_view), name='products_spu_clear_cache'),
        ]
        return custom_urls + urls
    
    def attribute_api_view(self, request):
        """属性 API 代理视图"""
        from .views import AttributeAPIView
        return AttributeAPIView.as_view()(request)
    
    def category_attributes_view(self, request, category_id):
        """分类属性推荐 API 代理视图"""
        from .views import CategoryAttributesAPIView
        return CategoryAttributesAPIView.as_view()(request, category_id)
    
    def attribute_values_view(self, request, attribute_id):
        """属性值 API 代理视图"""
        from .views import attribute_values_api
        return attribute_values_api(request, attribute_id)
    
    def clear_cache_view(self, request):
        """清除缓存 API 代理视图"""
        from .views import clear_attribute_cache
        return clear_attribute_cache(request)




class ProductImageInline(admin.TabularInline):
    """产品图片内联编辑"""
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'order', 'is_active']
    
    class Media:
        css = {
            'all': ()
        }
        js = ()


class SKUAttributeValueForm(forms.ModelForm):
    """SKU属性值表单"""
    
    class Meta:
        model = SKUAttributeValue
        fields = ['attribute', 'attribute_value']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 属性字段设置
        self.fields['attribute'].queryset = Attribute.objects.filter(is_active=True).order_by('order', 'name')
        self.fields['attribute'].empty_label = "--- 请选择属性 ---"
        
        # 属性值字段初始设置
        if self.instance and self.instance.pk and self.instance.attribute:
            # 编辑现有记录时，显示该属性的所有值
            self.fields['attribute_value'].queryset = AttributeValue.objects.filter(
                attribute=self.instance.attribute,
                is_active=True
            ).order_by('order', 'value')
        else:
            # 新建记录时，初始为空
            self.fields['attribute_value'].queryset = AttributeValue.objects.none()
            
        self.fields['attribute_value'].empty_label = "--- 请先选择属性 ---"
    
    def clean_attribute_value(self):
        """验证属性值是否属于选定的属性"""
        attribute = self.cleaned_data.get('attribute')
        attribute_value = self.cleaned_data.get('attribute_value')
        
        if attribute and attribute_value:
            # 动态验证：检查属性值是否属于选定的属性
            if not AttributeValue.objects.filter(
                id=attribute_value.id,
                attribute=attribute,
                is_active=True
            ).exists():
                raise forms.ValidationError("所选属性值不属于选定的属性")
        
        return attribute_value
    
    def clean(self):
        """表单整体验证"""
        cleaned_data = super().clean()
        attribute = cleaned_data.get('attribute')
        attribute_value = cleaned_data.get('attribute_value')
        
        # 如果选择了属性但没有选择属性值，给出提示
        if attribute and not attribute_value:
            raise forms.ValidationError("请为选定的属性选择一个属性值")
        
        # 如果选择了属性值但没有选择属性，给出提示
        if attribute_value and not attribute:
            raise forms.ValidationError("请先选择属性")
        
        return cleaned_data


class SKUAttributeValueInline(admin.TabularInline):
    """SKU属性值内联编辑"""
    model = SKUAttributeValue
    form = SKUAttributeValueForm
    extra = 1
    min_num = 0
    max_num = 20
    fields = ['attribute', 'attribute_value']
    
    def get_verbose_name(self):
        return "SKU属性值"
    
    def get_verbose_name_plural(self):
        return "SKU属性值"
    
    # 添加自定义 CSS 和 JavaScript
    class Media:
        css = {
            'all': ('admin/css/sku_attribute_value_inline.css',)
        }
        js = ('admin/js/sku_attribute_value_inline.js',)
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('attribute', 'attribute_value')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """为外键字段设置默认值和过滤"""
        if db_field.name == "attribute":
            # 获取所有可用属性
            kwargs["queryset"] = Attribute.objects.filter(is_active=True).order_by('order', 'name')
            
        elif db_field.name == "attribute_value":
            # 初始时显示空的queryset，由JavaScript动态加载
            kwargs["queryset"] = AttributeValue.objects.none()
            
            # 自定义属性值显示格式
            from django.forms import ModelChoiceField
            class AttributeValueChoiceField(ModelChoiceField):
                def label_from_instance(self, obj):
                    return obj.display_name or obj.value
            
            kwargs["form_class"] = AttributeValueChoiceField
            
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_extra(self, request, obj=None, **kwargs):
        """动态设置额外表单数量"""
        if obj and obj.spu:
            # 获取SPU的必填属性数量
            required_count = obj.spu.spuattribute_set.filter(is_required=True).count()
            # 获取当前SKU已有的属性数量
            existing_count = obj.sku_attribute_values.count()
            # 计算需要额外添加的表单数量
            extra_needed = max(0, required_count - existing_count)
            return extra_needed + 1  # 至少保留1个额外表单
        return 1
    
    def get_formset(self, request, obj=None, **kwargs):
        """自定义表单集，用于自动同步SPU必填属性"""
        # 动态设置extra数量
        if obj and obj.spu:
            kwargs['extra'] = self.get_extra(request, obj, **kwargs)
        
        formset_class = super().get_formset(request, obj, **kwargs)
        
        # 自定义formset类，添加SPU属性同步功能
        class SPUSyncFormSet(formset_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                
                # 如果是编辑现有SKU，自动同步必填属性
                if obj and obj.spu:
                    self.sync_required_attributes_from_spu(obj.spu)
            
            def sync_required_attributes_from_spu(self, spu):
                """从SPU同步必填属性"""
                # 获取SPU的必填属性
                required_spu_attributes = spu.spuattribute_set.filter(is_required=True).select_related('attribute')
                
                # 获取当前SKU已有的属性ID
                existing_attributes = set()
                for form in self.forms:
                    if form.instance and form.instance.attribute_id:
                        existing_attributes.add(form.instance.attribute_id)
                
                # 为空表单设置必填属性的初始值
                empty_form_index = 0
                for spu_attr in required_spu_attributes:
                    if spu_attr.attribute.id not in existing_attributes:
                        # 找到一个空表单
                        while empty_form_index < len(self.forms):
                            form = self.forms[empty_form_index]
                            if not form.instance.attribute_id:
                                # 设置属性
                                form.initial['attribute'] = spu_attr.attribute.id
                                form.instance.attribute = spu_attr.attribute
                                
                                # 如果SPU属性有默认值，设置默认属性值
                                if spu_attr.default_value:
                                    try:
                                        default_attr_value = spu_attr.attribute.values.filter(
                                            value=spu_attr.default_value,
                                            is_active=True
                                        ).first()
                                        if default_attr_value:
                                            form.initial['attribute_value'] = default_attr_value.id
                                            form.instance.attribute_value = default_attr_value
                                    except:
                                        pass
                                
                                empty_form_index += 1
                                break
                            empty_form_index += 1
        
        return SPUSyncFormSet


@admin.register(SKU)
class SKUAdmin(BaseModelAdmin):
    """SKU管理 - ROYANA品牌优化版"""
    
    list_display = ['get_product_code', 'name', 'spu', 'brand', 'get_price_display', 'get_attributes_display', 'stock_quantity', 'status', 'is_featured', 'updated_at']
    list_filter = ['spu', 'brand', 'status', 'is_featured', 'updated_at', SeriesFilter, WidthFilter]  # 使用自定义过滤器
    search_fields = ['name', 'code', 'spu__name', 'brand__name']
    list_editable = ['stock_quantity', 'status', 'is_featured']
    ordering = ['-updated_at','brand','spu','code']
    inlines = [SKUAttributeValueInline, ProductImageInline, ProductsDimensionInline, SKUPricingRuleInline]
    actions = ['sync_from_spu_action']
    
    # 添加自定义 CSS 和 JavaScript
    class Media:
        css = {
            'all': ('admin/css/sku_admin.css',)
        }
        js = ('admin/js/enhanced_admin.js', 'admin/js/sku_dimension_sync.js')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'code', 'spu', 'brand'),
            'description': '产品的基本标识信息和关联关系。编码格式：如N-U30-7256-L'
        }),
        ('价格信息', {
            'fields': ('price', 'cost_price', 'market_price'),
            'description': '产品定价信息，支持成本价、售价、市场价管理'
        }),
        ('库存信息', {
            'fields': ('stock_quantity', 'min_stock'),
            'description': '库存数量和安全库存设置'
        }),
        ('产品信息', {
            'fields': ('description', 'remarks', 'main_image', 'selling_points', 'tags'),
            'classes': ('collapse',),
            'description': '产品详细信息和营销材料'
        }),
        ('状态和时间', {
            'fields': ('status', 'is_featured', 'launch_date'),
            'classes': ('collapse',),
            'description': '产品状态管理和上市信息'
        }),
        ('高级配置说明', {
            'fields': (),
            'description': '<strong>高级配置指南：</strong><br/>'
                          '• <strong>属性值配置</strong>：设置此SKU的具体属性值，如颜色、尺寸等<br/>'
                          '• <strong>产品图片</strong>：上传产品的展示图片<br/>'
                          '• <strong>产品尺寸</strong>：定义产品的标准尺寸信息，用于动态价格计算（自动继承SPU尺寸模板，可修改）<br/>'
                          '• <strong>专属加价规则</strong>：设置仅适用于此SKU的特殊加价规则（优先级高于SPU规则，默认展开）<br/>'
                          '• 保存后可在下方的内联编辑区域进行详细配置',
            'classes': ('collapse',)
        }),
    )
    
    def get_product_code(self, obj):
        """显示产品编码，突出NOVO系列特征"""
        if 'NOVO' in obj.code or 'N-' in obj.code:
            return format_html(
                '<span style="background-color: #007cba; color: white; padding: 2px 4px; border-radius: 3px; font-family: monospace;">{}</span>',
                obj.code
            )
        return obj.code
    
    get_product_code.short_description = '产品编码'
    get_product_code.admin_order_field = 'code'
    
    def get_price_display(self, obj):
        """价格显示，根据价格区间使用不同颜色"""
        price = obj.price
        if price >= 1000:
            color = '#dc3545'  # 红色：高价位
        elif price >= 600:
            color = '#ffc107'  # 黄色：中价位
        else:
            color = '#28a745'  # 绿色：低价位
            
        return format_html(
            '<span style="color: {}; font-weight: bold;">¥{}</span>',
            color, price
        )
    
    get_price_display.short_description = '售价'
    get_price_display.admin_order_field = 'price'
    
    def get_attributes_display(self, obj):
        """显示SKU的规格属性"""
        # 获取SKU的属性值
        attribute_values = obj.sku_attribute_values.select_related('attribute', 'attribute_value').all()
        
        if not attribute_values:
            return format_html('<span style="font-style: italic; color: #999;">无属性</span>')
        
        # 预定义的属性类型颜色映射
        type_color_map = {
            'text': '#424242',        # 深灰色 - 文本类型
            'number': '#1976d2',      # 蓝色 - 数字类型  
            'select': '#388e3c',      # 绿色 - 选择类型
            'multiselect': '#7b1fa2', # 紫色 - 多选类型
            'boolean': '#f57c00',     # 橙色 - 布尔类型
            'date': '#d32f2f',        # 红色 - 日期类型
            'color': '#e91e63',       # 粉色 - 颜色类型
            'image': '#795548',       # 棕色 - 图片类型
        }
        
        # 特定属性编码的颜色覆盖（优先级更高）
        code_color_map = {
            'WIDTH': '#1976d2',       # 蓝色 - 宽度
            'DIRECTION': '#388e3c',   # 绿色 - 开门方向
            'TYPE': '#7b1fa2',        # 紫色 - 类型
            'BOARD_LEVEL': '#f57c00', # 橙色 - 板子级别
            'COLOR': '#5d4037',       # 棕色 - 颜色
            'MATERIAL': '#5d4037',    # 棕色 - 材质
        }
        
        # 默认颜色池（用于未知属性）
        default_colors = [
            '#1976d2', '#388e3c', '#7b1fa2', '#f57c00', '#d32f2f',
            '#e91e63', '#795548', '#607d8b', '#ff5722', '#9c27b0',
            '#2196f3', '#4caf50', '#ff9800', '#673ab7', '#009688'
        ]
        
        def get_attribute_color(attribute):
            """获取属性的显示颜色"""
            # 1. 优先使用特定属性编码的颜色
            if attribute.code in code_color_map:
                return code_color_map[attribute.code]
            
            # 2. 根据属性类型获取颜色
            if attribute.type in type_color_map:
                return type_color_map[attribute.type]
            
            # 3. 使用默认颜色池，基于属性ID确保一致性
            color_index = attribute.id % len(default_colors)
            return default_colors[color_index]
        
        formatted_attrs = []
        for sku_attr_value in attribute_values:
            attribute = sku_attr_value.attribute
            attribute_value = sku_attr_value.attribute_value
            
            if attribute_value and attribute_value.value:  # 只显示有值的属性
                # 获取属性颜色
                color = get_attribute_color(attribute)
                
                # 获取显示值
                display_value = attribute_value.display_name or attribute_value.value
                
                # 特殊处理某些属性的显示值
                if attribute.code == 'WIDTH' and display_value.isdigit():
                    display_value = f"{display_value}cm"
                elif attribute.code == 'DIRECTION':
                    if display_value.upper() == 'L':
                        display_value = "左开"
                    elif display_value.upper() == 'R':
                        display_value = "右开"
                
                # 特殊处理颜色属性，显示颜色方块
                if attribute.type == 'color' and attribute_value.color_code:
                    color_square = f'<span style="display: inline-block; width: 12px; height: 12px; background-color: {attribute_value.color_code}; border: 1px solid #ccc; margin-right: 3px; vertical-align: middle;"></span>'
                    formatted_value = f'{color_square}<span style="color: {color}; font-weight: 600;">{display_value}</span>'
                else:
                    formatted_value = f'<span style="color: {color}; font-weight: 600;">{display_value}</span>'
                
                formatted_attrs.append(formatted_value)
        
        return format_html('&nbsp;|&nbsp;'.join(formatted_attrs)) if formatted_attrs else format_html('<span style="font-style: italic; color: #999;">无属性</span>')
    
    get_attributes_display.short_description = '规格属性'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('spu', 'brand')
    
    def has_change_permission(self, request, obj=None):
        """检查修改权限"""
        if obj and obj.status == 'discontinued':
            # 停产产品不允许修改
            if not request.user.is_superuser:
                return False
        return super().has_change_permission(request, obj)
    
    def get_readonly_fields(self, request, obj=None):
        """SKU模型没有created_at和updated_at字段，因此不添加到只读字段"""
        readonly_fields = list(self.readonly_fields)
        
        # 如果是停产产品，除了状态字段，其他都设为只读
        if obj and obj.status == 'discontinued' and not request.user.is_superuser:
            readonly_fields.extend(['name', 'code', 'spu', 'brand', 'price', 'cost_price', 'market_price'])
            
        return readonly_fields
    
    def has_delete_permission(self, request, obj=None):
        """删除权限检查"""
        return super().has_delete_permission(request, obj)
    

    
    def save_model(self, request, obj, form, change):
        """重写保存方法，简化处理逻辑"""
        # 保存前验证
        try:
            obj.full_clean()
        except ValidationError as e:
            print(f"验证失败: {e}")
            # 将验证错误转换为用户友好的消息
            from django.contrib import messages
            if hasattr(e, 'error_dict'):
                for field, errors in e.error_dict.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error.message}')
            else:
                messages.error(request, f'数据验证错误: {e}')
            raise
        
        super().save_model(request, obj, form, change)
        
        # 如果是新创建的SKU且有SPU，自动同步SPU的属性和加价规则
        if not change and obj.spu:
            self.sync_spu_attributes_and_rules(obj)
    
    def save_formset(self, request, form, formset, change):
        """重写保存formset方法，处理内联表单的数据"""
        instances = formset.save(commit=False)
        
        # 如果这是SKU属性值的formset，需要特殊处理
        if hasattr(formset, 'model') and formset.model.__name__ == 'SKUAttributeValue':
            # 对于新创建的SKU，先保存主对象以获取ID
            if not form.instance.pk:
                form.instance.save()
            
            # 处理每个保存的实例
            for instance in instances:
                if hasattr(instance, 'attribute') and hasattr(instance, 'get_display_value'):
                    # 这是SKUAttributeValue实例
                    instance.sku = form.instance
                    instance.save()
            
            # 处理删除的实例
            for instance in formset.deleted_objects:
                instance.delete()
            
            # 检查必填属性是否都有值
            self.ensure_required_attributes(form.instance)
            
        else:
            # 其他formset的默认处理
            for instance in instances:
                instance.save()
            
            # 处理删除的实例
            for instance in formset.deleted_objects:
                instance.delete()
        
        formset.save_m2m()

    def ensure_required_attributes(self, sku):
        """确保SKU具有所有必填属性的值"""
        if not sku.spu:
            return
            
        required_attributes = sku.spu.spuattribute_set.filter(is_required=True)
        
        for spu_attr in required_attributes:
            # 检查是否已经有这个属性的值
            existing_value = sku.sku_attribute_values.filter(
                attribute=spu_attr.attribute
            ).first()
            
            if not existing_value:
                # 如果没有，创建一个带有默认值的记录
                default_value = spu_attr.default_value
                if default_value:
                    # 尝试匹配预定义的属性值
                    try:
                        from .models import AttributeValue, SKUAttributeValue
                        attribute_value = AttributeValue.objects.get(
                            attribute=spu_attr.attribute,
                            value=default_value,
                            is_active=True
                        )
                        SKUAttributeValue.objects.create(
                            sku=sku,
                            attribute=spu_attr.attribute,
                            attribute_value=attribute_value
                        )
                    except AttributeValue.DoesNotExist:
                        # 如果没有匹配的预定义值，使用自定义值
                        from .models import SKUAttributeValue
                        SKUAttributeValue.objects.create(
                            sku=sku,
                            attribute=spu_attr.attribute,
                            custom_value=default_value
                        )
                else:
                    # 如果没有默认值，创建空的记录等待用户填写
                    from .models import SKUAttributeValue
                    SKUAttributeValue.objects.create(
                        sku=sku,
                        attribute=spu_attr.attribute,
                        custom_value=''
                    )

    def sync_spu_attributes_and_rules(self, sku):
        """同步SPU的属性、尺寸模板和加价规则到新创建的SKU"""
        if not sku.spu:
            return
            
        from .models import SKUAttributeValue, ProductsPricingRule, ProductsDimension
        
        print(f"开始同步SPU '{sku.spu.name}' 的属性、尺寸模板和加价规则到SKU '{sku.name}'")
        
        # 1. 同步SPU的所有属性
        spu_attributes = sku.spu.spuattribute_set.all().select_related('attribute')
        
        for spu_attr in spu_attributes:
            # 检查SKU是否已经有这个属性的值
            existing_value = sku.sku_attribute_values.filter(
                attribute=spu_attr.attribute
            ).first()
            
            if not existing_value:
                # 如果没有，创建属性值记录
                if spu_attr.default_value:
                    # 尝试匹配预定义的属性值
                    try:
                        from .models import AttributeValue
                        attribute_value = AttributeValue.objects.filter(
                            attribute=spu_attr.attribute,
                            value=spu_attr.default_value,
                            is_active=True
                        ).first()
                        
                        if attribute_value:
                            SKUAttributeValue.objects.create(
                                sku=sku,
                                attribute=spu_attr.attribute,
                                attribute_value=attribute_value
                            )
                            print(f"  同步属性: {spu_attr.attribute.name} = {attribute_value.value}")
                        else:
                            # 使用自定义值
                            SKUAttributeValue.objects.create(
                                sku=sku,
                                attribute=spu_attr.attribute,
                                custom_value=spu_attr.default_value
                            )
                            print(f"  同步属性: {spu_attr.attribute.name} = {spu_attr.default_value} (自定义值)")
                    except Exception as e:
                        print(f"  属性同步失败: {spu_attr.attribute.name} - {e}")
                else:
                    # 创建空的属性记录等待用户填写
                    SKUAttributeValue.objects.create(
                        sku=sku,
                        attribute=spu_attr.attribute,
                        custom_value=''
                    )
                    print(f"  创建空属性: {spu_attr.attribute.name}")
        
        # 2. 同步SPU的尺寸模板到SKU
        spu_dimension_templates = sku.spu.dimension_templates.all()
        
        for template in spu_dimension_templates:
            # 检查SKU是否已经有这个类型的尺寸
            existing_dimension = sku.dimensions.filter(
                dimension_type=template.dimension_type
            ).first()
            
            if not existing_dimension:
                # 如果没有，基于模板创建SKU尺寸
                ProductsDimension.objects.create(
                    sku=sku,
                    dimension_type=template.dimension_type,
                    standard_value=template.default_value,
                    min_value=template.min_value,
                    max_value=template.max_value,
                    unit=template.unit,
                    custom_unit=template.custom_unit,
                    tolerance=template.tolerance,
                    is_key_dimension=template.is_key_dimension,
                    description=template.description,
                    created_by=getattr(self.request, 'user', None) if hasattr(self, 'request') else None
                )
                print(f"  同步尺寸: {template.get_dimension_type_display()} = {template.default_value}{template.get_display_unit()}")
            else:
                print(f"  尺寸已存在: {template.get_dimension_type_display()}")
        
        # 3. 同步SPU级别的加价规则（复制为SKU专属规则）
        spu_pricing_rules = ProductsPricingRule.objects.filter(
            spu=sku.spu,
            sku__isnull=True,  # SPU级别的规则
            is_active=True
        )
        
        for spu_rule in spu_pricing_rules:
            # 检查是否已存在相同的SKU专属规则
            existing_rule = ProductsPricingRule.objects.filter(
                spu=sku.spu,
                sku=sku,
                name=spu_rule.name,
                rule_type=spu_rule.rule_type
            ).first()
            
            if not existing_rule:
                # 创建SKU专属的加价规则（复制SPU规则）
                ProductsPricingRule.objects.create(
                    spu=sku.spu,
                    sku=sku,
                    name=f"{spu_rule.name} (SKU专属)",
                    rule_type=spu_rule.rule_type,
                    threshold_value=spu_rule.threshold_value,
                    price_increment=spu_rule.price_increment,
                    unit_increment=spu_rule.unit_increment,
                    calculation_method=spu_rule.calculation_method,
                    multiplier=spu_rule.multiplier,
                    max_increment=spu_rule.max_increment,
                    effective_date=spu_rule.effective_date,
                    expiry_date=spu_rule.expiry_date,
                    is_active=spu_rule.is_active,
                    description=f"从SPU规则自动同步: {spu_rule.name}"
                )
                print(f"  同步加价规则: {spu_rule.name} -> {spu_rule.name} (SKU专属)")
        
        print(f"同步完成：SPU '{sku.spu.name}' -> SKU '{sku.name}'")

    def sync_from_spu_action(self, request, queryset):
        """批量同步SPU属性、尺寸模板和加价规则到选中的SKU"""
        updated_count = 0
        skipped_count = 0
        
        for sku in queryset:
            if sku.spu:
                self.sync_spu_attributes_and_rules(sku)
                updated_count += 1
            else:
                skipped_count += 1
        
        if updated_count > 0:
            self.message_user(
                request,
                f"成功同步了 {updated_count} 个SKU的属性、尺寸模板和加价规则。"
            )
        
        if skipped_count > 0:
            self.message_user(
                request,
                f"跳过了 {skipped_count} 个没有关联SPU的SKU。",
                level='warning'
            )
    
    sync_from_spu_action.short_description = "🔄 从SPU同步属性、尺寸和规则"


# SPU Dimension Template Admin 配置
@admin.register(SPUDimensionTemplate)
class SPUDimensionTemplateAdmin(BaseModelAdmin):
    """SPU尺寸模板管理"""
    
    list_display = ['spu', 'dimension_type', 'default_value', 'get_unit_display', 'is_required', 'is_key_dimension', 'order']
    list_filter = ['dimension_type', 'unit', 'is_required', 'is_key_dimension', 'spu__brand']
    search_fields = ['spu__name', 'spu__code', 'description']
    list_editable = ['order', 'is_required', 'is_key_dimension']
    ordering = ['spu', 'order', 'dimension_type']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('spu', 'dimension_type', 'default_value', 'unit', 'custom_unit')
        }),
        ('范围限制', {
            'fields': ('min_value', 'max_value', 'tolerance'),
            'classes': ('collapse',)
        }),
        ('配置选项', {
            'fields': ('is_required', 'is_key_dimension', 'order')
        }),
        ('描述信息', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )
    
    def get_unit_display(self, obj):
        """获取单位显示"""
        return obj.get_display_unit()
    
    get_unit_display.short_description = '单位'


# SPU Attribute Admin 配置
@admin.register(SPUAttribute)
class SPUAttributeAdmin(BaseModelAdmin):
    """SPU属性关联管理"""
    
    list_display = ['spu', 'attribute', 'is_required', 'order']
    list_filter = ['is_required', 'spu', 'attribute']
    search_fields = ['spu__name', 'attribute__name']
    list_editable = ['is_required', 'order']
    ordering = ['spu', 'order', 'attribute']
    
    def get_readonly_fields(self, request, obj=None):
        """SPUAttribute模型没有created_at和updated_at字段，因此不添加到只读字段"""
        # 只返回基类定义的只读字段，不添加时间戳字段
        return list(self.readonly_fields)
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('spu', 'attribute')


# SKUAttributeValue Admin 配置
@admin.register(SKUAttributeValue)
class SKUAttributeValueAdmin(BaseModelAdmin):
    """SKU属性值管理"""
    
    list_display = ['sku', 'attribute', 'get_value_display', 'get_attribute_type', 'created_at']
    list_filter = ['attribute', 'attribute__type', 'created_at', 'sku__spu', 'sku__brand']
    search_fields = ['sku__name', 'sku__code', 'attribute__name', 'custom_value', 'attribute_value__value']
    ordering = ['sku', 'attribute__order', 'attribute']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('sku', 'attribute')
        }),
        ('属性值', {
            'fields': ('attribute_value', 'custom_value'),
            'description': '对于选择类型的属性请选择"属性值"，对于文本/数字类型请填写"自定义值"'
        }),
    )
    
    def get_value_display(self, obj):
        """显示属性值"""
        value = obj.get_display_value()
        if obj.attribute.type == 'color' and obj.attribute_value and obj.attribute_value.color_code:
            return format_html(
                '<span style="background-color: {}; width: 20px; height: 20px; display: inline-block; margin-right: 5px; border: 1px solid #ccc;"></span>{}',
                obj.attribute_value.color_code,
                value
            )
        elif obj.attribute.type == 'image' and obj.attribute_value and obj.attribute_value.image:
            return format_html(
                '<img src="{}" style="width: 30px; height: 30px; object-fit: cover; margin-right: 5px;" />{}',
                obj.attribute_value.image.url,
                value
            )
        return value or "-"
    get_value_display.short_description = "属性值"
    
    def get_attribute_type(self, obj):
        """显示属性类型"""
        return obj.attribute.get_type_display()
    get_attribute_type.short_description = "属性类型"
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """自定义外键字段显示"""
        if db_field.name == "sku":
            kwargs["queryset"] = SKU.objects.select_related('spu', 'brand').order_by('spu__name', 'brand__name', 'name')
        elif db_field.name == "attribute":
            kwargs["queryset"] = Attribute.objects.filter(is_active=True).order_by('order', 'name')
            
            # 自定义属性显示格式，包含类型信息
            class AttributeChoiceFieldWithType(ModelChoiceField):
                def label_from_instance(self, obj):
                    type_display = dict(obj.ATTRIBUTE_TYPES).get(obj.type, obj.type)
                    unit_info = f" ({obj.unit})" if obj.unit else ""
                    return f"{obj.name} [{type_display}]{unit_info} - {obj.code}"
            
            kwargs["form_class"] = AttributeChoiceFieldWithType
            
        elif db_field.name == "attribute_value":
            kwargs["queryset"] = AttributeValue.objects.select_related('attribute').filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'sku__spu', 'sku__brand', 'attribute', 'attribute_value'
        )


# ProductImage Admin 配置
@admin.register(ProductImage)
class ProductImageAdmin(BaseModelAdmin):
    """产品图片管理"""
    
    list_display = ['get_image_display', 'sku', 'alt_text', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['sku__name', 'alt_text']
    list_editable = ['order', 'is_active']
    ordering = ['sku', 'order']
    
    def get_image_display(self, obj):
        """显示图片"""
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "无图片"
    get_image_display.short_description = '图片'
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('sku')


# 自定义 Admin 站点配置
admin.site.site_header = '整木定制产品库管理系统'
admin.site.site_title = '产品库管理'
admin.site.index_title = '产品数据管理'

# 自定义管理站点的中文化配置
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

class ChineseAdminSite(AdminSite):
    """中文化的管理站点"""
    site_header = _('整木定制产品库管理系统')
    site_title = _('产品库管理')
    index_title = _('产品数据管理')
    
    def each_context(self, request):
        context = super().each_context(request)
        context['site_header'] = self.site_header
        context['site_title'] = self.site_title
        context['index_title'] = self.index_title
        return context


@admin.register(ProductsPricingRule)
class ProductsPricingRuleAdmin(admin.ModelAdmin):
    """产品加价规则管理"""
    
    list_display = [
        'name', 'rule_scope_display', 'spu', 'sku', 'rule_type', 
        'threshold_value', 'price_increment', 'is_active', 'priority_display'
    ]
    
    list_filter = [
        'rule_type', 'calculation_method', 'is_active', 
        'effective_date', 'spu__brand', 'spu__category',
        ('sku', admin.RelatedOnlyFieldListFilter),  # 只显示有SKU的规则
    ]
    
    search_fields = [
        'name', 'description', 'spu__name', 'sku__name', 'sku__code'
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'priority_display']
    
    fieldsets = [
        ('规则归属', {
            'fields': ['spu', 'sku'],
            'description': '选择SPU（必须）和SKU（可选）。如果选择SKU，规则仅应用于该SKU；否则应用于整个SPU。'
        }),
        ('基本信息', {
            'fields': ['name', 'rule_type', 'description']
        }),
        ('计算参数', {
            'fields': [
                'threshold_value', 'unit_increment', 'calculation_method',
                'price_increment', 'multiplier', 'max_increment'
            ]
        }),
        ('状态和有效期', {
            'fields': ['is_active', 'effective_date', 'expiry_date']
        }),
        ('系统信息', {
            'fields': ['priority_display', 'created_at', 'updated_at', 'created_by'],
            'classes': ['collapse']
        })
    ]
    
    def rule_scope_display(self, obj):
        """显示规则作用范围"""
        if obj.sku:
            return format_html(
                '<span style="color: #e74c3c; font-weight: bold;">SKU专属</span>'
            )
        else:
            return format_html(
                '<span style="color: #3498db;">SPU通用</span>'
            )
    rule_scope_display.short_description = '规则范围'
    
    def priority_display(self, obj):
        """显示规则优先级"""
        return f"{obj.priority} ({'高' if obj.priority == 10 else '中'})"
    priority_display.short_description = '优先级'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """优化外键字段的选择"""
        if db_field.name == "sku":
            # 获取当前选择的SPU
            if request.resolver_match.kwargs.get('object_id'):
                try:
                    rule = ProductsPricingRule.objects.get(
                        pk=request.resolver_match.kwargs['object_id']
                    )
                    if rule.spu:
                        kwargs["queryset"] = SKU.objects.filter(
                            spu=rule.spu, status='active'
                        )
                except ProductsPricingRule.DoesNotExist:
                    pass
            else:
                # 添加新规则时，默认不显示任何SKU选项
                kwargs["queryset"] = SKU.objects.none()
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        """保存时设置创建人"""
        if not change:  # 新建时
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """优化查询性能"""
        return super().get_queryset(request).select_related(
            'spu', 'sku', 'created_by'
        )
    
    class Media:
        js = ['admin/js/pricing_rule_admin.js']  # 添加自定义JavaScript


class ProductsDimensionAdmin(admin.ModelAdmin):
    """产品尺寸管理"""
    
    list_display = [
        'sku', 'dimension_type', 'standard_value', 'get_unit_display_custom', 
        'min_value', 'max_value', 'is_key_dimension', 'tolerance'
    ]
    
    list_filter = [
        'dimension_type', 'unit', 'is_key_dimension', 
        'sku__spu__brand', 'sku__spu__category',
        ('sku', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'sku__name', 'sku__code', 'sku__spu__name', 'description'
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'get_unit_display_custom']
    
    fieldsets = [
        ('关联产品', {
            'fields': ['sku'],
            'description': '选择此尺寸信息所属的SKU产品'
        }),
        ('尺寸信息', {
            'fields': [
                'dimension_type', 'standard_value', 'unit', 'custom_unit',
                'min_value', 'max_value', 'tolerance'
            ]
        }),
        ('配置选项', {
            'fields': ['is_key_dimension', 'description']
        }),
        ('系统信息', {
            'fields': ['created_at', 'updated_at', 'created_by'],
            'classes': ['collapse']
        })
    ]
    
    def get_unit_display_custom(self, obj):
        """自定义单位显示"""
        return obj.get_display_unit()
    get_unit_display_custom.short_description = '单位'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """优化外键字段的选择"""
        if db_field.name == "sku":
            kwargs["queryset"] = SKU.objects.select_related('spu').filter(
                status__in=['active', 'draft']
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        """保存时设置创建人"""
        if not change:  # 新建时
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """优化查询性能"""
        return super().get_queryset(request).select_related(
            'sku__spu', 'created_by'
        )


@admin.register(ProductsDimension)
class ProductsDimensionAdmin(ModelAdmin):
    """产品尺寸管理"""
    
    list_display = [
        'sku', 'dimension_type', 'standard_value', 'get_display_unit',
        'min_value', 'max_value', 'tolerance', 'is_key_dimension'
    ]
    
    list_filter = [
        'dimension_type', 'unit', 'is_key_dimension'
    ]
    
    search_fields = ['sku__name', 'sku__code', 'description']
    
    list_editable = ['is_key_dimension']
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('基本信息', {
            'fields': ['sku', 'dimension_type', 'description']
        }),
        ('尺寸配置', {
            'fields': [
                'standard_value', 'min_value', 'max_value',
                'unit', 'custom_unit', 'tolerance'
            ]
        }),
        ('设置', {
            'fields': ['is_key_dimension']
        }),
        ('系统信息', {
            'fields': ['created_by', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    autocomplete_fields = ['sku', 'created_by']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sku', 'created_by')
    
    def save_model(self, request, obj, form, change):
        if not change:  # 新建时
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_display_unit(self, obj):
        """显示单位"""
        return obj.get_display_unit()
    get_display_unit.short_description = '单位'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # 根据单位类型显示/隐藏自定义单位字段
        if obj and obj.unit != 'custom':
            form.base_fields['custom_unit'].widget.attrs['style'] = 'display:none;'
        
        return form
    
    class Media:
        js = ('admin/js/dimension_admin.js',)  # 自定义JS文件


# ===== 导入系统 Admin 配置 =====

@admin.register(ImportTask)
class ImportTaskAdmin(admin.ModelAdmin):
    """导入任务管理"""
    
    list_display = [
        'name', 'task_type', 'status_badge', 'progress_bar', 
        'file_info', 'result_summary_display', 'created_by', 'created_at'
    ]
    list_filter = ['task_type', 'status', 'created_at', 'created_by']
    search_fields = ['name', 'error_details']
    readonly_fields = [
        'id', 'status', 'total_rows', 'processed_rows', 'success_rows',
        'error_rows', 'progress', 'result_summary', 'started_at', 
        'completed_at'
    ]
    fieldsets = [
        ('基本信息', {
            'fields': ['id', 'name', 'task_type', 'created_by', 'created_at']
        }),
        ('文件信息', {
            'fields': ['file_path']
        }),
        ('状态信息', {
            'fields': ['status', 'progress', 'started_at', 'completed_at']
        }),
        ('统计信息', {
            'fields': ['total_rows', 'processed_rows', 'success_rows', 'error_rows']
        }),
        ('结果详情', {
            'fields': ['result_summary', 'error_details'],
            'classes': ['collapse']
        }),
    ]
    
    def status_badge(self, obj):
        """状态徽章"""
        colors = {
            'pending': '#ffc107',
            'processing': '#17a2b8',
            'completed': '#28a745',
            'failed': '#dc3545',
            'partial': '#fd7e14'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 12px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = '状态'
    
    def progress_bar(self, obj):
        """进度条"""
        if obj.progress == 0:
            return '-'
        return format_html(
            '<div style="width: 100px; height: 20px; background-color: #e9ecef; '
            'border-radius: 10px; overflow: hidden;">'
            '<div style="width: {}%; height: 100%; background-color: #007bff; '
            'line-height: 20px; text-align: center; color: white; font-size: 12px;">'
            '{:.1f}%</div></div>',
            obj.progress, obj.progress
        )
    progress_bar.short_description = '进度'
    
    def file_info(self, obj):
        """文件信息"""
        import os
        if obj.file_path:
            filename = os.path.basename(obj.file_path)
            return format_html(
                '<span title="{}">{}</span>',
                obj.file_path, filename
            )
        return '-'
    file_info.short_description = '文件'
    
    def result_summary_display(self, obj):
        """结果摘要显示"""
        if obj.error_rows > 0:
            return format_html(
                '成功: {} | 错误: {} | <a href="{}">查看错误</a>',
                obj.success_rows, obj.error_rows,
                reverse('admin:products_importerror_changelist') + f'?task__id__exact={obj.id}'
            )
        return f'成功: {obj.success_rows}'
    result_summary_display.short_description = '结果摘要'
    
    def has_add_permission(self, request):
        """禁用添加权限（通过导入界面创建）"""
        return False


@admin.register(ImportError)
class ImportErrorAdmin(admin.ModelAdmin):
    """导入错误管理"""
    
    list_display = [
        'task_link', 'row_number', 'error_type_badge', 
        'field_name', 'error_message_short', 'created_at'
    ]
    list_filter = ['error_type', 'task__task_type', 'created_at']
    search_fields = ['error_message', 'field_name', 'task__name']
    readonly_fields = ['task', 'row_number', 'error_type', 'field_name', 'error_message', 'raw_data', 'created_at']
    
    def task_link(self, obj):
        """任务链接"""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:products_importtask_change', args=[obj.task.id]),
            obj.task.name
        )
    task_link.short_description = '导入任务'
    
    def error_type_badge(self, obj):
        """错误类型徽章"""
        colors = {
            'validation': '#dc3545',
            'format': '#fd7e14',
            'duplicate': '#ffc107',
            'reference': '#6c757d',
            'system': '#dc3545'
        }
        color = colors.get(obj.error_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 8px; font-size: 11px;">{}</span>',
            color, obj.get_error_type_display()
        )
    error_type_badge.short_description = '错误类型'
    
    def error_message_short(self, obj):
        """错误消息简短显示"""
        if len(obj.error_message) > 50:
            return obj.error_message[:50] + '...'
        return obj.error_message
    error_message_short.short_description = '错误消息'
    
    def has_add_permission(self, request):
        """禁用添加权限"""
        return False


@admin.register(ImportTemplate)
class ImportTemplateAdmin(admin.ModelAdmin):
    """导入模板管理"""
    
    list_display = [
        'name', 'template_type', 'is_active', 'created_at', 'updated_at'
    ]
    list_filter = ['template_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    
    fieldsets = [
        ('基本信息', {
            'fields': ['name', 'template_type', 'description', 'is_active']
        }),
        ('配置信息', {
            'fields': ['field_mapping', 'required_fields', 'validation_rules'],
            'classes': ['collapse']
        }),
        ('时间信息', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    readonly_fields = ['created_at', 'updated_at']





