# Generated manually to fix SKUAttributeValue model fields
# This migration adds missing fields for SKUAttributeValue model to match BaseModel

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0017_fix_remaining_model_fields'),
    ]

    operations = [
        # SKUAttributeValue already has updated_at field, only add is_active

        # Add is_active field to SKUAttributeValue (from ActiveModel via BaseModel)
        migrations.AddField(
            model_name='skuattributevalue',
            name='is_active',
            field=models.BooleanField(
                default=True,
                verbose_name='是否启用',
                db_comment='记录状态，false表示已禁用',
                help_text='禁用后该记录将不在前台显示'
            ),
        ),
    ]
