"""
分类管理 Admin 配置
"""

from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import messages
from mptt.admin import DraggableMPTTAdmin

from ..models import Category
from .base import BaseModelAdmin
from .filters import ActiveFilter, DateRangeFilter
from .mixins import BulkActionMixin, DisplayMixin, PermissionMixin


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin, BaseModelAdmin, BulkActionMixin, DisplayMixin, PermissionMixin):
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
    
    def sort_alphabetically(self, request, queryset):
        """按字母顺序排序"""
        levels = {}
        for obj in queryset:
            if obj.level not in levels:
                levels[obj.level] = []
            levels[obj.level].append(obj)
        
        updated_count = 0
        for level, categories in levels.items():
            categories.sort(key=lambda x: x.name)
            for i, category in enumerate(categories):
                category.order = i + 1
                category.save(update_fields=['order'])
                updated_count += 1
        
        Category.objects.rebuild()
        self.message_user(request, f'成功对 {updated_count} 个分类进行了字母排序')
    sort_alphabetically.short_description = "按字母顺序排序"
    
    def sort_by_order(self, request, queryset):
        """按 order 字段排序"""
        levels = {}
        for obj in queryset:
            if obj.level not in levels:
                levels[obj.level] = []
            levels[obj.level].append(obj)
        
        updated_count = 0
        for level, categories in levels.items():
            categories.sort(key=lambda x: (x.order, x.name))
            for i, category in enumerate(categories):
                if category.order != i + 1:
                    category.order = i + 1
                    category.save(update_fields=['order'])
                    updated_count += 1
        
        Category.objects.rebuild()
        self.message_user(request, f'成功对 {updated_count} 个分类按 order 字段进行了排序')
    sort_by_order.short_description = "按 order 字段排序"
    
    def reset_order(self, request, queryset):
        """重置排序（按ID顺序）"""
        levels = {}
        for obj in queryset:
            if obj.level not in levels:
                levels[obj.level] = []
            levels[obj.level].append(obj)
        
        updated_count = 0
        for level, categories in levels.items():
            categories.sort(key=lambda x: x.id)
            for i, category in enumerate(categories):
                category.order = i + 1
                category.save(update_fields=['order'])
                updated_count += 1
        
        Category.objects.rebuild()
        self.message_user(request, f'成功重置了 {updated_count} 个分类的排序')
    reset_order.short_description = "重置排序（按创建顺序）"
    
    def has_delete_permission(self, request, obj=None):
        """分类删除权限控制"""
        if not request.user.is_superuser:
            return False
        
        if obj and obj.get_children().exists():
            return False
        
        if obj and obj.spus.exists():
            return False
            
        return True
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """自定义父分类字段"""
        if db_field.name == "parent":
            if request.resolver_match.kwargs.get('object_id'):
                try:
                    current_id = int(request.resolver_match.kwargs['object_id'])
                    current_category = Category.objects.get(id=current_id)
                    exclude_ids = [current_id] + list(
                        current_category.get_descendants().values_list('id', flat=True)
                    )
                    kwargs["queryset"] = Category.objects.exclude(id__in=exclude_ids)
                except (ValueError, Category.DoesNotExist):
                    pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs) 