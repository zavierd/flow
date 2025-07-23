"""
Models 基础配置模块
包含所有模型的共用导入、基础类和配置
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from mptt.models import MPTTModel, TreeForeignKey
import uuid
from django.utils import timezone


class TimestampedModel(models.Model):
    """
    带时间戳的抽象基础模型
    为继承的模型自动添加创建时间和更新时间字段
    """
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
        abstract = True


class ActiveModel(models.Model):
    """
    带激活状态的抽象基础模型
    为继承的模型自动添加激活状态字段
    """
    is_active = models.BooleanField(
        default=True, 
        verbose_name="是否启用",
        db_comment="记录状态，false表示已禁用",
        help_text="禁用后该记录将不在前台显示"
    )

    class Meta:
        abstract = True


class OrderedModel(models.Model):
    """
    带排序的抽象基础模型
    为继承的模型自动添加排序字段
    """
    order = models.IntegerField(
        default=0, 
        verbose_name="排序",
        db_comment="显示顺序，数字越小越靠前",
        help_text="显示顺序，数字越小越靠前"
    )

    class Meta:
        abstract = True


class DescribedModel(models.Model):
    """
    带描述的抽象基础模型
    为继承的模型自动添加描述字段
    """
    description = models.TextField(
        blank=True, 
        default='',
        verbose_name="描述",
        db_comment="详细描述信息",
        help_text="详细描述信息"
    )

    class Meta:
        abstract = True


class CodedModel(models.Model):
    """
    带编码的抽象基础模型
    为继承的模型自动添加编码字段
    """
    code = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="编码",
        db_comment="唯一标识码，用于系统内部识别",
        help_text="英文编码，必须唯一"
    )

    class Meta:
        abstract = True


class BaseModel(TimestampedModel, ActiveModel):
    """
    基础模型，包含时间戳和激活状态
    适用于大部分业务模型
    """
    
    class Meta:
        abstract = True


class StandardModel(BaseModel, CodedModel, DescribedModel, OrderedModel):
    """
    标准模型，包含完整的基础字段
    适用于主要业务实体模型
    """
    
    class Meta:
        abstract = True


# 常用选择字段定义
COMMON_STATUS_CHOICES = [
    ('active', '启用'),
    ('inactive', '停用'),
    ('draft', '草稿'),
]

PRICE_UNIT_CHOICES = [
    ('元/件', '元/件'),
    ('元/㎡', '元/㎡'),
    ('元/米', '元/米'),
    ('元/套', '元/套'),
]

# 常用验证器
def validate_positive(value):
    """验证正数"""
    if value <= 0:
        raise ValidationError('该值必须大于0')

def validate_non_negative(value):
    """验证非负数"""
    if value < 0:
        raise ValidationError('该值不能为负数') 