"""
Admin基础配置
包含通用的ModelAdmin基类、分页器等基础组件
"""

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.core.paginator import Paginator
from django.db import connection, models
from django.forms import TextInput, Textarea
from django.conf import settings


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
            # 只对有这些字段的模型添加
            if hasattr(obj, 'created_at'):
                readonly_fields.append('created_at')
            if hasattr(obj, 'updated_at'):
                readonly_fields.append('updated_at')
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


class ChineseAdminSite(admin.AdminSite):
    """中文化的管理站点"""
    site_header = '整木定制产品库管理系统'
    site_title = '产品库管理'
    index_title = '产品数据管理'
    
    def each_context(self, request):
        context = super().each_context(request)
        context['site_header'] = self.site_header
        context['site_title'] = self.site_title
        context['index_title'] = self.index_title
        return context 