"""
导入相关模型
包含ImportTask、ImportTemplate、ImportError模型及其相关功能
"""

from django.db import models
from .base import *
from .mixins import ValidationMixin


class ImportTask(BaseModel):
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
        db_table_comment = "数据导入任务表 - 管理批量数据导入的任务状态和进度"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['status'], name='idx_import_task_status'),
            models.Index(fields=['task_type'], name='idx_import_task_type'),
            models.Index(fields=['created_by'], name='idx_import_task_creator'),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    def clean(self):
        """数据验证"""
        super().clean()
        
        # 验证进度值范围
        if not 0 <= self.progress <= 100:
            raise ValidationError({'progress': '进度值必须在0-100之间'})
        
        # 验证行数逻辑
        if self.processed_rows > self.total_rows:
            raise ValidationError({'processed_rows': '已处理行数不能超过总行数'})
        
        if self.success_rows + self.error_rows > self.processed_rows:
            raise ValidationError('成功行数与错误行数之和不能超过已处理行数')
    
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
    
    @property
    def success_rate(self):
        """成功率"""
        if self.processed_rows == 0:
            return 0
        return (self.success_rows / self.processed_rows) * 100
    
    @property
    def duration(self):
        """任务持续时间"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return timezone.now() - self.started_at
        return None
    
    def get_summary(self):
        """获取任务摘要"""
        return {
            'task_name': self.name,
            'task_type': self.get_task_type_display(),
            'status': self.get_status_display(),
            'total_rows': self.total_rows,
            'processed_rows': self.processed_rows,
            'success_rows': self.success_rows,
            'error_rows': self.error_rows,
            'success_rate': f"{self.success_rate:.1f}%",
            'progress': f"{self.progress:.1f}%",
            'duration': str(self.duration) if self.duration else None,
        }


class ImportTemplate(BaseModel, ValidationMixin):
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

    class Meta:
        verbose_name = "导入模板"
        verbose_name_plural = "导入模板"
        db_table_comment = "数据导入模板表 - 定义不同类型数据的导入规则和字段映射"
        ordering = ["name"]
        indexes = [
            models.Index(fields=['template_type'], name='idx_import_template_type'),
            models.Index(fields=['name'], name='idx_import_template_name'),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
    
    def clean(self):
        """数据验证"""
        super().clean()
        
        # 验证字段映射格式
        if not isinstance(self.field_mapping, dict):
            raise ValidationError({'field_mapping': '字段映射必须是字典格式'})
        
        # 验证必填字段格式
        if not isinstance(self.required_fields, list):
            raise ValidationError({'required_fields': '必填字段必须是列表格式'})
        
        # 验证验证规则格式
        if not isinstance(self.validation_rules, dict):
            raise ValidationError({'validation_rules': '验证规则必须是字典格式'})
    
    def get_mapped_field(self, excel_column):
        """根据Excel列名获取对应的模型字段"""
        return self.field_mapping.get(excel_column)
    
    def is_required_field(self, field_name):
        """检查字段是否为必填"""
        return field_name in self.required_fields
    
    def get_validation_rule(self, field_name):
        """获取字段的验证规则"""
        return self.validation_rules.get(field_name, {})
    
    def validate_data_row(self, data_row):
        """验证数据行"""
        errors = []
        
        # 检查必填字段
        for required_field in self.required_fields:
            if required_field not in data_row or not str(data_row[required_field]).strip():
                errors.append(f"必填字段 '{required_field}' 缺失或为空")
        
        # 应用验证规则
        for field_name, value in data_row.items():
            if field_name in self.validation_rules:
                rule = self.validation_rules[field_name]
                
                # 长度验证
                if 'max_length' in rule and len(str(value)) > rule['max_length']:
                    errors.append(f"字段 '{field_name}' 长度超过限制({rule['max_length']})")
                
                # 格式验证
                if 'pattern' in rule:
                    import re
                    if not re.match(rule['pattern'], str(value)):
                        errors.append(f"字段 '{field_name}' 格式不正确")
                
                # 数值范围验证
                if 'min_value' in rule:
                    try:
                        if float(value) < rule['min_value']:
                            errors.append(f"字段 '{field_name}' 值小于最小值({rule['min_value']})")
                    except (ValueError, TypeError):
                        pass
                
                if 'max_value' in rule:
                    try:
                        if float(value) > rule['max_value']:
                            errors.append(f"字段 '{field_name}' 值大于最大值({rule['max_value']})")
                    except (ValueError, TypeError):
                        pass
        
        return errors


class ImportError(BaseModel):
    """导入错误模型 - 记录导入过程中的错误信息"""
    
    ERROR_TYPE_CHOICES = [
        ("validation", "数据验证错误"),
        ("format", "格式错误"),
        ("duplicate", "重复数据"),
        ("reference", "引用错误"),
        ("system", "系统错误"),
        ("quality_check", "质量检测"),
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

    class Meta:
        verbose_name = "导入错误"
        verbose_name_plural = "导入错误"
        db_table_comment = "数据导入错误表 - 记录导入过程中的详细错误信息"
        ordering = ["task", "row_number"]
        indexes = [
            models.Index(fields=['task'], name='idx_import_error_task'),
            models.Index(fields=['error_type'], name='idx_import_error_type'),
            models.Index(fields=['row_number'], name='idx_import_error_row'),
        ]

    def __str__(self):
        return f"{self.task.name} - 第{self.row_number}行: {self.error_message[:50]}"
    
    def clean(self):
        """数据验证"""
        super().clean()
        
        # 验证行号必须大于0
        if self.row_number <= 0:
            raise ValidationError({'row_number': '行号必须大于0'})
        
        # 验证原始数据格式
        if not isinstance(self.raw_data, dict):
            raise ValidationError({'raw_data': '原始数据必须是字典格式'})
    
    def get_error_summary(self):
        """获取错误摘要"""
        return {
            'row_number': self.row_number,
            'error_type': self.get_error_type_display(),
            'field_name': self.field_name,
            'error_message': self.error_message,
            'raw_data_preview': str(self.raw_data)[:100] + '...' if len(str(self.raw_data)) > 100 else str(self.raw_data)
        } 