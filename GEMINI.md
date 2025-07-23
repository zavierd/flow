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

系统采用分层的产品数据模型设计，将“产品模板”与“具体商品”分离：

1.  **Category (分类)** - 使用 `django-mptt` 实现无限级分类，支持树状结构和拖拽排序。
2.  **Brand (品牌)** - 管理品牌信息，包含Logo、联系人等。
3.  **Attribute (属性)** - **规格字典**，定义产品有哪些“可能性”，如“颜色”、“尺寸”。
4.  **AttributeValue (属性值)** - **规格选项**，定义每个规格的具体选项，如“红色”、“蓝色”。
5.  **SPU (SPU产品单元)** - **产品模板**，定义一类产品的共同特性和可配置规格范围。
6.  **SPUAttribute (SPU属性关联)** - **模板规格范围**，指明一个SPU可选哪些`Attribute`。
7.  **SKU (SKU产品)** - **具体商品**，是SPU的一个实例，拥有独立的价格和库存。
8.  **SKUAttributeValue (SKU属性值)** - **商品规格赋值**，为SKU指定具体的`AttributeValue`。
9.  **ProductImage (产品图片)** - 管理SKU的多张展示图片。

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

- **Django 5.0**: 基于最新的Django版本构建。
- **Django REST Framework**: 提供了一套完整的REST API。
- **django-mptt**: 实现高效的树状分类查询和管理。
- **环境变量配置**: 通过`.env`文件区分开发与生产环境，配置数据库、缓存等。
- **Docker & Nginx**: 使用Docker进行容器化部署，Nginx处理静态文件服务。

### 访问地址

- **管理后台**: http://localhost
- **API接口**: http://localhost/api/
- **健康检查**: http://localhost/health/