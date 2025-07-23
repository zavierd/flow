## **整木定制产品库管理系统 \- 技术产品需求文档 (PRD V2.0)**

| 文档版本 | V2.0 | 状态 | 待开发 (Ready for Dev) |
| :---- | :---- | :---- | :---- |
| **创建日期** | 2025年07月14日 | **负责人** | 张威 |
| **技术栈** | **Python 3.12+, Django 5.x, Django REST Framework** |  |  |
| **数据库** | **PostgreSQL 16+** |  |  |

### **1\. 项目概述**

*(本章节与V1.0一致，旨在明确业务目标，此处从略)*

### **2\. 技术栈与项目结构**

#### **2.1. 技术栈详情**

* **后端框架:** Django 5.x  
* **API框架:** Django REST Framework (DRF) 3.15+  
* **数据库:** PostgreSQL 16+ (推荐，利用其高级特性) 或 MySQL 8.0+  
* **应用服务器:** Gunicorn  
* **Web服务器:** Nginx  
* **缓存:** Redis (用于缓存查询结果)

#### **2.2. Django 项目结构建议**

项目采用标准的Django结构，将所有产品库相关的功能封装在一个名为 products 的App中。

product\_library/  
├── manage.py  
├── product\_library/       \# Django项目配置目录  
│   ├── \_\_init\_\_.py  
│   ├── asgi.py  
│   ├── settings.py  
│   ├── urls.py  
│   └── wsgi.py  
├── products/              \# 核心App  
│   ├── \_\_init\_\_.py  
│   ├── admin.py           \# 核心：Admin后台配置  
│   ├── apps.py  
│   ├── models.py          \# 核心：数据模型定义  
│   ├── serializers.py     \# 核心：API序列化器  
│   ├── views.py           \# 核心：API视图  
│   ├── urls.py            \# App的URL配置  
│   └── ...  
└── requirements.txt       \# 项目依赖

### **3\. 核心数据模型 (products/models.py)**

以下是直接可在Django中使用的模型代码，已包含字段类型、关系和中文后台显示名称(verbose\_name)。

\# products/models.py  
from django.db import models

class Category(models.Model):  
    name \= models.CharField("分类名称", max\_length=100)  
    parent \= models.ForeignKey('self', on\_delete=models.SET\_NULL, null=True, blank=True, related\_name='children', verbose\_name="父分类")  
    description \= models.TextField("分类描述", blank=True)  
    sort\_order \= models.IntegerField("排序", default=0)

    class Meta:  
        verbose\_name \= "产品分类"  
        verbose\_name\_plural \= verbose\_name  
        ordering \= \['sort\_order'\]

    def \_\_str\_\_(self):  
        \# 用于在Admin中显示层级关系  
        path \= \[self.name\]  
        p \= self.parent  
        while p:  
            path.insert(0, p.name)  
            p \= p.parent  
        return ' \-\> '.join(path)

class Brand(models.Model):  
    name \= models.CharField("品牌名称", max\_length=100, unique=True)  
    logo\_url \= models.URLField("品牌Logo地址", max\_length=255, blank=True, null=True)  
      
    class Meta:  
        verbose\_name \= "合作品牌"  
        verbose\_name\_plural \= verbose\_name

    def \_\_str\_\_(self):  
        return self.name

class Attribute(models.Model):  
    name \= models.CharField("属性名", max\_length=100, unique=True)  
    code \= models.CharField("属性编码", max\_length=50, unique=True, help\_text="用于程序内部识别，如 'color'")

    class Meta:  
        verbose\_name \= "产品属性"  
        verbose\_name\_plural \= verbose\_name

    def \_\_str\_\_(self):  
        return self.name

