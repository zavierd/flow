"""
属性相关模型
包含Attribute和AttributeValue模型及其相关功能
"""

from django.db import models
from .base import *
from .mixins import ValidationMixin


class Attribute(StandardModel, ValidationMixin):
    """
    产品属性模型
    
    定义产品的各种属性类型，如颜色、尺寸、材质等
    支持多种数据类型：文本、数字、选择、布尔值等
    """
    
    ATTRIBUTE_TYPES = [
        ('text', '文本'),
        ('number', '数字'),
        ('select', '单选'),
        ('multiselect', '多选'),
        ('boolean', '布尔值'),
        ('date', '日期'),
        ('color', '颜色'),
        ('image', '图片'),
    ]
    
    name = models.CharField(
        max_length=100, 
        verbose_name="属性名称",
        db_comment="属性的显示名称",
        help_text="属性的显示名称，如：颜色、尺寸、材质等"
    )
    type = models.CharField(
        max_length=20, 
        choices=ATTRIBUTE_TYPES, 
        default='text',
        verbose_name="属性类型",
        db_comment="属性的数据类型，决定了值的存储和显示方式",
        help_text="选择合适的属性类型"
    )
    unit = models.CharField(
        max_length=20, 
        blank=True, 
        default='',
        verbose_name="单位",
        db_comment="属性值的计量单位，如cm、kg等",
        help_text="属性值的单位，如：cm、kg、㎡等"
    )
    is_required = models.BooleanField(
        default=False, 
        verbose_name="是否必填",
        db_comment="创建产品时是否必须填写此属性",
        help_text="勾选后创建产品时必须设置此属性"
    )
    is_filterable = models.BooleanField(
        default=True, 
        verbose_name="是否可筛选",
        db_comment="是否可以作为筛选条件在前台使用",
        help_text="勾选后可在产品列表页面作为筛选条件"
    )

    class Meta:
        verbose_name = "属性"
        verbose_name_plural = "属性"
        db_table_comment = "产品属性定义表 - 定义产品的各种可配置属性类型"
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['code'], name='idx_attribute_code'),
            models.Index(fields=['type'], name='idx_attribute_type'),
            models.Index(fields=['is_active'], name='idx_attribute_active'),
            models.Index(fields=['order'], name='idx_attribute_order'),
        ]

    def __str__(self):
        return self.name
    
    def clean(self):
        """数据验证"""
        super().clean()
        
        # 验证必填字段
        self.validate_required_fields(['name', 'code', 'type'])
    
    def get_values_count(self):
        """获取属性值数量"""
        return self.values.filter(is_active=True).count()
    
    def get_available_values(self):
        """获取可用的属性值"""
        return self.values.filter(is_active=True).order_by('order', 'value')
    
    def can_delete(self):
        """检查是否可以删除"""
        # 检查是否有关联的SPU
        spu_count = self.spus.count()
        if spu_count > 0:
            return False, f"该属性被{spu_count}个SPU使用，无法删除"
        
        # 检查是否有关联的SKU属性值
        sku_attr_count = self.sku_attribute_values.count()
        if sku_attr_count > 0:
            return False, f"该属性被{sku_attr_count}个SKU使用，无法删除"
        
        return True, "可以删除"
    
    def get_type_display_info(self):
        """获取属性类型的详细信息"""
        type_info = {
            'text': {'icon': 'text', 'description': '可输入任意文本'},
            'number': {'icon': 'number', 'description': '仅允许输入数字'},
            'select': {'icon': 'list', 'description': '从预定义选项中选择一个'},
            'multiselect': {'icon': 'list-check', 'description': '从预定义选项中选择多个'},
            'boolean': {'icon': 'toggle', 'description': '是/否选择'},
            'date': {'icon': 'calendar', 'description': '日期选择器'},
            'color': {'icon': 'color', 'description': '颜色选择器'},
            'image': {'icon': 'image', 'description': '图片上传'},
        }
        return type_info.get(self.type, {'icon': 'help', 'description': '未知类型'})


class AttributeValue(BaseModel, ValidationMixin):
    """
    属性值模型
    
    存储属性的具体可选值，如颜色属性的"红色"、"蓝色"等
    支持颜色代码和图片展示
    """
    
    attribute = models.ForeignKey(
        Attribute, 
        on_delete=models.CASCADE, 
        related_name='values',
        verbose_name="属性",
        db_comment="所属的属性ID"
    )
    value = models.CharField(
        max_length=200, 
        verbose_name="属性值",
        db_comment="属性的具体值，如红色、30cm等",
        help_text="属性的具体值"
    )
    display_name = models.CharField(
        max_length=200, 
        blank=True, 
        default='',
        verbose_name="显示名称",
        db_comment="属性值的显示名称，为空时使用value字段",
        help_text="前台显示的名称，留空则使用属性值"
    )
    color_code = models.CharField(
        max_length=7, 
        blank=True, 
        default='',
        verbose_name="颜色代码",
        db_comment="颜色属性的十六进制颜色代码，如#FF0000",
        help_text="颜色属性专用，格式如：#FF0000"
    )
    image = models.ImageField(
        upload_to='attributes/images/', 
        null=True, 
        blank=True, 
        verbose_name="图片",
        db_comment="属性值的展示图片文件路径",
        help_text="属性值的展示图片"
    )
    order = models.IntegerField(
        default=0, 
        verbose_name="排序",
        db_comment="同属性下值的显示顺序，数字越小越靠前",
        help_text="在同一属性下的显示顺序"
    )

    class Meta:
        verbose_name = "属性值"
        verbose_name_plural = "属性值"
        db_table_comment = "属性值表 - 存储每个属性的具体可选值"
        ordering = ['order', 'value']
        unique_together = ['attribute', 'value']
        indexes = [
            models.Index(fields=['attribute'], name='idx_attr_value_attribute'),
            models.Index(fields=['is_active'], name='idx_attr_value_active'),
            models.Index(fields=['order'], name='idx_attr_value_order'),
        ]

    def __str__(self):
        return f"{self.attribute.name}: {self.display_name or self.value}"
    
    def clean(self):
        """数据验证"""
        super().clean()
        
        # 验证必填字段
        self.validate_required_fields(['value'])
        
        # 验证颜色代码格式
        if self.color_code:
            import re
            if not re.match(r'^#[0-9A-Fa-f]{6}$', self.color_code):
                raise ValidationError({'color_code': '颜色代码格式不正确，应为#RRGGBB格式'})
        
        # 验证属性类型与字段的匹配
        if self.attribute:
            if self.attribute.type == 'color' and not self.color_code and not self.image:
                raise ValidationError('颜色类型的属性值需要设置颜色代码或图片')
    
    def get_display_value(self):
        """获取显示值"""
        return self.display_name or self.value
    
    def get_usage_count(self):
        """获取使用次数"""
        return self.sku_attribute_values.count()
    
    def can_delete(self):
        """检查是否可以删除"""
        usage_count = self.get_usage_count()
        if usage_count > 0:
            return False, f"该属性值被{usage_count}个SKU使用，无法删除"
        
        return True, "可以删除" 