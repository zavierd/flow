"""
属性和属性值管理 Admin 配置
"""

from django.contrib import admin
from django.forms import ModelChoiceField
from django.utils.html import format_html
from django.contrib import messages
from django.core.exceptions import ValidationError

from ..models import Attribute, AttributeValue
from .base import BaseModelAdmin
from .filters import ActiveFilter, DateRangeFilter
from .mixins import BulkActionMixin, DisplayMixin, ValidationMixin


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


@admin.register(Attribute)
class AttributeAdmin(BaseModelAdmin, BulkActionMixin, DisplayMixin, ValidationMixin):
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
        
        standardized = value.strip()
        
        import re
        standardized = re.sub(r'\s+', ' ', standardized)
        
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
        error = self.clean_unique_code(obj, 'code')
        if error:
            messages.error(request, error)
            return
        
        if obj.type in ['select', 'multiselect'] and not change:
            obj.is_filterable = True
        elif obj.type in ['text', 'image'] and not change:
            obj.is_filterable = False
            
        super().save_model(request, obj, form, change)
        
        if not change and obj.type in ['select', 'multiselect']:
            messages.info(request, f'属性 "{obj.name}" 创建成功！请在下方添加可选的属性值。')
    
    def has_delete_permission(self, request, obj=None):
        """属性删除权限控制"""
        if not request.user.is_superuser:
            return False
        
        if obj and obj.spus.exists():
            return False
            
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


@admin.register(AttributeValue)
class AttributeValueAdmin(BaseModelAdmin, BulkActionMixin, DisplayMixin):
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
        
        standardized = value.strip()
        
        import re
        standardized = re.sub(r'\s+', ' ', standardized)
        
        if value_obj.attribute.type == 'color':
            if standardized.startswith('#'):
                standardized = standardized.upper()
            else:
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
            standardized = re.sub(r'[^\d\.\-\+]', '', standardized)
        
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
        
        if not obj.display_name:
            obj.display_name = obj.value
            
        if obj.color_code:
            import re
            if not re.match(r'^#[0-9A-Fa-f]{6}$', obj.color_code):
                messages.error(request, '颜色代码格式不正确，应为 #RRGGBB 格式（如 #FF0000）')
                return
                
        super().save_model(request, obj, form, change) 