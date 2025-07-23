"""
SKU相关模型
包含SKU、SKUAttributeValue、ProductImage模型及其相关功能
"""

from django.db import models
from .base import *
from .mixins import CreatedByMixin, PriceMixin, StockMixin, AttributeConfigMixin, ValidationMixin


class SKU(StandardModel, CreatedByMixin, PriceMixin, StockMixin, AttributeConfigMixin, ValidationMixin):
    """
    SKU (Stock Keeping Unit) 模型
    
    代表一个具体的可销售商品，具有唯一的价格、库存和属性组合。
    SKU是SPU的一个具体实例。
    """
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('active', '上架'),
        ('inactive', '下架'),
        ('discontinued', '停产'),
    ]
    
    name = models.CharField(
        max_length=200, 
        verbose_name="产品名称",
        db_comment="SKU的完整名称，包含属性信息",
        help_text="产品名称，建议包含关键属性信息"
    )
    sku_id = models.UUIDField(
        default=uuid.uuid4, 
        editable=False, 
        unique=True, 
        verbose_name="SKU ID",
        db_comment="系统生成的UUID，用于内部唯一标识"
    )
    
    # 关联SPU和品牌
    spu = models.ForeignKey(
        'SPU', 
        on_delete=models.CASCADE, 
        related_name='skus',
        verbose_name="SPU产品单元",
        db_comment="基于的SPU模板ID"
    )
    brand = models.ForeignKey(
        'Brand', 
        on_delete=models.CASCADE, 
        related_name='skus',
        verbose_name="品牌",
        db_comment="所属的品牌ID"
    )
    
    # 价格信息
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0)],
        verbose_name="价格",
        db_comment="产品售价，单位：元",
        help_text="产品的销售价格"
    )
    cost_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="成本价",
        db_comment="产品成本价，单位：元",
        help_text="产品的成本价格（内部使用）"
    )
    market_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="市场价",
        db_comment="产品市场指导价，单位：元",
        help_text="产品的市场指导价格"
    )
    
    # 库存信息
    stock_quantity = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0)],
        verbose_name="库存数量",
        db_comment="当前库存数量",
        help_text="产品的当前库存数量"
    )
    min_stock = models.IntegerField(
        default=10, 
        validators=[MinValueValidator(0)],
        verbose_name="最小库存",
        db_comment="库存预警阈值，低于此值将触发预警",
        help_text="库存预警线，低于此值将提醒补货"
    )
    
    # 产品信息
    remarks = models.TextField(
        blank=True, 
        default='',
        verbose_name="备注说明",
        db_comment="产品的补充说明信息，如配件、特殊说明等",
        help_text="产品的额外补充说明，如：一块可调节隔板"
    )
    main_image = models.ImageField(
        upload_to='products/images/', 
        null=True, 
        blank=True, 
        verbose_name="主图",
        db_comment="产品主图文件路径",
        help_text="产品的主要展示图片"
    )
    
    # 营销信息
    selling_points = models.TextField(
        blank=True, 
        default='',
        verbose_name="卖点",
        db_comment="产品的主要卖点和特色介绍",
        help_text="产品的主要卖点，用于营销推广"
    )
    tags = models.CharField(
        max_length=500, 
        blank=True, 
        default='',
        verbose_name="标签",
        db_comment="产品标签，用逗号分隔",
        help_text="产品标签，多个标签用逗号分隔"
    )
    
    # 状态和时间信息
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='draft', 
        verbose_name="状态",
        db_comment="产品状态：草稿、上架、下架、停产",
        help_text="产品的当前状态"
    )
    is_featured = models.BooleanField(
        default=False, 
        verbose_name="是否推荐",
        db_comment="是否为推荐产品，用于首页等位置展示",
        help_text="勾选后将在推荐位置展示"
    )
    launch_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="上市日期",
        db_comment="产品的上市日期",
        help_text="产品的预计或实际上市日期"
    )

    class Meta:
        verbose_name = "SKU产品"
        verbose_name_plural = "SKU产品"
        db_table_comment = "品牌产品表 - 具体的可销售产品，包含价格库存等销售信息"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code'], name='idx_sku_code'),
            models.Index(fields=['spu'], name='idx_sku_spu'),
            models.Index(fields=['brand'], name='idx_sku_brand'),
            models.Index(fields=['status'], name='idx_sku_status'),
            models.Index(fields=['is_featured'], name='idx_sku_featured'),
            models.Index(fields=['stock_quantity'], name='idx_sku_stock'),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """数据验证"""
        super().clean()
        
        # 验证必填字段
        self.validate_required_fields(['name', 'code', 'spu', 'brand'])
        
        # 验证价格逻辑（由PriceMixin处理）
        self.validate_price_logic()
        
        # 验证属性配置（暂时禁用严格验证）
        # self.validate_configuration()
    
    def validate_configuration(self):
        """验证属性配置的有效性 - 只使用关系表存储"""
        # 获取SPU的必填属性
        required_attributes = self.spu.spuattribute_set.filter(is_required=True)
        missing_attributes = []
        
        for spu_attr in required_attributes:
            attr_code = spu_attr.attribute.code
            
            # 检查关系表配置
            if self.pk:
                relational_value = self.get_relational_attribute_value(attr_code)
                if relational_value and str(relational_value).strip():
                    continue
            else:
                # 对于新创建的SKU，如果有默认值就使用默认值
                if spu_attr.default_value and str(spu_attr.default_value).strip():
                    continue
            
            # 记录缺失的必填属性
            missing_attributes.append(spu_attr.attribute.name)
        
        if missing_attributes:
            raise ValidationError(f"缺少必填属性: {', '.join(missing_attributes)}")

    def get_relational_attribute_value(self, attribute_code):
        """获取指定属性的关系表存储值 - 安全版本"""
        # 如果SKU还没有主键（尚未保存），返回None
        if not self.pk:
            return None
            
        try:
            sku_attr_value = self.sku_attribute_values.select_related('attribute', 'attribute_value').get(
                attribute__code=attribute_code
            )
            # 优先返回自定义值，其次返回预定义值
            if sku_attr_value.custom_value:
                return sku_attr_value.custom_value
            elif sku_attr_value.attribute_value:
                return sku_attr_value.attribute_value.value
            return None
        except (SKUAttributeValue.DoesNotExist, ValueError):
            return None

    def set_relational_attribute_value(self, attribute_code, value):
        """设置指定属性的关系表存储值"""
        try:
            from .attribute_models import Attribute, AttributeValue
            attribute = Attribute.objects.get(code=attribute_code)
        except Attribute.DoesNotExist:
            raise ValueError(f"属性 {attribute_code} 不存在")
        
        # 获取或创建SKUAttributeValue记录
        sku_attr_value, created = self.sku_attribute_values.get_or_create(
            attribute=attribute,
            defaults={'custom_value': ''}
        )
        
        # 尝试匹配预定义的属性值
        try:
            from .attribute_models import AttributeValue
            attribute_value = AttributeValue.objects.get(
                attribute=attribute, 
                value=value, 
                is_active=True
            )
            sku_attr_value.attribute_value = attribute_value
            sku_attr_value.custom_value = ''  # 清空自定义值
        except AttributeValue.DoesNotExist:
            # 如果没有匹配的预定义值，使用自定义值
            sku_attr_value.attribute_value = None
            sku_attr_value.custom_value = str(value)
        
        sku_attr_value.save()

    def get_all_relational_attributes(self):
        """获取所有关系表存储的属性值"""
        return {
            rel_attr.attribute.code: rel_attr.get_display_value() 
            for rel_attr in self.sku_attribute_values.select_related('attribute', 'attribute_value').all()
        }


