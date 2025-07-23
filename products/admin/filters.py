"""
Admin过滤器
包含各种自定义的过滤器类
"""

from django.contrib.admin.filters import SimpleListFilter
from django.utils import timezone
from datetime import timedelta


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