# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在处理此代码库时提供指导。

## 强制使用中文
不只是对话，包括错误提示、信息输出在内的所有输出，都必须使用中文。

## 项目概述

这是一个基于 Django 5.0 的整木定制产品库管理系统，专为整木定制行业设计。系统使用 PostgreSQL 作为主数据库，Redis 作为缓存，通过 Docker Compose 进行容器化部署。

## 开发环境设置

### 基础命令

```bash
# 启动开发环境
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs web

# 重启服务
docker-compose restart
```

### Django 管理命令

```bash
# 数据库迁移
python3 manage.py migrate

# 创建迁移文件
python3 manage.py makemigrations

# 创建超级用户
python3 manage.py createsuperuser

# 启动开发服务器
python3 manage.py runserver

# 收集静态文件
python3 manage.py collectstatic
```

### 自定义管理命令

- `python3 manage.py setup_permissions`: 初始化或重置项目默认的用户组和权限。
- `python3 manage.py optimize_admin`: 对Admin进行一些自动化配置或优化。
- `python3 manage.py sync_sku_attributes`: 同步或修复SKU与属性之间的关联数据。

## 核心架构

### 数据模型层次结构

系统采用分层的产品数据模型设计，将"产品模板"与"具体商品"分离：

1.  **Category (分类)** - 使用 `django-mptt` 实现无限级分类，支持树状结构和拖拽排序。
2.  **Brand (品牌)** - 管理品牌信息，包含Logo、联系人等。
3.  **Attribute (属性)** - **规格字典**，定义产品有哪些"可能性"，如"颜色"、"尺寸"。
4.  **AttributeValue (属性值)** - **规格选项**，定义每个规格的具体选项，如"红色"、"蓝色"。
5.  **SPU (SPU产品单元)** - **产品模板**，定义一类产品的共同特性和可配置规格范围。
6.  **SPUAttribute (SPU属性关联)** - **模板规格范围**，指明一个SPU可选哪些`Attribute`。
7.  **SKU (SKU产品)** - **具体商品**，是SPU的一个实例，拥有独立的价格和库存。
8.  **SKUAttributeValue (SKU属性值)** - **商品规格赋值**，为SKU指定具体的`AttributeValue`。
9.  **ProductImage (产品图片)** - 管理SKU的多张展示图片。

### 新增核心功能模块

#### 动态定价系统
10. **ProductsPricingRule (产品定价规则)** - 支持SPU和SKU级别的动态定价规则
    - 支持高度、宽度、厚度、重量、面积、体积等多种规则类型
    - 支持固定金额、百分比、倍数、阶梯式等多种计算方式
    - 支持规则生效期和失效期管理
    - 支持最大加价限制

#### 产品尺寸管理
11. **ProductsDimension (产品尺寸)** - 存储SKU的标准尺寸信息
    - 支持高度、宽度、厚度、长度、直径、半径、面积、体积、重量等尺寸类型
    - 支持最小值、最大值和公差设置
    - 支持关键尺寸标识（影响定价）
    - 支持自定义单位

12. **SPUDimensionTemplate (SPU尺寸模板)** - 定义SPU级别的标准尺寸模板
    - 为基于SPU创建SKU时提供尺寸模板
    - 支持必填尺寸配置
    - 支持尺寸排序和继承

### SPU/SKU与属性的核心关系

这是一个两阶段的实例化过程：

1.  **模板定义阶段 (SPU)**
    - **流程**: `SPU` -> `SPUAttribute` -> `Attribute`
    - **目的**: 定义一个产品模板有哪些**可配置的规格**。
    - **例子**: “iPhone 15 Pro”(SPU)通过`SPUAttribute`关联到“颜色”和“存储容量”(Attribute)，定义了它的规格范围。

2.  **实例创建阶段 (SKU)**
    - **流程**: `SKU` -> `SKUAttributeValue` -> `AttributeValue`
    - **目的**: 为一个具体商品**赋予明确的规格值**。
    - **例子**: 一个“具体商品”(SKU)通过`SKUAttributeValue`关联到“蓝色”和“256GB”(AttributeValue)，从而成为一个可销售的独立商品。

### 属性存储机制

系统采用灵活且标准化的**关系型存储**方式管理产品属性，取代了容易出错的JSON字段：
- `SKUAttributeValue` 模型是核心，它作为中间表，将`SKU`、`Attribute`和`AttributeValue`关联起来。
- 支持两种赋值模式：
  1.  **预定义值**: 关联到`AttributeValue`表中的一个现有记录（用于选择、颜色等类型）。
  2.  **自定义值**: 在`custom_value`字段中直接填写（用于文本、数字等需要用户输入的类型）。
