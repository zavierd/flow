---
type: "agent_requested"
---

# 开发规范总览

Flow项目的完整开发规范体系，基于实际项目经验总结的最佳实践。

## **规范文档结构**

### **核心规范**
- **[debugging_priority.md](debugging_priority.md)** - 调试和问题解决的优先级原则
- **[django_modular_development.md](django_modular_development.md)** - Django模块化开发通用规范
- **[flow_project_standards.md](flow_project_standards.md)** - Flow项目特定开发规范
- **[cursor_rules.md](cursor_rules.md)** - Cursor规则文件格式规范
- **[self_improve.md](self_improve.md)** - 规则自我改进机制

### **业务功能规范**
- **[ai_import_system.md](ai_import_system.md)** - AI数据导入系统开发规范
- **[product_attribute_system.md](product_attribute_system.md)** - 产品属性系统开发规范
- **[paste_import_system.md](paste_import_system.md)** - 粘贴导入系统开发规范

### **工具和流程**
- **[cursor_rules.mdc](mdc:.cursor/rules/cursor_rules.mdc)** - Cursor编辑器和规则系统的使用规范
- **[self_improve.mdc](mdc:.cursor/rules/self_improve.mdc)** - 规则系统的自我改进机制
- **[taskmaster/](mdc:.cursor/rules/taskmaster/)** - 任务管理和开发流程规范

## **规范应用场景**

### **日常开发**
1. **问题排查**: 遵循 [debugging_priority.mdc](mdc:.cursor/rules/debugging_priority.mdc) 的优先级原则
2. **代码组织**: 应用 [django_modular_development.mdc](mdc:.cursor/rules/django_modular_development.mdc) 的模块化规范
3. **项目特定**: 参考 [flow_project_standards.mdc](mdc:.cursor/rules/flow_project_standards.mdc) 的业务规范

### **重构场景**
- **大文件拆分**: 超过500行时按模块化规范拆分
- **功能模块**: 单一职责原则，避免功能混合
- **性能优化**: 统一查询优化和缓存策略

### **团队协作**
- **代码审查**: 使用规范中的检查清单
- **分支管理**: 按功能模块创建分支
- **提交规范**: 描述性提交信息

## **规范执行优先级**

### **必须遵循 (alwaysApply: true)**
1. **调试优先级原则** - 代码优先、文档查询、数据库结构了解
2. **模块化开发** - 文件大小控制、职责分离、代码复用
3. **项目特定规范** - 业务逻辑、数据结构、性能要求

### **建议遵循**
- **工具使用规范** - 提高开发效率
- **流程管理** - 任务跟踪和项目管理

## **实际应用示例**

### **admin.py重构案例**
基于 [django_modular_development.mdc](mdc:.cursor/rules/django_modular_development.mdc) 规范：

```
原始状态: products/admin.py (2889行)
↓ 重构后
products/admin/
├── __init__.py              # 统一注册
├── base.py                  # 基础类
├── mixins.py                # 功能混入
├── filters.py               # 过滤器
├── category_admin.py        # 分类管理
├── brand_admin.py           # 品牌管理
├── attribute_admin.py       # 属性管理
├── spu_admin.py            # SPU管理
├── sku_admin.py            # SKU管理
└── product_admin.py        # 其他产品管理
```

**效果**:
- ✅ 代码可维护性显著提升
- ✅ 团队协作效率提高
- ✅ 减少merge冲突
- ✅ 功能模块清晰分离

## **规范更新机制**

### **触发条件**
- 新的代码模式出现3次以上
- 重复的代码审查意见
- 性能或安全问题
- 框架或工具升级

### **更新流程**
1. **识别问题**: 代码审查中发现模式
2. **分析影响**: 评估改进收益
3. **制定规范**: 编写具体规则
4. **验证效果**: 在实际项目中测试
5. **推广应用**: 更新相关规范

### **版本管理**
- **向后兼容**: 新规范不破坏现有代码
- **渐进式应用**: 新功能应用新规范
- **文档同步**: 规范变更时更新相关文档

## **常见问题和解决方案**

### **Q: 如何判断文件是否需要拆分？**
A: 参考 [django_modular_development.mdc](mdc:.cursor/rules/django_modular_development.mdc)：
- 文件超过500行
- 包含多个不同的功能域
- 团队成员经常在同一文件产生merge冲突

### **Q: 如何保持向后兼容性？**
A: 使用导入机制：
```python
# 原文件保留，通过导入维持兼容性
from .admin import *
```

### **Q: 性能优化的优先级？**
A: 按 [flow_project_standards.mdc](mdc:.cursor/rules/flow_project_standards.mdc)：
1. 数据库查询优化
2. 缓存策略
3. 前端资源优化
4. 代码结构优化

## **快速参考**

### **开发前检查**
- [ ] 查看 [public.sql](mdc:public.sql) 了解数据结构
- [ ] 确认业务需求和设计规范
- [ ] 选择合适的模块进行修改

### **代码审查检查**
- [ ] 模块职责单一
- [ ] 文件大小合理
- [ ] 性能优化到位
- [ ] 测试覆盖充分
- [ ] 文档注释完整

### **提交前检查**
- [ ] 功能完整性验证
- [ ] 性能回归测试
- [ ] 代码风格一致
- [ ] 提交信息描述清楚

---

这套规范体系基于实际项目经验总结，旨在提高代码质量、开发效率和团队协作。定期回顾和更新规范，确保与项目发展同步。
