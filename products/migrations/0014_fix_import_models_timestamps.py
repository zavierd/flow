# Generated manually to fix timestamp fields for import models
# This migration adds missing updated_at fields to import models

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0013_add_import_models'),
    ]

    operations = [
        # Add updated_at field to ImportTask
        migrations.AddField(
            model_name='importtask',
            name='updated_at',
            field=models.DateTimeField(
                auto_now=True,
                verbose_name='更新时间',
                db_comment='记录最后更新的时间戳'
            ),
        ),

        # Add is_active field to ImportTask (from ActiveModel)
        migrations.AddField(
            model_name='importtask',
            name='is_active',
            field=models.BooleanField(
                default=True,
                verbose_name='是否启用',
                db_comment='记录状态，false表示已禁用',
                help_text='禁用后该记录将不在前台显示'
            ),
        ),

        # ImportTemplate already has updated_at and is_active fields

        # Add updated_at field to ImportError
        migrations.AddField(
            model_name='importerror',
            name='updated_at',
            field=models.DateTimeField(
                auto_now=True,
                verbose_name='更新时间',
                db_comment='记录最后更新的时间戳'
            ),
        ),

        # Add is_active field to ImportError (from ActiveModel)
        migrations.AddField(
            model_name='importerror',
            name='is_active',
            field=models.BooleanField(
                default=True,
                verbose_name='是否启用',
                db_comment='记录状态，false表示已禁用',
                help_text='禁用后该记录将不在前台显示'
            ),
        ),
    ]
