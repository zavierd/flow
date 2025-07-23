from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from products.models import Category, Brand, Attribute, AttributeValue, SPU, SKU, SPUAttribute, ProductImage


class Command(BaseCommand):
    help = '设置产品管理系统的用户组和权限'

    def handle(self, *args, **options):
        """执行权限设置"""
        
        # 创建用户组
        self.create_user_groups()
        
        # 设置权限
        self.setup_permissions()
        
        self.stdout.write(
            self.style.SUCCESS('权限设置完成！')
        )

    def create_user_groups(self):
        """创建用户组"""
        
        groups = [
            {
                'name': '产品专员',
                'description': '负责产品信息录入、维护和管理'
            },
            {
                'name': '销售设计师',
                'description': '查询产品信息，进行方案设计'
            },
            {
                'name': '产品管理员',
                'description': '产品数据管理和维护'
            }
        ]
        
        for group_data in groups:
            group, created = Group.objects.get_or_create(
                name=group_data['name']
            )
            if created:
                self.stdout.write(f'创建用户组: {group.name}')
            else:
                self.stdout.write(f'用户组已存在: {group.name}')

    def setup_permissions(self):
        """设置权限"""
        
        # 获取用户组
        product_specialist = Group.objects.get(name='产品专员')
        sales_designer = Group.objects.get(name='销售设计师')
        product_manager = Group.objects.get(name='产品管理员')
        
        # 产品专员权限 - 可以添加和修改产品信息
        specialist_permissions = [
            'products.add_sku',
            'products.change_sku',
            'products.view_sku',
            'products.add_productimage',
            'products.change_productimage',
            'products.view_productimage',
            'products.view_spu',
            'products.view_brand',
            'products.view_category',
            'products.view_attribute',
            'products.view_attributevalue',
        ]
        
        # 销售设计师权限 - 只能查看产品信息
        designer_permissions = [
            'products.view_sku',
            'products.view_spu',
            'products.view_brand',
            'products.view_category',
            'products.view_attribute',
            'products.view_attributevalue',
            'products.view_productimage',
        ]
        
        # 产品管理员权限 - 可以管理所有产品相关数据
        manager_permissions = [
            'products.add_category',
            'products.change_category',
            'products.view_category',
            'products.add_brand',
            'products.change_brand',
            'products.view_brand',
            'products.add_attribute',
            'products.change_attribute',
            'products.view_attribute',
            'products.add_attributevalue',
            'products.change_attributevalue',
            'products.view_attributevalue',
            'products.add_spu',
            'products.change_spu',
            'products.view_spu',
            'products.add_spuattribute',
            'products.change_spuattribute',
            'products.view_spuattribute',
            'products.add_sku',
            'products.change_sku',
            'products.view_sku',
            'products.add_productimage',
            'products.change_productimage',
            'products.view_productimage',
        ]
        
        # 分配权限
        self.assign_permissions(product_specialist, specialist_permissions, '产品专员')
        self.assign_permissions(sales_designer, designer_permissions, '销售设计师')
        self.assign_permissions(product_manager, manager_permissions, '产品管理员')

    def assign_permissions(self, group, permission_codenames, group_name):
        """为用户组分配权限"""
        
        permissions = []
        for codename in permission_codenames:
            try:
                app_label, perm_codename = codename.split('.')
                permission = Permission.objects.get(
                    codename=perm_codename,
                    content_type__app_label=app_label
                )
                permissions.append(permission)
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'权限不存在: {codename}')
                )
                continue
        
        # 清空现有权限并重新分配
        group.permissions.clear()
        group.permissions.add(*permissions)
        
        self.stdout.write(
            self.style.SUCCESS(f'为 {group_name} 分配了 {len(permissions)} 个权限')
        )

    def add_arguments(self, parser):
        """添加命令参数"""
        parser.add_argument(
            '--reset',
            action='store_true',
            help='重置所有权限设置',
        ) 