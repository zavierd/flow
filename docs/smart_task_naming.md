# 🏷️ 智能任务名称生成功能

## 🎯 功能概述

系统现在支持智能任务名称生成，用户无需手动填写任务名称，系统会根据导入方式、模板类型和当前时间自动生成有意义的任务名称。

## 📋 命名规则

### 1. **基本格式**
```
{导入类型}_{日期}_{时间}
```

### 2. **导入类型规则**
根据模板类型和导入方式的组合生成：

| 模板类型 | 导入方式 | 生成名称前缀 |
|----------|----------|-------------|
| AI数据格式 | 直接粘贴 | `AI数据粘贴导入` |
| AI数据格式 | 文件上传 | `AI数据文件导入` |
| Royana传统格式 | 直接粘贴 | `Royana粘贴导入` |
| Royana传统格式 | 文件上传 | `Royana文件导入` |

### 3. **时间格式**
- **日期格式**：`YYYYMMDD`（如：20250120）
- **时间格式**：`HHMM`（如：1423）

## 🌟 示例名称

### AI数据格式 + 直接粘贴
```
AI数据粘贴导入_20250120_1423
```

### AI数据格式 + 文件上传
```
AI数据文件导入_20250120_1456
```

### Royana传统格式 + 直接粘贴
```
Royana粘贴导入_20250120_0930
```

### Royana传统格式 + 文件上传
```
Royana文件导入_20250120_1615
```

## 🔧 技术实现

### 1. **JavaScript生成函数**
```javascript
function generateDefaultTaskName() {
    const now = new Date();
    const templateType = document.querySelector('input[name="templateType"]:checked').value;
    const importMethod = document.querySelector('input[name="importMethod"]:checked').value;
    
    // 格式化日期时间
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hour = String(now.getHours()).padStart(2, '0');
    const minute = String(now.getMinutes()).padStart(2, '0');
    
    const dateStr = `${year}${month}${day}`;
    const timeStr = `${hour}${minute}`;
    
    // 根据模板类型和导入方式生成名称
    let prefix = '';
    if (templateType === 'ai_data') {
        prefix = importMethod === 'paste' ? 'AI数据粘贴导入' : 'AI数据文件导入';
    } else {
        prefix = importMethod === 'paste' ? 'Royana粘贴导入' : 'Royana文件导入';
    }
    
    return `${prefix}_${dateStr}_${timeStr}`;
}
```

### 2. **动态Placeholder更新**
```javascript
function updateTaskNamePlaceholder() {
    const taskNameInput = document.getElementById('taskName');
    const defaultName = generateDefaultTaskName();
    taskNameInput.placeholder = `留空将自动生成：${defaultName}`;
}
```

### 3. **自动填充逻辑**
```javascript
// 在表单提交时检查并自动填充
let taskName = document.getElementById('taskName').value.trim();

if (!taskName) {
    taskName = generateDefaultTaskName();
    document.getElementById('taskName').value = taskName;
}
```

## ✨ 用户体验优化

### 1. **实时预览**
- 用户切换模板类型或导入方式时，placeholder会实时更新
- 显示当前设置下将生成的任务名称

### 2. **智能提示**
- 输入框下方显示提示：`💡 留空将根据导入方式和时间自动生成任务名称`
- Placeholder显示具体的生成示例

### 3. **灵活选择**
- 用户可以选择使用自动生成的名称
- 也可以手动输入自定义名称
- 系统会优先使用用户输入的名称

## 🎯 使用场景

### 1. **快速导入**
用户专注于数据准备和导入，无需考虑任务命名

### 2. **批量操作**
进行多次导入时，自动生成的时间戳确保名称唯一性

### 3. **团队协作**
统一的命名规范便于团队成员识别和管理导入任务

## 📊 优势分析

### 1. **提升效率**
- 减少用户输入，专注核心操作
- 避免命名纠结，提高操作流畅度

### 2. **规范管理**
- 统一的命名格式便于任务管理
- 时间戳确保任务名称的唯一性

### 3. **信息丰富**
- 名称包含导入类型、方式、时间等关键信息
- 便于后续查找和分析

### 4. **用户友好**
- 可选择使用自动生成或手动输入
- 实时预览生成的名称

## 🔄 动态更新机制

### 1. **触发条件**
- 页面加载时初始化
- 切换模板类型时更新
- 切换导入方式时更新

### 2. **更新内容**
- 输入框的placeholder文本
- 生成名称的前缀部分
- 时间戳保持实时

### 3. **事件绑定**
```javascript
// 模板类型切换事件
templateRadios.forEach(radio => {
    radio.addEventListener('change', function() {
        // ... 其他逻辑
        updateTaskNamePlaceholder();
    });
});

// 导入方式切换事件
importMethodRadios.forEach(radio => {
    radio.addEventListener('change', function() {
        toggleImportMethod();
        updateTaskNamePlaceholder();
    });
});
```

## 🎉 总结

智能任务名称生成功能通过以下方式提升用户体验：

1. **🚀 零输入成本**：用户无需思考任务命名
2. **📋 规范统一**：自动生成的名称格式统一
3. **⏰ 时间标识**：包含精确的时间信息
4. **🔧 灵活可选**：支持自动生成和手动输入
5. **📊 信息丰富**：名称包含关键的导入信息

现在用户可以享受更加便捷的导入体验：**选择模板 → 粘贴数据 → 一键导入**，系统会自动处理所有细节！🎯
