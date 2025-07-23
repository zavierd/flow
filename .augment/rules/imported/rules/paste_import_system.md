---
description: 粘贴导入系统开发规范和用户体验优化
globs: templates/import/*.html, static/js/import*.js, products/views.py
alwaysApply: true
---

# 粘贴导入系统开发规范

## **核心设计原则**

### **用户体验优先**
- **默认粘贴模式**：页面加载时自动选中粘贴导入
- **3步完成流程**：选择模板 → 粘贴数据 → 开始导入
- **即时反馈**：实时显示处理结果和错误信息
- **智能识别**：自动检测Markdown、CSV、制表符格式

### **技术架构原则**
- **无外部依赖**：使用原生JavaScript，避免jQuery等依赖
- **统一API接口**：所有导入方式使用同一个后端接口
- **健壮解析**：支持多种数据格式的智能解析
- **错误隔离**：单行错误不影响整体导入

## **前端实现规范**

### **数据格式检测**
```javascript
// ✅ DO: 智能格式检测
function processPasteData(pasteData) {
    if (pasteData.includes('|') && (pasteData.includes('---') || pasteData.includes(':---'))) {
        // Markdown表格格式
        return parseMarkdownTable(pasteData);
    } else if (pasteData.includes('\t')) {
        // 制表符分隔格式（Excel复制）
        return parseTabDelimitedData(pasteData);
    } else if (pasteData.includes(',')) {
        // CSV格式
        return pasteData;
    } else {
        throw new Error('无法识别的数据格式');
    }
}
```

### **Markdown表格解析**
```javascript
// ✅ DO: 健壮的Markdown表格解析
function parseMarkdownTable(markdownData) {
    const lines = markdownData.trim().split('\n');
    const csvLines = [];
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        // 跳过分隔行
        if (line.includes('---') || line.includes(':---')) {
            continue;
        }
        
        // 处理表格行
        if (line.startsWith('|') && line.endsWith('|')) {
            const cells = line.slice(1, -1).split('|').map(cell => {
                let cleanCell = cell.trim();
                
                // 处理<br>换行符
                cleanCell = cleanCell.replace(/<br\s*\/?>/gi, '\n');
                
                // 处理HTML标签
                cleanCell = cleanCell.replace(/<[^>]*>/g, '');
                
                // CSV转义
                if (cleanCell.includes(',') || cleanCell.includes('\n') || cleanCell.includes('"')) {
                    cleanCell = '"' + cleanCell.replace(/"/g, '""') + '"';
                }
                
                return cleanCell;
            });
            csvLines.push(cells.join(','));
        }
    }
    
    return csvLines.join('\n');
}
```

### **用户界面优化**
```javascript
// ✅ DO: 默认状态设置
document.addEventListener('DOMContentLoaded', function() {
    // 默认选中AI数据格式
    const aiDataRadio = document.querySelector('input[name="templateType"][value="ai_data"]');
    if (aiDataRadio) {
        aiDataRadio.checked = true;
    }
    
    // 默认选中粘贴导入
    const pasteRadio = document.querySelector('input[name="importMethod"][value="paste"]');
    if (pasteRadio) {
        pasteRadio.checked = true;
        toggleImportMethod('paste');
    }
});
```

## **后端集成规范**

### **统一API接口**
```python
# ✅ DO: 统一的导入接口
@csrf_exempt
@require_POST
def import_ai_data(request):
    """统一的数据导入接口，支持多种模板类型"""
    # 获取模板类型
    template_type = request.POST.get('template_type', 'ai_data')
    
    # 处理文件上传或直接数据
    if 'file' in request.FILES:
        # 文件上传处理
        uploaded_file = request.FILES['file']
        csv_content = process_uploaded_file(uploaded_file)
    elif 'csv_data' in request.POST:
        # 直接数据处理
        csv_content = request.POST['csv_data']
    
    # 使用统一的导入服务
    import_service = AIDataImportService(task)
    result = import_service.process_ai_data_import(csv_content)
    
    return JsonResponse(result)
```

### **多格式文件支持**
```python
# ✅ DO: 支持多种文件格式
def process_uploaded_file(uploaded_file):
    """处理上传的文件，支持CSV、Excel格式"""
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    
    if file_extension == '.csv':
        return uploaded_file.read().decode('utf-8')
    elif file_extension in ['.xlsx', '.xls']:
        # 处理Excel文件
        import pandas as pd
        df = pd.read_excel(BytesIO(uploaded_file.read()))
        return df.to_csv(index=False)
    else:
        raise ValueError(f'不支持的文件格式: {file_extension}')
```

## **错误处理规范**

### **前端错误处理**
```javascript
// ✅ DO: 完善的错误处理
async function submitImport() {
    try {
        // 数据处理
        const csvData = processPasteData(pasteData);
        
        // 发送请求
        const response = await fetch('/products/ai-data/import/', {
            method: 'POST',
            body: formData,
            headers: { 'X-CSRFToken': getCsrfToken() }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess(result.message);
        } else {
            showError(result.error);
        }
        
    } catch (error) {
        console.error('导入失败:', error);
        showError(`导入失败: ${error.message}`);
    }
}
```

### **后端错误处理**
```python
# ✅ DO: 详细的错误信息
try:
    result = import_service.process_ai_data_import(csv_content)
    return JsonResponse({
        'success': result['success'],
        'task_id': task.id,
        'total_rows': result['total_rows'],
        'success_rows': result['success_rows'],
        'error_rows': result['error_rows'],
        'message': f'导入完成：成功 {result["success_rows"]} 行，失败 {result["error_rows"]} 行'
    })
except Exception as e:
    logger.error(f"数据导入失败: {str(e)}")
    return JsonResponse({
        'success': False,
        'error': f'导入失败: {str(e)}'
    }, status=500)
```

## **性能优化规范**

### **前端性能优化**
- **延迟加载**：大数据量时使用分批处理
- **内存管理**：及时清理临时数据
- **用户反馈**：显示处理进度条

### **后端性能优化**
- **流式处理**：逐行处理大文件
- **事务控制**：合理使用数据库事务
- **内存优化**：避免一次性加载大量数据

## **用户体验优化**

### **界面交互优化**
```javascript
// ✅ DO: 智能任务名称生成
function generateDefaultTaskName() {
    const now = new Date();
    const timestamp = now.toISOString().slice(0, 19).replace(/[-:]/g, '').replace('T', '_');
    const templateType = document.querySelector('input[name="templateType"]:checked').value;
    const typeName = templateType === 'ai_data' ? 'AI数据' : 'Royana';
    return `${typeName}导入_${timestamp}`;
}
```

### **状态反馈优化**
- **即时反馈**：导入过程中显示实时状态
- **结果展示**：清晰显示成功/失败统计
- **错误详情**：提供详细的错误信息和修复建议

## **测试和验证**

### **功能测试覆盖**
- **格式支持测试**：Markdown、CSV、制表符格式
- **大数据量测试**：测试性能和稳定性
- **错误场景测试**：各种异常情况处理
- **用户体验测试**：完整的用户操作流程

### **兼容性测试**
- **浏览器兼容性**：主流浏览器支持
- **设备兼容性**：桌面和移动设备
- **数据格式兼容性**：各种数据源格式

## **维护和扩展**

### **代码维护原则**
- **模块化设计**：功能模块独立，便于维护
- **配置驱动**：通过配置文件管理业务规则
- **文档完善**：详细的代码注释和使用说明

### **功能扩展指南**
- **新格式支持**：添加新的数据格式解析器
- **新模板类型**：扩展模板类型选择
- **增强验证**：添加更多数据验证规则

---

遵循这些规范可以确保粘贴导入系统的用户体验、性能和可维护性。所有相关开发都应参考这些最佳实践。