class SKUAttributeValue(BaseModel):
    """
    SKU属性值关联模型 - 对应原始设计中的 tbl_sku_values
    
    使用关系型方式存储SKU的具体属性值
    支持预定义属性值和自定义值两种模式
    """
    
    sku = models.ForeignKey(
        SKU, 
        on_delete=models.CASCADE, 
        related_name='sku_attribute_values',
        verbose_name="SKU",
        db_comment="关联的SKU ID"
    )
    attribute = models.ForeignKey(
        'Attribute', 
        on_delete=models.CASCADE, 
        related_name='sku_attribute_values',
        verbose_name="属性",
        db_comment="关联的属性ID"
    )
    attribute_value = models.ForeignKey(
        'AttributeValue', 
        on_delete=models.CASCADE, 
        related_name='sku_attribute_values',
        null=True,
        blank=True,
        verbose_name="属性值",
        db_comment="关联的预定义属性值ID，与custom_value二选一"
    )
    
    # 可选的自定义值（用于文本、数字等非预定义值的属性）
    custom_value = models.CharField(
        max_length=500, 
        blank=True, 
        default='',
        verbose_name="自定义值",
        db_comment="自定义属性值，用于非预定义值的属性",
        help_text="当属性值不在预定义范围内时使用"
    )

    class Meta:
        verbose_name = "SKU属性值"
        verbose_name_plural = "SKU属性值"
        db_table_comment = "SKU属性值关联表 - 关系型存储每个SKU的具体属性值配置"
        unique_together = ['sku', 'attribute']  # 每个SKU的每个属性只能有一个值
        ordering = ['sku', 'attribute__order']
        indexes = [
            models.Index(fields=['sku'], name='idx_sku_attr_val_sku'),
            models.Index(fields=['attribute'], name='idx_sku_attr_val_attr'),
            models.Index(fields=['attribute_value'], name='idx_sku_attr_val_value'),
        ]

    def __str__(self):
        return f"{self.sku.name} - {self.attribute.name}: {self.get_display_value()}"

    def clean(self):
        """数据验证"""
        super().clean()
        
        # 确保attribute_value和custom_value不能同时为空
        if not self.attribute_value and not self.custom_value.strip():
            raise ValidationError("必须设置属性值或自定义值")
        
        # 对于选择类型的属性，必须使用预定义值
        if self.attribute.type in ['select', 'multiselect'] and not self.attribute_value:
            raise ValidationError(f"属性 '{self.attribute.name}' 必须选择预定义的值")
        
        # 验证属性值是否属于指定属性
        if self.attribute_value and self.attribute_value.attribute != self.attribute:
            raise ValidationError("属性值与属性不匹配")

    def get_display_value(self):
        """获取显示值"""
        if self.attribute_value:
            return self.attribute_value.display_name or self.attribute_value.value
        return self.custom_value


