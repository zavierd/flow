# Generated manually to fix Brand model fields
# This migration adds missing fields for Brand model to match StandardModel

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0014_fix_import_models_timestamps'),
    ]

    operations = [
        # Add order field to Brand (from OrderedModel)
        migrations.AddField(
            model_name='brand',
            name='order',
            field=models.IntegerField(
                default=0,
                verbose_name='排序',
                db_comment='显示顺序，数字越小越靠前',
                help_text='显示顺序，数字越小越靠前'
            ),
        ),
    ]
