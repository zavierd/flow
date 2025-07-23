"""
SPU相关模型
包含SPU、SPUAttribute、SPUDimensionTemplate模型及其相关功能
"""

from django.db import models
from .base import *
from .mixins import CreatedByMixin, ValidationMixin


class SPU(StandardModel, CreatedByMixin, ValidationMixin):
    """
    SPU (SPU产品单元) 模型
    
    代表一个SPU产品单元，它是一组具有共同属性的产品的集合。
    SPU本身不是一个具体的、可销售的商品，而是一个产品模板。
    例如，"iPhone 15 Pro"是一个SPU，而"蓝色、256GB的iPhone 15 Pro"是一个SKU。
    """
    
    name = models.CharField(
        max_length=200, 
        verbose_name="产品名称",
        db_comment="SPU的标准名称",
        help_text="产品的标准名称，如：NOVO系列单门单抽底柜"
    )
    category = models.ForeignKey(
        'Category', 
        on_delete=models.CASCADE, 
        related_name='spus',
        verbose_name="产品分类",
        db_comment="所属的产品分类ID"
    )
    brand = models.ForeignKey(
        'Brand', 
        on_delete=models.CASCADE, 
        related_name='spus',
        null=True,
        blank=True,
        verbose_name="品牌",
        db_comment="所属的品牌ID"
    )
    
    # 关联可配置属性
    attributes = models.ManyToManyField(
        'Attribute', 
        through='SPUAttribute',
        related_name='spus',
        verbose_name="可配置属性",
        help_text="该SPU支持配置的属性"
    )
    
    # 基础信息
    specifications = models.TextField(
        blank=True, 
        default='',
        verbose_name="规格说明",
        db_comment="产品的技术规格和参数说明",
        help_text="产品的技术规格和参数"
    )
    usage_scenario = models.TextField(
        blank=True, 
        default='',
        verbose_name="使用场景",
        db_comment="产品的适用场景和使用建议",
        help_text="产品的适用场景说明"
    )

    class Meta:
        verbose_name = "SPU产品单元"
        verbose_name_plural = "SPU产品单元"
        db_table_comment = "SPU产品单元(SPU)表 - 定义产品的通用属性和模板"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code'], name='idx_spu_code'),
            models.Index(fields=['category'], name='idx_spu_category'),
            models.Index(fields=['brand'], name='idx_spu_brand'),
            models.Index(fields=['is_active'], name='idx_spu_active'),
        ]

    def __str__(self):
        return self.name
    
    def clean(self):
        """数据验证"""
        super().clean()
        
        # 验证必填字段
        self.validate_required_fields(['name', 'code', 'category'])
    
    def get_sku_count(self):
        """获取基于此SPU的SKU数量"""
        return self.skus.filter(status='active').count()
    
    def get_total_sku_count(self):
        """获取基于此SPU的所有SKU数量（包括非活跃）"""
        return self.skus.count()
    
    def get_configurable_attributes(self):
        """获取可配置的属性列表"""
        return self.spuattribute_set.filter(
            attribute__is_active=True
        ).select_related('attribute').order_by('order')
    
    def get_required_attributes(self):
        """获取必填属性列表"""
        return self.spuattribute_set.filter(
            is_required=True,
            attribute__is_active=True
        ).select_related('attribute').order_by('order')
    
    def can_delete(self):
        """检查是否可以删除"""
        sku_count = self.get_total_sku_count()
        if sku_count > 0:
            return False, f"该SPU下还有{sku_count}个SKU，无法删除"
        
        return True, "可以删除"
    
    def create_default_sku(self, brand, **kwargs):
        """基于此SPU创建默认SKU"""
        from .sku_models import SKU
        
        # 设置默认属性
        sku_data = {
            'spu': self,
            'brand': brand,
            'name': f"{brand.name} {self.name}",
            'code': kwargs.get('code', ''),
            'price': kwargs.get('price', 0.00),
            'stock_quantity': kwargs.get('stock_quantity', 0),
        }
        sku_data.update(kwargs)
        
        return SKU.objects.create(**sku_data)


