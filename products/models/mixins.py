"""
Models 混入类模块
提供可复用的模型功能和方法
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class CreatedByMixin(models.Model):
    """
    创建人混入类
    为模型添加创建人字段和相关方法
    """
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="创建人",
        db_comment="创建此记录的用户ID"
    )

    class Meta:
        abstract = True

    def set_creator(self, user):
        """设置创建人"""
        if not self.pk and not self.created_by:
            self.created_by = user


class TreeMixin:
    """
    树形结构混入类
    为MPTT模型提供常用的树形操作方法
    """
    
    def get_full_path(self, separator=" > "):
        """获取完整的路径"""
        if hasattr(self, 'parent') and self.parent:
            return f"{self.parent.get_full_path(separator)}{separator}{self.name}"
        return self.name
        
    def get_level(self):
        """获取层级深度"""
        level = 0
        current = self
        while hasattr(current, 'parent') and current.parent:
            level += 1
            current = current.parent
        return level
    
    def get_children_count(self):
        """获取直接子节点数量"""
        if hasattr(self, 'children'):
            return self.children.filter(is_active=True).count()
        return 0
    
    def get_all_descendants_count(self):
        """获取所有后代节点数量"""
        if hasattr(self, 'get_descendants'):
            return self.get_descendants().filter(is_active=True).count()
        return 0


class PriceMixin(models.Model):
    """
    价格相关混入类
    为包含价格的模型提供价格计算和验证方法
    """
    
    class Meta:
        abstract = True
    
    def validate_price_logic(self):
        """验证价格逻辑"""
        errors = {}
        
        # 验证成本价不能高于售价
        if (hasattr(self, 'cost_price') and hasattr(self, 'price') and 
            self.cost_price and self.price and self.cost_price > self.price):
            errors['cost_price'] = "成本价不能高于售价"
            
        # 验证市场价不能低于售价
        if (hasattr(self, 'market_price') and hasattr(self, 'price') and 
            self.market_price and self.price and self.market_price < self.price):
            errors['market_price'] = "市场价不能低于售价"
        
        if errors:
            raise ValidationError(errors)
    
    def get_profit_margin(self):
        """计算利润率"""
        if (hasattr(self, 'cost_price') and hasattr(self, 'price') and 
            self.cost_price and self.price and self.cost_price > 0):
            return ((self.price - self.cost_price) / self.cost_price) * 100
        return 0
    
    def get_discount_rate(self):
        """计算折扣率"""
        if (hasattr(self, 'market_price') and hasattr(self, 'price') and 
            self.market_price and self.price and self.market_price > 0):
            return ((self.market_price - self.price) / self.market_price) * 100
        return 0


class StockMixin(models.Model):
    """
    库存相关混入类
    为包含库存的模型提供库存状态和预警方法
    """
    
    class Meta:
        abstract = True
    
    @property
    def is_in_stock(self):
        """是否有库存"""
        return hasattr(self, 'stock_quantity') and self.stock_quantity > 0

    @property
    def is_low_stock(self):
        """是否库存不足"""
        return (hasattr(self, 'stock_quantity') and hasattr(self, 'min_stock') and 
                self.stock_quantity <= self.min_stock)
    
    @property
    def stock_status(self):
        """库存状态"""
        if not self.is_in_stock:
            return "缺货"
        elif self.is_low_stock:
            return "库存不足"
        else:
            return "库存充足"
    
    def update_stock(self, quantity, operation='reduce'):
        """更新库存"""
        if not hasattr(self, 'stock_quantity'):
            return False
            
        if operation == 'reduce':
            if self.stock_quantity >= quantity:
                self.stock_quantity -= quantity
                return True
            return False
        elif operation == 'add':
            self.stock_quantity += quantity
            return True
        return False


class AttributeConfigMixin:
    """
    属性配置混入类
    为支持属性配置的模型提供属性操作方法
    """
    
    def get_attribute_value(self, attribute_code):
        """获取指定属性的值（适配不同存储方式）"""
        # 优先使用关系表存储
        if hasattr(self, 'get_relational_attribute_value'):
            return self.get_relational_attribute_value(attribute_code)
        return None

    def set_attribute_value(self, attribute_code, value):
        """设置指定属性的值（适配不同存储方式）"""
        # 优先使用关系表存储
        if hasattr(self, 'set_relational_attribute_value'):
            self.set_relational_attribute_value(attribute_code, value)

    def get_all_attributes(self):
        """获取所有属性值"""
        if hasattr(self, 'get_all_relational_attributes'):
            return self.get_all_relational_attributes()
        return {}
    
    def get_attribute_display_value(self, attribute_code):
        """获取属性的显示值"""
        value = self.get_attribute_value(attribute_code)
        if value:
            return str(value)
        return ""


class ValidationMixin:
    """
    验证混入类
    提供通用的数据验证方法
    """
    
    def validate_unique_code(self):
        """验证编码唯一性"""
        if hasattr(self, 'code') and self.code:
            queryset = self.__class__.objects.filter(code=self.code)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            if queryset.exists():
                raise ValidationError({'code': '该编码已存在'})
    
    def validate_required_fields(self, required_fields):
        """验证必填字段"""
        errors = {}
        for field in required_fields:
            if hasattr(self, field):
                value = getattr(self, field)
                if not value or (isinstance(value, str) and not value.strip()):
                    errors[field] = f"字段 {field} 不能为空"
        
        if errors:
            raise ValidationError(errors)
    
    def clean(self):
        """通用清理方法"""
        super().clean() if hasattr(super(), 'clean') else None
        
        # 执行编码唯一性验证
        if hasattr(self, 'code'):
            self.validate_unique_code()
        
        # 执行价格逻辑验证
        if isinstance(self, PriceMixin):
            self.validate_price_logic() 