"""
Products Models 模块
将原本臃肿的models.py文件拆分为多个专门的模块
遵循Django模块化开发规范，每个模块不超过500行代码
"""

# 导入基础模型和混入类
from .base import *
from .mixins import *

# 导入各个业务域的模型
from .category_models import Category
from .brand_models import Brand
from .attribute_models import Attribute, AttributeValue
from .spu_models import SPU, SPUAttribute, SPUDimensionTemplate
from .sku_models import SKU, SKUAttributeValue, ProductImage
from .pricing_models import ProductsPricingRule, ProductsDimension
from .import_models import ImportTask, ImportTemplate, ImportError

# 确保所有模型都可以从 products.models 直接导入
__all__ = [
    # 分类相关
    'Category',
    
    # 品牌相关
    'Brand',
    
    # 属性相关
    'Attribute',
    'AttributeValue',
    
    # SPU相关
    'SPU',
    'SPUAttribute', 
    'SPUDimensionTemplate',
    
    # SKU相关
    'SKU',
    'SKUAttributeValue',
    'ProductImage',
    
    # 定价相关
    'ProductsPricingRule',
    'ProductsDimension',
    
    # 导入相关
    'ImportTask',
    'ImportTemplate', 
    'ImportError',
] 