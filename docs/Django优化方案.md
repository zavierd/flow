我完全理解你的感受！Django admin的这些细节确实让人头疼。让我总结一下我们遇到的复杂性：

## Django Admin 的复杂性问题

### 1. **多层覆盖机制**
- 模型的 `verbose_name` 
- Inline类的 `verbose_name` 属性
- Inline类的 `get_verbose_name()` 方法
- 不同层级的优先级不明确

### 2. **缓存和重启问题**
- Python代码更改需要重启服务器
- 静态文件更改需要 `collectstatic`
- 有时还有Django内部缓存

### 3. **样式应用的不一致性**
- CSS选择器的特异性问题
- Django admin自带样式的覆盖
- 不同浏览器的缓存

### 4. **文档不够详细**
- 官方文档对这些细节描述不够
- 很多行为需要通过试错才能发现

## 建议的改进方案

为了减少这种复杂性，我建议：

1. **创建一个开发工具脚本**：
```python
# 创建 dev_tools.py
import os
import subprocess

def restart_and_collect():
    """重启服务器并收集静态文件"""
    subprocess.run(["pkill", "-f", "python manage.py runserver"])
    subprocess.run(["python", "manage.py", "collectstatic", "--noinput"])
    subprocess.run(["python", "manage.py", "runserver"], background=True)
```

2. **标准化命名约定**：
   - 所有inline都使用 `get_verbose_name()` 方法
   - 统一的CSS命名规范

3. **创建基础Inline类**：
```python
class BaseInline(admin.TabularInline):
    def get_verbose_name(self):
        return self.verbose_name_override or super().get_verbose_name()
```

你觉得这样的改进方案怎么样？或者你有其他想法来简化这个流程？