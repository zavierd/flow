# Django项目模块化工作流 Makefile
# 基于 .cursor/rules/django_modular_development.mdc 规范

.PHONY: help modular-check modular-preview modular-run modular-status modular-interactive test-after-modular

# 默认目标
help:
	@echo "Django项目模块化工作流命令"
	@echo "基于 .cursor/rules/django_modular_development.mdc 规范"
	@echo ""
	@echo "可用命令:"
	@echo "  modular-check       - 检查项目模块化复杂度"
	@echo "  modular-preview     - 预览模块化重构效果"
	@echo "  modular-run         - 执行模块化重构"
	@echo "  modular-interactive - 交互式模块化工作流 (推荐)"
	@echo "  modular-status      - 生成模块化状态报告"
	@echo "  test-after-modular  - 模块化后运行测试验证"
	@echo "  setup-scripts       - 设置脚本执行权限"
	@echo ""
	@echo "示例:"
	@echo "  make modular-interactive  # 开始交互式模块化流程"
	@echo "  make modular-check        # 快速检查当前状态"
	@echo "  make modular-preview      # 预览重构效果"

# 设置脚本执行权限
setup-scripts:
	@echo "🔧 设置模块化脚本执行权限..."
	@chmod +x scripts/check_modularization.py
	@chmod +x scripts/auto_modularize.py
	@chmod +x scripts/modularization_workflow.py
	@echo "✅ 脚本权限设置完成"

# 检查模块化复杂度
modular-check: setup-scripts
	@echo "🔍 检查Django项目模块化复杂度..."
	@python scripts/check_modularization.py .
	@echo ""
	@echo "💡 如需详细报告，运行: make modular-status"

# 预览模块化重构
modular-preview: setup-scripts
	@echo "👀 预览模块化重构效果..."
	@python scripts/auto_modularize.py . --dry-run
	@echo ""
	@echo "💡 如需执行重构，运行: make modular-run"

# 执行模块化重构
modular-run: setup-scripts
	@echo "⚠️  即将执行模块化重构，这将修改您的代码文件"
	@echo "建议先运行 'make modular-preview' 预览效果"
	@read -p "确定继续吗? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo ""; \
		echo "🔧 执行模块化重构..."; \
		python scripts/auto_modularize.py .; \
		echo ""; \
		echo "✅ 重构完成，建议运行: make test-after-modular"; \
	else \
		echo ""; \
		echo "❌ 重构已取消"; \
	fi

# 交互式模块化工作流 (推荐)
modular-interactive: setup-scripts
	@echo "🚀 启动交互式模块化工作流..."
	@python scripts/modularization_workflow.py . interactive

# 生成详细状态报告
modular-status: setup-scripts
	@echo "📊 生成模块化状态报告..."
	@python scripts/check_modularization.py . -o modularization_status.md
	@echo "✅ 报告已保存到: modularization_status.md"

# 模块化后测试验证
test-after-modular:
	@echo "🧪 运行测试验证模块化效果..."
	@echo "检查Django配置..."
	@python manage.py check
	@echo "运行数据库迁移检查..."
	@python manage.py makemigrations --dry-run
	@echo "运行单元测试..."
	@python manage.py test --verbosity=2
	@echo "✅ 测试验证完成"

# 清理模块化过程产生的文件
modular-clean:
	@echo "🧹 清理模块化相关文件..."
	@rm -f modularization_status.md
	@rm -f modularization_report.md
	@if [ -d .modularization_backup ]; then \
		echo "发现备份目录: .modularization_backup"; \
		read -p "是否删除备份目录? [y/N] " -n 1 -r; \
		if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
			rm -rf .modularization_backup; \
			echo ""; \
			echo "✅ 备份目录已删除"; \
		else \
			echo ""; \
			echo "💾 备份目录保留"; \
		fi \
	fi

# 快速检查+预览流程
modular-quick-check: modular-check modular-preview
	@echo ""
	@echo "🎯 快速检查完成，可运行以下命令:"
	@echo "  make modular-interactive  # 交互式模块化"
	@echo "  make modular-run          # 直接执行重构"

# 完整工作流
modular-full-workflow: modular-check modular-preview modular-run test-after-modular
	@echo "🎉 完整模块化工作流执行完成！"

# 项目特定命令 - 检查products应用
check-products:
	@echo "🔍 检查products应用模块化状态..."
	@if [ -f products/models.py ]; then \
		echo "📄 检查products/models.py"; \
		wc -l products/models.py; \
	fi
	@if [ -f products/admin.py ]; then \
		echo "📄 检查products/admin.py"; \
		wc -l products/admin.py; \
	fi
	@if [ -d products/models ]; then \
		echo "📁 products/models/ 目录已存在"; \
		ls -la products/models/; \
	fi
	@if [ -d products/admin ]; then \
		echo "📁 products/admin/ 目录已存在"; \
		ls -la products/admin/; \
	fi

# 开发辅助命令
dev-server: test-after-modular
	@echo "🚀 启动开发服务器..."
	@python manage.py runserver

# Git相关命令
git-commit-modular:
	@echo "📝 提交模块化变更..."
	@git add .
	@git status
	@echo ""
	@read -p "输入提交信息 (默认: refactor: 模块化Django组件，提升代码可维护性): " commit_msg; \
	commit_msg=$${commit_msg:-"refactor: 模块化Django组件，提升代码可维护性"}; \
	git commit -m "$$commit_msg"
	@echo "✅ 变更已提交"

# 显示模块化规范
show-rules:
	@echo "📖 Django模块化开发规范"
	@echo "位置: .cursor/rules/django_modular_development.mdc"
	@echo ""
	@if [ -f .cursor/rules/django_modular_development.mdc ]; then \
		head -20 .cursor/rules/django_modular_development.mdc; \
		echo "..."; \
		echo "完整内容请查看文件"; \
	else \
		echo "❌ 规范文件不存在"; \
	fi

# 检查模块化工具依赖
check-tools:
	@echo "🔧 检查模块化工具依赖..."
	@echo "Python版本:"
	@python3 --version 2>/dev/null || python --version 2>/dev/null || echo "Python未安装"
	@echo ""
	@echo "Django版本:"
	@python3 -c "import django; print(django.get_version())" 2>/dev/null || python -c "import django; print(django.get_version())" 2>/dev/null || echo "Django未安装"
	@echo ""
	@echo "必需脚本检查:"
	@for script in check_modularization.py auto_modularize.py modularization_workflow.py; do \
		if [ -f scripts/$$script ]; then \
			echo "✅ scripts/$$script"; \
		else \
			echo "❌ scripts/$$script (缺失)"; \
		fi \
	done
	@echo ""
	@echo "规范文件检查:"
	@if [ -f .cursor/rules/django_modular_development.mdc ]; then \
		echo "✅ .cursor/rules/django_modular_development.mdc"; \
	else \
		echo "❌ .cursor/rules/django_modular_development.mdc (缺失)"; \
	fi 