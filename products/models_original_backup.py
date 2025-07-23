from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from mptt.models import MPTTModel, TreeForeignKey
import uuid
from django.utils import timezone


class Category(MPTTModel):
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
    code = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="分类编码",
        db_comment="分类的唯一标识码，用于系统内部识别和API调用",
        help_text="英文编码，必须唯一，如：cabinet、base_cabinet等"
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
    order = models.IntegerField(
        default=0, 
        verbose_name="排序",
        db_comment="同级分类的显示顺序，数字越小越靠前",
        help_text="同级分类的显示顺序，数字越小越靠前"
    )
    description = models.TextField(
        blank=True, 
        default='',
        verbose_name="描述",
        db_comment="分类的详细描述信息",
        help_text="分类的详细描述，可选填写"
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name="是否启用",
        db_comment="分类状态，false表示已禁用",
        help_text="禁用后该分类及其子分类将不在前台显示"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="创建时间",
        db_comment="分类创建的时间戳"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="更新时间",
        db_comment="分类最后更新的时间戳"
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
        ]
        
    def __str__(self):
        return self.name
        
    def get_full_path(self):
        """获取完整的分类路径"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name
        
    def get_level(self):
        """获取分类层级"""
        level = 0
        current = self
        while current.parent:
            level += 1
            current = current.parent
        return level


class Brand(models.Model):
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
    code = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="品牌编码",
        db_comment="品牌的唯一标识码，用于系统内部识别",
        help_text="英文编码，必须唯一，如：ROYANA、OPPEIN等"
    )
    logo = models.ImageField(
        upload_to='brands/logos/', 
        null=True, 
        blank=True, 
        verbose_name="品牌Logo",
        db_comment="品牌标志图片文件路径",
        help_text="建议上传PNG格式，尺寸200x200像素"
    )
    description = models.TextField(
        blank=True, 
        default='',
        verbose_name="品牌描述",
        db_comment="品牌的详细介绍和特色描述",
        help_text="品牌的详细介绍，包括历史、特色、理念等"
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
    
    is_active = models.BooleanField(
        default=True, 
        verbose_name="是否启用",
        db_comment="品牌状态，false表示已禁用",
        help_text="禁用后该品牌的产品将不在前台显示"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="创建时间",
        db_comment="品牌创建的时间戳"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="更新时间",
        db_comment="品牌最后更新的时间戳"
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


class Attribute(models.Model):
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
    code = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="属性编码",
        db_comment="属性的唯一标识码，用于系统内部识别",
        help_text="英文编码，必须唯一，如：COLOR、SIZE、MATERIAL等"
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
    description = models.TextField(
        blank=True, 
        default='',
        verbose_name="描述",
        db_comment="属性的详细描述信息",
        help_text="属性的详细说明"
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
    order = models.IntegerField(
        default=0, 
        verbose_name="排序",
        db_comment="属性的显示顺序，数字越小越靠前",
        help_text="属性的显示顺序，数字越小越靠前"
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name="是否启用",
        db_comment="属性状态，false表示已禁用",
        help_text="禁用后该属性将不在产品配置中显示"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="创建时间",
        db_comment="属性创建的时间戳"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="更新时间",
        db_comment="属性最后更新的时间戳"
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


class AttributeValue(models.Model):
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
    is_active = models.BooleanField(
        default=True, 
        verbose_name="是否启用",
        db_comment="属性值状态，false表示已禁用",
        help_text="禁用后该属性值不可选择"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="创建时间",
        db_comment="属性值创建的时间戳"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="更新时间",
        db_comment="属性值最后更新的时间戳"
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


class SPU(models.Model):
    """
    SPU (SPU产品单元) 模型
    
    代表一个SPU产品单元，它是一组具有共同属性的产品的集合。
    SPU本身不是一个具体的、可销售的商品，而是一个产品模板。
    例如，“iPhone 15 Pro”是一个SPU，而“蓝色、256GB的iPhone 15 Pro”是一个SKU。
    """
    
    name = models.CharField(
        max_length=200, 
        verbose_name="产品名称",
        db_comment="SPU的标准名称",
        help_text="产品的标准名称，如：NOVO系列单门单抽底柜"
    )
    code = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="产品编码",
        db_comment="SPU的唯一标识码",
        help_text="产品编码，必须唯一，如：N-US-7256"
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='spus',
        verbose_name="产品分类",
        db_comment="所属的产品分类ID"
    )
    brand = models.ForeignKey(
        Brand, 
        on_delete=models.CASCADE, 
        related_name='spus',
        null=True,
        blank=True,
        verbose_name="品牌",
        db_comment="所属的品牌ID"
    )
    description = models.TextField(
        blank=True, 
        default='',
        verbose_name="产品描述",
        db_comment="SPU的详细描述信息",
        help_text="产品的详细描述"
    )
    
    # 关联可配置属性
    attributes = models.ManyToManyField(
        Attribute, 
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
    
    is_active = models.BooleanField(
        default=True, 
        verbose_name="是否启用",
        db_comment="SPU状态，false表示已禁用",
        help_text="禁用后基于此SPU的SKU将不可创建"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="创建时间",
        db_comment="SPU创建的时间戳"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="更新时间",
        db_comment="SPU最后更新的时间戳"
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="创建人",
        db_comment="创建此SPU的用户ID"
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


class SPUAttribute(models.Model):
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
        Attribute, 
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


class SKU(models.Model):
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
    code = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="产品编码",
        db_comment="SKU的唯一标识码，通常包含属性编码",
        help_text="产品编码，必须唯一，如：N-US30-10-7256-L"
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
        SPU, 
        on_delete=models.CASCADE, 
        related_name='skus',
        verbose_name="SPU产品单元",
        db_comment="基于的SPU模板ID"
    )
    brand = models.ForeignKey(
        Brand, 
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
    description = models.TextField(
        blank=True, 
        default='',
        verbose_name="产品描述",
        db_comment="SKU的详细描述信息",
        help_text="产品的详细描述"
    )
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
    
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="创建时间",
        db_comment="SKU创建的时间戳"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="更新时间",
        db_comment="SKU最后更新的时间戳"
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="创建人",
        db_comment="创建此SKU的用户ID"
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

    def get_attribute_value(self, attribute_code):
        """获取指定属性的值(关系表存储)"""
        return self.get_relational_attribute_value(attribute_code)

    def set_attribute_value(self, attribute_code, value):
        """设置指定属性的值(关系表存储)"""
        self.set_relational_attribute_value(attribute_code, value)

    def clean(self):
        """数据验证"""
        super().clean()
        
        # 暂时禁用严格的属性配置验证，避免提交时的验证错误
        # 如果需要启用，可以取消注释下面的代码
        # try:
        #     self.validate_configuration()
        # except ValidationError as e:
        #     # 直接抛出原始的ValidationError，不要包装
        #     raise e
            
        # 验证价格逻辑
        if self.cost_price and self.price and self.cost_price > self.price:
            raise ValidationError("成本价不能高于售价")
            
        if self.market_price and self.price and self.market_price < self.price:
            raise ValidationError("市场价不能低于售价")

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
            
        # 验证所有关系表配置值的有效性
        if self.pk:
            for sku_attr_value in self.sku_attribute_values.all():
                value = sku_attr_value.custom_value or (sku_attr_value.attribute_value.value if sku_attr_value.attribute_value else None)
                if value and str(value).strip():
                    try:
                        self._validate_attribute_value(sku_attr_value.attribute, value)
                    except ValidationError:
                        # 忽略无效属性值
                        pass

    def _validate_attribute_value(self, attribute, value):
        """验证单个属性值的有效性"""
        if attribute.type == 'number':
            try:
                float(value)
            except (ValueError, TypeError):
                raise ValidationError(f"属性 '{attribute.name}' 的值必须是数字")
                
        elif attribute.type == 'boolean':
            if not isinstance(value, bool):
                raise ValidationError(f"属性 '{attribute.name}' 的值必须是布尔值")
                
        elif attribute.type == 'select':
            # 验证选择值是否在允许的范围内
            valid_values = list(attribute.values.filter(is_active=True).values_list('value', flat=True))
            if value not in valid_values:
                raise ValidationError(f"属性 '{attribute.name}' 的值 '{value}' 不在允许的选择范围内")
                
        elif attribute.type == 'multiselect':
            if not isinstance(value, list):
                raise ValidationError(f"属性 '{attribute.name}' 的值必须是列表格式")
            
            valid_values = list(attribute.values.filter(is_active=True).values_list('value', flat=True))
            for v in value:
                if v not in valid_values:
                    raise ValidationError(f"属性 '{attribute.name}' 的值 '{v}' 不在允许的选择范围内")

    def save(self, *args, **kwargs):
        """保存时进行验证和数据处理"""
        # 在保存前进行完整验证
        self.full_clean()
        
        # 如果是新记录且没有设置创建人，尝试从请求中获取
        if not self.pk and not self.created_by:
            # 这里可以通过中间件或其他方式获取当前用户
            pass
            
        super().save(*args, **kwargs)

    @property
    def is_in_stock(self):
        """是否有库存"""
        return self.stock_quantity > 0

    @property
    def is_low_stock(self):
        """是否库存不足"""
        return self.stock_quantity <= self.min_stock

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

    def sync_json_to_relational(self):
        """同步JSON存储的属性值到关系表（已废弃，保留为兼容性）"""
        # 这个方法已经不再需要，因为attribute_values字段已被移除
        # 现在直接使用关系表存储属性值
        pass

    def sync_relational_to_json(self):
        """同步关系表的属性值到JSON字段（已废弃，保留为兼容性）"""
        # 这个方法已经不再需要，因为attribute_values字段已被移除
        # 现在直接使用关系表存储属性值
        pass


class SKUAttributeValue(models.Model):
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
        Attribute, 
        on_delete=models.CASCADE, 
        related_name='sku_attribute_values',
        verbose_name="属性",
        db_comment="关联的属性ID"
    )
    attribute_value = models.ForeignKey(
        AttributeValue, 
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
    
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="创建时间",
        db_comment="记录创建的时间戳"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="更新时间",
        db_comment="记录最后更新的时间戳"
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


class ProductImage(models.Model):
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
    is_active = models.BooleanField(
        default=True, 
        verbose_name="是否启用",
        db_comment="图片状态，false表示已禁用",
        help_text="禁用后该图片不会在前台显示"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="创建时间",
        db_comment="图片上传的时间戳"
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


class ProductsPricingRule(models.Model):
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
        SPU,
        on_delete=models.CASCADE,
        related_name='pricing_rules',
        verbose_name="SPU",
        help_text="规则所属的SPU，当SKU为空时应用于整个SPU"
    )
    
    sku = models.ForeignKey(
        SKU,
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
    is_active = models.BooleanField(
        default=True,
        verbose_name="是否激活"
    )
    
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
    
    description = models.TextField(
        blank=True,
        verbose_name="规则描述",
        help_text="详细的规则说明"
    )
    
    # 审计字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="创建人"
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
        from django.core.exceptions import ValidationError
        
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
    
    def calculate_increment(self, excess_value):
        """
        计算超出部分的加价
        
        Args:
            excess_value (Decimal): 超出阈值的数值
            
        Returns:
            Decimal: 计算出的加价金额
        """
        from decimal import Decimal
        import math
        
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
        from django.utils import timezone
        
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
        # 使用数据库字段排序，而不是添加计算字段
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


class ProductsDimension(models.Model):
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
        SKU,
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
    
    description = models.TextField(
        blank=True,
        default='',
        verbose_name="尺寸描述",
        db_comment="尺寸的详细描述和说明",
        help_text="尺寸的详细描述，包括测量方法、特殊说明等"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间",
        db_comment="记录创建的时间戳"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间",
        db_comment="记录最后更新的时间戳"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_dimensions',
        verbose_name="创建人",
        db_comment="创建此记录的用户ID"
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
            raise ValidationError("标准值必须大于0")
        
        # 验证最小值和最大值的逻辑关系
        if self.min_value is not None and self.standard_value < self.min_value:
            raise ValidationError("标准值不能小于最小值")
        
        if self.max_value is not None and self.standard_value > self.max_value:
            raise ValidationError("标准值不能大于最大值")
        
        if self.min_value is not None and self.max_value is not None:
            if self.min_value >= self.max_value:
                raise ValidationError("最小值必须小于最大值")
        
        # 验证公差必须大于等于0
        if self.tolerance < 0:
            raise ValidationError("公差不能为负数")
        
        # 验证自定义单位
        if self.unit == 'custom' and not self.custom_unit.strip():
            raise ValidationError("选择自定义单位时，必须填写自定义单位名称")
    
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


class SPUDimensionTemplate(models.Model):
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
    
    description = models.TextField(
        blank=True,
        default='',
        verbose_name="尺寸描述",
        db_comment="尺寸的详细描述和说明",
        help_text="尺寸的详细描述，包括测量方法、特殊说明等"
    )
    
    order = models.IntegerField(
        default=0,
        verbose_name="排序",
        db_comment="尺寸在SPU下的显示顺序",
        help_text="在产品尺寸配置界面的显示顺序"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间",
        db_comment="记录创建的时间戳"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间",
        db_comment="记录最后更新的时间戳"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_spu_dimension_templates',
        verbose_name="创建人",
        db_comment="创建此记录的用户ID"
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
        """模型验证"""
        super().clean()
        
        # 验证默认值必须大于0
        if self.default_value <= 0:
            raise ValidationError("默认值必须大于0")
        
        # 验证最小值和最大值的逻辑关系
        if self.min_value is not None and self.default_value < self.min_value:
            raise ValidationError("默认值不能小于最小值")
        
        if self.max_value is not None and self.default_value > self.max_value:
            raise ValidationError("默认值不能大于最大值")
        
        if self.min_value is not None and self.max_value is not None:
            if self.min_value >= self.max_value:
                raise ValidationError("最小值必须小于最大值")
        
        # 验证公差必须大于等于0
        if self.tolerance < 0:
            raise ValidationError("公差不能为负数")
        
        # 验证自定义单位
        if self.unit == 'custom' and not self.custom_unit.strip():
            raise ValidationError("选择自定义单位时，必须填写自定义单位名称")
    
    def get_display_unit(self):
        """获取显示用的单位"""
        if self.unit == 'custom':
            return self.custom_unit
        return self.get_unit_display()


# =============================================================================
# 导入系统相关模型
# =============================================================================

class ImportTask(models.Model):
    """导入任务模型 - 管理批量数据导入任务"""
    
    TASK_TYPE_CHOICES = [
        ("products", "产品数据"),
        ("categories", "分类数据"),
        ("brands", "品牌数据"),
        ("attributes", "属性数据"),
        ("mixed", "混合数据"),
    ]
    
    STATUS_CHOICES = [
        ("pending", "待处理"),
        ("processing", "处理中"),
        ("completed", "已完成"),
        ("failed", "失败"),
        ("partial", "部分成功"),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="任务ID"
    )
    
    name = models.CharField(
        max_length=200,
        verbose_name="任务名称",
        help_text="导入任务的名称"
    )
    
    task_type = models.CharField(
        max_length=20,
        choices=TASK_TYPE_CHOICES,
        default="products",
        verbose_name="导入类型"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="任务状态"
    )
    
    file_path = models.FileField(
        upload_to="import/files/",
        verbose_name="导入文件",
        help_text="上传的Excel文件"
    )
    
    total_rows = models.IntegerField(
        default=0,
        verbose_name="总行数"
    )
    
    processed_rows = models.IntegerField(
        default=0,
        verbose_name="已处理行数"
    )
    
    success_rows = models.IntegerField(
        default=0,
        verbose_name="成功行数"
    )
    
    error_rows = models.IntegerField(
        default=0,
        verbose_name="错误行数"
    )
    
    progress = models.FloatField(
        default=0.0,
        verbose_name="进度百分比",
        help_text="0-100"
    )
    
    result_summary = models.JSONField(
        default=dict,
        verbose_name="结果摘要",
        help_text="导入结果的详细统计"
    )
    
    error_details = models.TextField(
        blank=True,
        verbose_name="错误详情",
        help_text="导入过程中的错误信息"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )
    
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="开始时间"
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="完成时间"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="创建人"
    )
    
    class Meta:
        verbose_name = "导入任务"
        verbose_name_plural = "导入任务"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    def update_progress(self, processed=None, success=None, errors=None, progress=None):
        """更新导入进度"""
        if processed is not None:
            self.processed_rows = processed
        if success is not None:
            self.success_rows = success
        if errors is not None:
            self.error_rows = errors
        if progress is not None:
            self.progress = progress
        self.save()
    
    def start_task(self):
        """开始任务"""
        self.status = 'processing'
        self.started_at = timezone.now()
        self.save()
    
    def complete_task(self, status='completed'):
        """完成任务"""
        self.status = status
        self.completed_at = timezone.now()
        self.progress = 100.0
        self.save()
    
    def fail_task(self, error_message):
        """任务失败"""
        self.status = 'failed'
        self.completed_at = timezone.now()
        self.error_details = error_message
        self.save()


class ImportTemplate(models.Model):
    """导入模板模型 - 管理不同类型的导入模板配置"""
    
    TEMPLATE_TYPE_CHOICES = [
        ("products", "产品数据"),
        ("categories", "分类数据"),
        ("brands", "品牌数据"),
        ("attributes", "属性数据"),
        ("mixed", "混合数据"),
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="模板名称"
    )
    
    template_type = models.CharField(
        max_length=20,
        choices=TEMPLATE_TYPE_CHOICES,
        verbose_name="模板类型"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="模板描述"
    )
    
    field_mapping = models.JSONField(
        verbose_name="字段映射",
        help_text="Excel列名到模型字段的映射关系"
    )
    
    required_fields = models.JSONField(
        default=list,
        verbose_name="必填字段",
        help_text="必须提供的字段列表"
    )
    
    validation_rules = models.JSONField(
        default=dict,
        verbose_name="验证规则",
        help_text="字段验证规则"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="是否启用"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间"
    )
    
    class Meta:
        verbose_name = "导入模板"
        verbose_name_plural = "导入模板"
        ordering = ["name"]
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class ImportError(models.Model):
    """导入错误模型 - 记录导入过程中的错误信息"""
    
    ERROR_TYPE_CHOICES = [
        ("validation", "数据验证错误"),
        ("format", "格式错误"),
        ("duplicate", "重复数据"),
        ("reference", "引用错误"),
        ("system", "系统错误"),
    ]
    
    task = models.ForeignKey(
        ImportTask,
        on_delete=models.CASCADE,
        related_name="errors",
        verbose_name="导入任务"
    )
    
    row_number = models.IntegerField(
        verbose_name="行号"
    )
    
    error_type = models.CharField(
        max_length=20,
        choices=ERROR_TYPE_CHOICES,
        verbose_name="错误类型"
    )
    
    field_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="字段名"
    )
    
    error_message = models.TextField(
        verbose_name="错误消息"
    )
    
    raw_data = models.JSONField(
        verbose_name="原始数据",
        help_text="导致错误的原始行数据"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )
    
    class Meta:
        verbose_name = "导入错误"
        verbose_name_plural = "导入错误"
        ordering = ["task", "row_number"]
    
    def __str__(self):
        return f"{self.task.name} - 第{self.row_number}行: {self.error_message[:50]}"
