---
type: "always_apply"
---

# Flow项目开发规范

整木定制产品库管理系统的特定开发规范和最佳实践。

## **项目架构规范**

### **应用结构标准**
- **products/**: 核心产品管理功能
  - `admin/`: 后台管理界面模块（模块化设计）
  - `models/`: 数据模型（已模块化拆分）
  - `views/`: 视图逻辑
  - `services/`: 业务逻辑服务层
  - `config/`: 配置文件和映射
  - `utils/`: 工具函数
  - `api/`: API接口

### **数据库设计原则**
- **参考 [public.sql](mdc:public.sql) 了解当前表结构**
- **SPU-SKU模型**: 严格区分标准产品单元和库存单元
- **属性系统**: 灵活的EAV模型支持产品属性扩展
- **分类体系**: 多级分类支持，便于产品组织
- **导入系统**: 支持AI数据格式和传统Royana格式双模板导入

## **Admin模块开发规范**

### **遵循模块化结构**
基于 [django_modular_development.mdc](mdc:.cursor/rules/django_modular_development.mdc) 的规范：

```python
products/admin/
├── __init__.py              # 统一注册入口
├── base.py                  # LargeTablePaginator, BaseModelAdmin
├── mixins.py                # BulkActionMixin, DisplayMixin等
├── filters.py               # SeriesFilter, WidthFilter等
├── category_admin.py        # 分类管理
├── brand_admin.py           # 品牌管理
├── attribute_admin.py       # 属性管理
├── spu_admin.py            # SPU管理
├── sku_admin.py            # SKU管理
├── product_admin.py        # 其他产品相关管理
└── import_admin.py         # 数据导入系统
```

### **性能优化要求**
- **必须使用 `LargeTablePaginator`** 处理大数据表
- **查询优化**: 使用 `select_related` 和 `prefetch_related`
- **缓存策略**: 对频繁查询的数据进行缓存
- **批量操作**: 提供批量编辑和删除功能

## **业务逻辑规范**

### **产品数据处理**
- **SPU管理**:
  - 标准产品信息录入
  - SKU变体自动生成
  - 属性值关联管理

- **分类管理**:
  - 多级分类树状结构
  - 分类属性继承机制
  - 支持批量分类调整

### **属性系统设计**
- **属性定义**: 规范化属性名称和类型
- **属性值**: 支持多种数据类型（文本、数值、枚举等）
- **属性继承**: 分类属性向产品传递

### **数据导入规范**
- **双模板系统**: AI数据格式和传统Royana格式
- **服务层架构**: 使用专用的导入服务类处理业务逻辑
- **配置驱动**: 通过配置文件管理字段映射和验证规则
- **数据验证**: 严格的数据格式检查和属性完整性验证
- **错误处理**: 详细的错误日志和用户反馈
- **批量处理**: 支持大批量数据导入和事务安全

## **前端开发规范**

### **模板组织**
```
templates/
├── admin/                   # Django Admin模板覆盖
├── products/               # 产品相关模板
└── base.html               # 基础模板
```

### **静态资源管理**
```
static/
├── css/                    # 样式文件
├── js/                     # JavaScript文件
├── images/                 # 图片资源
└── admin/                  # Admin界面定制
```

## **数据库操作规范**

### **查询优化**
- **✅ DO: 查看数据库结构**
```python
# 操作前先查看 public.sql 了解表结构
# 理解字段约束和关系
```

- **✅ DO: 使用连接查询减少数据库访问**
```python
# 优化SKU查询
skus = SKU.objects.select_related(
    'spu', 'spu__category', 'spu__brand'
).prefetch_related(
    'attribute_values__attribute'
)
```

### **数据完整性**
- **外键约束**: 严格维护数据关系
- **数据验证**: 在模型层和表单层双重验证
- **事务处理**: 复杂操作使用数据库事务

## **错误处理和日志**

### **异常处理**
- **用户友好的错误消息**
- **详细的开发者日志**
- **错误恢复机制**

### **日志规范**
```python
import logging

logger = logging.getLogger(__name__)

# 记录重要操作
logger.info(f"用户 {user} 创建了产品 {product}")

# 记录错误详情
logger.error(f"导入失败: {error_details}", exc_info=True)
```

## **测试规范**

### **测试覆盖要求**
- **模型测试**: 验证数据模型正确性
- **Admin测试**: 确保后台功能正常
- **API测试**: 验证接口功能和性能
- **集成测试**: 端到端业务流程测试

### **测试数据管理**
- **使用 fixtures 准备测试数据**
- **避免依赖生产数据**
- **清理测试后的数据**

## **部署和维护**

### **Docker配置**
- **参考 [Dockerfile](mdc:Dockerfile) 和 [docker-compose.yml](mdc:docker-compose.yml)**
- **环境变量管理**
- **数据卷挂载**

### **数据库备份**
- **定期备份策略**
- **备份验证机制**
- **灾难恢复计划**

## **代码质量控制**

### **代码审查要点**
- [ ] 遵循Django最佳实践
- [ ] 模块化结构合理
- [ ] 性能优化到位
- [ ] 错误处理完善
- [ ] 文档注释完整
- [ ] 测试覆盖充分

### **性能监控**
- **数据库查询时间**
- **页面加载速度**
- **内存使用情况**
- **并发处理能力**

## **团队协作**

### **分支策略**
```bash
main                        # 生产分支
├── develop                 # 开发分支
├── feature/admin-module    # 功能分支
├── feature/api-v2         # API改进
└── hotfix/critical-bug    # 紧急修复
```

### **提交规范**
```bash
# 功能开发
git commit -m "feat(admin): 添加SKU批量编辑功能"

# 性能优化
git commit -m "perf(database): 优化产品查询性能"

# 问题修复
git commit -m "fix(import): 修复数据导入编码问题"

# 重构
git commit -m "refactor(admin): 模块化admin.py文件"
```

## **安全规范**

### **数据保护**
- **用户权限控制**
- **敏感数据加密**
- **SQL注入防护**
- **XSS攻击防护**

### **访问控制**
- **基于角色的权限系统**
- **操作日志记录**
- **会话管理**

## **文档维护**

### **必需文档**
- **API文档**: 接口规范和示例
- **部署文档**: 环境配置和部署步骤
- **用户手册**: 系统使用指南
- **开发指南**: 新人上手指南

### **文档更新策略**
- **代码变更时同步更新文档**
- **定期审查文档准确性**
- **用户反馈收集和处理**

---

遵循这些规范可以确保Flow项目的代码质量、系统稳定性和团队协作效率。所有开发活动都应优先查看相关文档和代码，理解业务逻辑后再进行开发。
