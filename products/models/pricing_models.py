"""
定价相关模型
包含ProductsPricingRule和ProductsDimension模型及其相关功能
"""

from django.db import models
from decimal import Decimal
import math
from .base import *
from .mixins import CreatedByMixin, ValidationMixin


class ProductsPricingRule(BaseModel, CreatedByMixin):
    """产品加价规则模型 - 支持SPU级别和SKU级别的规则"""
    
    RULE_TYPE_CHOICES = [
        ('height', '高度'),
        ('width', '宽度'),
        ('depth', '厚度/深度'),
        ('weight', '重量'),
        ('area', '面积'),
        ('volume', '体积'),
    ]
    
    CALCULATION_METHOD_CHOICES = [
        ('fixed', '固定金额'),
        ('percentage', '百分比'),
        ('multiplier', '倍数'),
        ('step', '阶梯式'),
    ]
    
    # 规则归属
    spu = models.ForeignKey(
        'SPU',
        on_delete=models.CASCADE,
        related_name='pricing_rules',
        verbose_name="SPU",
        help_text="规则所属的SPU，当SKU为空时应用于整个SPU"
    )
    
    sku = models.ForeignKey(
        'SKU',
        on_delete=models.CASCADE,
        related_name='pricing_rules',
        verbose_name="SKU",
        null=True,
        blank=True,
        help_text="可选：指定SKU时，规则仅应用于该SKU（优先级高于SPU规则）"
    )
    
    # 规则基本信息
    rule_type = models.CharField(
        max_length=20,
        choices=RULE_TYPE_CHOICES,
        verbose_name="规则类型",
        help_text="指定这个规则适用于哪种尺寸维度"
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name="规则名称",
        help_text="便于识别的规则名称"
    )
    
    # 规则计算参数
    threshold_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="阈值",
        help_text="超过此值开始计费，例如高度超过2335mm"
    )
    
    unit_increment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1,
        verbose_name="单位增量",
        help_text="计费单位，例如每10mm"
    )
    
    calculation_method = models.CharField(
        max_length=20,
        choices=CALCULATION_METHOD_CHOICES,
        default='step',
        verbose_name="计算方式"
    )
    
    price_increment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="价格增量",
        help_text="每个单位增量的价格，例如每10mm加收20元"
    )
    
    multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        verbose_name="倍数",
        help_text="用于倍数计算方式"
    )
    
    max_increment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="最大加价",
        help_text="可选：限制最大加价金额"
    )
    
    # 规则状态和有效期
    effective_date = models.DateField(
        default=timezone.now,
        verbose_name="生效日期",
        help_text="规则开始生效的日期"
    )
    
    expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="失效日期",
        help_text="可选：规则失效的日期"
    )

    class Meta:
        db_table = 'products_pricing_rule'
        verbose_name = "产品加价规则"
        verbose_name_plural = "产品加价规则"
        ordering = ['spu', 'sku', 'rule_type', 'threshold_value']
        # 确保同一个SKU/SPU+规则类型+阈值的唯一性
        unique_together = [
            ['spu', 'sku', 'rule_type', 'threshold_value'],
        ]
        indexes = [
            models.Index(fields=['spu'], name='idx_pricing_rule_spu'),
            models.Index(fields=['sku'], name='idx_pricing_rule_sku'),
            models.Index(fields=['rule_type'], name='idx_pricing_rule_type'),
            models.Index(fields=['effective_date'], name='idx_pricing_rule_effective'),
        ]
    
    def __str__(self):
        rule_scope = f"SKU:{self.sku.name}" if self.sku else f"SPU:{self.spu.name}"
        return f"{rule_scope} - {self.get_rule_type_display()} - {self.name}"
    
    @property
    def rule_scope(self):
        """返回规则作用范围"""
        return "SKU专属" if self.sku else "SPU通用"
    
    @property
    def priority(self):
        """返回规则优先级，SKU专属规则优先级更高"""
        return 10 if self.sku else 5
    
    def clean(self):
        """模型验证"""
        super().clean()
        
        # 确保SKU属于对应的SPU
        if self.sku and self.sku.spu != self.spu:
            raise ValidationError({
                'sku': '选择的SKU必须属于所选的SPU'
            })
        
        # 确保生效日期早于失效日期
        if self.expiry_date and self.effective_date > self.expiry_date:
            raise ValidationError({
                'expiry_date': '失效日期必须晚于生效日期'
            })
        
        # 验证阈值和增量必须大于0
        if self.threshold_value <= 0:
            raise ValidationError({'threshold_value': '阈值必须大于0'})
        
        if self.unit_increment <= 0:
            raise ValidationError({'unit_increment': '单位增量必须大于0'})
    
    def calculate_increment(self, excess_value):
        """
        计算超出部分的加价
        
        Args:
            excess_value (Decimal): 超出阈值的数值
            
        Returns:
            Decimal: 计算出的加价金额
        """
        if excess_value <= 0:
            return Decimal('0')
        
        if self.calculation_method == 'fixed':
            # 固定金额
            increment = self.price_increment
        elif self.calculation_method == 'percentage':
            # 百分比（基于超出值）
            increment = excess_value * (self.price_increment / 100)
        elif self.calculation_method == 'multiplier':
            # 倍数
            increment = excess_value * self.multiplier * self.price_increment
        elif self.calculation_method == 'step':
            # 阶梯式（默认）- 按unit_increment计算步数
            steps = math.ceil(excess_value / self.unit_increment)
            increment = steps * self.price_increment
        else:
            increment = Decimal('0')
        
        # 应用最大加价限制
        if self.max_increment:
            increment = min(increment, self.max_increment)
        
        return increment
    
    @classmethod
    def get_applicable_rules(cls, sku, dimension_type=None):
        """
        获取适用于指定SKU的规则，按优先级排序
        
        Args:
            sku (SKU): SKU实例
            dimension_type (str): 可选，筛选特定维度类型的规则
            
        Returns:
            QuerySet: 适用的规则，按优先级排序（SKU专属 > SPU通用）
        """
        from django.db.models import Q, Case, When, IntegerField
        
        rules_query = cls.objects.filter(
            Q(spu=sku.spu) &  # 属于同一个SPU
            Q(Q(sku__isnull=True) | Q(sku=sku)) &  # SPU通用规则或SKU专属规则
            Q(is_active=True) &  # 激活状态
            Q(effective_date__lte=timezone.now().date()) &  # 已生效
            Q(Q(expiry_date__isnull=True) | Q(expiry_date__gt=timezone.now().date()))  # 未失效
        )
        
        if dimension_type:
            rules_query = rules_query.filter(rule_type=dimension_type)
        
        # 按优先级排序：SKU专属规则(sku非空) > SPU通用规则(sku为空)
        rules_query = rules_query.order_by(
            Case(
                When(sku__isnull=False, then=0),  # SKU专属规则排在前面
                default=1,  # SPU通用规则排在后面
                output_field=IntegerField()
            ),
            'rule_type', 
            'threshold_value'
        )
        
        return rules_query


