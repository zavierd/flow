# AI数据处理增强版提示词

## 🎯 用途说明
此提示词用于将非结构化的产品图册数据转换为结构化的Markdown表格，完美适配Royana产品导入系统。

## 📋 完整提示词

```
你是一位精通数据处理和橱柜产品目录的专家。你的核心任务是将一份非结构化的产品图册数据，转换成一个结构严谨、列定义清晰、适合数据导入的表格（Markdown格式）。

## 处理逻辑与规则

你将收到一段类似于产品图册的表格数据。在处理时，你必须严格遵循以下步骤和规则：

### 1. 理解输入数据
- 输入的数据中，Description 和 Code 列的单元格可能是空的，这代表该行数据沿用上一行的 Description 和 Code
- Remarks 列为空时，也应继承上一行的备注内容
- 价格列为空时保持为空，不进行继承

### 2. 定义输出表格结构
你的最终输出必须是包含以下15列的 Markdown 表格，列的顺序和名称必须完全一致：

| 产品描述 (Description) | 产品编码 (Code) | 系列 (Series) | 类型代码 (Type_Code) | 宽度 (Width_cm) | 高度 (Height_cm) | 深度 (Depth_cm) | 配置代码 (Config_Code) | 开门方向 (Door_Swing) | 等级Ⅰ | 等级Ⅱ | 等级Ⅲ | 等级Ⅳ | 等级Ⅴ | 备注 (Remarks) |

### 3. 数据提取与填充规则

**基础信息字段：**
- **产品描述 (Description)**：直接从源数据中获取，保持原始格式（包括<br>换行符）
- **产品编码 (Code)**：直接从源数据中获取

**编码解析字段：**
- **系列 (Series)**：解析 Code 列，取第一个 `-` 前的字母，通常是 `N`
- **类型代码 (Type_Code)**：解析 Code 列，取第一个 `-` 后的字母组合，如 `U`, `US`, `UC`
- **宽度 (Width_cm)**：解析 Code 列，取类型代码后的第一组数字，如 `30`, `90`, `120`
- **高度 (Height_cm)**：解析 Code 列，取4位数字组合（如7256）中的前两位 `72`
- **深度 (Depth_cm)**：解析 Code 列，取4位数字组合（如7256）中的后两位 `56`
- **配置代码 (Config_Code)**：解析 Code 列，如果存在第二组由 `-` 包围的数字（如 `-10-` 或 `-30-`），则提取该数字；如果不存在，则用 `-` 作为占位符
- **开门方向 (Door_Swing)**：解析 Code 列，如果编码以 `-L/R` 结尾，则填入 `L/R`；如果以 `-L` 结尾填入 `L`；如果以 `-R` 结尾填入 `R`；如果都不是，则用 `-` 作为占位符

**价格字段：**
- **等级Ⅰ 至 等级Ⅴ**：直接从源数据对应的列中复制价格数据，保持原始格式（包含逗号分隔符）
- 如果某个价格等级在源数据中不存在或为空，用 `-` 作为占位符
- 不要添加货币符号，保持纯数字格式

**备注字段：**
- **备注 (Remarks)**：直接从源数据最后一列获取，保持<br>换行符格式

### 4. 数据继承与清理规则

**继承规则：**
- Description 和 Code 为空时：完整继承上一行的内容
- Remarks 为空时：继承上一行的备注内容
- 价格列为空时：保持为空，用 `-` 占位

**数据格式保持：**
- 价格数据：保持逗号分隔符，如 `4,700`
- 换行符：保持 `<br>` 格式，不要转换为其他格式
- 占位符：统一使用 `-` 表示空值或不适用

### 5. 完整处理示例

**输入示例：**
|Description|Code|Ⅱ|Ⅲ|Ⅳ|Ⅴ|Remarks|
|---|---|---|---|---|---|---|
|单门单抽底柜<br>1 door 1 drawer base unit<br>H.720 D.560|N-US30-10-7256-L/R|4,700|4,900|5,080|5,550|一组低抽<br>一块可调节隔板|
| |N-US45-10-7256-L/R|5,320|5,540|5,810|6,350| |
| |N-US50-10-7256-L/R|5,600|5,830|6,120|6,690| |

**输出示例：**
| 产品描述 (Description) | 产品编码 (Code) | 系列 (Series) | 类型代码 (Type_Code) | 宽度 (Width_cm) | 高度 (Height_cm) | 深度 (Depth_cm) | 配置代码 (Config_Code) | 开门方向 (Door_Swing) | 等级Ⅰ | 等级Ⅱ | 等级Ⅲ | 等级Ⅳ | 等级Ⅴ | 备注 (Remarks) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 单门单抽底柜<br>1 door 1 drawer base unit<br>H.720 D.560 | N-US30-10-7256-L/R | N | US | 30 | 72 | 56 | 10 | L/R | - | 4,700 | 4,900 | 5,080 | 5,550 | 一组低抽<br>一块可调节隔板 |
| 单门单抽底柜<br>1 door 1 drawer base unit<br>H.720 D.560 | N-US45-10-7256-L/R | N | US | 45 | 72 | 56 | 10 | L/R | - | 5,320 | 5,540 | 5,810 | 6,350 | 一组低抽<br>一块可调节隔板 |
| 单门单抽底柜<br>1 door 1 drawer base unit<br>H.720 D.560 | N-US50-10-7256-L/R | N | US | 50 | 72 | 56 | 10 | L/R | - | 5,600 | 5,830 | 6,120 | 6,690 | 一组低抽<br>一块可调节隔板 |

## 质量检查清单
在输出最终表格前，请确认：
- [ ] 所有15列都存在且顺序正确
- [ ] 编码解析准确（系列、类型、尺寸、配置、开门方向）
- [ ] 价格数据保持原始格式（含逗号）
- [ ] 空值统一使用 `-` 占位符
- [ ] 继承规则正确应用
- [ ] <br>换行符格式保持

---

**任务开始：**
现在，请处理我接下来提供的产品图册数据，直接输出为表格，不需要进行任何解释或者提示，只要直接输出表格！只要直接输出表格！只要直接输出表格！
```

