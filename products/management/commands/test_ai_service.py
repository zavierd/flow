"""
测试AI服务连接和功能
"""

from django.core.management.base import BaseCommand
from products.services.ai_services import DeepSeekService, AttributeAnalyzer


class Command(BaseCommand):
    help = '测试AI服务连接和功能'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-connection',
            action='store_true',
            help='测试DeepSeek API连接'
        )
        parser.add_argument(
            '--test-attribute-analysis',
            action='store_true',
            help='测试属性分析功能'
        )
        parser.add_argument(
            '--test-all',
            action='store_true',
            help='运行所有测试'
        )

    def handle(self, *args, **options):
        if options['test_all']:
            self.test_connection()
            self.test_attribute_analysis()
        elif options['test_connection']:
            self.test_connection()
        elif options['test_attribute_analysis']:
            self.test_attribute_analysis()
        else:
            self.stdout.write(self.style.WARNING('请指定测试类型，使用 --help 查看选项'))

    def test_connection(self):
        """测试DeepSeek API连接"""
        self.stdout.write(self.style.SUCCESS('🔌 测试DeepSeek API连接...'))
        
        service = DeepSeekService()
        
        # 检查配置
        self.stdout.write(f'API密钥配置: {"✅ 已配置" if service.api_key else "❌ 未配置"}')
        self.stdout.write(f'API地址: {service.base_url}')
        self.stdout.write(f'模型: {service.model}')
        
        if not service.is_available():
            self.stdout.write(self.style.ERROR('❌ DeepSeek服务不可用，请检查配置'))
            return
        
        # 测试连接
        self.stdout.write('🧪 执行连接测试...')
        result = service.test_connection()
        
        if result['success']:
            self.stdout.write(self.style.SUCCESS(f'✅ {result["message"]}'))
            self.stdout.write(f'响应长度: {result["response_length"]} 字符')
            self.stdout.write(f'API密钥: {result["api_key_prefix"]}')
        else:
            self.stdout.write(self.style.ERROR(f'❌ 连接测试失败: {result["error"]}'))
            if 'details' in result:
                self.stdout.write(f'详情: {result["details"]}')

    def test_attribute_analysis(self):
        """测试属性分析功能"""
        self.stdout.write(self.style.SUCCESS('\n🤖 测试属性分析功能...'))
        
        analyzer = AttributeAnalyzer()
        
        # 测试数据
        test_cases = [
            {
                'attr_name': '材质',
                'attr_value': '实木颗粒板',
                'context': {
                    '产品描述': 'NOVO系列单门底柜',
                    '系列': 'NOVO',
                    '类型代码': 'U'
                }
            },
            {
                'attr_name': '颜色',
                'attr_value': '胡桃木色',
                'context': {
                    '产品描述': 'CLASSIC系列吊柜',
                    '系列': 'CLASSIC',
                    '类型代码': 'W'
                }
            },
            {
                'attr_name': '厚度',
                'attr_value': '18mm',
                'context': {
                    '产品描述': '现代简约风格柜体',
                    '系列': 'MODERN',
                    '类型代码': 'U'
                }
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            self.stdout.write(f'\n📋 测试用例 {i}: {test_case["attr_name"]} = {test_case["attr_value"]}')
            
            try:
                result = analyzer.analyze_single_attribute(
                    test_case['attr_name'],
                    test_case['attr_value'],
                    test_case['context']
                )
                
                if result:
                    self.stdout.write(self.style.SUCCESS('✅ 分析成功'))
                    self.stdout.write(f'  显示名称: {result["display_name"]}')
                    self.stdout.write(f'  显示值: {result["display_value"]}')
                    self.stdout.write(f'  属性类型: {result["attribute_type"]}')
                    self.stdout.write(f'  可筛选: {result["filterable"]}')
                    self.stdout.write(f'  重要程度: {result["importance"]}/5')
                    self.stdout.write(f'  置信度: {result.get("confidence", 0):.2f}')
                    
                    if result.get('source') == 'default':
                        self.stdout.write(self.style.WARNING('  ⚠️ 使用默认分析（AI不可用）'))
                    else:
                        self.stdout.write(self.style.SUCCESS('  🤖 AI分析结果'))
                else:
                    self.stdout.write(self.style.ERROR('❌ 分析失败'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ 分析异常: {str(e)}'))
        
        # 批量分析测试
        self.stdout.write(f'\n🔄 测试批量分析...')
        unknown_attributes = {
            test_case['attr_name']: test_case['attr_value'] 
            for test_case in test_cases
        }
        
        try:
            batch_results = analyzer.analyze_attributes_batch(
                unknown_attributes, 
                test_cases[0]['context']
            )
            
            self.stdout.write(self.style.SUCCESS(f'✅ 批量分析完成，处理 {len(batch_results)} 个属性'))
            
            # 显示分析摘要
            summary = analyzer.get_analysis_summary(batch_results)
            self.stdout.write(f'\n📊 分析摘要:')
            self.stdout.write(f'  总数: {summary["total"]}')
            self.stdout.write(f'  AI处理: {summary["ai_processed"]}')
            self.stdout.write(f'  默认处理: {summary["default_processed"]}')
            self.stdout.write(f'  平均置信度: {summary["average_confidence"]}')
            self.stdout.write(f'  高重要性: {summary["high_importance_count"]}')
            self.stdout.write(f'  可筛选: {summary["filterable_count"]}')
            
            # 属性类型分布
            type_dist = summary["attribute_types"]
            if type_dist:
                self.stdout.write(f'  类型分布: {", ".join([f"{k}({v})" for k, v in type_dist.items()])}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ 批量分析失败: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ 属性分析测试完成'))

    def display_ai_status(self):
        """显示AI服务状态"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('🤖 AI服务状态'))
        self.stdout.write('='*60)
        
        service = DeepSeekService()
        analyzer = AttributeAnalyzer()
        
        self.stdout.write(f'DeepSeek服务: {"✅ 可用" if service.is_available() else "❌ 不可用"}')
        self.stdout.write(f'属性分析器: {"✅ 就绪" if analyzer else "❌ 异常"}')
        self.stdout.write(f'置信度阈值: {analyzer.confidence_threshold}')
        self.stdout.write(f'使用真实AI: {analyzer.use_real_ai}')
        
        if service.is_available():
            self.stdout.write(f'API地址: {service.base_url}')
            self.stdout.write(f'模型: {service.model}')
            self.stdout.write(f'最大令牌: {service.max_tokens}')
            self.stdout.write(f'温度: {service.temperature}')
        
        self.stdout.write('='*60)