class SPUAttribute(BaseModel):
    """
    SPU与属性的关联模型
    
    定义SPU支持哪些属性配置以及这些属性的默认值和约束
    """
    
    spu = models.ForeignKey(
        SPU, 
        on_delete=models.CASCADE, 
        verbose_name="SPU",
        db_comment="关联的SPU ID"
    )
    attribute = models.ForeignKey(
        'Attribute', 
        on_delete=models.CASCADE, 
        verbose_name="属性",
        db_comment="关联的属性ID"
    )
    is_required = models.BooleanField(
        default=False, 
        verbose_name="是否必填",
        db_comment="在此SPU下创建SKU时是否必须配置此属性",
        help_text="勾选后基于此SPU创建SKU时必须配置此属性"
    )
    default_value = models.CharField(
        max_length=200, 
        blank=True, 
        default='',
        verbose_name="默认值",
        db_comment="此属性在该SPU下的默认值",
        help_text="创建SKU时的默认属性值"
    )
    order = models.IntegerField(
        default=0, 
        verbose_name="排序",
        db_comment="属性在该SPU下的显示顺序",
        help_text="在产品配置界面的显示顺序"
    )

    class Meta:
        verbose_name = "SPU属性关联"
        verbose_name_plural = "SPU属性关联"
        db_table_comment = "SPU属性关联表 - 定义每个SPU支持的属性配置"
        unique_together = ['spu', 'attribute']
        ordering = ['order']
        indexes = [
            models.Index(fields=['spu'], name='idx_spu_attr_spu'),
            models.Index(fields=['attribute'], name='idx_spu_attr_attribute'),
        ]

    def __str__(self):
        return f"{self.spu.name} - {self.attribute.name}"
    
    def clean(self):
        """数据验证"""
        super().clean()
        
        # 验证默认值的有效性
        if self.default_value and self.attribute:
            # 对于选择类型的属性，验证默认值是否在可选值中
            if self.attribute.type in ['select', 'multiselect']:
                valid_values = self.attribute.values.filter(
                    is_active=True
                ).values_list('value', flat=True)
                
                if self.attribute.type == 'select':
                    if self.default_value not in valid_values:
                        raise ValidationError({
                            'default_value': f'默认值必须是属性的有效值之一：{", ".join(valid_values)}'
                        })
                elif self.attribute.type == 'multiselect':
                    # 多选的默认值用逗号分隔
                    default_values = [v.strip() for v in self.default_value.split(',')]
                    invalid_values = [v for v in default_values if v not in valid_values]
                    if invalid_values:
                        raise ValidationError({
                            'default_value': f'无效的默认值：{", ".join(invalid_values)}'
                        })


