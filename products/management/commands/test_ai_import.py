from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from products.services.ai_data_import_service import AIDataImportService
from products.models import ImportTask
import os


class Command(BaseCommand):
    help = '测试AI数据导入功能'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='CSV文件路径')
        parser.add_argument('--user', type=str, default='admin', help='用户名')

    def handle(self, *args, **options):
        try:
            # 获取用户
            user = User.objects.get(username=options['user'])
            self.stdout.write(f"使用用户: {user.username}")

            # 读取CSV文件
            file_path = options.get('file', 'test_data.csv')
            if not os.path.exists(file_path):
                self.stdout.write(self.style.ERROR(f'文件不存在: {file_path}'))
                return

            with open(file_path, 'r', encoding='utf-8') as f:
                csv_content = f.read()

            self.stdout.write(f"读取文件: {file_path}")
            self.stdout.write(f"文件大小: {len(csv_content)} 字符")

            # 创建导入任务
            task = ImportTask.objects.create(
                name=f'测试AI数据导入_{os.path.basename(file_path)}',
                task_type='ai_data',
                created_by=user,
                status='pending'
            )

            self.stdout.write(f"创建任务: {task.id}")

            # 创建AI数据导入服务
            import_service = AIDataImportService(task)

            # 测试CSV解析
            self.stdout.write("开始解析CSV数据...")
            rows = import_service._parse_ai_csv_data(csv_content)

            if rows is None:
                self.stdout.write(self.style.ERROR("CSV解析失败"))
                return

            self.stdout.write(f"解析成功，共 {len(rows)} 行数据")

            # 显示前几行数据
            for i, row in enumerate(rows[:3]):
                self.stdout.write(f"第 {i+1} 行数据:")
                for key, value in row.items():
                    self.stdout.write(f"  {key}: {value}")
                self.stdout.write("")

            # 测试处理第一行数据
            if rows:
                self.stdout.write("测试处理第一行数据...")
                try:
                    import_service._process_ai_data_row(rows[0], 2)
                    self.stdout.write(self.style.SUCCESS("第一行数据处理成功"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"第一行数据处理失败: {str(e)}"))
                    import traceback
                    traceback.print_exc()

        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'用户不存在: {options["user"]}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'测试失败: {str(e)}'))
            import traceback
            traceback.print_exc()
