"""
SKU管理 Admin 配置
包含SKU和SKU属性值的管理
"""

from django.contrib import admin
from django.forms import ModelChoiceField, ModelForm
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from django.contrib import messages
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse

from ..models import SKU, SKUAttributeValue, Attribute, AttributeValue, ProductImage, ProductsDimension, ProductsPricingRule
from .base import BaseModelAdmin
from .filters import ActiveFilter, DateRangeFilter, SeriesFilter, WidthFilter
from .mixins import BulkActionMixin, DisplayMixin


class SKUAttributeValueForm(forms.ModelForm):
    """SKU属性值表单"""
    
    class Meta:
        model = SKUAttributeValue
        fields = ['attribute', 'attribute_value']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['attribute'].queryset = Attribute.objects.filter(is_active=True).order_by('order', 'name')
        self.fields['attribute'].empty_label = "--- 请选择属性 ---"
        
        if self.instance and self.instance.pk and self.instance.attribute:
            self.fields['attribute_value'].queryset = AttributeValue.objects.filter(
                attribute=self.instance.attribute,
                is_active=True
            ).order_by('order', 'value')
        else:
            self.fields['attribute_value'].queryset = AttributeValue.objects.none()
            
        self.fields['attribute_value'].empty_label = "--- 请先选择属性 ---"
    
    def clean_attribute_value(self):
        """验证属性值是否属于选定的属性"""
        attribute = self.cleaned_data.get('attribute')
        attribute_value = self.cleaned_data.get('attribute_value')
        
        if attribute and attribute_value:
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
        
        if attribute and not attribute_value:
            raise forms.ValidationError("请为选定的属性选择一个属性值")
        
        if attribute_value and not attribute:
            raise forms.ValidationError("请先选择属性")
        
        return cleaned_data


class BulkStatusUpdateForm(forms.Form):
    """批量状态更新表单"""

    STATUS_CHOICES = [
        ('active', '在售'),
        ('inactive', '停售'),
        ('out_of_stock', '缺货'),
        ('discontinued', '停产'),
        ('pre_order', '预售'),
    ]

    new_status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        label='新状态',
        help_text='选择要批量设置的新状态'
    )

    update_stock = forms.BooleanField(
        required=False,
        label='同时更新库存',
        help_text='勾选此项可以同时设置库存数量'
    )

    stock_quantity = forms.IntegerField(
        required=False,
        min_value=0,
        label='库存数量',
        help_text='当勾选"同时更新库存"时，设置的库存数量'
    )

    reason = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label='变更原因',
        help_text='可选：记录状态变更的原因'
    )

    def clean(self):
        cleaned_data = super().clean()
        update_stock = cleaned_data.get('update_stock')
        stock_quantity = cleaned_data.get('stock_quantity')

        if update_stock and stock_quantity is None:
            raise forms.ValidationError('勾选"同时更新库存"时，必须填写库存数量')

        return cleaned_data


class SKUAttributeValueInline(admin.TabularInline):
    """SKU属性值内联编辑"""
    model = SKUAttributeValue
    form = SKUAttributeValueForm
    extra = 1
    min_num = 0
    max_num = 20
    fields = ['attribute', 'attribute_value']
    
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
            kwargs["queryset"] = Attribute.objects.filter(is_active=True).order_by('order', 'name')
            
        elif db_field.name == "attribute_value":
            kwargs["queryset"] = AttributeValue.objects.none()
            
            class AttributeValueChoiceField(ModelChoiceField):
                def label_from_instance(self, obj):
                    return obj.display_name or obj.value
            
            kwargs["form_class"] = AttributeValueChoiceField
            
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ProductImageInline(admin.TabularInline):
    """产品图片内联编辑"""
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'order', 'is_active']


class ProductsDimensionInline(admin.TabularInline):
    """SKU产品尺寸内联编辑器"""
    model = ProductsDimension
    extra = 1
    min_num = 0
    max_num = 8
    
    fields = [
        'dimension_type', 'standard_value', 'unit', 
        'min_value', 'max_value', 'is_key_dimension'
    ]
    
    verbose_name = "产品尺寸"
    verbose_name_plural = "产品尺寸"
    classes = []


class SKUPricingRuleInline(admin.TabularInline):
    """SKU专属加价规则内联编辑器"""
    model = ProductsPricingRule
    extra = 1
    min_num = 0
    max_num = 3
    
    fields = ['name', 'rule_type', 'threshold_value', 'unit_increment', 'price_increment', 'is_active']
    exclude = ['spu']
    
    verbose_name = "SKU专属加价规则"
    verbose_name_plural = "SKU专属加价规则"
    classes = []
    
    def get_queryset(self, request):
        """只显示当前SKU的专属规则"""
        queryset = super().get_queryset(request)
        return queryset.filter(
            sku__isnull=False,
            spu__isnull=False
        ).select_related('spu', 'sku')


