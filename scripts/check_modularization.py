#!/usr/bin/env python3
"""
Django项目模块化检查脚本

基于.cursor/rules/django_modular_development.mdc规范
自动检测需要模块化的文件并提供重构建议
"""

import os
import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple, Optional


class ModularizationChecker:
    """模块化检查器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.report = defaultdict(list)
        
    def check_file_complexity(self, file_path: Path) -> Tuple[bool, str, Dict]:
        """检查文件是否需要模块化"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            return False, f"无法读取文件: {e}", {}
        
        line_count = len(lines)
        content = ''.join(lines)
        
        # 分析文件结构
        analysis = self._analyze_file_structure(content, file_path)
        
        # 检查行数
        if line_count > 500:
            return True, f"文件行数({line_count})超过500行限制", analysis
        
        # 检查类数量
        if analysis['class_count'] > 10:
            return True, f"类数量({analysis['class_count']})过多，建议拆分", analysis
        
        # 检查业务域混合
        if len(analysis['business_domains']) > 3:
            return True, f"包含多个业务域({len(analysis['business_domains'])})，建议拆分", analysis
        
        # 检查复杂度指标
        complexity_score = self._calculate_complexity_score(analysis)
        if complexity_score > 7:
            return True, f"复杂度分数({complexity_score})过高，建议拆分", analysis
            
        return False, "文件复杂度正常", analysis
    
    def _analyze_file_structure(self, content: str, file_path: Path) -> Dict:
        """分析文件结构"""
        analysis = {
            'class_count': 0,
            'function_count': 0,
            'import_count': 0,
            'business_domains': set(),
            'model_classes': [],
            'admin_classes': [],
            'view_classes': [],
            'complexity_indicators': [],
            'file_type': self._determine_file_type(file_path),
        }
        
        # 统计类和函数
        class_pattern = r'^class\s+(\w+).*?:'
        function_pattern = r'^def\s+(\w+)'
        import_pattern = r'^(?:from|import)\s+'
        
        for line in content.split('\n'):
            line = line.strip()
            
            # 统计类
            class_match = re.match(class_pattern, line)
            if class_match:
                class_name = class_match.group(1)
                analysis['class_count'] += 1
                
                # 识别业务域
                domain = self._extract_business_domain(class_name)
                if domain:
                    analysis['business_domains'].add(domain)
                
                # 分类不同类型的类
                if 'models' in str(file_path):
                    if 'Admin' not in class_name:
                        analysis['model_classes'].append(class_name)
                elif 'admin' in str(file_path):
                    analysis['admin_classes'].append(class_name)
                elif 'view' in str(file_path):
                    analysis['view_classes'].append(class_name)
            
            # 统计函数
            if re.match(function_pattern, line):
                analysis['function_count'] += 1
            
            # 统计导入
            if re.match(import_pattern, line):
                analysis['import_count'] += 1
        
        # 检查复杂度指标
        analysis['complexity_indicators'] = self._find_complexity_indicators(content)
        
        return analysis
    
    def _determine_file_type(self, file_path: Path) -> str:
        """确定文件类型"""
        path_str = str(file_path).lower()
        if 'models' in path_str:
            return 'models'
        elif 'admin' in path_str:
            return 'admin'
        elif 'view' in path_str:
            return 'views'
        elif 'serializer' in path_str:
            return 'serializers'
        else:
            return 'unknown'
    
    def _extract_business_domain(self, class_name: str) -> Optional[str]:
        """从类名提取业务域"""
        # 常见的业务域关键词
        domains = {
            'category': 'Category',
            'brand': 'Brand', 
            'product': 'Product',
            'sku': 'SKU',
            'spu': 'SPU',
            'attribute': 'Attribute',
            'price': 'Pricing',
            'pricing': 'Pricing',
            'dimension': 'Dimension',
            'import': 'Import',
            'export': 'Export',
            'user': 'User',
            'order': 'Order',
            'payment': 'Payment',
            'inventory': 'Inventory',
            'stock': 'Stock',
        }
        
        class_lower = class_name.lower()
        for keyword, domain in domains.items():
            if keyword in class_lower:
                return domain
        
        return None
    
    def _find_complexity_indicators(self, content: str) -> List[str]:
        """查找复杂度指标"""
        indicators = []
        
        # 检查长方法
        method_pattern = r'def\s+\w+.*?:\s*\n(.*?)(?=\n\s*def|\n\s*class|\Z)'
        methods = re.findall(method_pattern, content, re.DOTALL)
        for method in methods:
            if len(method.split('\n')) > 20:
                indicators.append('存在过长方法(>20行)')
                break
        
        # 检查深度嵌套
        if re.search(r'\s{16,}', content):  # 4层以上缩进
            indicators.append('存在深度嵌套(>4层)')
        
        # 检查过多字段
        field_count = len(re.findall(r'\w+\s*=\s*models\.\w+Field', content))
        if field_count > 15:
            indicators.append(f'模型字段过多({field_count}个)')
        
        # 检查重复代码模式
        common_patterns = [
            r'list_display\s*=',
            r'list_filter\s*=',
            r'search_fields\s*=',
            r'verbose_name\s*=',
        ]
        
        pattern_counts = {}
        for pattern in common_patterns:
            count = len(re.findall(pattern, content))
            if count > 5:
                pattern_counts[pattern] = count
        
        if pattern_counts:
            indicators.append('存在重复代码模式')
        
        return indicators
    
    def _calculate_complexity_score(self, analysis: Dict) -> int:
        """计算复杂度分数(1-10)"""
        score = 0
        
        # 基于行数
        if analysis.get('line_count', 0) > 1000:
            score += 3
        elif analysis.get('line_count', 0) > 500:
            score += 2
        
        # 基于类数量
        if analysis['class_count'] > 15:
            score += 3
        elif analysis['class_count'] > 10:
            score += 2
        elif analysis['class_count'] > 5:
            score += 1
        
        # 基于业务域数量
        domain_count = len(analysis['business_domains'])
        if domain_count > 5:
            score += 2
        elif domain_count > 3:
            score += 1
        
        # 基于复杂度指标
        score += len(analysis['complexity_indicators'])
        
        return min(score, 10)
    
    def generate_modularization_plan(self, file_path: Path, analysis: Dict) -> Dict:
        """生成模块化方案"""
        plan = {
            'file_path': str(file_path),
            'file_type': analysis['file_type'],
            'recommended_structure': {},
            'migration_steps': [],
            'estimated_effort': 'medium',
        }
        
        # 根据文件类型生成不同的方案
        if analysis['file_type'] == 'models':
            plan.update(self._generate_models_plan(file_path, analysis))
        elif analysis['file_type'] == 'admin':
            plan.update(self._generate_admin_plan(file_path, analysis))
        elif analysis['file_type'] == 'views':
            plan.update(self._generate_views_plan(file_path, analysis))
        
        return plan
    
    def _generate_models_plan(self, file_path: Path, analysis: Dict) -> Dict:
        """生成models模块化方案"""
        app_name = file_path.parent.name
        base_dir = file_path.parent / 'models'
        
        # 按业务域分组模型
        domain_groups = defaultdict(list)
        for model_class in analysis['model_classes']:
            domain = self._extract_business_domain(model_class)
            if domain:
                domain_groups[domain].append(model_class)
            else:
                domain_groups['misc'].append(model_class)
        
        recommended_structure = {
            '__init__.py': '统一导入入口',
            'base.py': '抽象基类和公共配置',
            'mixins.py': '可复用混入类',
            'managers.py': '自定义管理器',
        }
        
        # 为每个业务域创建文件
        for domain, models in domain_groups.items():
            if domain != 'misc':
                filename = f"{domain.lower()}_models.py"
                recommended_structure[filename] = f"{domain}业务域模型: {', '.join(models)}"
        
        if domain_groups['misc']:
            recommended_structure['misc_models.py'] = f"其他模型: {', '.join(domain_groups['misc'])}"
        
        migration_steps = [
            "1. 备份原始models.py文件",
            "2. 创建models/目录结构",
            "3. 创建base.py和mixins.py基础组件",
            "4. 按业务域迁移模型到对应文件",
            "5. 更新__init__.py统一导入",
            "6. 替换原models.py为兼容性导入",
            "7. 运行测试验证功能完整性",
        ]
        
        return {
            'recommended_structure': recommended_structure,
            'migration_steps': migration_steps,
            'estimated_effort': 'high' if len(analysis['model_classes']) > 15 else 'medium',
        }
    
    def _generate_admin_plan(self, file_path: Path, analysis: Dict) -> Dict:
        """生成admin模块化方案"""
        app_name = file_path.parent.name
        base_dir = file_path.parent / 'admin'
        
        # 按业务域分组Admin类
        domain_groups = defaultdict(list)
        for admin_class in analysis['admin_classes']:
            # 去掉Admin后缀获取模型名
            model_name = admin_class.replace('Admin', '')
            domain = self._extract_business_domain(model_name)
            if domain:
                domain_groups[domain].append(admin_class)
            else:
                domain_groups['misc'].append(admin_class)
        
        recommended_structure = {
            '__init__.py': '统一注册入口',
            'base.py': '基础Admin类和配置',
            'mixins.py': '可复用功能混入',
            'filters.py': '自定义过滤器',
        }
        
        # 为每个业务域创建文件
        for domain, admins in domain_groups.items():
            if domain != 'misc':
                filename = f"{domain.lower()}_admin.py"
                recommended_structure[filename] = f"{domain}业务域Admin: {', '.join(admins)}"
        
        if domain_groups['misc']:
            recommended_structure['misc_admin.py'] = f"其他Admin: {', '.join(domain_groups['misc'])}"
        
        migration_steps = [
            "1. 备份原始admin.py文件",
            "2. 创建admin/目录结构", 
            "3. 创建base.py和mixins.py基础组件",
            "4. 按业务域迁移Admin类到对应文件",
            "5. 更新__init__.py统一注册",
            "6. 替换原admin.py为兼容性导入",
            "7. 验证Admin界面功能正常",
        ]
        
        return {
            'recommended_structure': recommended_structure,
            'migration_steps': migration_steps,
            'estimated_effort': 'medium' if len(analysis['admin_classes']) > 10 else 'low',
        }
    
    def _generate_views_plan(self, file_path: Path, analysis: Dict) -> Dict:
        """生成views模块化方案"""
        # Views模块化方案（简化版）
        recommended_structure = {
            '__init__.py': '统一导入入口',
            'base.py': '基础视图类',
            'mixins.py': '视图混入类',
        }
        
        migration_steps = [
            "1. 分析现有视图功能",
            "2. 按功能域重组视图类",
            "3. 创建views/目录结构",
            "4. 迁移视图到对应模块",
        ]
        
        return {
            'recommended_structure': recommended_structure,
            'migration_steps': migration_steps,
            'estimated_effort': 'medium',
        }
    
    def scan_project(self) -> Dict:
        """扫描整个项目"""
        results = {
            'files_checked': 0,
            'files_need_refactor': 0,
            'recommendations': [],
            'summary': {},
        }
        
        # 查找Django应用目录
        for app_dir in self.project_root.iterdir():
            if not app_dir.is_dir() or app_dir.name.startswith('.'):
                continue
            
            # 检查是否是Django应用（包含models.py或admin.py）
            models_file = app_dir / 'models.py'
            admin_file = app_dir / 'admin.py'
            views_file = app_dir / 'views.py'
            
            for file_path in [models_file, admin_file, views_file]:
                if file_path.exists():
                    results['files_checked'] += 1
                    
                    needs_refactor, reason, analysis = self.check_file_complexity(file_path)
                    
                    if needs_refactor:
                        results['files_need_refactor'] += 1
                        plan = self.generate_modularization_plan(file_path, analysis)
                        
                        recommendation = {
                            'file_path': str(file_path),
                            'reason': reason,
                            'analysis': analysis,
                            'plan': plan,
                        }
                        results['recommendations'].append(recommendation)
        
        # 生成摘要
        results['summary'] = self._generate_summary(results)
        
        return results
    
    def _generate_summary(self, results: Dict) -> Dict:
        """生成扫描摘要"""
        summary = {
            'total_files': results['files_checked'],
            'files_need_refactor': results['files_need_refactor'],
            'refactor_rate': 0,
            'file_types': defaultdict(int),
            'business_domains': set(),
            'estimated_total_effort': 'low',
        }
        
        if results['files_checked'] > 0:
            summary['refactor_rate'] = results['files_need_refactor'] / results['files_checked'] * 100
        
        effort_scores = {'low': 1, 'medium': 2, 'high': 3}
        total_effort_score = 0
        
        for rec in results['recommendations']:
            file_type = rec['analysis']['file_type']
            summary['file_types'][file_type] += 1
            
            domains = rec['analysis']['business_domains']
            summary['business_domains'].update(domains)
            
            effort = rec['plan']['estimated_effort']
            total_effort_score += effort_scores.get(effort, 1)
        
        # 计算总体工作量
        if total_effort_score > 6:
            summary['estimated_total_effort'] = 'high'
        elif total_effort_score > 3:
            summary['estimated_total_effort'] = 'medium'
        
        summary['business_domains'] = list(summary['business_domains'])
        
        return summary
    
    def generate_report(self, results: Dict, output_file: Optional[str] = None) -> str:
        """生成检查报告"""
        report_lines = [
            "# Django项目模块化检查报告",
            "",
            f"扫描时间: {self._get_current_time()}",
            f"项目路径: {self.project_root}",
            "",
            "## 扫描摘要",
            "",
            f"- 检查文件数量: {results['summary']['total_files']}",
            f"- 需要重构文件: {results['summary']['files_need_refactor']}",
            f"- 重构比例: {results['summary']['refactor_rate']:.1f}%",
            f"- 预估总工作量: {results['summary']['estimated_total_effort']}",
            "",
            "### 文件类型分布",
        ]
        
        for file_type, count in results['summary']['file_types'].items():
            report_lines.append(f"- {file_type}: {count}个文件")
        
        report_lines.extend([
            "",
            "### 业务域分布",
        ])
        
        for domain in results['summary']['business_domains']:
            report_lines.append(f"- {domain}")
        
        if results['recommendations']:
            report_lines.extend([
                "",
                "## 详细建议",
                "",
            ])
            
            for i, rec in enumerate(results['recommendations'], 1):
                report_lines.extend([
                    f"### {i}. {rec['file_path']}",
                    "",
                    f"**问题**: {rec['reason']}",
                    "",
                    "**分析结果**:",
                    f"- 类数量: {rec['analysis']['class_count']}",
                    f"- 函数数量: {rec['analysis']['function_count']}",
                    f"- 业务域: {', '.join(rec['analysis']['business_domains']) if rec['analysis']['business_domains'] else '未识别'}",
                    f"- 文件类型: {rec['analysis']['file_type']}",
                    "",
                    "**建议的模块结构**:",
                ])
                
                for filename, description in rec['plan']['recommended_structure'].items():
                    report_lines.append(f"- `{filename}`: {description}")
                
                report_lines.extend([
                    "",
                    "**迁移步骤**:",
                ])
                
                for step in rec['plan']['migration_steps']:
                    report_lines.append(f"- {step}")
                
                report_lines.extend([
                    "",
                    f"**预估工作量**: {rec['plan']['estimated_effort']}",
                    "",
                ])
        else:
            report_lines.extend([
                "",
                "## 🎉 恭喜！",
                "",
                "所有检查的文件都符合模块化规范，无需重构。",
                "",
            ])
        
        report_lines.extend([
            "",
            "---",
            "",
            "本报告基于 `.cursor/rules/django_modular_development.mdc` 规范生成",
            "",
        ])
        
        report_content = '\n'.join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"报告已保存到: {output_file}")
        
        return report_content
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    parser = argparse.ArgumentParser(description='Django项目模块化检查工具')
    parser.add_argument('project_path', nargs='?', default='.', 
                       help='Django项目根目录路径 (默认: 当前目录)')
    parser.add_argument('-o', '--output', 
                       help='报告输出文件路径')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='显示详细信息')
    
    args = parser.parse_args()
    
    project_path = Path(args.project_path).resolve()
    
    if not project_path.exists():
        print(f"错误: 项目路径不存在: {project_path}")
        sys.exit(1)
    
    print(f"正在扫描Django项目: {project_path}")
    print("基于规范: .cursor/rules/django_modular_development.mdc")
    print()
    
    checker = ModularizationChecker(project_path)
    results = checker.scan_project()
    
    # 生成报告
    output_file = args.output
    if not output_file and results['files_need_refactor'] > 0:
        output_file = project_path / 'modularization_report.md'
    
    report = checker.generate_report(results, output_file)
    
    # 显示结果
    print("=" * 60)
    print("扫描完成！")
    print(f"检查文件数量: {results['summary']['total_files']}")
    print(f"需要重构文件: {results['summary']['files_need_refactor']}")
    
    if results['files_need_refactor'] > 0:
        print(f"重构比例: {results['summary']['refactor_rate']:.1f}%")
        print(f"预估工作量: {results['summary']['estimated_total_effort']}")
        print()
        print("发现需要重构的文件:")
        for rec in results['recommendations']:
            print(f"  - {rec['file_path']}: {rec['reason']}")
    else:
        print("🎉 所有文件都符合模块化规范！")
    
    if args.verbose and not output_file:
        print()
        print("详细报告:")
        print("-" * 40)
        print(report)


if __name__ == '__main__':
    main() 