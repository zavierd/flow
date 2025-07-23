"""
品牌管理 Admin 配置
"""

import os
from django.contrib import admin
from django.db.models import Count
from django.http import JsonResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from ..models import Brand
from .base import BaseModelAdmin
from .filters import ActiveFilter, DateRangeFilter
from .mixins import BulkActionMixin, DisplayMixin, AjaxMixin


@admin.register(Brand)
class BrandAdmin(BaseModelAdmin, BulkActionMixin, DisplayMixin, AjaxMixin):
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
                    logo_path = brand.logo.path
                    brand.logo.delete(save=False)
                    brand.save()
                    
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
    
    def export_brands(self, request, queryset):
        """导出品牌"""
        # 这里可以实现品牌导出逻辑
        self.message_user(request, f'导出功能正在开发中。选中了 {queryset.count()} 个品牌。', messages.INFO)
    export_brands.short_description = "导出选中的品牌"
    
    def has_delete_permission(self, request, obj=None):
        """品牌删除权限控制"""
        if not request.user.is_superuser:
            return False
        
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