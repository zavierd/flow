# Generated manually to fix remaining model fields
# This migration adds missing fields for ProductImage and SKU models

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0016_fix_all_standard_model_fields'),
    ]

    operations = [
        # Add updated_at field to ProductImage (from TimestampedModel via BaseModel)
        migrations.AddField(
            model_name='productimage',
            name='updated_at',
            field=models.DateTimeField(
                auto_now=True,
                verbose_name='更新时间',
                db_comment='记录最后更新的时间戳'
            ),
        ),
        
        # Add is_active field to SKU (from ActiveModel via BaseModel/StandardModel)
        migrations.AddField(
            model_name='sku',
            name='is_active',
            field=models.BooleanField(
                default=True,
                verbose_name='是否启用',
                db_comment='记录状态，false表示已禁用',
                help_text='禁用后该记录将不在前台显示'
            ),
        ),
    ]
