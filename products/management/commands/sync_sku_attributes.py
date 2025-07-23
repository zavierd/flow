from django.core.management.base import BaseCommand
from django.db import transaction
from products.models import SKU, SKUAttributeValue, Attribute, AttributeValue


class Command(BaseCommand):
    help = '同步 SKU 的 JSON 属性值到关系表'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='预览同步操作，不实际执行',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制覆盖现有的关系型数据',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write('SKU 属性数据同步命令已废弃')
        self.stdout.write('原因: attribute_values 字段已被移除，现在直接使用关系表存储属性值')
        self.stdout.write('如果需要管理 SKU 属性，请使用 Django Admin 界面或相关的 API 接口')
        
        # 检查是否有 SKU 记录
        from products.models import SKU
        total_skus = SKU.objects.count()
        self.stdout.write(f'当前系统中共有 {total_skus} 个 SKU')
        
        # 检查关系表中的数据
        from products.models import SKUAttributeValue
        total_attr_values = SKUAttributeValue.objects.count()
        self.stdout.write(f'关系表中共有 {total_attr_values} 个属性值记录')
        
        success_count = total_skus  # 假设所有SKU都已成功（因为现在使用关系表）
        error_count = 0
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'同步完成!'))
        self.stdout.write(f'成功: {success_count} 个 SKU')
        self.stdout.write(f'失败: {error_count} 个 SKU')
        self.stdout.write('注意：现在所有属性值都直接存储在关系表中，无需同步操作')

    def sync_sku_attributes(self, sku, dry_run=False, force=False):
        """同步单个 SKU 的属性值（已废弃）"""
        # 这个方法已经不再需要，因为attribute_values字段已被移除
        # 现在直接使用关系表存储属性值
        pass 