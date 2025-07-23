"""
品牌相关模型
包含Brand模型及其相关功能
"""

from django.db import models
from .base import *
from .mixins import ValidationMixin


class Brand(StandardModel, ValidationMixin):
    """
    品牌模型
    
    管理产品品牌信息，包括品牌基础信息、联系方式等
    支持品牌Logo上传和官方网站链接
    """
    
    name = models.CharField(
        max_length=100, 
        verbose_name="品牌名称",
        db_comment="品牌的正式名称",
        help_text="品牌的正式名称，如：Royana、欧派等"
    )
    logo = models.ImageField(
        upload_to='brands/logos/', 
        null=True, 
        blank=True, 
        verbose_name="品牌Logo",
        db_comment="品牌标志图片文件路径",
        help_text="建议上传PNG格式，尺寸200x200像素"
    )
    website = models.URLField(
        blank=True, 
        default='',
        verbose_name="官方网站",
        db_comment="品牌官方网站地址",
        help_text="品牌官方网站URL，如：https://www.royana.com"
    )
    
    # 联系人信息
    contact_person = models.CharField(
        max_length=50, 
        blank=True, 
        default='',
        verbose_name="联系人",
        db_comment="品牌联系人姓名",
        help_text="品牌方联系人姓名"
    )
    contact_phone = models.CharField(
        max_length=20, 
        blank=True, 
        default='',
        verbose_name="联系电话",
        db_comment="品牌联系电话号码",
        help_text="联系电话，如：400-888-8888"
    )
    contact_email = models.EmailField(
        blank=True, 
        default='',
        verbose_name="联系邮箱",
        db_comment="品牌联系邮箱地址",
        help_text="联系邮箱地址"
    )

    class Meta:
        verbose_name = "品牌"
        verbose_name_plural = "品牌"
        db_table_comment = "品牌信息表 - 管理产品品牌的基础信息和联系方式"
        ordering = ['name']
        indexes = [
            models.Index(fields=['code'], name='idx_brand_code'),
            models.Index(fields=['is_active'], name='idx_brand_active'),
            models.Index(fields=['name'], name='idx_brand_name'),
        ]

    def __str__(self):
        return self.name
    
    def clean(self):
        """数据验证"""
        super().clean()
        
        # 验证必填字段
        self.validate_required_fields(['name', 'code'])
        
        # 验证联系方式至少填写一种
        if not any([self.contact_person, self.contact_phone, self.contact_email]):
            pass  # 联系方式可以都为空，作为可选信息
    
    def get_spu_count(self):
        """获取该品牌下的SPU数量"""
        return self.spus.filter(is_active=True).count()
    
    def get_sku_count(self):
        """获取该品牌下的SKU数量"""
        return self.skus.filter(status='active').count()
    
    def get_contact_info(self):
        """获取完整的联系信息"""
        info = []
        if self.contact_person:
            info.append(f"联系人：{self.contact_person}")
        if self.contact_phone:
            info.append(f"电话：{self.contact_phone}")
        if self.contact_email:
            info.append(f"邮箱：{self.contact_email}")
        return " | ".join(info) if info else "暂无联系信息"
    
    def get_logo_url(self):
        """获取Logo URL"""
        if self.logo:
            return self.logo.url
        return None
    
    def can_delete(self):
        """检查是否可以删除"""
        # 检查是否有关联的SPU
        spu_count = self.get_spu_count()
        if spu_count > 0:
            return False, f"该品牌下还有{spu_count}个SPU，无法删除"
        
        # 检查是否有关联的SKU
        sku_count = self.get_sku_count()
        if sku_count > 0:
            return False, f"该品牌下还有{sku_count}个SKU，无法删除"
        
        return True, "可以删除" 