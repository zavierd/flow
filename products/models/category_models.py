"""
分类相关模型
包含Category模型及其相关功能
"""

from django.db import models
from .base import *
from .mixins import TreeMixin, ValidationMixin


class Category(MPTTModel, StandardModel, TreeMixin, ValidationMixin):
    """
    产品分类模型 - 支持无限级分类
    
    使用MPTT(Modified Preorder Tree Traversal)实现高效的树形结构查询
    支持产品的多级分类管理，适用于复杂的产品分类体系
    """
    
    name = models.CharField(
        max_length=100, 
        verbose_name="分类名称",
        db_comment="分类的显示名称，如：橱柜、地柜、吊柜等",
        help_text="分类的显示名称，建议简洁明确"
    )
    parent = TreeForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children',
        db_index=True,
        verbose_name="父分类",
        db_comment="上级分类，为空表示顶级分类",
        help_text="选择上级分类，留空表示顶级分类"
    )
    
    class MPTTMeta:
        order_insertion_by = ['order', 'name']
    
    class Meta:
        verbose_name = "产品分类"
        verbose_name_plural = "产品分类"
        db_table_comment = "产品分类表 - 管理产品的多级分类体系，支持无限级嵌套"
        ordering = ['tree_id', 'lft']
        indexes = [
            models.Index(fields=['code'], name='idx_category_code'),
            models.Index(fields=['is_active'], name='idx_category_active'),
            models.Index(fields=['parent'], name='idx_category_parent'),
            models.Index(fields=['order'], name='idx_category_order'),
        ]
        
    def __str__(self):
        return self.name
    
    def clean(self):
        """数据验证"""
        super().clean()
        
        # 验证父分类不能是自己
        if self.parent and self.parent == self:
            raise ValidationError({'parent': '父分类不能是自己'})
        
        # 验证不能设置子级分类为父分类（防止循环引用）
        if self.parent and self.pk:
            descendants = self.get_descendants(include_self=True)
            if self.parent in descendants:
                raise ValidationError({'parent': '不能选择子级分类作为父分类'})
    
    def get_product_count(self):
        """获取该分类下的产品数量（包括子分类）"""
        from .spu_models import SPU
        # 获取当前分类及所有子分类
        categories = self.get_descendants(include_self=True)
        return SPU.objects.filter(category__in=categories, is_active=True).count()
    
    def get_direct_product_count(self):
        """获取该分类下的直接产品数量（不包括子分类）"""
        from .spu_models import SPU
        return SPU.objects.filter(category=self, is_active=True).count()
    
    def get_breadcrumb(self):
        """获取面包屑导航"""
        ancestors = self.get_ancestors(include_self=True)
        return [{'name': cat.name, 'code': cat.code} for cat in ancestors]
    
    def can_delete(self):
        """检查是否可以删除"""
        # 检查是否有子分类
        if self.get_children().exists():
            return False, "该分类下还有子分类，无法删除"
        
        # 检查是否有关联的产品
        if self.get_direct_product_count() > 0:
            return False, "该分类下还有产品，无法删除"
        
        return True, "可以删除" 