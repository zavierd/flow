# 🏠 整木定制产品库管理系统

一套专为整木定制行业设计的产品数据管理平台，帮助企业高效管理产品分类、品牌、属性、SKU/SPU 等核心业务数据。

## ✨ 系统特色

- **📂 无限级分类管理** - 支持树状结构展示和拖拽排序
- **🏷️ 完整品牌管理** - Logo、联系人、关联统计
- **🔧 灵活属性系统** - 8种属性类型，支持动态配置
- **📦 SPU/SKU管理** - SPU产品单元和库存单元完整管理
- **👥 多角色权限** - 系统管理员、产品专员、销售设计师
- **🚀 现代化界面** - 响应式设计，专业管理面板
- **⚡ REST API** - 完整的 API 接口支持
- **🔧 模块化架构** - 基于最佳实践的代码组织结构

## 🚀 快速开始

### 环境要求
- Docker 和 Docker Compose
- Python 3.12+
- PostgreSQL 12+

### 启动系统
```bash
# 1. 克隆项目
git clone [repository-url]
cd Flow

# 2. 启动服务
docker-compose up -d

# 3. 数据库迁移
python3 manage.py migrate

# 4. 创建管理员
python3 manage.py createsuperuser

# 5. 启动开发服务器
python3 manage.py runserver
```

### 访问系统
- **管理后台**: http://localhost:8000
- **API 接口**: http://localhost:8000/api/
- **健康检查**: http://localhost:8000/health/

## 🛠️ 开发工具

### Django模块化工作流
项目采用模块化架构设计，提供了完整的模块化工具链：

```bash
# 快速检查项目模块化状态
make modular-check

# 交互式模块化工作流 (推荐新用户)
make modular-interactive

# 预览模块化重构效果
make modular-preview

# 生成详细状态报告
make modular-status

# 查看所有可用命令
make help
```

### 模块化工具说明
- **检查工具** (`scripts/check_modularization.py`) - 分析代码复杂度和模块化建议
- **重构工具** (`scripts/auto_modularize.py`) - 自动执行模块化重构
- **工作流管理** (`scripts/modularization_workflow.py`) - 集成工作流管理
- **规范文档** (`.cursor/rules/django_modular_development.mdc`) - 模块化开发规范

## 📚 文档指南

### 🆕 新手用户
如果您是第一次使用系统，建议按以下顺序阅读：

1. **[开发规范总览](.cursor/rules/README.mdc)** - 了解项目的开发规范体系
2. **[Django模块化开发规范](.cursor/rules/django_modular_development.mdc)** - 学习模块化最佳实践
3. **[Flow项目特定规范](.cursor/rules/flow_project_standards.mdc)** - 了解项目特定要求
4. **[调试优先级规则](.cursor/rules/debugging_priority.mdc)** - 掌握问题排查方法

### 🔧 开发者指南

#### 代码组织规范
项目遵循严格的模块化开发规范：

- **文件大小限制**: 单个文件不超过500行
- **单一职责原则**: 每个模块专注一个业务域
- **代码复用**: 使用基础类和混入类避免重复
- **性能优化**: 统一的查询优化和缓存策略

#### 模块化架构示例
```
products/
├── models/              # 模型模块化
│   ├── __init__.py      # 统一导入
│   ├── base.py          # 抽象基类
│   ├── mixins.py        # 功能混入
│   ├── category_models.py
│   ├── brand_models.py
│   ├── spu_models.py
│   └── sku_models.py
├── admin/               # Admin模块化
│   ├── __init__.py      # 统一注册
│   ├── base.py          # 基础Admin类
│   ├── mixins.py        # 功能混入
│   ├── category_admin.py
│   └── brand_admin.py
└── views/               # 视图模块化
    ├── __init__.py
    ├── base.py
    └── api/
```

#### 模块化重构流程
1. **检查阶段**: 运行 `make modular-check` 识别需要重构的文件
2. **预览阶段**: 运行 `make modular-preview` 查看重构方案
3. **执行阶段**: 运行 `make modular-interactive` 进行交互式重构
4. **验证阶段**: 运行 `make test-after-modular` 确保功能正常

