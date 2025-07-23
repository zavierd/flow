from django.core.management.base import BaseCommand
from django.apps import apps
from django.conf import settings
from django.db import connection
from django.core.cache import cache
import os
import time
from pathlib import Path


class Command(BaseCommand):
    help = '优化Django Admin性能和配置'

    def add_arguments(self, parser):
        parser.add_argument(
            '--analyze',
            action='store_true',
            help='分析当前admin性能',
        )
        parser.add_argument(
            '--optimize',
            action='store_true', 
            help='应用性能优化',
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='清理缓存和临时文件',
        )
        parser.add_argument(
            '--report',
            action='store_true',
            help='生成优化报告',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Django Admin优化工具')
        )
        
        if options['analyze']:
            self.analyze_performance()
        
        if options['optimize']:
            self.apply_optimizations()
        
        if options['cleanup']:
            self.cleanup_cache()
        
        if options['report']:
            self.generate_report()
        
        if not any(options.values()):
            self.show_help()

    def analyze_performance(self):
        """分析当前admin性能"""
        self.stdout.write('\n📊 分析Admin性能...')
        
        # 分析模型数据量
        models_info = []
        for model in apps.get_models():
            if model._meta.app_label == 'products':
                try:
                    count = model.objects.count()
                    table_name = model._meta.db_table
                    
                    # 获取表大小（PostgreSQL）
                    with connection.cursor() as cursor:
                        try:
                            cursor.execute(
                                "SELECT pg_size_pretty(pg_total_relation_size(%s))",
                                [table_name]
                            )
                            size = cursor.fetchone()[0]
                        except:
                            size = '未知'
                    
                    models_info.append({
                        'model': model.__name__,
                        'count': count,
                        'size': size,
                        'needs_optimization': count > 10000
                    })
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠️  无法分析模型 {model.__name__}: {e}')
                    )
        
        # 显示分析结果
        self.stdout.write('\n📈 模型数据分析:')
        for info in models_info:
            status = '🔴 需要优化' if info['needs_optimization'] else '🟢 正常'
            self.stdout.write(
                f"  {info['model']:15} | {info['count']:8,} 条记录 | {info['size']:10} | {status}"
            )
        
        # 分析查询性能
        self.analyze_queries()
        
        # 分析索引使用情况
        self.analyze_indexes()

    def analyze_queries(self):
        """分析查询性能"""
        self.stdout.write('\n🔍 分析查询性能...')
        
        # 模拟常见admin查询
        from products.models import Category, Brand, SPU, SKU
        
        queries = [
            ('分类列表查询', lambda: list(Category.objects.all()[:25])),
            ('品牌列表查询', lambda: list(Brand.objects.all()[:25])),
            ('SPU列表查询', lambda: list(SPU.objects.select_related('category', 'brand')[:25])),
            ('SKU列表查询', lambda: list(SKU.objects.select_related('spu', 'brand')[:25])),
        ]
        
        for name, query_func in queries:
            start_time = time.time()
            try:
                query_func()
                duration = (time.time() - start_time) * 1000
                status = '🟢 快' if duration < 100 else ('🟡 中等' if duration < 500 else '🔴 慢')
                self.stdout.write(f"  {name:15} | {duration:6.1f}ms | {status}")
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  {name:15} | 错误: {e}")
                )

    def analyze_indexes(self):
        """分析索引使用情况"""
        self.stdout.write('\n📇 分析索引使用情况...')
        
        try:
            with connection.cursor() as cursor:
                # 获取未使用的索引（PostgreSQL）
                cursor.execute("""
                    SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
                    FROM pg_stat_user_indexes 
                    WHERE schemaname = 'public' 
                    AND idx_tup_read = 0 
                    AND idx_tup_fetch = 0
                """)
                
                unused_indexes = cursor.fetchall()
                if unused_indexes:
                    self.stdout.write('  🔴 发现未使用的索引:')
                    for idx in unused_indexes:
                        self.stdout.write(f"    - {idx[2]} on {idx[1]}")
                else:
                    self.stdout.write('  🟢 所有索引都有被使用')
                    
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'  ⚠️  无法分析索引: {e}')
            )

    def apply_optimizations(self):
        """应用性能优化"""
        self.stdout.write('\n⚡ 应用性能优化...')
        
        optimizations = [
            ('清理过期缓存', self.clear_expired_cache),
            ('优化静态文件', self.optimize_static_files),
            ('生成缺失索引', self.create_missing_indexes),
            ('更新数据库统计信息', self.update_db_stats),
            ('清理会话数据', self.cleanup_sessions),
        ]
        
        for name, func in optimizations:
            try:
                self.stdout.write(f'  📌 {name}...')
                func()
                self.stdout.write(f'    ✅ {name}完成')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'    ❌ {name}失败: {e}')
                )

    def clear_expired_cache(self):
        """清理过期缓存"""
        if not settings.DEBUG:
            cache.clear()
            self.stdout.write(self.style.SUCCESS('✓ 过期缓存已清理'))
        else:
            self.stdout.write(self.style.WARNING('开发环境：跳过缓存清理'))

    def optimize_static_files(self):
        """优化静态文件"""
        # 压缩CSS和JS文件
        static_root = getattr(settings, 'STATIC_ROOT', None)
        if static_root and os.path.exists(static_root):
            import gzip
            import shutil
            
            for root, dirs, files in os.walk(static_root):
                for file in files:
                    if file.endswith(('.css', '.js')):
                        file_path = os.path.join(root, file)
                        gz_path = file_path + '.gz'
                        
                        # 如果gzip文件不存在或源文件更新
                        if not os.path.exists(gz_path) or os.path.getmtime(file_path) > os.path.getmtime(gz_path):
                            with open(file_path, 'rb') as f_in:
                                with gzip.open(gz_path, 'wb') as f_out:
                                    shutil.copyfileobj(f_in, f_out)

    def create_missing_indexes(self):
        """创建缺失的索引"""
        from django.db import models
        from products.models import Category, Brand, SPU, SKU, Attribute, AttributeValue
        
        # 常见的需要索引的字段组合
        index_suggestions = [
            (Category, ['parent_id', 'is_active']),
            (Brand, ['is_active', 'created_at']),
            (SPU, ['category_id', 'is_active']),
            (SKU, ['spu_id', 'status']),
            (Attribute, ['type', 'is_active']),
            (AttributeValue, ['attribute_id', 'is_active']),
        ]
        
        for model, fields in index_suggestions:
            # 检查是否已存在组合索引
            existing_indexes = [idx.fields for idx in model._meta.indexes]
            if fields not in existing_indexes:
                self.stdout.write(f'    💡 建议为 {model.__name__} 添加索引: {fields}')

    def update_db_stats(self):
        """更新数据库统计信息"""
        try:
            with connection.cursor() as cursor:
                # PostgreSQL
                if connection.vendor == 'postgresql':
                    cursor.execute("ANALYZE;")
                # MySQL
                elif connection.vendor == 'mysql':
                    cursor.execute("ANALYZE TABLE products_category, products_brand, products_spu, products_sku;")
        except Exception as e:
            raise Exception(f"更新统计信息失败: {e}")

    def cleanup_sessions(self):
        """清理过期会话"""
        from django.core.management import call_command
        try:
            call_command('clearsessions')
        except Exception as e:
            raise Exception(f"清理会话失败: {e}")

    def cleanup_cache(self):
        """清理缓存和临时文件"""
        self.stdout.write('\n🧹 清理缓存和临时文件...')
        
        cleanups = [
            ('Django缓存', lambda: cache.clear() if not settings.DEBUG else None),
            ('Python缓存', self.clear_python_cache),
            ('临时文件', self.clear_temp_files),
            ('过期会话', self.cleanup_sessions),
        ]
        
        for name, func in cleanups:
            try:
                self.stdout.write(f'  📌 清理{name}...')
                func()
                self.stdout.write(f'    ✅ {name}清理完成')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'    ❌ {name}清理失败: {e}')
                )

    def clear_python_cache(self):
        """清理Python缓存"""
        import shutil
        import sys
        
        # 清理__pycache__目录
        for root, dirs, files in os.walk('.'):
            if '__pycache__' in dirs:
                pycache_path = os.path.join(root, '__pycache__')
                shutil.rmtree(pycache_path)

    def clear_temp_files(self):
        """清理临时文件"""
        import tempfile
        temp_dir = tempfile.gettempdir()
        
        # 清理Django临时文件
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.startswith('django_') and file.endswith('.tmp'):
                    try:
                        os.remove(os.path.join(root, file))
                    except:
                        pass

    def generate_report(self):
        """生成优化报告"""
        self.stdout.write('\n📋 生成优化报告...')
        
        report_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'models': [],
            'recommendations': [],
            'performance': {}
        }
        
        # 收集模型信息
        for model in apps.get_models():
            if model._meta.app_label == 'products':
                try:
                    count = model.objects.count()
                    report_data['models'].append({
                        'name': model.__name__,
                        'count': count,
                        'table': model._meta.db_table
                    })
                except:
                    pass
        
        # 生成建议
        report_data['recommendations'] = [
            '启用查询缓存以提高重复查询性能',
            '为大表启用分页优化',
            '使用select_related和prefetch_related优化关联查询',
            '定期清理过期数据和日志文件',
            '监控慢查询并优化索引',
        ]
        
        # 保存报告
        report_file = 'admin_optimization_report.json'
        import json
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        self.stdout.write(f'  ✅ 报告已保存到: {report_file}')

    def show_help(self):
        """显示帮助信息"""
        help_text = """
🔧 Django Admin优化工具使用指南

可用选项:
  --analyze     分析当前admin性能状况
  --optimize    应用性能优化措施  
  --cleanup     清理缓存和临时文件
  --report      生成优化建议报告

使用示例:
  python manage.py optimize_admin --analyze
  python manage.py optimize_admin --optimize --cleanup
  python manage.py optimize_admin --report

💡 建议定期运行此工具以保持最佳性能
        """
        self.stdout.write(help_text) 