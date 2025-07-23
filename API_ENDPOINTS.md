# 整木定制产品库管理系统 - API 端点文档

## 基础信息
- **基础URL**: `http://localhost:8000/api/`
- **认证**: 支持 Session Authentication 和 Token Authentication
- **权限**: 大部分只读接口允许匿名访问
- **数据格式**: JSON
- **分页**: 默认每页20条记录

## API 端点列表

### 1. 产品相关 API

#### 1.1 产品列表 (Products)
- **URL**: `/api/products/`
- **方法**: GET
- **描述**: 获取产品列表，支持分页、排序和过滤
- **查询参数**:
  - `page`: 页码
  - `page_size`: 每页记录数
  - `search`: 搜索关键词
  - `ordering`: 排序字段 (`name`, `price`, `stock_quantity`, `created_at`)
  - `brand`: 品牌ID筛选
  - `spu__category`: 分类ID筛选
  - `status`: 状态筛选
  - `is_featured`: 是否推荐
  - `min_price`: 最低价格
  - `max_price`: 最高价格
  - `in_stock`: 是否有库存 (true/false)
  - `category`: 分类ID (支持子分类)
  - `attr_[属性编码]`: 属性筛选 (如 `attr_material=实木`)

#### 1.2 产品详情
- **URL**: `/api/products/{id}/`
- **方法**: GET
- **描述**: 获取单个产品的详细信息

#### 1.3 推荐产品
- **URL**: `/api/products/featured/`
- **方法**: GET
- **描述**: 获取推荐产品列表

#### 1.4 最新产品
- **URL**: `/api/products/latest/`
- **方法**: GET
- **描述**: 获取最新产品列表

#### 1.5 产品搜索
- **URL**: `/api/products/search/`
- **方法**: GET
- **描述**: 高级产品搜索
- **查询参数**:
  - `q`: 搜索关键词

### 2. 分类相关 API

#### 2.1 分类列表
- **URL**: `/api/categories/`
- **方法**: GET
- **描述**: 获取产品分类列表
- **查询参数**:
  - `parent`: 父分类ID (null 或空字符串表示顶级分类)
  - `search`: 搜索关键词
  - `ordering`: 排序字段

#### 2.2 分类详情
- **URL**: `/api/categories/{id}/`
- **方法**: GET
- **描述**: 获取单个分类的详细信息

#### 2.3 分类树
- **URL**: `/api/categories/tree/`
- **方法**: GET
- **描述**: 获取完整的分类树结构

### 3. 品牌相关 API

#### 3.1 品牌列表
- **URL**: `/api/brands/`
- **方法**: GET
- **描述**: 获取品牌列表
- **查询参数**:
  - `search`: 搜索关键词
  - `ordering`: 排序字段

#### 3.2 品牌详情
- **URL**: `/api/brands/{id}/`
- **方法**: GET
- **描述**: 获取单个品牌的详细信息

### 4. 属性相关 API

#### 4.1 属性列表
- **URL**: `/api/attributes/`
- **方法**: GET
- **描述**: 获取产品属性列表
- **查询参数**:
  - `filterable`: 只返回可筛选的属性 (true/false)
  - `search`: 搜索关键词
  - `ordering`: 排序字段

#### 4.2 属性详情
- **URL**: `/api/attributes/{id}/`
- **方法**: GET
- **描述**: 获取单个属性的详细信息

### 5. SPU 相关 API

#### 5.1 SPU 列表
- **URL**: `/api/spus/`
- **方法**: GET
- **描述**: 获取SPU产品单元列表
- **查询参数**:
  - `category`: 分类ID筛选
  - `is_active`: 是否激活
  - `search`: 搜索关键词
  - `ordering`: 排序字段

#### 5.2 SPU 详情
- **URL**: `/api/spus/{id}/`
- **方法**: GET
- **描述**: 获取单个SPU的详细信息

### 6. 筛选器 API

#### 6.1 筛选器数据
- **URL**: `/api/filters/`
- **方法**: GET
- **描述**: 获取用于产品筛选的所有可用选项
- **返回数据**:
  - `categories`: 分类列表
  - `brands`: 品牌列表
  - `attributes`: 可筛选属性列表
  - `price_range`: 价格范围 (`min_price`, `max_price`)
  - `status_choices`: 状态选项

## 响应格式

### 成功响应
```json
{
  "count": 总记录数,
  "next": "下一页URL",
  "previous": "上一页URL",
  "results": [
    // 数据数组
  ]
}
```

### 错误响应
```json
{
  "detail": "错误信息"
}
```

## 使用示例

### 获取产品列表
```bash
curl "http://localhost:8000/api/products/?page=1&page_size=10"
```

### 按分类筛选产品
```bash
curl "http://localhost:8000/api/products/?category=1"
```

### 按价格范围筛选产品
```bash
curl "http://localhost:8000/api/products/?min_price=100&max_price=1000"
```

### 按属性筛选产品
```bash
curl "http://localhost:8000/api/products/?attr_material=实木"
```

### 搜索产品
```bash
curl "http://localhost:8000/api/products/search/?q=橱柜"
```

### 获取筛选器数据
```bash
curl "http://localhost:8000/api/filters/"
```

### 获取分类树
```bash
curl "http://localhost:8000/api/categories/tree/"
```

## 注意事项

1. **缓存**: 分类和品牌接口有15分钟缓存，筛选器接口有30分钟缓存
2. **权限**: 目前大部分接口允许匿名访问，生产环境需要根据需求调整权限
3. **性能**: 查询已经进行了优化，使用了 `select_related` 和 `prefetch_related`
4. **图片URL**: 所有图片字段都会返回完整的URL地址
5. **属性筛选**: 使用 `attr_` 前缀加属性编码进行筛选
6. **分类筛选**: 支持子分类，会自动包含所有子分类的产品

## 后续扩展

- 添加用户认证相关API
- 添加购物车和订单管理API
- 添加产品评价和评分API
- 添加库存管理API
- 添加数据统计和报表API 