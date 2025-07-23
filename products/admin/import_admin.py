from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db import models
from django.forms import Textarea
from products.models import ImportTask, ImportError, ImportTemplate


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
        'completed_at', 'duration_display', 'created_at'
    ]
    fieldsets = [
        ('基本信息', {
            'fields': ['id', 'name', 'task_type', 'created_by', 'created_at']
        }),
        ('文件信息', {
            'fields': ['file_path']
        }),
        ('状态信息', {
            'fields': ['status', 'progress', 'started_at', 'completed_at', 'duration_display']
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
        if obj.file_path:
            filename = obj.file_path.name.split('/')[-1]
            return format_html(
                '<a href="{}" target="_blank" title="点击下载文件">{}</a>',
                obj.file_path.url, filename
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
    
    def duration_display(self, obj):
        """执行时间显示"""
        if obj.duration:
            total_seconds = int(obj.duration.total_seconds())
            minutes, seconds = divmod(total_seconds, 60)
            return f'{minutes}分{seconds}秒'
        return '-'
    duration_display.short_description = '执行时间'
    
    def has_add_permission(self, request):
        """禁用添加权限（通过导入界面创建）"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """只读权限"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """允许删除"""
        return True


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
    
    def has_change_permission(self, request, obj=None):
        """只读权限"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """允许删除"""
        return True


@admin.register(ImportTemplate)
class ImportTemplateAdmin(admin.ModelAdmin):
    """导入模板管理"""
    
    list_display = [
        'name', 'template_type', 'is_active', 'created_at', 'updated_at'
    ]
    list_filter = ['template_type', 'is_active', 'created_at']
    search_fields = ['name']
    
    fieldsets = [
        ('基本信息', {
            'fields': ['name', 'template_type', 'is_active']
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
    
    formfield_overrides = {
        models.JSONField: {'widget': Textarea(attrs={'rows': 10, 'cols': 80})},
    }
    
    def save_model(self, request, obj, form, change):
        """保存模板时的处理"""
        super().save_model(request, obj, form, change)
        
        # 这里可以添加模板保存后的处理逻辑
        # 例如：验证模板配置、生成示例文件等