class AttributeValue(models.Model):  
    attribute \= models.ForeignKey(Attribute, on\_delete=models.CASCADE, related\_name='values', verbose\_name="所属属性")  
    value \= models.CharField("属性值", max\_length=100)

    class Meta:  
        verbose\_name \= "属性值"  
        verbose\_name\_plural \= verbose\_name  
        unique\_together \= ('attribute', 'value')  
        ordering \= \['attribute', 'value'\]

    def \_\_str\_\_(self):  
        return f"{self.attribute.name}: {self.value}"

class SPU(models.Model):  
    name \= models.CharField("SPU标准名称", max\_length=255)  
    spu\_code \= models.CharField("SPU编码", max\_length=100, unique=True)  
    category \= models.ForeignKey(Category, on\_delete=models.PROTECT, verbose\_name="所属分类")  
    description \= models.TextField("SPU描述", blank=True)  
    configurable\_attributes \= models.ManyToManyField(Attribute, verbose\_name="可配置属性")  
      
    class Meta:  
        verbose\_name \= "SPU (标准产品单元)"  
        verbose\_name\_plural \= verbose\_name

    def \_\_str\_\_(self):  
        return self.name

class SKU(models.Model):  
    spu \= models.ForeignKey(SPU, on\_delete=models.CASCADE, related\_name='skus', verbose\_name="所属SPU")  
    brand \= models.ForeignKey(Brand, on\_delete=models.PROTECT, verbose\_name="所属品牌")  
    sku\_code \= models.CharField("SKU编码", max\_length=100, unique=True, blank=True, help\_text="留空可自动生成")  
    brand\_product\_name \= models.CharField("品牌产品名称", max\_length=255)  
    price \= models.DecimalField("价格", max\_digits=10, decimal\_places=2)  
    price\_unit \= models.CharField("计价单位", max\_length=20, default='元/平方米')  
      
    \# 将SKU的具体配置通过一个中间表关联起来  
    \# 此处使用ManyToManyField并指定through模型是最佳实践  
    configuration \= models.ManyToManyField(AttributeValue, through='SKUConfiguration', verbose\_name="具体配置")

    class Meta:  
        verbose\_name \= "SKU (品牌产品)"  
        verbose\_name\_plural \= verbose\_name

    def \_\_str\_\_(self):  
        return self.brand\_product\_name

class SKUConfiguration(models.Model):  
    """SKU配置的中间表"""  
    sku \= models.ForeignKey(SKU, on\_delete=models.CASCADE)  
    attribute \= models.ForeignKey(Attribute, on\_delete=models.CASCADE, verbose\_name="属性")  
    value \= models.ForeignKey(AttributeValue, on\_delete=models.CASCADE, verbose\_name="属性值")

    class Meta:  
        verbose\_name \= "SKU配置"  
        verbose\_name\_plural \= verbose\_name  
        unique\_together \= ('sku', 'attribute') \# 一个SKU的一个属性只能有一个值

### **4\. 功能性需求 (基于Django Admin)**

**核心思想：** V1.0的大部分后台管理功能，将通过深度定制Django Admin来实现，而非从零手写界面。

#### **4.1. 通用Admin配置**

* **FR4.1.1:** 在 products/admin.py 中注册以上所有模型 (Category, Brand, Attribute, AttributeValue, SPU, SKU)，使其出现在Admin后台。

#### **4.2. Category, Brand, Attribute 模型后台**

* **FR4.2.1:** CategoryAdmin:  
  * list\_display 应包含 \_\_str\_\_, sort\_order，以清晰展示层级。  
  * 推荐使用 django-mptt 或类似库来优化树状层级展示和编辑体验。  
* **FR4.2.2:** AttributeAdmin:  
  * 使用 admin.TabularInline 在属性编辑页面直接管理其下的 AttributeValue (属性值)。  
  * list\_display 包含 name, code。

#### **4.3. SPU 模型后台 (SPUAdmin)**

