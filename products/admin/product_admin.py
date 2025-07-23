"""
产品相关 Admin 配置
包含产品图片、产品加价规则、产品尺寸的管理
"""

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import messages

from ..models import ProductImage, ProductsPricingRule, ProductsDimension
from .base import BaseModelAdmin
from .filters import ActiveFilter, DateRangeFilter
from .mixins import BulkActionMixin, DisplayMixin


@admin.register(ProductImage)
class ProductImageAdmin(BaseModelAdmin, BulkActionMixin, DisplayMixin):
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


@admin.register(ProductsPricingRule)
class ProductsPricingRuleAdmin(BaseModelAdmin, BulkActionMixin, DisplayMixin):
    """产品加价规则管理"""
    
    list_display = [
        'name', 'rule_scope_display', 'spu', 'sku', 'rule_type', 
        'threshold_value', 'price_increment', 'is_active', 'priority_display'
    ]
    
    list_filter = [
        'rule_type', 'calculation_method', 'is_active', 
        'effective_date', 'spu__brand', 'spu__category',
        ('sku', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'name', 'spu__name', 'sku__name', 'sku__code'
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'priority_display']
    
    fieldsets = [
        ('规则归属', {
            'fields': ['spu', 'sku'],
            'description': '选择SPU（必须）和SKU（可选）。如果选择SKU，规则仅应用于该SKU；否则应用于整个SPU。'
        }),
        ('基本信息', {
            'fields': ['name', 'rule_type']
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
                kwargs["queryset"] = SKU.objects.none()
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        """保存时设置创建人"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """优化查询性能"""
        return super().get_queryset(request).select_related(
            'spu', 'sku', 'created_by'
        )
    
    class Media:
        js = ['admin/js/pricing_rule_admin.js']


@admin.register(ProductsDimension)
class ProductsDimensionAdmin(BaseModelAdmin, BulkActionMixin, DisplayMixin):
    """产品尺寸管理"""
    
    list_display = [
        'sku', 'dimension_type', 'standard_value', 'get_display_unit',
        'min_value', 'max_value', 'tolerance', 'is_key_dimension'
    ]
    
    list_filter = [
        'dimension_type', 'unit', 'is_key_dimension'
    ]
    
    search_fields = ['sku__name', 'sku__code']
    
    list_editable = ['is_key_dimension']
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('基本信息', {
            'fields': ['sku', 'dimension_type']
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
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_display_unit(self, obj):
        """显示单位"""
        return obj.get_display_unit()
    get_display_unit.short_description = '单位'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        if obj and obj.unit != 'custom':
            form.base_fields['custom_unit'].widget.attrs['style'] = 'display:none;'
        
        return form
    
    class Media:
        js = ('admin/js/dimension_admin.js',) 