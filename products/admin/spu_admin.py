"""
SPU管理 Admin 配置
包含SPU、SPU属性、SPU尺寸模板的管理
"""

from django.contrib import admin
from django.db.models import Count
from django.forms import ModelChoiceField, ModelForm, Select
from django.http import JsonResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from django.contrib import messages

from ..models import SPU, SPUAttribute, SPUDimensionTemplate, Attribute, AttributeValue, ProductsPricingRule
from .base import BaseModelAdmin
from .filters import ActiveFilter, DateRangeFilter
from .mixins import BulkActionMixin, DisplayMixin


class SPUAttributeInline(admin.TabularInline):
    """SPU属性内联编辑 - 优化版"""
    model = SPUAttribute
    extra = 1
    min_num = 0
    max_num = 20
    
    fields = ['attribute', 'get_attribute_info', 'is_required', 'default_value', 'get_values_preview', 'order']
    readonly_fields = ['get_attribute_info', 'get_values_preview']
    
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
                'text': '#007cba',      
                'number': '#28a745',    
                'select': '#ffc107',    
                'multiselect': '#fd7e14', 
                'boolean': '#6c757d',   
                'date': '#17a2b8',      
                'color': '#e83e8c',     
                'image': '#6f42c1',     
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
            values = attr.values.filter(is_active=True)[:5]
            
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
            kwargs["queryset"] = Attribute.objects.filter(is_active=True).order_by('order', 'name')
            
            class AttributeChoiceField(ModelChoiceField):
                def label_from_instance(self, obj):
                    type_display = dict(obj.ATTRIBUTE_TYPES).get(obj.type, obj.type)
                    unit_info = f" ({obj.unit})" if obj.unit else ""
                    return f"{obj.name} [{type_display}]{unit_info} - {obj.code}"
            
            kwargs["form_class"] = AttributeChoiceField
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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
    classes = []


class ProductsPricingRuleInline(admin.TabularInline):
    """SPU产品加价规则内联编辑器"""
    model = ProductsPricingRule
    extra = 1
    min_num = 0
    max_num = 5
    
    fields = ['name', 'rule_type', 'threshold_value', 'price_increment', 'is_active']
    
    verbose_name = "加价规则"
    verbose_name_plural = "加价规则"
    classes = []
    
    def get_queryset(self, request):
        """只显示SPU级别的规则（sku为空的规则）"""
        return super().get_queryset(request).filter(sku__isnull=True)


@admin.register(SPU)
class SPUAdmin(BaseModelAdmin, BulkActionMixin, DisplayMixin):
    """SPU管理 - ROYANA品牌优化版"""
    
    list_display = ['name', 'code', 'category', 'brand', 'get_attribute_count', 'get_sku_count', 'get_price_range', 'is_active', 'created_at']
    list_filter = ['category', 'brand', 'is_active', 'created_at', 'attributes__type']
    search_fields = ['name', 'code', 'description', 'attributes__name', 'attributes__code']
    list_editable = ['is_active']
    ordering = ['brand', 'category', 'name']
    filter_horizontal = []
    inlines = [SPUAttributeInline, SPUDimensionTemplateInline, ProductsPricingRuleInline]
    actions = ['duplicate_spu', 'copy_attributes', 'activate_spu', 'deactivate_spu', 'create_standard_skus']
    
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
    
    def get_queryset(self, request):
        """优化查询，避免N+1问题"""
        return super().get_queryset(request).select_related('category', 'brand').prefetch_related(
            'spuattribute_set__attribute',
            'skus'
        ).annotate(
            spuattribute_count=Count('spuattribute'),
            sku_count=Count('skus')
        )
    
    def duplicate_spu(self, request, queryset):
        """复制SPU"""
        duplicated_count = 0
        for spu in queryset:
            new_spu = SPU.objects.create(
                name=f"{spu.name} (副本)",
                code=f"{spu.code}_copy_{duplicated_count + 1}",
                category=spu.category,
                brand=spu.brand,
                description=spu.description,
                specifications=spu.specifications,
                usage_scenario=spu.usage_scenario,
                is_active=False,
                created_by=request.user
            )
            
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
    
    def create_standard_skus(self, request, queryset):
        """为选中的SPU创建标准SKU"""
        # 这里可以实现标准SKU创建逻辑
        self.message_user(request, f'标准SKU创建功能正在开发中。选中了 {queryset.count()} 个SPU。', messages.INFO)
    create_standard_skus.short_description = "创建标准SKU"

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
        from ..views import AttributeAPIView
        return AttributeAPIView.as_view()(request)
    
    def category_attributes_view(self, request, category_id):
        """分类属性推荐 API 代理视图"""
        from ..views import CategoryAttributesAPIView
        return CategoryAttributesAPIView.as_view()(request, category_id)
    
    def attribute_values_view(self, request, attribute_id):
        """属性值 API 代理视图"""
        from ..views import attribute_values_api
        return attribute_values_api(request, attribute_id)
    
    def clear_cache_view(self, request):
        """清除缓存 API 代理视图"""
        from ..views import clear_attribute_cache
        return clear_attribute_cache(request)


@admin.register(SPUAttribute)
class SPUAttributeAdmin(BaseModelAdmin):
    """SPU属性关联管理"""
    
    list_display = ['spu', 'attribute', 'is_required', 'order']
    list_filter = ['is_required', 'spu', 'attribute']
    search_fields = ['spu__name', 'attribute__name']
    list_editable = ['is_required', 'order']
    ordering = ['spu', 'order', 'attribute']
    
    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('spu', 'attribute')


@admin.register(SPUDimensionTemplate)
class SPUDimensionTemplateAdmin(BaseModelAdmin):
    """SPU尺寸模板管理"""
    
    list_display = ['spu', 'dimension_type', 'default_value', 'get_unit_display', 'is_required', 'is_key_dimension', 'order']
    list_filter = ['dimension_type', 'unit', 'is_required', 'is_key_dimension', 'spu__brand']
    search_fields = ['spu__name', 'spu__code']
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

    )
    
    def get_unit_display(self, obj):
        """获取单位显示"""
        return obj.get_display_unit()
    
    get_unit_display.short_description = '单位' 