* **FR4.3.1:** list\_display 应包含 name, spu\_code, category。  
* **FR4.3.2:** list\_filter 应支持按 category 筛选。  
* **FR4.3.3:** search\_fields 应支持按 name, spu\_code 搜索。  
* **FR4.3.4:** 对于 configurable\_attributes (多对多字段)，在编辑页使用 filter\_horizontal 小部件，方便用户左右穿梭选择。

#### **4.4. SKU 模型后台 (SKUAdmin) \- (核心与难点)**

* **FR4.4.1 \- 列表页:**  
  * list\_display 应包含 brand\_product\_name, brand, spu, price, price\_unit。  
  * list\_filter 应支持按 brand 和 spu 筛选。  
  * search\_fields 应支持按 brand\_product\_name, sku\_code 搜索。  
* **FR4.4.2 \- 编辑/创建页:**  
  * **FR4.4.2.1 (动态配置):** 这是后台交互的核心。当用户在创建SKU的页面**选择一个SPU**后，页面需要通过JavaScript (Ajax) **动态加载**该SPU所关联的 configurable\_attributes，并以表单的形式展现出来。每个属性提供一个下拉框，下拉框的选项为该属性对应的所有AttributeValue。  
  * **FR4.4.2.2 (数据保存):** 当用户提交表单时，除了保存SKU本身的信息到SKU表，还需要将用户选择的属性-值对，保存到 SKUConfiguration 中间表中。  
  * **FR4.4.2.3 (使用Inline):** 在SKU的编辑页面，使用 admin.TabularInline 来展示和编辑其已有的配置 (SKUConfiguration 记录)，让管理员可以清晰地看到该SKU的具体配置。

### **5\. REST API 需求 (products/views.py & serializers.py)**

利用Django REST Framework为未来的前端或第三方应用提供数据接口。

* **FR5.1 \- Serializers (serializers.py):**  
  * 为 Category, Brand, SPU, SKU 等核心模型创建 ModelSerializer。  
  * SKUSerializer 需要进行嵌套序列化，以在其JSON输出中包含完整的品牌信息、SPU信息以及详细的配置信息（属性名和属性值）。  
* **FR5.2 \- Views & URLs (views.py, urls.py):**  
  * 使用 viewsets.ReadOnlyModelViewSet 快速创建只读的API端点。  
  * **Endpoint 1:** /api/products/skus/  
    * GET: 返回SKU列表，支持通过查询参数进行过滤，例如 ?brand=1, ?category=3, ?attribute\_value=5。  
  * **Endpoint 2:** /api/products/skus/\<id\>/  
    * GET: 返回单个SKU的详细信息。  
  * **Endpoint 3:** /api/products/filters/  
    * GET: 返回一个用于构建前端筛选器的JSON结构，包含所有可用的分类、品牌以及属性和属性值。

### **6\. 用户角色与权限**

* **FR6.1 \- 创建用户组:**  
  * 在Django Admin中创建两个用户组: 产品专员 (ProductManager) 和 销售设计师 (SalesDesigner)。  
* **FR6.2 \- 分配权限:**  
  * **产品专员组:** 授予对 products App下所有模型的 add, change, delete, view 权限。  
  * **销售设计师组:** 仅授予所有模型的 view 权限。他们可以通过Admin后台查看产品，但不能修改。未来API开发完成后，他们将主要使用基于API的前端应用。

### **7\. 部署清单**

* **代码管理:** Git (使用 a .gitignore file for Django).  
* **依赖管理:** 使用 pip freeze \> requirements.txt 生成依赖文件。  
* **环境变量:** 使用 .env 文件配合 python-decouple 或 django-environ 库管理敏感信息（SECRET\_KEY, DATABASE\_URL, DEBUG状态），严禁硬编码在settings.py中。  
* **服务器配置:**  
  * Nginx作为反向代理，并负责托管静态文件 (STATIC\_ROOT)。  
  * Gunicorn作为应用服务器运行Django App。  
  * 使用supervisor或systemd来管理Gunicorn进程。  
  * 配置数据库备份策略。