### 🆕 新手用户
如果您是第一次使用系统，建议按以下顺序阅读：

1. **[产品管理基础](docs/user_guide/01_product_basics.md)** - 产品分类和属性设置
2. **[品牌管理指南](docs/user_guide/02_brand_management.md)** - 品牌创建和维护  
3. **[SPU/SKU管理](docs/user_guide/03_sku_spu_guide.md)** - 产品单元管理
4. **[权限角色说明](docs/user_guide/04_user_roles.md)** - 了解不同角色功能

### 👨‍💻 开发者文档

#### 核心架构
- **[数据模型设计](docs/dev_guide/01_data_models.md)** - 数据库设计说明
- **[API 接口文档](API_ENDPOINTS.md)** - REST API 完整说明
- **[权限系统](docs/dev_guide/03_permission_system.md)** - 权限控制机制

#### 部署运维
- **[Docker 部署](docs/deployment/01_docker_setup.md)** - 容器化部署指南
- **[数据库配置](docs/deployment/02_database_config.md)** - PostgreSQL 配置
- **[性能调优](docs/deployment/03_performance_tuning.md)** - 系统优化建议

## 🏗️ 项目结构

```
Flow/
├── 📁 .cursor/rules/          # 开发规范和代码标准
│   ├── django_modular_development.mdc  # Django模块化规范
│   ├── flow_project_standards.mdc      # 项目特定规范
│   └── debugging_priority.mdc          # 调试优先级规则
├── 📁 scripts/               # 自动化工具脚本
│   ├── check_modularization.py         # 模块化检查工具
│   ├── auto_modularize.py              # 自动重构工具
│   └── modularization_workflow.py      # 工作流管理器
├── 📁 products/              # 核心产品管理应用
│   ├── 📁 models/            # 模块化数据模型
│   ├── 📁 admin/             # 模块化管理界面
│   ├── 📁 views/             # 模块化视图逻辑
│   └── 📁 api/               # REST API接口
├── 📁 docs/                  # 项目文档
├── 📁 static/                # 静态资源文件
├── 📁 templates/             # 模板文件
├── 🐳 docker-compose.yml     # Docker编排配置
├── 🔧 Makefile              # 自动化命令集合
├── 📄 requirements.txt      # Python依赖
└── 📋 public.sql            # 数据库结构文档
```

## 🔄 持续改进

### 代码质量保证
- **自动化检查**: 集成模块化复杂度检查
- **规范遵循**: 基于最佳实践的开发规范
- **定期重构**: 主动识别和优化技术债务
- **测试覆盖**: 完整的功能和性能测试

### 团队协作
- **分支策略**: 基于功能模块的分支管理
- **代码审查**: 标准化的审查清单
- **文档维护**: 实时更新的开发文档
- **知识分享**: 定期的技术分享和培训

## 🤝 参与贡献

我们欢迎所有形式的贡献！在提交代码前，请确保：

1. **遵循开发规范**: 阅读 `.cursor/rules/` 目录下的规范文档
2. **代码模块化**: 使用 `make modular-check` 检查代码复杂度
3. **测试通过**: 运行 `make test-after-modular` 确保功能正常
4. **文档更新**: 同步更新相关文档

### 贡献流程
```bash
# 1. Fork 项目并创建分支
git checkout -b feature/your-feature

# 2. 开发过程中保持模块化
make modular-interactive

# 3. 测试验证
make test-after-modular

# 4. 提交代码
make git-commit-modular

# 5. 创建 Pull Request
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔗 相关链接

- **[API 文档](API_ENDPOINTS.md)** - 完整的 REST API 说明
- **[数据库文档](public.sql)** - 数据库结构和关系
- **[开发规范](.cursor/rules/)** - 代码标准和最佳实践
- **[问题反馈](https://github.com/your-repo/issues)** - Bug 报告和功能请求

---

💡 **提示**: 使用 `make help` 查看所有可用的开发命令，`make modular-interactive` 开始模块化之旅！ 