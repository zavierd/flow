---
description: 产品属性系统开发规范和最佳实践
globs: products/models/attribute_*.py, products/admin/attribute_*.py, products/services/*attribute*.py
alwaysApply: true
---

# 产品属性系统开发规范

## **核心架构原则**

### **EAV模型设计**
- **Attribute**: 属性定义（如：宽度、颜色、材质）
- **AttributeValue**: 属性值（如：30cm、红色、实木）
- **SKUAttributeValue**: SKU-属性值关联（实际产品的属性配置）
- **SPUAttribute**: SPU-属性关联（产品模板支持的属性）

### **属性类型系统**
```python
# ✅ DO: 标准属性类型定义
ATTRIBUTE_TYPES = [
    ('text', '文本'),
    ('number', '数字'),
    ('select', '单选'),
    ('multiselect', '多选'),
    ('boolean', '布尔值'),
    ('date', '日期'),
    ('color', '颜色'),
    ('image', '图片'),
]
```

## **属性编码规范**

### **标准编码映射**
```python
# ✅ DO: 统一的属性编码系统
ATTRIBUTE_CODE_MAPPING = {
    '宽度': 'WIDTH',
    '高度': 'HEIGHT', 
    '深度': 'DEPTH',
    '柜体类型': 'CABINET_TYPE',
    '门板方向': 'DOOR_DIRECTION',
    '配置代码': 'CONFIG_CODE',
    '备注说明': 'REMARKS',
    '英文名称': 'ENGLISH_NAME',
    '价格等级I': 'PRICE_LEVEL_1',
    '价格等级II': 'PRICE_LEVEL_2',
    '价格等级III': 'PRICE_LEVEL_3',
    '价格等级IV': 'PRICE_LEVEL_4',
    '价格等级V': 'PRICE_LEVEL_5',
}
```

### **编码生成规则**
- **英文大写**：使用英文大写字母
- **下划线分隔**：多词使用下划线连接
- **语义明确**：编码能够清晰表达属性含义
- **避免冲突**：确保编码在系统中唯一

## **属性创建最佳实践**

### **智能类型判断**
```python
# ✅ DO: 智能属性类型判断
def _determine_attribute_type(self, value) -> str:
    """根据值的特征智能判断属性类型"""
    if isinstance(value, (int, float)):
        return 'number'
    elif isinstance(value, str):
        # 门板方向等预定义选项
        if value in ['左开', '右开', '左开/右开', '双开', '-']:
            return 'select'
        # 短文本通常是选择项
        elif len(value) < 50:
            return 'select'
        # 长文本使用文本类型
        else:
            return 'text'
    else:
        return 'text'
```

### **属性创建流程**
```python
# ✅ DO: 完整的属性创建流程
def _create_sku_attribute_value(self, sku: SKU, attr_name: str, attr_value):
    # 1. 生成标准编码
    attr_code = self._generate_attribute_code(attr_name)
    
    # 2. 创建或获取属性
    attribute, created = Attribute.objects.get_or_create(
        code=attr_code,
        defaults={
            'name': attr_name,
            'type': self._determine_attribute_type(attr_value),
            'is_required': False,
            'is_filterable': attr_name in FILTERABLE_ATTRIBUTES
        }
    )
    
    # 3. 创建或获取属性值
    attribute_value, created = AttributeValue.objects.get_or_create(
        attribute=attribute,
        value=str(attr_value),
        defaults={'display_name': str(attr_value)}
    )
    
    # 4. 创建SKU属性值关联
    SKUAttributeValue.objects.get_or_create(
        sku=sku,
        attribute=attribute,
        defaults={'attribute_value': attribute_value}
    )
    
    # 5. 确保SPU属性关联
    self._ensure_spu_attribute(sku.spu, attribute)
```

## **SPU属性关联管理**

### **自动关联策略**
```python
# ✅ DO: 自动创建SPU属性关联
def _ensure_spu_attribute(self, spu: SPU, attribute: Attribute):
    """确保SPU关联了指定属性"""
    SPUAttribute.objects.get_or_create(
        spu=spu,
        attribute=attribute,
        defaults={
            'is_required': attribute.code in REQUIRED_ATTRIBUTES,
            'order': self._get_attribute_order(attribute.code)
        }
    )
```

### **属性显示顺序**
```python
# ✅ DO: 规范的属性显示顺序
ATTRIBUTE_ORDER_MAPPING = {
    'WIDTH': 1,      # 宽度（最重要）
    'HEIGHT': 2,     # 高度
    'DEPTH': 3,      # 深度
    'CABINET_TYPE': 4,   # 柜体类型
    'DOOR_DIRECTION': 5, # 门板方向
    'CONFIG_CODE': 6,    # 配置代码
    'ENGLISH_NAME': 7,   # 英文名称
    'PRICE_LEVEL_1': 8,  # 价格等级
    'PRICE_LEVEL_2': 9,
    'PRICE_LEVEL_3': 10,
    'PRICE_LEVEL_4': 11,
    'PRICE_LEVEL_5': 12,
    'REMARKS': 13,       # 备注（最后）
}
```

## **属性值处理规范**

### **数据清理和标准化**
```python
# ✅ DO: 属性值标准化处理
def _normalize_attribute_value(self, attr_name: str, value) -> str:
    """标准化属性值"""
    if isinstance(value, (int, float)):
        # 数字类型：去除不必要的小数点
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)
    elif isinstance(value, str):
        # 字符串类型：去除首尾空格
        value = value.strip()
        
        # 特殊处理：门板方向映射
        if attr_name == '开门方向':
            return DOOR_SWING_MAPPING.get(value, value)
        
        return value
    else:
        return str(value)
```

### **空值处理策略**
- **跳过空值**：`None`、空字符串、`'-'`等跳过处理
- **默认值处理**：为重要属性提供合理默认值
- **继承处理**：从SPU或分类继承默认属性值

## **属性筛选和查询优化**

### **可筛选属性配置**
```python
# ✅ DO: 定义可筛选属性
FILTERABLE_ATTRIBUTES = [
    '宽度', '高度', '深度',      # 尺寸属性
    '柜体类型', '门板方向',       # 分类属性
    '系列',                     # 产品系列
]
```

### **查询优化**
```python
# ✅ DO: 优化属性查询
def get_sku_attributes(self, sku_id):
    """获取SKU的所有属性（优化版）"""
    return SKUAttributeValue.objects.filter(
        sku_id=sku_id
    ).select_related(
        'attribute', 'attribute_value'
    ).order_by(
        'attribute__order', 'attribute__name'
    )
```

## **Admin界面集成**

### **属性管理界面**
```python
# ✅ DO: 完善的属性管理
@admin.register(Attribute)
class AttributeAdmin(BaseModelAdmin):
    list_display = [
        'name', 'code', 'type', 'is_required', 
        'is_filterable', 'get_values_count'
    ]
    list_filter = ['type', 'is_required', 'is_filterable']
    search_fields = ['name', 'code']
    ordering = ['order', 'name']
```

### **SKU属性值内联编辑**
```python
# ✅ DO: SKU属性值内联管理
class SKUAttributeValueInline(admin.TabularInline):
    model = SKUAttributeValue
    extra = 0
    autocomplete_fields = ['attribute', 'attribute_value']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'attribute', 'attribute_value'
        )
```

## **数据验证规范**

### **属性值验证**
```python
# ✅ DO: 属性值验证
def validate_attribute_value(self, attribute: Attribute, value: str):
    """验证属性值的有效性"""
    if attribute.type == 'number':
        try:
            float(value)
        except ValueError:
            raise ValidationError(f"属性 {attribute.name} 的值必须是数字")
    
    elif attribute.type == 'select':
        # 验证是否在预定义值范围内
        valid_values = attribute.values.filter(
            is_active=True
        ).values_list('value', flat=True)
        
        if value not in valid_values:
            raise ValidationError(
                f"属性 {attribute.name} 的值必须在 {list(valid_values)} 中选择"
            )
```

### **必填属性检查**
```python
# ✅ DO: 必填属性验证
def validate_required_attributes(self, sku: SKU):
    """验证SKU是否设置了所有必填属性"""
    required_attrs = sku.spu.spuattribute_set.filter(
        is_required=True
    ).values_list('attribute__code', flat=True)
    
    existing_attrs = sku.sku_attribute_values.values_list(
        'attribute__code', flat=True
    )
    
    missing_attrs = set(required_attrs) - set(existing_attrs)
    if missing_attrs:
        raise ValidationError(f"缺少必填属性: {', '.join(missing_attrs)}")
```

## **性能优化建议**

### **查询优化**
- **使用select_related**：预加载关联的属性和属性值
- **使用prefetch_related**：批量加载多对多关系
- **添加数据库索引**：为常用查询字段添加索引

### **缓存策略**
- **属性定义缓存**：缓存常用的属性定义
- **属性值缓存**：缓存热门的属性值选项
- **查询结果缓存**：缓存复杂的属性查询结果

---

遵循这些规范可以确保产品属性系统的一致性、可维护性和高性能。所有属性相关的开发都应参考这些最佳实践。
