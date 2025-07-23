# Generated manually to fix all StandardModel fields
# This migration adds missing fields for models that inherit StandardModel

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0015_fix_brand_model_fields'),
    ]

    operations = [
        # Add order field to SKU (from OrderedModel via StandardModel)
        migrations.AddField(
            model_name='sku',
            name='order',
            field=models.IntegerField(
                default=0,
                verbose_name='排序',
                db_comment='显示顺序，数字越小越靠前',
                help_text='显示顺序，数字越小越靠前'
            ),
        ),
        
        # Add order field to SPU (from OrderedModel via StandardModel)
        migrations.AddField(
            model_name='spu',
            name='order',
            field=models.IntegerField(
                default=0,
                verbose_name='排序',
                db_comment='显示顺序，数字越小越靠前',
                help_text='显示顺序，数字越小越靠前'
            ),
        ),
    ]