- 通过 `get_relational_attribute_value()` 和 `set_relational_attribute_value()` 方法进行统一的属性读写访问。

### 后台管理 (Admin) 增强

为了提升运营效率，Django Admin 界面进行了大量定制化增强：

- **动态属性显示**: 在SKU列表中，使用不同颜色和格式清晰地展示各SKU的复杂规格。
- **MPTT分类管理**: 分类列表支持树状结构展示和鼠标拖拽排序。
- **自定义过滤器**: 提供了如按“产品系列”、“产品宽度”等业务逻辑进行筛选的功能。
- **优化的内联表单**: 在添加/修改SPU或SKU时，通过JavaScript动态过滤和加载关联的属性和属性值，提升了用户体验。
- **Logo和图片预览**: 在品牌和图片管理中提供即时预览功能。

### 应用结构

- **product_library/** - Django项目主配置。
- **products/** - 核心产品管理应用。
  - `models.py` - 包含上述所有核心数据模型。
  - `admin.py` - Django Admin的全部定制化配置。
  - `views.py` & `serializers.py` - 为REST API提供视图和序列化器。
  - `management/commands/` - 自定义管理命令。

### 技术特点

- **Django 5.0.6**: 基于最新的Django版本构建，充分利用最新特性。
- **Django REST Framework 3.15.2**: 提供了一套完整的REST API。
- **PostgreSQL**: 使用PostgreSQL 16.0作为主数据库，支持复杂的数据关系。
- **Redis**: 使用Redis 5.0.7作为缓存和会话存储。
- **django-mptt 0.16.0**: 实现高效的树状分类查询和管理。
- **Gunicorn**: 使用Gunicorn 22.0.0作为WSGI应用服务器。
- **环境变量配置**: 通过python-decouple进行配置管理。
- **Docker & Nginx**: 使用Docker进行容器化部署，Nginx处理静态文件服务。
- **图片处理**: 使用Pillow 10.3.0进行图片处理和优化。
- **CORS支持**: 通过django-cors-headers支持跨域请求。

### 核心业务逻辑

#### 动态定价计算
- 支持基于产品尺寸的动态定价
- 规则优先级：SKU专属规则 > SPU通用规则
- 支持阶梯式加价：根据超出标准尺寸的数量按步长计算
- 支持多种计算方式：固定金额、百分比、倍数、阶梯式
- 支持最大加价限制和规则有效期管理

#### 属性存储架构
- 完全基于关系型数据库的属性存储系统
- 支持预定义属性值和自定义属性值
- 属性值通过SKUAttributeValue模型统一管理
- 提供完整的属性值验证和类型检查机制

#### 产品尺寸管理
- 支持多维度尺寸信息存储
- 每个SKU可配置多种尺寸类型
- 支持尺寸公差和范围限制
- 关键尺寸标识用于动态定价计算

### 数据库架构信息

#### 数据库统计（截至2025年7月18日）
- **总表数**: 20+个核心业务表
- **产品数据规模**: 
  - 品牌数: 23个
  - 产品分类: 53个
  - 产品属性: 48个
  - 属性值: 200个
  - SPU: 53个
  - SKU: 210个
  - 产品尺寸: 16个
  - 定价规则: 10个

#### 数据库设计特点
- **完整的注释系统**: 所有表和字段都有详细的中文注释
- **性能优化**: 针对查询频繁的字段创建了专门的索引
- **数据完整性**: 使用外键约束和唯一约束确保数据一致性
- **审计追踪**: 所有核心表都包含创建时间、更新时间和创建人信息

### 核心API功能

#### 产品管理API
- 支持SPU和SKU的完整CRUD操作
- 支持产品属性的动态配置
- 支持产品分类的树状结构查询
- 支持产品图片的多图上传和管理

#### 动态定价API
- 支持基于尺寸的实时价格计算
- 支持定价规则的灵活配置
- 支持批量价格计算和预览

#### 数据查询API
- 支持复杂的产品筛选和搜索
- 支持分页和排序
- 支持关联数据的预加载优化

### 访问地址

- **管理后台**: http://localhost
- **API接口**: http://localhost/api/
- **健康检查**: http://localhost/health/