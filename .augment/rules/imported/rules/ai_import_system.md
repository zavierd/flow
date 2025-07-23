---
description: AI数据导入系统开发规范和最佳实践
globs: products/services/ai_*.py, products/config/ai_*.py, templates/import/*.html
alwaysApply: true
---

# AI数据导入系统开发规范

## **核心架构原则**

### **服务层设计**
- **专用服务类**：每种数据格式使用独立的服务类
  ```python
  # ✅ DO: 专用服务类
  class AIDataImportService:
      """专门处理AI模型输出的15列标准化数据格式"""
      
  class RoyanaImportService:
      """处理传统Royana格式数据"""
  ```

- **配置驱动**：使用配置文件管理字段映射和验证规则
  ```python
  # ✅ DO: 配置文件驱动
  from products.config.ai_data_mapping import (
      AI_DATA_FIELD_MAPPING, CABINET_TYPE_MAPPING, DOOR_SWING_MAPPING
  )
  ```

### **数据处理流水线**
- **分层处理**：解析 → 预处理 → 验证 → 转换 → 存储
- **事务安全**：每行数据使用独立事务
- **错误隔离**：单行错误不影响其他数据处理

## **AI数据格式规范**

### **标准15列格式**
```python
# ✅ DO: 标准字段映射
AI_DATA_FIELD_MAPPING = {
    '产品描述 (Description)': '产品描述',
    '产品编码 (Code)': '产品编码',
    '系列 (Series)': '系列',
    '类型代码 (Type_Code)': '类型代码',
    '宽度 (Width_cm)': '宽度',
    '高度 (Height_cm)': '高度',
    '深度 (Depth_cm)': '深度',
    '配置代码 (Config_Code)': '配置代码',
    '开门方向 (Door_Swing)': '开门方向',
    '等级Ⅰ': '价格等级I',
    '等级Ⅱ': '价格等级II',
    '等级Ⅲ': '价格等级III',
    '等级Ⅳ': '价格等级IV',
    '等级Ⅴ': '价格等级V',
    '备注 (Remarks)': '备注'
}
```

### **数据预处理规则**
- **价格清理**：去除逗号分隔符，转换为数字
- **描述解析**：提取中英文对照信息
- **门板方向映射**：标准化门板方向描述
- **空值处理**：智能处理空单元格和默认值

## **属性系统规范**

### **属性创建模式**
```python
# ✅ DO: 规范的属性创建
def _create_sku_attribute_value(self, sku: SKU, attr_name: str, attr_value):
    # 生成标准编码
    attr_code = self._generate_attribute_code(attr_name)
    
    # 创建属性
    attribute, created = Attribute.objects.get_or_create(
        code=attr_code,
        defaults={
            'name': attr_name,
            'type': self._determine_attribute_type(attr_value),
            'is_required': False,
            'is_filterable': attr_name in FILTERABLE_ATTRIBUTES
        }
    )
    
    # 确保SPU关联
    self._ensure_spu_attribute(sku.spu, attribute)
```

### **属性编码映射**
```python
# ✅ DO: 标准化属性编码
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
    # ... 更多映射
}
```

### **智能类型判断**
```python
# ✅ DO: 智能属性类型判断
def _determine_attribute_type(self, value) -> str:
    if isinstance(value, (int, float)):
        return 'number'
    elif isinstance(value, str):
        if value in ['左开', '右开', '左开/右开', '双开', '-']:
            return 'select'
        elif len(value) < 50:
            return 'select'
        else:
            return 'text'
    else:
        return 'text'
```

## **数据导入最佳实践**

### **CSV解析处理**
- **支持多格式**：Markdown表格、制表符分隔、标准CSV
- **智能识别**：自动检测数据格式
- **错误处理**：详细的解析错误信息

```python
# ✅ DO: 健壮的CSV解析
def _parse_ai_csv_data(self, csv_content: str) -> Optional[List[Dict]]:
    try:
        # 检测并处理Markdown表格
        if '|' in csv_content and ('---' in csv_content or ':---' in csv_content):
            csv_content = self._convert_markdown_to_csv(csv_content)
        
        # 使用csv.DictReader解析
        reader = csv.DictReader(StringIO(csv_content))
        return list(reader)
    except Exception as e:
        logger.error(f"CSV解析失败: {str(e)}")
        return None
```

### **产品数据创建流程**
1. **品牌管理**：自动创建或获取ROYANA品牌
2. **分类创建**：基于柜体类型智能分类
3. **SPU生成**：使用系列+类型+尺寸生成SPU
4. **SKU创建**：创建具体可销售产品
5. **属性关联**：建立完整的属性关系

### **错误处理策略**
```python
# ✅ DO: 完善的错误处理
def _add_error(self, row_number: int, field: str, value: str, message: str, row_data: Dict):
    error = {
        'row_number': row_number,
        'field': field,
        'value': value,
        'message': message,
        'row_data': row_data
    }
    self.errors.append(error)
    
    # 保存到数据库
    ImportError.objects.create(
        task=self.task,
        row_number=row_number,
        field_name=field,
        field_value=value,
        error_message=message,
        row_data=json.dumps(row_data, ensure_ascii=False)
    )
```

## **前端集成规范**

### **模板类型选择**
- **默认选中**：AI数据格式为默认选项
- **智能切换**：根据用户选择调整界面
- **统一接口**：所有格式使用同一个导入接口

### **用户体验优化**
- **粘贴优先**：默认启用直接粘贴模式
- **即时反馈**：实时显示导入进度和结果
- **错误提示**：详细的错误信息和修复建议

## **性能优化原则**

### **无外部依赖**
- **✅ DO**: 使用Python标准库csv模块
- **❌ DON'T**: 依赖pandas等重型库

### **内存优化**
- **流式处理**：逐行处理大文件
- **事务控制**：合理使用数据库事务
- **查询优化**：使用select_related和prefetch_related

## **测试和验证**

### **数据完整性检查**
- **属性关联**：验证SPU-属性关联完整性
- **数据类型**：确认属性类型正确设置
- **关系完整**：检查SKU-属性值关联

### **功能测试覆盖**
- **格式支持**：测试Markdown、CSV、制表符格式
- **错误处理**：测试各种异常情况
- **性能测试**：大批量数据导入测试

## **扩展开发指南**

### **新增数据格式**
1. 创建专用服务类
2. 定义字段映射配置
3. 实现数据预处理逻辑
4. 添加前端模板选项
5. 编写测试用例

### **属性系统扩展**
- **新属性类型**：扩展ATTRIBUTE_TYPES选择
- **验证规则**：添加属性值验证逻辑
- **显示优化**：优化属性在管理界面的显示

---

遵循这些规范可以确保AI数据导入系统的稳定性、可维护性和扩展性。所有新功能开发都应优先参考这些模式和最佳实践。
