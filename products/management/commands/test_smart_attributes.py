"""
测试智能属性处理功能
"""

from django.core.management.base import BaseCommand
from products.services.import_system.orchestrator import ImportOrchestrator
from products.models import ImportTask
import csv
from io import StringIO


class Command(BaseCommand):
    help = '测试智能属性处理功能'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-unknown-attributes',
            action='store_true',
            help='测试未定义属性的智能处理'
        )

    def handle(self, *args, **options):
        if options['test_unknown_attributes']:
            self.test_unknown_attributes()

    def test_unknown_attributes(self):
        """测试未定义属性的智能处理"""
        self.stdout.write(self.style.SUCCESS('🧪 开始测试智能属性处理功能...'))
        
        # 创建包含未定义属性的测试数据
        test_csv = self._generate_test_data_with_unknown_attributes()
        
        # 创建或获取测试用户
        from django.contrib.auth.models import User
        test_user, created = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@example.com'}
        )

        # 创建导入任务
        task = ImportTask.objects.create(
            name='智能属性测试任务',
            task_type='products',
            status='pending',
            total_rows=0,
            created_by=test_user
        )

        # 创建导入编排器
        orchestrator = ImportOrchestrator(task)
        
        # 执行导入
        self.stdout.write('📊 开始处理包含未定义属性的测试数据...')
        result = orchestrator.process_import(test_csv)
        
        # 显示结果
        self._display_test_results(result, task)
        
        # 显示智能属性处理统计
        self._display_smart_attribute_stats(task)

    def _generate_test_data_with_unknown_attributes(self):
        """生成包含未定义属性的测试数据"""
        # 标准15列 + 额外的未定义属性
        test_data = [
            {
                # 标准属性
                '产品描述 (Description)': 'NOVO系列单门底柜<br>Single Door Base Cabinet<br>现代简约风格',
                '产品编码 (Code)': 'N-NOVO80-TEST-001',
                '系列 (Series)': 'NOVO',
                '类型代码 (Type_Code)': 'U',
                '宽度 (Width_cm)': '80',
                '高度 (Height_cm)': '72',
                '深度 (Depth_cm)': '56',
                '配置代码 (Config_Code)': 'STD-001',
                '开门方向 (Door_Swing)': 'L',
                '等级Ⅰ': '1,200',
                '等级Ⅱ': '1,350',
                '等级Ⅲ': '1,500',
                '等级Ⅳ': '1,650',
                '等级Ⅴ': '1,800',
                '备注 (Remarks)': '标准配置',
                
                # 未定义属性（测试AI智能处理）
                '材质': '实木颗粒板',
                '颜色': '胡桃木色',
                '风格': '现代简约',
                '厚度': '18mm',
                '重量': '25kg',
                '产地': '广东佛山',
                '环保等级': 'E1',
                '表面工艺': '三聚氰胺贴面',
                '包装方式': '平板包装',
                '质保期': '3年'
            },
            {
                # 标准属性
                '产品描述 (Description)': 'CLASSIC系列双门吊柜<br>Double Door Wall Cabinet<br>经典传统风格',
                '产品编码 (Code)': 'N-CLASSIC90-TEST-002',
                '系列 (Series)': 'CLASSIC',
                '类型代码 (Type_Code)': 'W',
                '宽度 (Width_cm)': '90',
                '高度 (Height_cm)': '60',
                '深度 (Depth_cm)': '35',
                '配置代码 (Config_Code)': 'STD-002',
                '开门方向 (Door_Swing)': 'L/R',
                '等级Ⅰ': '800',
                '等级Ⅱ': '900',
                '等级Ⅲ': '1,000',
                '等级Ⅳ': '1,100',
                '等级Ⅴ': '1,200',
                '备注 (Remarks)': '经典款式',
                
                # 未定义属性（不同的属性组合）
                '材质': '多层实木板',
                '颜色': '原木色',
                '风格': '欧式古典',
                '厚度': '16mm',
                '承重': '15kg',
                '产地': '江苏南京',
                '环保等级': 'E0',
                '门板类型': '实木门板',
                '五金品牌': 'Blum',
                '安装方式': '壁挂式'
            }
        ]
        
        # 转换为CSV格式
        if not test_data:
            return ""

        # 获取所有字段名（合并所有行的字段）
        all_fieldnames = set()
        for row in test_data:
            all_fieldnames.update(row.keys())
        fieldnames = list(all_fieldnames)

        # 创建CSV内容
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(test_data)

        csv_content = output.getvalue()
        output.close()

        return csv_content

    def _display_test_results(self, result, task):
        """显示测试结果"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📊 智能属性处理测试结果'))
        self.stdout.write('='*60)

        # 基础统计
        self.stdout.write(f'任务ID: {task.id}')
        self.stdout.write(f'导入成功: {result.success}')
        self.stdout.write(f'总行数: {getattr(result, "total_rows", 0)}')
        self.stdout.write(f'成功行数: {getattr(result, "success_rows", 0)}')
        self.stdout.write(f'失败行数: {getattr(result, "error_rows", 0)}')

        total_rows = getattr(result, "total_rows", 1)
        success_rows = getattr(result, "success_rows", 0)
        success_rate = success_rows / max(total_rows, 1) * 100
        self.stdout.write(f'成功率: {success_rate:.1f}%')

    def _display_smart_attribute_stats(self, task):
        """显示智能属性处理统计"""
        self.stdout.write('\n' + '-'*40)
        self.stdout.write(self.style.WARNING('🤖 智能属性处理统计'))
        self.stdout.write('-'*40)
        
        # 这里可以查询数据库获取实际的智能属性处理结果
        from products.models import Attribute, AttributeValue, SKU
        
        # 统计新创建的属性
        recent_attributes = Attribute.objects.filter(
            description__contains='AI智能识别'
        ).order_by('-id')[:20]
        
        if recent_attributes:
            self.stdout.write(f'🏷️ 发现 {recent_attributes.count()} 个AI创建的属性:')
            for attr in recent_attributes:
                self.stdout.write(f'  • {attr.name} ({attr.type}) - 可筛选: {attr.is_filterable}')
        else:
            self.stdout.write('⚠️ 未发现AI创建的属性（可能AI服务未启用或处理失败）')
        
        # 统计SKU数量
        total_skus = SKU.objects.count()
        self.stdout.write(f'📦 当前SKU总数: {total_skus}')
        
        # 统计属性值数量
        total_attr_values = AttributeValue.objects.count()
        self.stdout.write(f'🔢 当前属性值总数: {total_attr_values}')
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ 智能属性处理测试完成！'))
        
        # 提供查看建议
        self.stdout.write('\n💡 建议操作:')
        self.stdout.write('1. 检查Django Admin中的属性管理页面')
        self.stdout.write('2. 查看产品详情页面的属性显示')
        self.stdout.write('3. 测试属性筛选功能')
        self.stdout.write('4. 检查日志文件中的AI处理详情')