class ProductImage(BaseModel):
    """
    产品图片模型
    
    存储SKU的多张产品图片，支持排序和状态管理
    """
    
    sku = models.ForeignKey(
        SKU, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name="产品",
        db_comment="关联的SKU ID"
    )
    image = models.ImageField(
        upload_to='products/images/', 
        verbose_name="图片",
        db_comment="产品图片文件路径",
        help_text="产品图片文件"
    )
    alt_text = models.CharField(
        max_length=200, 
        blank=True, 
        default='',
        verbose_name="图片描述",
        db_comment="图片的替代文本，用于SEO和无障碍访问",
        help_text="图片的替代文本描述"
    )
    order = models.IntegerField(
        default=0, 
        verbose_name="排序",
        db_comment="图片的显示顺序，数字越小越靠前",
        help_text="图片的显示顺序"
    )

    class Meta:
        verbose_name = "产品图片"
        verbose_name_plural = "产品图片"
        db_table_comment = "产品图片表 - 存储每个SKU的多张产品展示图片"
        ordering = ['order']
        indexes = [
            models.Index(fields=['sku'], name='idx_product_image_sku'),
            models.Index(fields=['order'], name='idx_product_image_order'),
            models.Index(fields=['is_active'], name='idx_product_image_active'),
        ]

    def __str__(self):
        return f"{self.sku.name} - 图片{self.order}" 