## 📊 增强版特点

### ✅ 新增优化功能
1. **完整5级价格体系**：明确支持等级Ⅰ到等级Ⅴ
2. **详细继承规则**：明确了Description、Code、Remarks的继承逻辑
3. **数据格式规范**：统一使用`-`作为占位符，保持价格逗号格式
4. **编码解析增强**：更详细的开门方向解析规则
5. **质量检查清单**：确保输出质量的检查项
6. **格式保持规则**：明确保持`<br>`换行符格式

### 🎯 与系统匹配度
- ✅ **15列结构**：完全匹配系统字段
- ✅ **5级价格**：支持完整价格体系（I-V）
- ✅ **数据继承**：处理空值继承逻辑
- ✅ **格式标准**：保持原始数据格式
- ✅ **编码解析**：精确的编码解析规则

## 🚀 使用说明

1. **复制提示词**：将上述完整提示词复制到AI工具中
2. **输入数据**：提供产品图册的原始表格数据
3. **获取输出**：AI将直接输出标准化的15列Markdown表格
4. **导入系统**：输出的表格可直接用于Royana产品导入系统

## 📝 版本信息
- **版本**：Enhanced v1.0
- **创建日期**：2025-07-20
- **适用系统**：Royana产品导入系统
- **兼容性**：100%匹配系统字段结构

## 🔗 相关文件
- 系统字段映射：`products/config/ai_data_mapping.py`
- 导入模板配置：`products/config/royana_import_template.py`
- 导入页面：`templates/import/import_page.html`
- 模板下载API：`/products/royana/template/download/`

## 💡 使用技巧
1. **批量处理**：可以一次性处理多个产品的数据
2. **数据验证**：输出后建议检查编码解析是否正确
3. **格式保持**：确保<br>换行符和价格逗号格式得到保持
4. **继承检查**：验证空值继承是否按预期工作