class ProductsDimension(BaseModel, CreatedByMixin):
    """
    产品尺寸模型 - 存储每个SKU的标准尺寸信息
    
    用于动态价格计算，支持高度、宽度、厚度等尺寸信息
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
    
    sku = models.ForeignKey(
        'SKU',
        on_delete=models.CASCADE,
        related_name='dimensions',
        verbose_name="SKU",
        db_comment="关联的SKU产品",
        help_text="此尺寸信息所属的SKU产品"
    )
    
    dimension_type = models.CharField(
        max_length=20,
        choices=DIMENSION_TYPE_CHOICES,
        verbose_name="尺寸类型",
        db_comment="尺寸的类型，如高度、宽度、厚度等",
        help_text="选择尺寸的类型"
    )
    
    standard_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="标准值",
        db_comment="产品的标准尺寸值",
        help_text="产品的标准尺寸值，用于计算加价"
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
    
    is_key_dimension = models.BooleanField(
        default=False,
        verbose_name="是否关键尺寸",
        db_comment="是否为影响定价的关键尺寸",
        help_text="是否为影响定价的关键尺寸"
    )

    class Meta:
        verbose_name = "产品尺寸"
        verbose_name_plural = "产品尺寸"
        db_table_comment = "产品尺寸表 - 存储每个SKU的标准尺寸信息"
        ordering = ['sku', 'dimension_type']
        indexes = [
            models.Index(fields=['sku'], name='idx_dimension_sku'),
            models.Index(fields=['dimension_type'], name='idx_dimension_type'),
            models.Index(fields=['is_key_dimension'], name='idx_dimension_key'),
            models.Index(fields=['standard_value'], name='idx_dimension_standard'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['sku', 'dimension_type'],
                name='unique_dimension_per_sku_type'
            )
        ]
    
    def __str__(self):
        unit_display = self.custom_unit if self.unit == 'custom' else self.get_unit_display()
        return f"{self.sku.name} - {self.get_dimension_type_display()}: {self.standard_value}{unit_display}"
    
    def clean(self):
        """模型验证"""
        super().clean()
        
        # 验证标准值必须大于0
        if self.standard_value <= 0:
            raise ValidationError({'standard_value': '标准值必须大于0'})
        
        # 验证最小值和最大值的逻辑关系
        if self.min_value is not None and self.standard_value < self.min_value:
            raise ValidationError({'standard_value': '标准值不能小于最小值'})
        
        if self.max_value is not None and self.standard_value > self.max_value:
            raise ValidationError({'standard_value': '标准值不能大于最大值'})
        
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
    
    def is_within_range(self, value):
        """检查给定值是否在允许范围内"""
        if self.min_value is not None and value < self.min_value:
            return False
        if self.max_value is not None and value > self.max_value:
            return False
        return True
    
    def get_excess_value(self, actual_value):
        """计算超出标准值的数量"""
        if actual_value <= self.standard_value:
            return 0
        return actual_value - self.standard_value
    
    def is_within_tolerance(self, value):
        """检查给定值是否在公差范围内"""
        if self.tolerance <= 0:
            return value == self.standard_value
        
        lower_bound = self.standard_value - self.tolerance
        upper_bound = self.standard_value + self.tolerance
        
        return lower_bound <= value <= upper_bound 