@admin.register(SKU)
class SKUAdmin(BaseModelAdmin, BulkActionMixin, DisplayMixin):
    """SKU管理 - ROYANA品牌优化版"""
    
    list_display = ['get_product_code', 'name', 'spu', 'brand', 'get_price_display', 'get_attributes_display', 'stock_quantity', 'status', 'is_featured', 'updated_at']
    list_filter = ['spu', 'brand', 'status', 'is_featured', 'updated_at', SeriesFilter, WidthFilter]
    search_fields = ['name', 'code', 'spu__name', 'brand__name']
    list_editable = ['stock_quantity', 'status', 'is_featured']
    ordering = ['-updated_at','brand','spu','code']
    inlines = [SKUAttributeValueInline, ProductImageInline, ProductsDimensionInline, SKUPricingRuleInline]
    actions = [
        'sync_from_spu_action',
        'bulk_update_status_action',
        'bulk_set_active_action',
        'bulk_set_inactive_action',
        'bulk_set_out_of_stock_action'
    ]
    
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
        attribute_values = obj.sku_attribute_values.select_related('attribute', 'attribute_value').all()
        
        if not attribute_values:
            return format_html('<span style="font-style: italic; color: #999;">无属性</span>')
        
        type_color_map = {
            'text': '#424242',        
            'number': '#1976d2',      
            'select': '#388e3c',      
            'multiselect': '#7b1fa2', 
            'boolean': '#f57c00',     
            'date': '#d32f2f',        
            'color': '#e91e63',       
            'image': '#795548',       
        }
        
        code_color_map = {
            'WIDTH': '#1976d2',       
            'DIRECTION': '#388e3c',   
            'TYPE': '#7b1fa2',        
            'BOARD_LEVEL': '#f57c00', 
            'COLOR': '#5d4037',       
            'MATERIAL': '#5d4037',    
        }
        
        default_colors = [
            '#1976d2', '#388e3c', '#7b1fa2', '#f57c00', '#d32f2f',
            '#e91e63', '#795548', '#607d8b', '#ff5722', '#9c27b0',
            '#2196f3', '#4caf50', '#ff9800', '#673ab7', '#009688'
        ]
        
        def get_attribute_color(attribute):
            """获取属性的显示颜色"""
            if attribute.code in code_color_map:
                return code_color_map[attribute.code]
            
            if attribute.type in type_color_map:
                return type_color_map[attribute.type]
            
            color_index = attribute.id % len(default_colors)
            return default_colors[color_index]
        
        formatted_attrs = []
        for sku_attr_value in attribute_values:
            attribute = sku_attr_value.attribute
            attribute_value = sku_attr_value.attribute_value
            
            if attribute_value and attribute_value.value:
                color = get_attribute_color(attribute)
                display_value = attribute_value.display_name or attribute_value.value
                
                if attribute.code == 'WIDTH' and display_value.isdigit():
                    display_value = f"{display_value}cm"
                elif attribute.code == 'DIRECTION':
                    if display_value.upper() == 'L':
                        display_value = "左开"
                    elif display_value.upper() == 'R':
                        display_value = "右开"
                
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
            if not request.user.is_superuser:
                return False
        return super().has_change_permission(request, obj)
    
    def get_readonly_fields(self, request, obj=None):
        """SKU模型没有created_at和updated_at字段，因此不添加到只读字段"""
        readonly_fields = list(self.readonly_fields)
        
        if obj and obj.status == 'discontinued' and not request.user.is_superuser:
            readonly_fields.extend(['name', 'code', 'spu', 'brand', 'price', 'cost_price', 'market_price'])
            
        return readonly_fields
    
    def save_model(self, request, obj, form, change):
        """重写保存方法，简化处理逻辑"""
        try:
            obj.full_clean()
        except ValidationError as e:
            print(f"验证失败: {e}")
            if hasattr(e, 'error_dict'):
                for field, errors in e.error_dict.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error.message}')
            else:
                messages.error(request, f'数据验证错误: {e}')
            raise
        
        super().save_model(request, obj, form, change)
        
        if not change and obj.spu:
            self.sync_spu_attributes_and_rules(obj)
    
    def sync_spu_attributes_and_rules(self, sku):
        """同步SPU的属性、尺寸模板和加价规则到新创建的SKU"""
        if not sku.spu:
            return
            
        from ..models import SKUAttributeValue, ProductsPricingRule, ProductsDimension
        
        print(f"开始同步SPU '{sku.spu.name}' 的属性、尺寸模板和加价规则到SKU '{sku.name}'")
        
        # 1. 同步SPU的所有属性
        spu_attributes = sku.spu.spuattribute_set.all().select_related('attribute')
        
        for spu_attr in spu_attributes:
            existing_value = sku.sku_attribute_values.filter(
                attribute=spu_attr.attribute
            ).first()
            
            if not existing_value:
                if spu_attr.default_value:
                    try:
                        from ..models import AttributeValue
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
                            SKUAttributeValue.objects.create(
                                sku=sku,
                                attribute=spu_attr.attribute,
                                custom_value=spu_attr.default_value
                            )
                            print(f"  同步属性: {spu_attr.attribute.name} = {spu_attr.default_value} (自定义值)")
                    except Exception as e:
                        print(f"  属性同步失败: {spu_attr.attribute.name} - {e}")
                else:
                    SKUAttributeValue.objects.create(
                        sku=sku,
                        attribute=spu_attr.attribute,
                        custom_value=''
                    )
                    print(f"  创建空属性: {spu_attr.attribute.name}")
        
        # 2. 同步SPU的尺寸模板到SKU
        spu_dimension_templates = sku.spu.dimension_templates.all()
        
        for template in spu_dimension_templates:
            existing_dimension = sku.dimensions.filter(
                dimension_type=template.dimension_type
            ).first()
            
            if not existing_dimension:
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
                    created_by=getattr(request, 'user', None) if hasattr(self, 'request') else None
                )
                print(f"  同步尺寸: {template.get_dimension_type_display()} = {template.default_value}{template.get_display_unit()}")
            else:
                print(f"  尺寸已存在: {template.get_dimension_type_display()}")
        
        # 3. 同步SPU级别的加价规则（复制为SKU专属规则）
        spu_pricing_rules = ProductsPricingRule.objects.filter(
            spu=sku.spu,
            sku__isnull=True,
            is_active=True
        )
        
        for spu_rule in spu_pricing_rules:
            existing_rule = ProductsPricingRule.objects.filter(
                spu=sku.spu,
                sku=sku,
                name=spu_rule.name,
                rule_type=spu_rule.rule_type
            ).first()
            
            if not existing_rule:
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

    def get_urls(self):
        """添加自定义URL"""
        urls = super().get_urls()
        custom_urls = [
            path(
                'bulk-status-update/',
                self.admin_site.admin_view(self.bulk_status_update_view),
                name='products_sku_bulk_status_update',
            ),
        ]
        return custom_urls + urls

    def bulk_update_status_action(self, request, queryset):
        """批量更新状态 - 高级选项"""
        selected = queryset.values_list('pk', flat=True)
        return HttpResponseRedirect(
            reverse('admin:products_sku_bulk_status_update') +
            f'?ids={",".join(str(pk) for pk in selected)}'
        )
    bulk_update_status_action.short_description = "📝 批量修改状态（高级）"

    def bulk_status_update_view(self, request):
        """批量状态更新视图"""
        if request.method == 'POST':
            form = BulkStatusUpdateForm(request.POST)
            if form.is_valid():
                ids = request.POST.get('ids', '').split(',')
                if ids and ids[0]:
                    queryset = SKU.objects.filter(pk__in=ids)

                    new_status = form.cleaned_data['new_status']
                    update_stock = form.cleaned_data['update_stock']
                    stock_quantity = form.cleaned_data['stock_quantity']
                    reason = form.cleaned_data['reason']

                    updated_count = 0
                    for sku in queryset:
                        sku.status = new_status
                        if update_stock:
                            sku.stock_quantity = stock_quantity
                        sku.save()
                        updated_count += 1

                    # 记录操作日志
                    status_display = dict(form.STATUS_CHOICES)[new_status]
                    message = f'批量更新了 {updated_count} 个SKU的状态为"{status_display}"'
                    if update_stock:
                        message += f'，库存设置为 {stock_quantity}'
                    if reason:
                        message += f'。原因：{reason}'

                    self.message_user(request, message)
                    return HttpResponseRedirect(reverse('admin:products_sku_changelist'))
        else:
            ids = request.GET.get('ids', '')
            form = BulkStatusUpdateForm(initial={'ids': ids})

        # 获取选中的SKU信息
        if request.GET.get('ids'):
            ids = request.GET.get('ids').split(',')
            selected_skus = SKU.objects.filter(pk__in=ids).select_related('spu', 'brand')
        else:
            selected_skus = SKU.objects.none()

        context = {
            'form': form,
            'selected_skus': selected_skus,
            'ids': request.GET.get('ids', ''),
            'title': '批量修改SKU状态',
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
        }

        return render(request, 'admin/products/sku/bulk_status_update.html', context)

    def bulk_set_active_action(self, request, queryset):
        """批量设置为在售"""
        updated = queryset.update(status='active')
        self.message_user(request, f'成功将 {updated} 个SKU设置为在售状态')
    bulk_set_active_action.short_description = "✅ 批量设置为在售"

    def bulk_set_inactive_action(self, request, queryset):
        """批量设置为停售"""
        updated = queryset.update(status='inactive')
        self.message_user(request, f'成功将 {updated} 个SKU设置为停售状态')
    bulk_set_inactive_action.short_description = "⏸️ 批量设置为停售"

    def bulk_set_out_of_stock_action(self, request, queryset):
        """批量设置为缺货"""
        updated = queryset.update(status='out_of_stock', stock_quantity=0)
        self.message_user(request, f'成功将 {updated} 个SKU设置为缺货状态，库存已清零')
    bulk_set_out_of_stock_action.short_description = "📦 批量设置为缺货"


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