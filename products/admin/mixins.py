"""
Admin混入类
包含可重用的功能混入类
"""

from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils.html import format_html
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class BulkActionMixin:
    """批量操作混入类"""
    
    def bulk_activate(self, request, queryset):
        """批量激活"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'成功激活 {updated} 个项目。', messages.SUCCESS)
    bulk_activate.short_description = "激活选中的项目"
    
    def bulk_deactivate(self, request, queryset):
        """批量停用"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'成功停用 {updated} 个项目。', messages.SUCCESS)
    bulk_deactivate.short_description = "停用选中的项目"


class DisplayMixin:
    """显示相关的混入类"""
    
    def get_status_badge(self, obj, field='is_active'):
        """获取状态徽章"""
        if getattr(obj, field, False):
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">启用</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">禁用</span>'
            )
    
    def get_count_link(self, obj, related_field, admin_name, label=''):
        """获取计数链接"""
        count = getattr(obj, f'{related_field}_count', getattr(obj, related_field).count())
        if count > 0:
            url = reverse(f'admin:products_{admin_name}_changelist') + f'?{related_field}__id__exact={obj.id}'
            return format_html(
                '<a href="{}" style="color: #007cba; text-decoration: none;">{} 个{}</a>',
                url, count, label
            )
        return f'{count} 个{label}'


class AjaxMixin:
    """Ajax相关的混入类"""
    
    @method_decorator(csrf_exempt)
    def ajax_response(self, request, success=True, message='', data=None):
        """统一的Ajax响应"""
        return JsonResponse({
            'success': success,
            'message': message,
            'data': data or {}
        })


class PermissionMixin:
    """权限相关的混入类"""
    
    def check_related_objects(self, obj, related_fields):
        """检查是否有关联对象"""
        for field in related_fields:
            if hasattr(obj, field) and getattr(obj, field).exists():
                return True
        return False
    
    def has_delete_permission_with_relations(self, request, obj=None, related_fields=None):
        """检查删除权限（考虑关联对象）"""
        if not request.user.is_superuser:
            return False
        
        if obj and related_fields:
            if self.check_related_objects(obj, related_fields):
                return False
        
        return True


class ValidationMixin:
    """验证相关的混入类"""
    
    def clean_unique_code(self, obj, field='code'):
        """验证唯一编码"""
        import re
        code = getattr(obj, field, '')
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', code):
            return f'{field}必须以字母开头，只能包含字母、数字和下划线'
        return None
    
    def validate_email(self, email):
        """验证邮箱格式"""
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(email)
            return None
        except ValidationError:
            return '请输入有效的邮箱地址'
    
    def validate_phone(self, phone):
        """验证电话格式"""
        import re
        if not re.match(r'^[\d\-\+\(\)\s]+$', phone):
            return '请输入有效的电话号码'
        return None 