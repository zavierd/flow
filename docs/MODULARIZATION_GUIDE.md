# Django模块化开发快速指南

本指南帮助开发者快速上手Flow项目的模块化开发规范和工具。

## 🚀 快速开始

### 1. 检查当前项目状态

```bash
# 使用make命令 (推荐)
make modular-check

# 或直接使用脚本
python3 scripts/check_modularization.py .
```

### 2. 交互式模块化 (新手推荐)

```bash
# 启动交互式工作流
make modular-interactive

# 或使用脚本
python3 scripts/modularization_workflow.py . interactive
```

### 3. 预览重构效果

```bash
# 预览模块化重构
make modular-preview

# 或使用脚本
python3 scripts/auto_modularize.py . --dry-run
```

### 4. 执行重构

```bash
# 交互式执行 (推荐)
make modular-interactive

# 批量执行
make modular-run
```

### 5. 验证结果

```bash
# 运行测试验证
make test-after-modular

# 检查Django配置
python3 manage.py check
```

## 📋 工具说明

### 检查工具 (`check_modularization.py`)

**功能**: 分析代码复杂度，识别需要模块化的文件

**使用方法**:
```bash
# 基本检查
python3 scripts/check_modularization.py .

# 生成详细报告
python3 scripts/check_modularization.py . -o report.md

# 显示详细信息
python3 scripts/check_modularization.py . -v
```

**输出示例**:
```
正在扫描Django项目: /path/to/project
基于规范: .cursor/rules/django_modular_development.mdc

=============================================================
扫描完成！
检查文件数量: 6
需要重构文件: 2
重构比例: 33.3%
预估工作量: medium

发现需要重构的文件:
  - products/models.py: 文件行数(2062)超过500行限制
  - products/admin.py: 文件行数(2889)超过500行限制
```

### 重构工具 (`auto_modularize.py`)

**功能**: 自动执行模块化重构

**使用方法**:
```bash
# 预览模式 (不修改文件)
python3 scripts/auto_modularize.py . --dry-run

# 执行重构
python3 scripts/auto_modularize.py .

# 重构指定文件
python3 scripts/auto_modularize.py . -f products/models.py products/admin.py
```

**重构过程**:
1. 自动备份原始文件到 `.modularization_backup/`
2. 分析代码结构和业务域
3. 创建模块化目录结构
4. 按业务域拆分代码
5. 生成兼容性导入文件
6. 保持向后兼容性

### 工作流管理器 (`modularization_workflow.py`)

**功能**: 集成检查、预览、重构的完整工作流

**使用方法**:
```bash
# 交互式工作流 (推荐)
python3 scripts/modularization_workflow.py . interactive

# 仅检查
python3 scripts/modularization_workflow.py . check

# 预览重构
python3 scripts/modularization_workflow.py . preview

# 批量处理
python3 scripts/modularization_workflow.py . batch

# 生成状态报告
python3 scripts/modularization_workflow.py . status
```

## 🏗️ 模块化架构

### Models模块化结构

**重构前**:
```
products/
└── models.py  (2062行)
```

**重构后**:
```
products/
├── models.py              # 兼容性导入
└── models/
    ├── __init__.py        # 统一导入入口 (50行)
    ├── base.py            # 抽象基类 (180行)
    ├── mixins.py          # 功能混入 (150行)
    ├── category_models.py # 分类模型 (120行)
    ├── brand_models.py    # 品牌模型 (80行)
    ├── attribute_models.py # 属性模型 (200行)
    ├── spu_models.py      # SPU模型 (300行)
    ├── sku_models.py      # SKU模型 (250行)
    ├── pricing_models.py  # 定价模型 (180行)
    └── import_models.py   # 导入模型 (150行)
```

### Admin模块化结构

**重构前**:
```
products/
└── admin.py  (2889行)
```

**重构后**:
```
products/
├── admin.py               # 兼容性导入
└── admin/
    ├── __init__.py        # 统一注册入口
    ├── base.py            # 基础Admin类
    ├── mixins.py          # 功能混入
    ├── filters.py         # 自定义过滤器
    ├── category_admin.py  # 分类管理
    ├── brand_admin.py     # 品牌管理
    ├── attribute_admin.py # 属性管理
    ├── spu_admin.py       # SPU管理
    ├── sku_admin.py       # SKU管理
    └── product_admin.py   # 其他产品管理
```

## 📖 最佳实践

### 1. 文件大小控制

**规则**: 单个文件不超过500行

**检查方法**:
```bash
# 检查文件行数
wc -l products/models.py

# 自动检查所有文件
make modular-check
```

### 2. 业务域分离

**原则**: 每个模块只负责一个业务域

**示例**:
- `category_models.py` - 仅包含分类相关模型
- `brand_models.py` - 仅包含品牌相关模型
- `spu_models.py` - 仅包含SPU相关模型

### 3. 代码复用

**使用抽象基类**:
```python
# models/base.py
class BaseModel(TimestampedModel, ActiveModel):
    class Meta:
        abstract = True
```

**使用混入类**:
```python
# models/mixins.py
class TreeMixin(models.Model):
    parent = models.ForeignKey('self', ...)
    level = models.PositiveIntegerField(...)
    
    class Meta:
        abstract = True
```

### 4. 向后兼容性

**兼容性导入**:
```python
# models.py (重构后)
"""
兼容性导入文件
原始models.py已备份为models_original_backup.py
"""
from .models import *
```

## 🔧 开发工作流

### 新功能开发

1. **检查复杂度**:
```bash
make modular-check
```

2. **开发功能**:
   - 遵循模块化规范
   - 单个文件不超过500行
   - 使用基础类和混入类

3. **重构检查**:
```bash
# 如果文件过大，及时重构
make modular-interactive
```

4. **测试验证**:
```bash
make test-after-modular
```

### 重构现有代码

1. **状态分析**:
```bash
make modular-status
```

2. **交互式重构**:
```bash
make modular-interactive
```

3. **验证结果**:
```bash
make test-after-modular
```

4. **提交代码**:
```bash
make git-commit-modular
```

## 🐛 常见问题

### Q: 重构后导入报错怎么办？

**A**: 检查兼容性导入文件是否正确生成

```bash
# 检查导入文件
cat products/models.py

# 确保包含
from .models import *
```

### Q: 如何撤销重构？

**A**: 使用备份文件恢复

```bash
# 查找备份文件
ls .modularization_backup/

# 恢复原始文件
cp .modularization_backup/models_20241201_143022.py products/models.py
```

### Q: 重构后Admin界面异常？

**A**: 检查Admin注册是否正确

```bash
# 检查Django配置
python3 manage.py check

# 检查Admin注册
cat products/admin/__init__.py
```

### Q: 如何自定义业务域？

**A**: 修改脚本中的业务域映射

编辑 `scripts/auto_modularize.py` 中的 `_extract_business_domain` 方法。

## 📚 参考资料

- **[Django模块化开发规范](.cursor/rules/django_modular_development.mdc)** - 完整规范文档
- **[Flow项目特定规范](.cursor/rules/flow_project_standards.mdc)** - 项目特定要求
- **[调试优先级规则](.cursor/rules/debugging_priority.mdc)** - 问题排查指南

## 🎯 下一步

1. **运行检查**: `make modular-check`
2. **交互式重构**: `make modular-interactive`
3. **学习规范**: 阅读 `.cursor/rules/` 目录下的文档
4. **持续改进**: 定期运行复杂度检查

---

💡 **提示**: 建议先在测试环境进行重构，验证无误后再应用到生产环境。 