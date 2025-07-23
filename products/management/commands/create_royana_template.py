"""
创建Royana产品导入模板的管理命令
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from products.models import ImportTemplate
from products.config.royana_import_template import ROYANA_IMPORT_TEMPLATE
import json


class Command(BaseCommand):
    help = '创建Royana产品导入模板'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='如果模板已存在，则更新它',
        )

    def handle(self, *args, **options):
        self.stdout.write('开始创建Royana产品导入模板...')
        
        try:
            with transaction.atomic():
                template_name = ROYANA_IMPORT_TEMPLATE['name']
                
                # 检查模板是否已存在
                existing_template = ImportTemplate.objects.filter(name=template_name).first()
                
                if existing_template:
                    if options['update']:
                        self.stdout.write(f'更新现有模板: {template_name}')
                        self._update_template(existing_template)
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'模板 "{template_name}" 已存在，使用 --update 参数来更新它')
                        )
                        return
                else:
                    self.stdout.write(f'创建新模板: {template_name}')
                    self._create_template()
                
                self.stdout.write(
                    self.style.SUCCESS('Royana产品导入模板创建/更新成功！')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'创建模板失败: {str(e)}')
            )
            raise

    def _create_template(self):
        """创建新模板"""
        # 直接使用SQL创建，因为模型定义与数据库结构不一致
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO products_importtemplate
                (name, template_type, description, field_mapping, required_fields, validation_rules, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, [
                ROYANA_IMPORT_TEMPLATE['name'],
                ROYANA_IMPORT_TEMPLATE['template_type'],
                ROYANA_IMPORT_TEMPLATE['description'],
                json.dumps(ROYANA_IMPORT_TEMPLATE['field_mapping']),
                json.dumps(ROYANA_IMPORT_TEMPLATE['required_fields']),
                json.dumps(ROYANA_IMPORT_TEMPLATE['validation_rules']),
                True
            ])

    def _update_template(self, template):
        """更新现有模板"""
        template.template_type = ROYANA_IMPORT_TEMPLATE['template_type']
        template.field_mapping = ROYANA_IMPORT_TEMPLATE['field_mapping']
        template.required_fields = ROYANA_IMPORT_TEMPLATE['required_fields']
        template.validation_rules = ROYANA_IMPORT_TEMPLATE['validation_rules']
        template.save()
