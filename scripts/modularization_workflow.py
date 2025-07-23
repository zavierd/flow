#!/usr/bin/env python3
"""
Django模块化工作流脚本

集成检查、分析和自动重构功能的一站式工具
基于.cursor/rules/django_modular_development.mdc规范
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Optional


class ModularizationWorkflow:
    """模块化工作流管理器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.scripts_dir = self.project_root / 'scripts'
        
    def check_dependencies(self) -> bool:
        """检查依赖脚本是否存在"""
        required_scripts = [
            'check_modularization.py',
            'auto_modularize.py'
        ]
        
        missing_scripts = []
        for script in required_scripts:
            script_path = self.scripts_dir / script
            if not script_path.exists():
                missing_scripts.append(script)
        
        if missing_scripts:
            print(f"❌ 缺少必需的脚本: {', '.join(missing_scripts)}")
            print(f"请确保以下脚本存在于 {self.scripts_dir} 目录:")
            for script in missing_scripts:
                print(f"  - {script}")
            return False
        
        return True
    
    def run_complexity_check(self, output_file: Optional[str] = None) -> Dict:
        """运行复杂度检查"""
        print("🔍 运行复杂度检查...")
        
        cmd = [sys.executable, str(self.scripts_dir / 'check_modularization.py'), str(self.project_root)]
        if output_file:
            cmd.extend(['-o', output_file])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✅ 复杂度检查完成")
                print(result.stdout)
                
                # 解析输出获取结果
                lines = result.stdout.split('\n')
                files_checked = 0
                files_need_refactor = 0
                
                for line in lines:
                    if "检查文件数量:" in line:
                        files_checked = int(line.split(':')[1].strip())
                    elif "需要重构文件:" in line:
                        files_need_refactor = int(line.split(':')[1].strip())
                
                return {
                    'success': True,
                    'files_checked': files_checked,
                    'files_need_refactor': files_need_refactor,
                    'output': result.stdout
                }
            else:
                print(f"❌ 复杂度检查失败: {result.stderr}")
                return {'success': False, 'error': result.stderr}
                
        except Exception as e:
            print(f"❌ 运行复杂度检查时出错: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_auto_modularize(self, files: Optional[List[str]] = None, dry_run: bool = False) -> Dict:
        """运行自动模块化"""
        action = "预览模块化" if dry_run else "执行模块化"
        print(f"🔧 {action}...")
        
        cmd = [sys.executable, str(self.scripts_dir / 'auto_modularize.py'), str(self.project_root)]
        
        if files:
            cmd.extend(['-f'] + files)
        
        if dry_run:
            cmd.append('--dry-run')
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print(f"✅ {action}完成")
                print(result.stdout)
                return {
                    'success': True,
                    'output': result.stdout
                }
            else:
                print(f"❌ {action}失败: {result.stderr}")
                return {'success': False, 'error': result.stderr}
                
        except Exception as e:
            print(f"❌ 运行{action}时出错: {e}")
            return {'success': False, 'error': str(e)}
    
    def interactive_workflow(self):
        """交互式工作流"""
        print("🚀 Django模块化工作流")
        print("基于 .cursor/rules/django_modular_development.mdc 规范")
        print("=" * 60)
        
        # 1. 检查依赖
        if not self.check_dependencies():
            return
        
        # 2. 运行复杂度检查
        print("\n步骤 1: 复杂度分析")
        print("-" * 30)
        
        check_result = self.run_complexity_check()
        if not check_result['success']:
            print("复杂度检查失败，无法继续")
            return
        
        files_need_refactor = check_result.get('files_need_refactor', 0)
        
        if files_need_refactor == 0:
            print("\n🎉 所有文件都符合模块化规范，无需重构！")
            return
        
        # 3. 询问是否继续
        print(f"\n发现 {files_need_refactor} 个文件需要重构")
        
        while True:
            choice = input("\n请选择操作:\n1. 预览重构 (推荐)\n2. 执行重构\n3. 退出\n请输入选择 (1-3): ").strip()
            
            if choice == '1':
                print("\n步骤 2: 预览重构")
                print("-" * 30)
                self.run_auto_modularize(dry_run=True)
                
                continue_choice = input("\n是否执行实际重构? (y/N): ").strip().lower()
                if continue_choice in ['y', 'yes']:
                    print("\n步骤 3: 执行重构")
                    print("-" * 30)
                    refactor_result = self.run_auto_modularize(dry_run=False)
                    
                    if refactor_result['success']:
                        print("\n🎉 模块化重构完成！")
                        self.show_next_steps()
                    break
                else:
                    print("重构已取消")
                    break
                    
            elif choice == '2':
                confirm = input("⚠️  确定要直接执行重构吗? 建议先预览 (y/N): ").strip().lower()
                if confirm in ['y', 'yes']:
                    print("\n步骤 2: 执行重构")
                    print("-" * 30)
                    refactor_result = self.run_auto_modularize(dry_run=False)
                    
                    if refactor_result['success']:
                        print("\n🎉 模块化重构完成！")
                        self.show_next_steps()
                    break
                else:
                    continue
                    
            elif choice == '3':
                print("退出工作流")
                break
                
            else:
                print("无效选择，请重新输入")
    
    def show_next_steps(self):
        """显示后续步骤"""
        print("\n📋 后续步骤建议:")
        print("1. 运行测试确保功能正常:")
        print("   python manage.py test")
        print("\n2. 检查Django Admin界面:")
        print("   python manage.py runserver")
        print("\n3. 提交代码变更:")
        print("   git add .")
        print("   git commit -m 'refactor: 模块化Django组件，提升代码可维护性'")
        print("\n4. 定期运行复杂度检查:")
        print("   python scripts/check_modularization.py")
        print("\n5. 参考规范文档:")
        print("   .cursor/rules/django_modular_development.mdc")
    
    def batch_workflow(self, files: Optional[List[str]] = None, force: bool = False):
        """批量处理工作流"""
        print("🔄 批量模块化工作流")
        print("=" * 40)
        
        # 检查依赖
        if not self.check_dependencies():
            return
        
        # 运行检查
        check_result = self.run_complexity_check()
        if not check_result['success']:
            print("复杂度检查失败，终止批量处理")
            return
        
        files_need_refactor = check_result.get('files_need_refactor', 0)
        
        if files_need_refactor == 0:
            print("🎉 所有文件都符合规范，无需处理")
            return
        
        # 执行重构
        if not force:
            print("⚠️  批量模式将直接修改文件，建议先运行交互模式预览")
            confirm = input("确定继续吗? (y/N): ").strip().lower()
            if confirm not in ['y', 'yes']:
                print("批量处理已取消")
                return
        
        refactor_result = self.run_auto_modularize(files=files, dry_run=False)
        
        if refactor_result['success']:
            print("\n🎉 批量模块化完成！")
            self.show_next_steps()
        else:
            print("批量处理失败")
    
    def generate_status_report(self, output_file: Optional[str] = None) -> bool:
        """生成状态报告"""
        print("📊 生成模块化状态报告...")
        
        # 生成详细报告
        report_file = output_file or str(self.project_root / 'modularization_status.md')
        check_result = self.run_complexity_check(output_file=report_file)
        
        if check_result['success']:
            print(f"✅ 状态报告已保存到: {report_file}")
            return True
        else:
            print("生成状态报告失败")
            return False


def main():
    parser = argparse.ArgumentParser(description='Django模块化工作流管理器')
    parser.add_argument('project_path', nargs='?', default='.', 
                       help='Django项目根目录路径 (默认: 当前目录)')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 交互式工作流
    interactive_parser = subparsers.add_parser('interactive', help='交互式模块化工作流')
    
    # 检查命令
    check_parser = subparsers.add_parser('check', help='仅运行复杂度检查')
    check_parser.add_argument('-o', '--output', help='报告输出文件')
    
    # 批量处理命令
    batch_parser = subparsers.add_parser('batch', help='批量模块化处理')
    batch_parser.add_argument('-f', '--files', nargs='+', help='指定要处理的文件')
    batch_parser.add_argument('--force', action='store_true', help='跳过确认提示')
    
    # 预览命令
    preview_parser = subparsers.add_parser('preview', help='预览模块化效果')
    preview_parser.add_argument('-f', '--files', nargs='+', help='指定要预览的文件')
    
    # 状态报告命令
    status_parser = subparsers.add_parser('status', help='生成模块化状态报告')
    status_parser.add_argument('-o', '--output', help='报告输出文件')
    
    args = parser.parse_args()
    
    project_path = Path(args.project_path).resolve()
    
    if not project_path.exists():
        print(f"错误: 项目路径不存在: {project_path}")
        sys.exit(1)
    
    workflow = ModularizationWorkflow(project_path)
    
    try:
        if args.command == 'interactive' or args.command is None:
            workflow.interactive_workflow()
        elif args.command == 'check':
            workflow.run_complexity_check(output_file=args.output)
        elif args.command == 'batch':
            workflow.batch_workflow(files=args.files, force=args.force)
        elif args.command == 'preview':
            workflow.run_auto_modularize(files=args.files, dry_run=True)
        elif args.command == 'status':
            workflow.generate_status_report(output_file=args.output)
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n操作被用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 