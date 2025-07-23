# Flow 项目理解总结

## 项目概述

Flow 是一个专为整木定制行业设计的产品数据管理平台，旨在帮助企业高效管理产品分类、品牌、属性、SKU/SPU 等核心业务数据。

## 技术架构

### 后端技术栈
- **Django 4.x**: Python Web框架
- **PostgreSQL**: 主数据库
- **Redis**: 缓存系统
- **Docker**: 容器化部署

### 核心组件
1. **产品管理模块** (`products/`)
   - 分类管理 (Category)
   - 品牌管理 (Brand)
   - 属性系统 (Attribute/AttributeValue)
   - SPU/SKU管理 (SPU/SKU)
   - 产品图片管理 (ProductImage)
   - 产品尺寸管理 (ProductDimension)
   - 定价规则 (PricingRule)

2. **模块化架构**
   - 采用模块化设计，将模型、Admin、视图等按功能拆分
   - 使用Django MPTT实现无限级分类
   - EAV (Entity-Attribute-Value) 模型支持灵活的产品属性配置

3. **REST API**
   - 提供完整的RESTful API接口
   - 支持产品查询、筛选、搜索等功能
   - 集成Django REST Framework

## 数据模型设计

### 核心概念
- **SPU (Standard Product Unit)**: 标准产品单元，定义产品的通用属性模板
- **SKU (Stock Keeping Unit)**: 库存单元，是SPU的一个具体实例，具有唯一的价格、库存和属性组合
- **属性系统**: 支持8种属性类型（文本、数字、选择、多选、布尔值、日期、颜色、图片）

### 关键模型关系
1. **Category**: 支持无限级分类树结构
2. **Brand**: 品牌信息管理
3. **Attribute/AttributeValue**: 灵活的属性定义系统
4. **SPU**: 产品模板，关联分类和品牌
5. **SPUAttribute**: 定义SPU支持的属性及默认值
6. **SKU**: 具体产品，关联SPU、品牌和属性值
7. **SKUAttributeValue**: SKU的具体属性值配置（关系型存储）

## 系统特点

### 功能特性
- 无限级分类管理
- 完整品牌管理
- 灵活属性系统
- SPU/SKU管理
- 多角色权限控制
- 现代化管理界面
- 完整REST API

### 开发规范
- 严格的模块化架构
- 代码质量控制（文件大小限制、单一职责原则）
- 性能优化（查询优化、缓存策略）
- 模块化重构工具链
- 完善的文档和注释

### 部署运维
- Docker容器化部署
- PostgreSQL数据库
- Redis缓存
- Nginx反向代理
- Gunicorn应用服务器

## 业务流程

1. **产品创建流程**:
   - 创建分类和品牌
   - 定义产品属性
   - 创建SPU模板
   - 基于SPU创建SKU实例
   - 配置SKU属性值和价格库存

2. **数据查询流程**:
   - 通过API接口查询产品列表
   - 支持多维度过滤和搜索
   - 支持分页和排序

## 项目优势

1. **行业定制**: 专为整木定制行业设计，满足特定业务需求
2. **模块化架构**: 代码组织清晰，易于维护和扩展
3. **灵活配置**: 强大的属性系统支持产品多样化配置
4. **高性能**: 优化的数据库查询和缓存机制
5. **易用性**: 现代化的管理界面和完整的API接口