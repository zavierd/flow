# Generated manually to fix final model fields
# This migration adds missing fields for SPUAttribute and ProductsDimension models

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0018_fix_skuattributevalue_fields'),
    ]

    operations = [
        # Add BaseModel fields to SPUAttribute
        migrations.AddField(
            model_name='spuattribute',
            name='created_at',
            field=models.DateTimeField(
                auto_now_add=True,
                verbose_name='创建时间',
                db_comment='记录创建的时间戳',
                null=True  # 允许为空，因为现有记录没有这个字段
            ),
        ),
        migrations.AddField(
            model_name='spuattribute',
            name='updated_at',
            field=models.DateTimeField(
                auto_now=True,
                verbose_name='更新时间',
                db_comment='记录最后更新的时间戳'
            ),
        ),
        migrations.AddField(
            model_name='spuattribute',
            name='is_active',
            field=models.BooleanField(
                default=True,
                verbose_name='是否启用',
                db_comment='记录状态，false表示已禁用',
                help_text='禁用后该记录将不在前台显示'
            ),
        ),
        
        # Add is_active field to ProductsDimension
        migrations.AddField(
            model_name='productsdimension',
            name='is_active',
            field=models.BooleanField(
                default=True,
                verbose_name='是否启用',
                db_comment='记录状态，false表示已禁用',
                help_text='禁用后该记录将不在前台显示'
            ),
        ),
    ]
