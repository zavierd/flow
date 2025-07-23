"""
Products Models 配置
原始文件已被模块化拆分到 products/models/ 目录中
此文件用于保持向后兼容性和统一的导入入口

模块化结构说明：
- base.py: 基础模型类和公共配置
- mixins.py: 可复用的模型混入类
- category_models.py: 分类相关模型
- brand_models.py: 品牌相关模型  
- attribute_models.py: 属性相关模型
- spu_models.py: SPU相关模型
- sku_models.py: SKU相关模型
- pricing_models.py: 定价相关模型
- import_models.py: 导入相关模型

优化说明：
1. 按业务域拆分模型，每个文件不超过500行
2. 使用混入类提供可复用功能
3. 抽象基类减少重复代码
4. 统一的验证和业务逻辑
5. 模块化导入保持向后兼容
"""

# 导入所有的模型配置
from products.models import *

# 保持向后兼容性的导入
# 确保原有的导入语句仍然可以正常工作
# 例如：from products.models import Category, Brand, SKU 等
