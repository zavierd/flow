"""
检查和修复Admin类中的readonly字段配置
确保created_at和updated_at字段正确设置为readonly
"""

from django.core.management.base import BaseCommand
from django.contrib import admin
from django.apps import apps
import inspect


class Command(BaseCommand):
    help = '检查和修复Admin类中的readonly字段配置'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check',
            action='store_true',
            help='检查Admin配置问题'
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='自动修复配置问题（仅显示建议）'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 检查Admin readonly字段配置...'))
        
        if options['check']:
            self.check_admin_configs()
        
        if options['fix']:
            self.suggest_fixes()
        
        if not any(options.values()):
            self.check_admin_configs()

    def check_admin_configs(self):
        """检查所有Admin配置"""
        issues = []
        
        # 获取所有注册的Admin类
        for model, admin_class in admin.site._registry.items():
            if model._meta.app_label == 'products':
                model_issues = self.check_model_admin(model, admin_class)
                if model_issues:
                    issues.extend(model_issues)
        
        # 显示结果
        if issues:
            self.stdout.write(self.style.WARNING(f'\n⚠️ 发现 {len(issues)} 个配置问题:'))
            for issue in issues:
                self.stdout.write(f'  • {issue}')
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ 所有Admin配置都正确！'))

    def check_model_admin(self, model, admin_class):
        """检查单个模型的Admin配置"""
        issues = []
        model_name = model.__name__
        admin_name = admin_class.__class__.__name__

        # 检查字段是否存在
        field_issues = self.check_field_existence(model, admin_class)
        issues.extend(field_issues)

        # 检查模型是否有时间戳字段
        has_created_at = hasattr(model, 'created_at')
        has_updated_at = hasattr(model, 'updated_at')

        if not (has_created_at or has_updated_at):
            return issues
        
        # 获取readonly_fields
        readonly_fields = getattr(admin_class, 'readonly_fields', [])
        if callable(readonly_fields):
            # 如果是方法，尝试调用获取默认值
            try:
                readonly_fields = readonly_fields(None, None)
            except:
                readonly_fields = []
        
        # 获取fieldsets中的字段
        fieldsets = getattr(admin_class, 'fieldsets', None)
        fieldset_fields = []
        if fieldsets:
            for fieldset in fieldsets:
                if isinstance(fieldset, (list, tuple)) and len(fieldset) >= 2:
                    fieldset_options = fieldset[1]
                    if isinstance(fieldset_options, dict) and 'fields' in fieldset_options:
                        fields = fieldset_options['fields']
                        if isinstance(fields, (list, tuple)):
                            fieldset_fields.extend(fields)
        
        # 检查created_at字段
        if has_created_at:
            if 'created_at' in fieldset_fields and 'created_at' not in readonly_fields:
                issues.append(f'{admin_name}: created_at字段在fieldsets中但不在readonly_fields中')
        
        # 检查updated_at字段
        if has_updated_at:
            if 'updated_at' in fieldset_fields and 'updated_at' not in readonly_fields:
                issues.append(f'{admin_name}: updated_at字段在fieldsets中但不在readonly_fields中')
        
        return issues

    def check_field_existence(self, model, admin_class):
        """检查Admin配置中引用的字段是否在模型中存在"""
        issues = []
        model_name = model.__name__
        admin_name = admin_class.__class__.__name__

        # 获取模型的所有字段名
        model_fields = set()
        for field in model._meta.get_fields():
            model_fields.add(field.name)

        # 检查search_fields
        search_fields = getattr(admin_class, 'search_fields', [])
        for field_name in search_fields:
            # 处理跨表查询字段（如 'task__name'）
            base_field = field_name.split('__')[0]
            if base_field not in model_fields:
                issues.append(f'{admin_name}: search_fields中的字段 "{field_name}" 在模型 {model_name} 中不存在')

        # 检查list_display
        list_display = getattr(admin_class, 'list_display', [])
        for field_name in list_display:
            # 跳过方法名（通常不是模型字段）
            if hasattr(admin_class, field_name):
                continue
            base_field = field_name.split('__')[0]
            if base_field not in model_fields:
                issues.append(f'{admin_name}: list_display中的字段 "{field_name}" 在模型 {model_name} 中不存在')

        # 检查fieldsets
        fieldsets = getattr(admin_class, 'fieldsets', None)
        if fieldsets:
            for fieldset in fieldsets:
                if isinstance(fieldset, (list, tuple)) and len(fieldset) >= 2:
                    fieldset_options = fieldset[1]
                    if isinstance(fieldset_options, dict) and 'fields' in fieldset_options:
                        fields = fieldset_options['fields']
                        if isinstance(fields, (list, tuple)):
                            for field_name in fields:
                                # 跳过方法名
                                if hasattr(admin_class, field_name):
                                    continue
                                base_field = field_name.split('__')[0]
                                if base_field not in model_fields:
                                    issues.append(f'{admin_name}: fieldsets中的字段 "{field_name}" 在模型 {model_name} 中不存在')

        # 检查readonly_fields
        readonly_fields = getattr(admin_class, 'readonly_fields', [])
        if callable(readonly_fields):
            try:
                readonly_fields = readonly_fields(None, None)
            except:
                readonly_fields = []

        for field_name in readonly_fields:
            # 跳过方法名
            if hasattr(admin_class, field_name):
                continue
            base_field = field_name.split('__')[0]
            if base_field not in model_fields:
                issues.append(f'{admin_name}: readonly_fields中的字段 "{field_name}" 在模型 {model_name} 中不存在')

        return issues

    def suggest_fixes(self):
        """建议修复方案"""
        self.stdout.write(self.style.SUCCESS('\n💡 修复建议:'))
        
        suggestions = [
            '1. 将created_at和updated_at字段添加到readonly_fields中',
            '2. 或者使用BaseModelAdmin基类，它会自动处理时间戳字段',
            '3. 确保fieldsets中的时间戳字段都在readonly_fields中',
            '4. 对于auto_now和auto_now_add字段，Django会自动设置为不可编辑'
        ]
        
        for suggestion in suggestions:
            self.stdout.write(f'  {suggestion}')
        
        self.stdout.write(self.style.WARNING('\n示例修复代码:'))
        example_code = '''
class YourModelAdmin(admin.ModelAdmin):
    readonly_fields = ['created_at', 'updated_at', 'other_readonly_fields']
    
    fieldsets = [
        ('基本信息', {
            'fields': ['name', 'description']
        }),
        ('时间信息', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
'''
        self.stdout.write(example_code)

    def get_model_timestamp_fields(self, model):
        """获取模型的时间戳字段"""
        timestamp_fields = []
        
        for field in model._meta.get_fields():
            if hasattr(field, 'auto_now_add') and field.auto_now_add:
                timestamp_fields.append(field.name)
            elif hasattr(field, 'auto_now') and field.auto_now:
                timestamp_fields.append(field.name)
        
        return timestamp_fields

    def check_field_editability(self, model, field_name):
        """检查字段是否可编辑"""
        try:
            field = model._meta.get_field(field_name)
            
            # 检查auto_now和auto_now_add
            if hasattr(field, 'auto_now_add') and field.auto_now_add:
                return False, 'auto_now_add=True'
            if hasattr(field, 'auto_now') and field.auto_now:
                return False, 'auto_now=True'
            
            # 检查editable属性
            if hasattr(field, 'editable') and not field.editable:
                return False, 'editable=False'
            
            return True, 'editable'
            
        except:
            return None, 'field_not_found'
