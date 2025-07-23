"""
测试AI增强功能的管理命令
"""

from django.core.management.base import BaseCommand
from products.utils.ai_feature_flags import AIFeatureFlags
from products.services.ai_enhanced.ai_quality_service import AIQualityService


class Command(BaseCommand):
    help = '测试AI增强功能'

    def add_arguments(self, parser):
        parser.add_argument(
            '--enable-quality',
            action='store_true',
            help='启用数据质量检测功能',
        )
        parser.add_argument(
            '--disable-quality',
            action='store_true',
            help='禁用数据质量检测功能',
        )
        parser.add_argument(
            '--test-quality',
            action='store_true',
            help='测试数据质量检测功能',
        )
        parser.add_argument(
            '--status',
            action='store_true',
            help='显示所有AI功能状态',
        )
        parser.add_argument(
            '--test-bad-data',
            action='store_true',
            help='测试包含问题的数据',
        )
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='清除AI功能缓存',
        )
        parser.add_argument(
            '--debug-settings',
            action='store_true',
            help='调试设置信息',
        )
        parser.add_argument(
            '--test-smart-attributes',
            action='store_true',
            help='测试智能属性提取功能',
        )
        parser.add_argument(
            '--enable-smart-attributes',
            action='store_true',
            help='启用智能属性提取功能',
        )
        parser.add_argument(
            '--test-deepseek-api',
            action='store_true',
            help='测试DeepSeek API功能',
        )
        parser.add_argument(
            '--test-full-import',
            action='store_true',
            help='测试完整的AI增强导入流程',
        )
        parser.add_argument(
            '--test-smart-validation',
            action='store_true',
            help='测试AI智能验证功能',
        )
        parser.add_argument(
            '--clear-product-data',
            action='store_true',
            help='清空产品和属性数据（已废弃，请使用 clear_product_data 命令）',
        )
        parser.add_argument(
            '--confirm-clear',
            action='store_true',
            help='确认清空数据操作（已废弃）',
        )
        parser.add_argument(
            '--test-simple-import',
            action='store_true',
            help='测试简单导入（不使用AI功能）',
        )
        parser.add_argument(
            '--test-modular-import',
            action='store_true',
            help='测试模块化导入系统',
        )

    def handle(self, *args, **options):
        if options['enable_quality']:
            AIFeatureFlags.enable_feature(AIFeatureFlags.QUALITY_DETECTION)
            self.stdout.write(
                self.style.SUCCESS('✅ 数据质量检测功能已启用')
            )

        elif options['disable_quality']:
            AIFeatureFlags.disable_feature(AIFeatureFlags.QUALITY_DETECTION)
            self.stdout.write(
                self.style.WARNING('⚠️ 数据质量检测功能已禁用')
            )

        elif options['test_quality']:
            self._test_quality_detection()

        elif options['test_bad_data']:
            self._test_bad_data()

        elif options['clear_cache']:
            AIFeatureFlags.clear_cache()
            self.stdout.write(
                self.style.SUCCESS('🧹 AI功能缓存已清除')
            )

        elif options['enable_smart_attributes']:
            AIFeatureFlags.enable_feature(AIFeatureFlags.SMART_ATTRIBUTES)
            self.stdout.write(
                self.style.SUCCESS('✅ 智能属性提取功能已启用')
            )

        elif options['test_smart_attributes']:
            self._test_smart_attributes()

        elif options['test_deepseek_api']:
            self._test_deepseek_api()

        elif options['test_full_import']:
            self._test_full_import()

        elif options['test_smart_validation']:
            self._test_smart_validation()

        elif options['clear_product_data']:
            self.stdout.write(
                self.style.WARNING('⚠️  --clear-product-data 已废弃')
            )
            self.stdout.write('请使用新的清理命令:')
            self.stdout.write('  python manage.py clear_product_data --summary  # 查看数据摘要')
            self.stdout.write('  python manage.py clear_product_data --dry-run  # 预览删除操作')
            self.stdout.write('  python manage.py clear_product_data --confirm  # 执行清理')
            return

        elif options['test_simple_import']:
            self._test_simple_import()

        elif options['test_modular_import']:
            self._test_modular_import()

        elif options['debug_settings']:
            self._debug_settings()

        elif options['status']:
            self._show_status()

        else:
            self.stdout.write(
                self.style.ERROR('请指定操作参数，使用 --help 查看帮助')
            )

    def _test_quality_detection(self):
        """测试数据质量检测功能"""
        self.stdout.write('🧪 测试数据质量检测功能...')

        try:
            # 首先测试导入
            self.stdout.write('📦 导入AI质量服务...')
            from products.services.ai_enhanced.ai_quality_service import AIQualityService
            self.stdout.write('✅ 导入成功')

            # 创建服务实例
            self.stdout.write('🔧 创建服务实例...')
            service = AIQualityService()
            self.stdout.write('✅ 服务实例创建成功')

            # 检查服务状态
            self.stdout.write(f'🔍 服务启用状态: {service.enabled}')

            if not service.enabled:
                self.stdout.write(self.style.WARNING('⚠️ 服务未启用，但继续测试...'))

            # 测试数据
            test_data = {
                '产品描述 (Description)': '单门底柜<br>1 door base unit',
                '产品编码 (Code)': 'N-U30-7256-L/R',
                '系列 (Series)': 'N',
                '类型代码 (Type_Code)': 'U',
                '宽度 (Width_cm)': 30,
                '高度 (Height_cm)': 72,
                '深度 (Depth_cm)': 56,
                '配置代码 (Config_Code)': '30',
                '开门方向 (Door_Swing)': 'L/R',
                '等级Ⅰ': '8,500',
                '等级Ⅱ': '8,890',
                '等级Ⅲ': '9,070',
                '等级Ⅳ': '9,230',
                '等级Ⅴ': '10,160',
                '备注 (Remarks)': '标准配置'
            }

            self.stdout.write('🔍 开始质量检测...')
            # 使用测试专用方法，忽略启用状态
            if hasattr(service, 'process_for_test'):
                result = service.process_for_test(test_data)
            else:
                result = service.process(test_data)

            if result:
                self.stdout.write('✅ 质量检测完成')
                self.stdout.write(f"📊 检测结果: {result.get('success', False)}")
                self.stdout.write(f"💯 质量评分: {result.get('quality_score', 0)}")
                self.stdout.write(f"📋 问题数量: {result.get('total_issues', 0)}")

                issues = result.get('issues', [])
                if issues:
                    self.stdout.write('⚠️ 发现的问题:')
                    for issue in issues:
                        self.stdout.write(f"  - [{issue.get('severity', 'unknown')}] {issue.get('message', '')}")
                else:
                    self.stdout.write('✅ 数据质量良好，未发现问题')

                suggestions = result.get('suggestions', [])
                if suggestions:
                    self.stdout.write('💡 修复建议:')
                    for suggestion in suggestions:
                        self.stdout.write(f"  - {suggestion.get('message', '')}")

            else:
                self.stdout.write(self.style.ERROR('❌ 质量检测返回空结果'))

        except Exception as e:
            import traceback
            self.stdout.write(
                self.style.ERROR(f'❌ 测试失败: {str(e)}')
            )
            self.stdout.write('📋 详细错误信息:')
            self.stdout.write(traceback.format_exc())

    def _test_smart_attributes(self):
        """测试智能属性提取功能"""
        self.stdout.write('🧠 测试智能属性提取功能...')

        try:
            # 导入服务
            from products.services.ai_enhanced.smart_attributes_service import SmartAttributesService
            service = SmartAttributesService()

            self.stdout.write(f'🔍 服务启用状态: {service.enabled}')

            # 测试复杂产品数据（会触发AI增强）
            test_data = {
                'brand': 'ROYANA',
                'description': '欧式古典风格橡木实木酒柜，带LED灯带，玻璃展示门，内置恒温系统，可存储120瓶红酒，表面采用手工雕花工艺，金色拉手',
                'code': 'CUSTOM-WINE-001',  # 非标准编码，会触发AI
                'series': 'LUXURY'
            }

            self.stdout.write('🔍 开始属性提取...')
            self.stdout.write(f'📋 测试数据: {test_data}')

            # 使用测试方法（忽略启用状态）
            if hasattr(service, 'process_for_test'):
                result = service.process_for_test(test_data)
            else:
                result = service.process(test_data)

            if result and result.get('success'):
                self.stdout.write('✅ 属性提取完成')
                self.stdout.write(f"📊 处理方式: {result.get('processing_method', 'unknown')}")
                self.stdout.write(f"🔧 规则提取: {result.get('rule_count', 0)} 个属性")
                self.stdout.write(f"🤖 AI提取: {result.get('ai_count', 0)} 个属性")
                self.stdout.write(f"📋 最终属性: {result.get('final_count', 0)} 个")

                attributes = result.get('attributes', [])
                if attributes:
                    self.stdout.write('🏷️ 提取的属性:')
                    for attr in attributes:
                        matched_status = '✅' if attr.get('matched_existing') else '🆕'
                        confidence = attr.get('confidence', 0)
                        source = attr.get('source', 'unknown')

                        self.stdout.write(
                            f"  {matched_status} {attr.get('attribute_name', '')}: "
                            f"{attr.get('value', '')} "
                            f"(置信度: {confidence:.2f}, 来源: {source})"
                        )
                else:
                    self.stdout.write('⚠️ 未提取到任何属性')

            else:
                error_msg = result.get('error', '未知错误') if result else '服务返回空结果'
                self.stdout.write(self.style.ERROR(f'❌ 属性提取失败: {error_msg}'))

        except Exception as e:
            import traceback
            self.stdout.write(
                self.style.ERROR(f'❌ 测试失败: {str(e)}')
            )
            self.stdout.write('📋 详细错误信息:')
            self.stdout.write(traceback.format_exc())

    def _test_deepseek_api(self):
        """测试DeepSeek API功能"""
        self.stdout.write('🤖 测试DeepSeek API功能...')

        try:
            # 导入DeepSeek服务
            from products.services.ai_enhanced.deepseek_service import DeepSeekService
            service = DeepSeekService()

            self.stdout.write(f'🔍 服务启用状态: {service.enabled}')
            self.stdout.write(f'🔑 API密钥配置: {"✅ 已配置" if service.api_key else "❌ 未配置"}')

            if not service.api_key:
                self.stdout.write(self.style.ERROR('❌ DeepSeek API密钥未配置'))
                return

            # 测试复杂产品数据（规则引擎难以处理的）
            complex_test_data = {
                'brand': 'ROYANA',
                'description': '欧式古典风格橡木实木酒柜，带LED灯带，玻璃展示门，内置恒温系统，可存储120瓶红酒，表面采用手工雕花工艺，金色拉手',
                'code': 'CUSTOM-WINE-001',  # 非标准编码
                'series': 'LUXURY'
            }

            self.stdout.write('🔍 开始AI属性提取...')
            self.stdout.write(f'📋 测试数据: {complex_test_data["description"][:50]}...')

            # 直接调用DeepSeek API
            result = service.extract_attributes(complex_test_data)

            if result and result.get('success'):
                self.stdout.write('✅ DeepSeek API调用成功')

                # 显示使用情况
                usage = result.get('usage', {})
                if usage:
                    self.stdout.write(f"💰 Token使用: 输入{usage.get('prompt_tokens', 0)}, 输出{usage.get('completion_tokens', 0)}, 总计{usage.get('total_tokens', 0)}")

                # 显示提取的属性
                attributes = result.get('attributes', [])
                if attributes:
                    self.stdout.write(f'🏷️ AI提取了 {len(attributes)} 个属性:')
                    for attr in attributes:
                        confidence = attr.get('confidence', 0)
                        unit = attr.get('unit', '')
                        unit_str = f" {unit}" if unit else ""

                        self.stdout.write(
                            f"  🤖 {attr.get('name', '')}: "
                            f"{attr.get('value', '')}{unit_str} "
                            f"(置信度: {confidence:.2f})"
                        )
                else:
                    self.stdout.write('⚠️ AI未提取到任何属性')

                # 显示原始响应（调试用）
                raw_response = result.get('raw_response', '')
                if raw_response:
                    self.stdout.write('📋 AI原始响应:')
                    self.stdout.write(raw_response[:500] + ('...' if len(raw_response) > 500 else ''))

            else:
                error_msg = result.get('error', '未知错误') if result else 'API调用返回空结果'
                self.stdout.write(self.style.ERROR(f'❌ DeepSeek API调用失败: {error_msg}'))

                # 显示原始响应（如果有）
                if result and 'raw_response' in result:
                    self.stdout.write('📋 错误响应:')
                    self.stdout.write(result['raw_response'])

        except Exception as e:
            import traceback
            self.stdout.write(
                self.style.ERROR(f'❌ 测试失败: {str(e)}')
            )
            self.stdout.write('📋 详细错误信息:')
            self.stdout.write(traceback.format_exc())

    def _test_full_import(self):
        """测试完整的AI增强导入流程"""
        self.stdout.write('🚀 测试完整的AI增强导入流程...')

        try:
            # 创建测试CSV数据
            test_csv = '''产品描述 (Description),产品编码 (Code),系列 (Series),类型代码 (Type_Code),宽度 (Width_cm),高度 (Height_cm),深度 (Depth_cm),配置代码 (Config_Code),开门方向 (Door_Swing),等级Ⅰ,等级Ⅱ,等级Ⅲ,等级Ⅳ,等级Ⅴ,备注 (Remarks)
欧式古典风格橡木实木酒柜<br>带LED灯带玻璃展示门<br>内置恒温系统可存储120瓶红酒,LUXURY-WINE-001,LUXURY,WC,120,200,60,WINE120,双开,15000,16000,17000,18000,20000,手工雕花工艺金色拉手
现代简约白色烤漆书柜<br>带隐藏式LED灯带<br>可调节层板设计,MODERN-BOOK-001,MODERN,BC,80,220,35,BOOK80,无门,8000,8500,9000,9500,10000,环保E0级板材'''

            self.stdout.write('📋 测试数据准备完成')

            # 创建导入任务
            from products.models import ImportTask
            from django.contrib.auth.models import User

            # 获取或创建测试用户
            user, created = User.objects.get_or_create(
                username='test_ai_user',
                defaults={'email': 'test@example.com'}
            )

            task = ImportTask.objects.create(
                name='AI增强导入测试',
                task_type='ai_data',
                created_by=user,
                status='pending'
            )

            self.stdout.write(f'📋 创建导入任务: {task.id}')

            # 使用AI数据导入服务
            from products.services.ai_data_import_service import AIDataImportService
            import_service = AIDataImportService(task)

            self.stdout.write('🔍 开始AI增强导入...')
            result = import_service.process_ai_data_import(test_csv)

            if result.get('success'):
                self.stdout.write('✅ AI增强导入完成')
                self.stdout.write(f"📊 总行数: {result.get('total_rows', 0)}")
                self.stdout.write(f"✅ 成功行数: {result.get('success_rows', 0)}")
                self.stdout.write(f"❌ 失败行数: {result.get('error_rows', 0)}")

                # 检查创建的产品
                from products.models import SKU, SKUAttributeValue

                created_skus = SKU.objects.filter(
                    code__in=['LUXURY-WINE-001', 'MODERN-BOOK-001']
                )

                self.stdout.write(f'🏷️ 创建的产品数量: {created_skus.count()}')

                for sku in created_skus:
                    self.stdout.write(f'\n📦 产品: {sku.code} - {sku.name}')

                    # 显示属性
                    attributes = SKUAttributeValue.objects.filter(sku=sku).select_related(
                        'attribute', 'attribute_value'
                    )

                    self.stdout.write(f'🏷️ 属性数量: {attributes.count()}')
                    for attr in attributes:
                        confidence = getattr(attr, 'confidence_score', 0) or 0
                        self.stdout.write(
                            f"  • {attr.attribute.name}: {attr.attribute_value.value} "
                            f"(置信度: {confidence:.2f})"
                        )

            else:
                self.stdout.write(self.style.ERROR(f'❌ 导入失败: {result.get("error", "未知错误")}'))

        except Exception as e:
            import traceback
            self.stdout.write(
                self.style.ERROR(f'❌ 测试失败: {str(e)}')
            )
            self.stdout.write('📋 详细错误信息:')
            self.stdout.write(traceback.format_exc())

    def _test_smart_validation(self):
        """测试AI智能验证功能"""
        self.stdout.write('🧠 测试AI智能验证功能...')

        try:
            from products.services.ai_enhanced.ai_quality_service import AIQualityService
            service = AIQualityService()

            # 测试包含业务逻辑问题的数据
            problematic_data = {
                '产品描述 (Description)': '欧式古典风格橡木实木酒柜，带LED灯带，玻璃展示门，内置恒温系统',
                '产品编码 (Code)': 'LUXURY-WINE-001',
                '系列 (Series)': 'LUXURY',
                '类型代码 (Type_Code)': 'WC',
                '宽度 (Width_cm)': 10,      # 问题：酒柜宽度只有10cm，不合理
                '高度 (Height_cm)': 300,    # 问题：高度300cm过高
                '深度 (Depth_cm)': 60,
                '配置代码 (Config_Code)': 'WINE120',
                '开门方向 (Door_Swing)': '双开',
                '等级Ⅰ': '50000',          # 问题：价格过高，不符合尺寸
                '等级Ⅱ': '55000',
                '等级Ⅲ': '60000',
                '等级Ⅳ': '65000',
                '等级Ⅴ': '70000',
                '备注 (Remarks)': '手工雕花工艺金色拉手'
            }

            self.stdout.write('🔍 开始智能验证...')
            self.stdout.write('📋 测试数据包含多个业务逻辑问题：')
            self.stdout.write('  • 酒柜宽度只有10cm（不合理）')
            self.stdout.write('  • 高度300cm（过高）')
            self.stdout.write('  • 价格5万起（与小尺寸不符）')

            # 使用测试方法
            if hasattr(service, 'process_for_test'):
                result = service.process_for_test(problematic_data)
            else:
                result = service.process(problematic_data)

            if result and result.get('success'):
                self.stdout.write('✅ 智能验证完成')
                self.stdout.write(f"💯 质量评分: {result.get('quality_score', 0)}")
                self.stdout.write(f"📋 问题数量: {result.get('total_issues', 0)}")

                issues = result.get('issues', [])
                if issues:
                    self.stdout.write('🚨 发现的问题:')
                    for issue in issues:
                        issue_type = issue.get('type', 'unknown')
                        severity = issue.get('severity', 'unknown')
                        message = issue.get('message', '')

                        # 区分AI验证和规则验证
                        if issue_type == 'ai_business_logic':
                            icon = '🤖'
                            source = 'AI验证'
                        else:
                            icon = '📊'
                            source = '规则验证'

                        severity_icon = {
                            'critical': '🔴',
                            'high': '🟠',
                            'medium': '🟡',
                            'low': '🟢'
                        }.get(severity, '⚪')

                        self.stdout.write(f"  {icon} {severity_icon} [{source}] {message}")

                suggestions = result.get('suggestions', [])
                if suggestions:
                    self.stdout.write('💡 修复建议:')
                    for suggestion in suggestions:
                        self.stdout.write(f"  💡 {suggestion.get('message', '')}")

            else:
                error_msg = result.get('error', '未知错误') if result else '服务返回空结果'
                self.stdout.write(self.style.ERROR(f'❌ 智能验证失败: {error_msg}'))

        except Exception as e:
            import traceback
            self.stdout.write(
                self.style.ERROR(f'❌ 测试失败: {str(e)}')
            )
            self.stdout.write('📋 详细错误信息:')
            self.stdout.write(traceback.format_exc())

    def _clear_product_data(self):
        """清空产品和属性数据"""
        self.stdout.write('🗑️ 开始清空产品和属性数据...')

        try:
            from django.db import transaction
            from products.models import (
                SKU, SPU, SKUAttributeValue, SPUAttribute,
                AttributeValue, Attribute, Brand, Category,
                ImportTask, ImportError
            )

            with transaction.atomic():
                # 统计当前数据
                sku_count = SKU.objects.count()
                spu_count = SPU.objects.count()
                attr_count = Attribute.objects.count()
                attr_value_count = AttributeValue.objects.count()
                brand_count = Brand.objects.count()
                category_count = Category.objects.count()

                self.stdout.write(f'📊 当前数据统计:')
                self.stdout.write(f'  • SKU: {sku_count} 个')
                self.stdout.write(f'  • SPU: {spu_count} 个')
                self.stdout.write(f'  • 属性: {attr_count} 个')
                self.stdout.write(f'  • 属性值: {attr_value_count} 个')
                self.stdout.write(f'  • 品牌: {brand_count} 个')
                self.stdout.write(f'  • 分类: {category_count} 个')

                # 按顺序删除数据（考虑外键约束）
                self.stdout.write('🗑️ 删除SKU属性值关联...')
                deleted_sku_attr_values = SKUAttributeValue.objects.all().delete()[0]

                self.stdout.write('🗑️ 删除SPU属性关联...')
                deleted_spu_attrs = SPUAttribute.objects.all().delete()[0]

                self.stdout.write('🗑️ 删除SKU...')
                deleted_skus = SKU.objects.all().delete()[0]

                self.stdout.write('🗑️ 删除SPU...')
                deleted_spus = SPU.objects.all().delete()[0]

                self.stdout.write('🗑️ 删除属性值...')
                deleted_attr_values = AttributeValue.objects.all().delete()[0]

                self.stdout.write('🗑️ 删除属性...')
                deleted_attrs = Attribute.objects.all().delete()[0]

                self.stdout.write('🗑️ 删除品牌...')
                deleted_brands = Brand.objects.all().delete()[0]

                self.stdout.write('🗑️ 删除分类...')
                deleted_categories = Category.objects.all().delete()[0]

                self.stdout.write('🗑️ 删除导入任务和错误记录...')
                deleted_import_errors = ImportError.objects.all().delete()[0]
                deleted_import_tasks = ImportTask.objects.all().delete()[0]

                # 显示删除结果
                self.stdout.write('✅ 数据清理完成！')
                self.stdout.write(f'📊 删除统计:')
                self.stdout.write(f'  • SKU属性值关联: {deleted_sku_attr_values} 个')
                self.stdout.write(f'  • SPU属性关联: {deleted_spu_attrs} 个')
                self.stdout.write(f'  • SKU: {deleted_skus} 个')
                self.stdout.write(f'  • SPU: {deleted_spus} 个')
                self.stdout.write(f'  • 属性值: {deleted_attr_values} 个')
                self.stdout.write(f'  • 属性: {deleted_attrs} 个')
                self.stdout.write(f'  • 品牌: {deleted_brands} 个')
                self.stdout.write(f'  • 分类: {deleted_categories} 个')
                self.stdout.write(f'  • 导入错误: {deleted_import_errors} 个')
                self.stdout.write(f'  • 导入任务: {deleted_import_tasks} 个')

                self.stdout.write('🎉 数据库已清空，可以开始测试AI增强导入功能！')

        except Exception as e:
            import traceback
            self.stdout.write(
                self.style.ERROR(f'❌ 数据清理失败: {str(e)}')
            )
            self.stdout.write('📋 详细错误信息:')
            self.stdout.write(traceback.format_exc())

    def _test_modular_import(self):
        """测试模块化导入系统"""
        self.stdout.write('🚀 测试模块化导入系统...')

        try:
            # 准备真实的AI数据测试用例 - 完整15列格式
            test_csv = '''产品描述 (Description),产品编码 (Code),系列 (Series),类型代码 (Type_Code),宽度 (Width_cm),高度 (Height_cm),深度 (Depth_cm),配置代码 (Config_Code),开门方向 (Door_Swing),等级Ⅰ,等级Ⅱ,等级Ⅲ,等级Ⅳ,等级Ⅴ,备注 (Remarks)
"NOVO系列单门底柜<br>Single Door Base Cabinet<br>现代简约风格",N-NOVO80-1-L,NOVO,U,80,72,56,STD-001,L,"1,200","1,350","1,500","1,650","1,800","标准配置<br>包含调节脚<br>环保E1级板材"
"NOVO系列单门单抽底柜<br>Single Door Single Drawer Base Cabinet<br>现代简约风格",N-NOVO90-2-R,NOVO,US,90,72,56,STD-002,R,"1,500","1,680","1,860","2,040","2,220","标准配置<br>包含调节脚和抽屉滑轨<br>环保E1级板材"
"CLASSIC系列内置抽屉柜<br>Built-in Drawer Cabinet<br>经典传统风格",N-CLASSIC60-3-LR,CLASSIC,UC,60,72,56,STD-003,L/R,980,"1,100","1,220","1,340","1,460","经典款式<br>三层抽屉设计<br>实木贴面"'''

            self.stdout.write('📋 测试数据准备完成')

            # 创建测试用户
            from django.contrib.auth.models import User
            user, created = User.objects.get_or_create(
                username='test_modular_user',
                defaults={'email': 'test_modular@example.com'}
            )

            # 创建导入任务
            from products.models import ImportTask
            task = ImportTask.objects.create(
                name='模块化导入测试',
                task_type='ai_data',
                created_by=user,
                status='pending'
            )

            self.stdout.write(f'📋 创建导入任务: {task.id}')

            # 使用模块化导入服务
            from products.services.ai_data_import_service_v2 import AIDataImportServiceV2
            import_service = AIDataImportServiceV2(task)

            self.stdout.write('🔍 开始模块化导入...')
            result = import_service.process_ai_data_import(test_csv)

            if result.get('success'):
                self.stdout.write('✅ 模块化导入完成')
                self.stdout.write(f"📊 总行数: {result.get('total_rows', 0)}")
                self.stdout.write(f"✅ 成功行数: {result.get('success_rows', 0)}")
                self.stdout.write(f"❌ 失败行数: {result.get('error_rows', 0)}")

                if result.get('errors'):
                    self.stdout.write('📋 错误详情:')
                    for error in result.get('errors', [])[:5]:  # 只显示前5个错误
                        self.stdout.write(f"  • {error}")
            else:
                self.stdout.write(f"❌ 模块化导入失败: {result.get('error', '未知错误')}")

        except Exception as e:
            import traceback
            self.stdout.write(
                self.style.ERROR(f'❌ 模块化导入测试失败: {str(e)}')
            )
            self.stdout.write('📋 详细错误信息:')
            self.stdout.write(traceback.format_exc())

    def _test_bad_data(self):
        """测试包含问题的数据"""
        self.stdout.write('🧪 测试包含问题的数据...')

        # 包含多种问题的测试数据
        bad_test_data = {
            '产品描述 (Description)': '',  # 空描述
            '产品编码 (Code)': 'INVALID-CODE',  # 无效编码格式
            '系列 (Series)': 'N',
            '类型代码 (Type_Code)': 'U',
            '宽度 (Width_cm)': 500,  # 超出合理范围
            '高度 (Height_cm)': 'abc',  # 无效格式
            '深度 (Depth_cm)': -10,  # 负数
            '配置代码 (Config_Code)': '30',
            '开门方向 (Door_Swing)': 'L/R',
            '等级Ⅰ': '50,000',  # 价格过高
            '等级Ⅱ': '1,000',   # 价格递减（逻辑错误）
            '等级Ⅲ': 'invalid', # 无效价格格式
            '等级Ⅳ': '2,000',
            '等级Ⅴ': '3,000',
            '备注 (Remarks)': '测试数据'
        }

        try:
            from products.services.ai_enhanced.ai_quality_service import AIQualityService
            service = AIQualityService()

            result = service.process_for_test(bad_test_data)

            if result and result.get('success'):
                self.stdout.write(f"💯 质量评分: {result.get('quality_score', 0)}")
                self.stdout.write(f"📋 问题数量: {result.get('total_issues', 0)}")

                issues = result.get('issues', [])
                if issues:
                    self.stdout.write('🚨 发现的问题:')
                    for issue in issues:
                        severity_icon = {
                            'critical': '🔴',
                            'high': '🟠',
                            'medium': '🟡',
                            'low': '🟢'
                        }.get(issue.get('severity', 'low'), '⚪')

                        self.stdout.write(f"  {severity_icon} [{issue.get('severity', 'unknown')}] {issue.get('message', '')}")

                suggestions = result.get('suggestions', [])
                if suggestions:
                    self.stdout.write('💡 修复建议:')
                    for suggestion in suggestions:
                        self.stdout.write(f"  💡 {suggestion.get('message', '')}")

            else:
                self.stdout.write(self.style.ERROR('❌ 测试失败'))

        except Exception as e:
            import traceback
            self.stdout.write(self.style.ERROR(f'❌ 测试失败: {str(e)}'))
            self.stdout.write(traceback.format_exc())

    def _debug_settings(self):
        """调试设置信息"""
        from django.conf import settings

        self.stdout.write('🔍 调试AI设置信息:')

        # 检查Django设置
        ai_features = getattr(settings, 'AI_FEATURES', None)
        self.stdout.write(f"📋 Django AI_FEATURES 设置: {ai_features}")

        # 检查每个功能的详细状态
        for flag_name in AIFeatureFlags.DEFAULT_FLAGS.keys():
            cache_key = f'ai_feature_{flag_name}'
            from django.core.cache import cache
            cached_value = cache.get(cache_key)

            if ai_features:
                settings_value = ai_features.get(flag_name, False)
            else:
                settings_value = None

            self.stdout.write(f"  🔧 {flag_name}:")
            self.stdout.write(f"    - 设置值: {settings_value}")
            self.stdout.write(f"    - 缓存值: {cached_value}")
            self.stdout.write(f"    - 最终值: {AIFeatureFlags.is_enabled(flag_name)}")

    def _show_status(self):
        """显示所有AI功能状态"""
        self.stdout.write('🤖 AI功能状态:')

        flags = AIFeatureFlags.get_all_flags()
        for flag_name, enabled in flags.items():
            status = '✅ 启用' if enabled else '❌ 禁用'
            self.stdout.write(f"  {flag_name}: {status}")