class SPUDimensionTemplate(BaseModel, CreatedByMixin):
    """
    SPU尺寸模板模型 - 定义SPU级别的标准尺寸模板
    
    当基于此SPU创建SKU时，自动继承这些尺寸配置
    """
    
    DIMENSION_TYPE_CHOICES = [
        ('height', '高度'),
        ('width', '宽度'),
        ('depth', '厚度/深度'),
        ('length', '长度'),
        ('diameter', '直径'),
        ('radius', '半径'),
        ('area', '面积'),
        ('volume', '体积'),
        ('weight', '重量'),
        ('custom', '自定义'),
    ]
    
    UNIT_CHOICES = [
        ('mm', '毫米'),
        ('cm', '厘米'),
        ('m', '米'),
        ('㎡', '平方米'),
        ('m³', '立方米'),
        ('kg', '千克'),
        ('g', '克'),
        ('custom', '自定义单位'),
    ]
    
    spu = models.ForeignKey(
        SPU,
        on_delete=models.CASCADE,
        related_name='dimension_templates',
        verbose_name="SPU",
        db_comment="关联的SPU产品单元",
        help_text="此尺寸模板所属的SPU"
    )
    
    dimension_type = models.CharField(
        max_length=20,
        choices=DIMENSION_TYPE_CHOICES,
        verbose_name="尺寸类型",
        db_comment="尺寸的类型，如高度、宽度、厚度等",
        help_text="选择尺寸的类型"
    )
    
    default_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="默认值",
        db_comment="SPU的默认尺寸值",
        help_text="基于此SPU创建SKU时的默认尺寸值"
    )
    
    min_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="最小值",
        db_comment="允许的最小尺寸值",
        help_text="允许的最小尺寸值，为空表示无限制"
    )
    
    max_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="最大值",
        db_comment="允许的最大尺寸值",
        help_text="允许的最大尺寸值，为空表示无限制"
    )
    
    unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        default='mm',
        verbose_name="单位",
        db_comment="尺寸的计量单位",
        help_text="尺寸的计量单位"
    )
    
    custom_unit = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name="自定义单位",
        db_comment="自定义的计量单位",
        help_text="当单位选择为自定义时，填写具体的单位名称"
    )
    
    tolerance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="公差",
        db_comment="尺寸的允许公差范围",
        help_text="尺寸的允许公差范围，±值"
    )
    
    is_required = models.BooleanField(
        default=True,
        verbose_name="是否必填",
        db_comment="基于此SPU创建SKU时是否必须设置此尺寸",
        help_text="勾选后基于此SPU创建SKU时必须设置此尺寸"
    )
    
    is_key_dimension = models.BooleanField(
        default=False,
        verbose_name="是否关键尺寸",
        db_comment="是否为影响定价的关键尺寸",
        help_text="是否为影响定价的关键尺寸"
    )
    
    order = models.IntegerField(
        default=0,
        verbose_name="排序",
        db_comment="尺寸在SPU下的显示顺序",
        help_text="在产品尺寸配置界面的显示顺序"
    )

    class Meta:
        verbose_name = "SPU尺寸模板"
        verbose_name_plural = "SPU尺寸模板"
        db_table_comment = "SPU尺寸模板表 - 定义SPU级别的标准尺寸模板"
        ordering = ['spu', 'order', 'dimension_type']
        indexes = [
            models.Index(fields=['spu'], name='idx_spu_dim_tmpl_spu'),
            models.Index(fields=['dimension_type'], name='idx_spu_dim_tmpl_type'),
            models.Index(fields=['is_key_dimension'], name='idx_spu_dim_tmpl_key'),
            models.Index(fields=['order'], name='idx_spu_dim_tmpl_order'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['spu', 'dimension_type'],
                name='unique_spu_dim_tmpl_per_type'
            )
        ]

    def __str__(self):
        unit_display = self.custom_unit if self.unit == 'custom' else self.get_unit_display()
        return f"{self.spu.name} - {self.get_dimension_type_display()}: {self.default_value}{unit_display}"
    
    def clean(self):
        """数据验证"""
        super().clean()
        
        # 验证默认值必须大于0
        if self.default_value <= 0:
            raise ValidationError({'default_value': '默认值必须大于0'})
        
        # 验证最小值和最大值的逻辑关系
        if self.min_value is not None and self.default_value < self.min_value:
            raise ValidationError({'default_value': '默认值不能小于最小值'})
        
        if self.max_value is not None and self.default_value > self.max_value:
            raise ValidationError({'default_value': '默认值不能大于最大值'})
        
        if self.min_value is not None and self.max_value is not None:
            if self.min_value >= self.max_value:
                raise ValidationError({'max_value': '最大值必须大于最小值'})
        
        # 验证公差必须大于等于0
        if self.tolerance < 0:
            raise ValidationError({'tolerance': '公差不能为负数'})
        
        # 验证自定义单位
        if self.unit == 'custom' and not self.custom_unit.strip():
            raise ValidationError({'custom_unit': '选择自定义单位时，必须填写自定义单位名称'})
    
    def get_display_unit(self):
        """获取显示用的单位"""
        if self.unit == 'custom':
            return self.custom_unit
        return self.get_unit_display() 