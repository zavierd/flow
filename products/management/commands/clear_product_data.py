"""
清空产品数据管理命令
提供安全的产品数据清理功能
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from products.services.import_system.utils.data_cleaner import DataCleaner


class Command(BaseCommand):
    help = '清空产品数据库 - 危险操作，需要确认'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='确认执行清理操作（必需）',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只显示统计信息，不执行实际删除',
        )
        parser.add_argument(
            '--types',
            nargs='+',
            help='指定要清理的数据类型 (sku, spu, attributes, brands, categories, import_tasks)',
        )
        parser.add_argument(
            '--summary',
            action='store_true',
            help='显示数据摘要',
        )

    def handle(self, *args, **options):
        cleaner = DataCleaner()
        
        # 显示数据摘要
        if options['summary']:
            self._show_data_summary(cleaner)
            return
        
        # 干运行模式
        if options['dry_run']:
            self._show_dry_run_info(cleaner)
            return
        
        # 执行清理
        if options['types']:
            # 清理指定类型的数据
            self._clear_specific_data(cleaner, options['types'], options['confirm'])
        else:
            # 清理所有产品数据
            self._clear_all_data(cleaner, options['confirm'])

    def _show_data_summary(self, cleaner: DataCleaner):
        """显示数据摘要"""
        self.stdout.write('📊 产品数据库摘要')
        self.stdout.write('=' * 50)
        
        summary = cleaner.get_data_summary()
        
        self.stdout.write(f'📈 总记录数: {summary["total_records"]:,}')
        self.stdout.write('')
        
        for category_name, category_data in summary['categories'].items():
            self.stdout.write(f'📂 {category_name.title()}: {category_data["count"]:,} 条记录')
            for detail_name, detail_count in category_data['details'].items():
                self.stdout.write(f'  • {detail_name}: {detail_count:,}')
            self.stdout.write('')
        
        if summary['total_records'] > 0:
            self.stdout.write(
                self.style.WARNING('⚠️  要清空所有数据，请运行:')
            )
            self.stdout.write(
                self.style.WARNING('   python manage.py clear_product_data --confirm')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ 数据库已经是空的')
            )

    def _show_dry_run_info(self, cleaner: DataCleaner):
        """显示干运行信息"""
        self.stdout.write('🔍 干运行模式 - 显示将要删除的数据')
        self.stdout.write('=' * 50)
        
        stats = cleaner._get_current_stats()
        total_records = sum(stats.values())
        
        if total_records == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ 数据库已经是空的，无需清理')
            )
            return
        
        self.stdout.write(f'📊 将要删除的数据:')
        self.stdout.write('')
        
        # 按删除顺序显示
        deletion_order = [
            ('SKU属性值关联', stats['sku_attribute_value_count']),
            ('SPU属性关联', stats['spu_attribute_count']),
            ('产品尺寸', stats['dimension_count']),
            ('产品定价规则', stats['pricing_rule_count']),
            ('SKU产品', stats['sku_count']),
            ('SPU产品', stats['spu_count']),
            ('属性值', stats['attribute_value_count']),
            ('属性', stats['attribute_count']),
            ('品牌', stats['brand_count']),
            ('产品分类', stats['category_count']),
            ('导入错误', stats['import_error_count']),
            ('导入任务', stats['import_task_count']),
        ]
        
        for name, count in deletion_order:
            if count > 0:
                self.stdout.write(f'  🗑️  {name}: {count:,} 条记录')
        
        self.stdout.write('')
        self.stdout.write(f'📈 总计: {total_records:,} 条记录')
        self.stdout.write('')
        self.stdout.write(
            self.style.WARNING('⚠️  要执行实际删除，请添加 --confirm 参数')
        )

    def _clear_all_data(self, cleaner: DataCleaner, confirm: bool):
        """清理所有数据"""
        if not confirm:
            self.stdout.write(
                self.style.ERROR('❌ 危险操作：清空产品数据需要 --confirm 参数')
            )
            self.stdout.write('使用方法: python manage.py clear_product_data --confirm')
            return
        
        self.stdout.write('🗑️ 开始清空产品数据...')
        self.stdout.write('')
        
        # 显示当前统计
        summary = cleaner.get_data_summary()
        self.stdout.write(f'📊 当前数据统计: {summary["total_records"]:,} 条记录')
        
        # 执行清理
        start_time = timezone.now()
        result = cleaner.clear_product_data(confirm=True)
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        if result['success']:
            self.stdout.write('')
            self.stdout.write('✅ 数据清理完成！')
            self.stdout.write(f'⏱️  耗时: {duration:.2f} 秒')
            self.stdout.write('')
            
            # 显示删除统计
            self.stdout.write('📊 删除统计:')
            for name, count in result['deletion_stats'].items():
                if count > 0:
                    self.stdout.write(f'  • {name}: {count:,} 条记录')
            
            # 显示最终统计
            total_deleted = sum(result['deletion_stats'].values())
            self.stdout.write('')
            self.stdout.write(f'🎯 总计删除: {total_deleted:,} 条记录')
            
            # 显示错误（如果有）
            if result['errors']:
                self.stdout.write('')
                self.stdout.write('⚠️  警告信息:')
                for error in result['errors']:
                    self.stdout.write(f'  • {error}')
            
            self.stdout.write('')
            self.stdout.write('🎉 数据库已清空，可以开始全新的数据导入！')
            
        else:
            self.stdout.write('')
            self.stdout.write(
                self.style.ERROR(f'❌ 数据清理失败: {result["error"]}')
            )
            if result.get('errors'):
                self.stdout.write('错误详情:')
                for error in result['errors']:
                    self.stdout.write(f'  • {error}')

    def _clear_specific_data(self, cleaner: DataCleaner, data_types: list, confirm: bool):
        """清理指定类型的数据"""
        if not confirm:
            self.stdout.write(
                self.style.ERROR('❌ 危险操作：清空数据需要 --confirm 参数')
            )
            return
        
        self.stdout.write(f'🗑️ 开始清空指定数据类型: {", ".join(data_types)}')
        
        result = cleaner.clear_specific_data(data_types, confirm=True)
        
        if result['success']:
            self.stdout.write('')
            self.stdout.write('✅ 指定数据清理完成！')
            self.stdout.write('')
            
            # 显示删除统计
            self.stdout.write('📊 删除统计:')
            for data_type, count in result['deletion_stats'].items():
                self.stdout.write(f'  • {data_type}: {count:,} 条记录')
            
            total_deleted = sum(result['deletion_stats'].values())
            self.stdout.write('')
            self.stdout.write(f'🎯 总计删除: {total_deleted:,} 条记录')
            
        else:
            self.stdout.write('')
            self.stdout.write(
                self.style.ERROR(f'❌ 数据清理失败: {result["error"]}')
            )
