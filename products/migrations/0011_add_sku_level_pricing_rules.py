# Generated by Django 5.0.6 on 2025-07-18 06:17

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_productspricingrule_productsdimension_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productspricingrule',
            options={'ordering': ['spu', 'sku', 'rule_type', 'threshold_value'], 'verbose_name': '产品加价规则', 'verbose_name_plural': '产品加价规则'},
        ),
        migrations.AlterModelTableComment(
            name='productspricingrule',
            table_comment=None,
        ),
        migrations.RemoveConstraint(
            model_name='productspricingrule',
            name='unique_pricing_rule_per_spu_type_threshold',
        ),
        migrations.RemoveIndex(
            model_name='productspricingrule',
            name='idx_pricing_rule_spu',
        ),
        migrations.RemoveIndex(
            model_name='productspricingrule',
            name='idx_pricing_rule_type',
        ),
        migrations.RemoveIndex(
            model_name='productspricingrule',
            name='idx_pricing_rule_active',
        ),
        migrations.RemoveIndex(
            model_name='productspricingrule',
            name='idx_pricing_rule_effective',
        ),
        migrations.RemoveIndex(
            model_name='productspricingrule',
            name='idx_pricing_rule_expiry',
        ),
        migrations.AddField(
            model_name='productspricingrule',
            name='sku',
            field=models.ForeignKey(blank=True, help_text='可选：指定SKU时，规则仅应用于该SKU（优先级高于SPU规则）', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pricing_rules', to='products.sku', verbose_name='SKU'),
        ),
        migrations.AlterField(
            model_name='productspricingrule',
            name='calculation_method',
            field=models.CharField(choices=[('fixed', '固定金额'), ('percentage', '百分比'), ('multiplier', '倍数'), ('step', '阶梯式')], default='step', max_length=20, verbose_name='计算方式'),
        ),
        migrations.AlterField(
            model_name='productspricingrule',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='productspricingrule',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='创建人'),
        ),
        migrations.AlterField(
            model_name='productspricingrule',
            name='description',
            field=models.TextField(blank=True, help_text='详细的规则说明', verbose_name='规则描述'),
        ),
        migrations.AlterField(
            model_name='productspricingrule',
            name='effective_date',
            field=models.DateField(default=django.utils.timezone.now, help_text='规则开始生效的日期', verbose_name='生效日期'),
        ),
        migrations.AlterField(
            model_name='productspricingrule',
            name='expiry_date',
            field=models.DateField(blank=True, help_text='可选：规则失效的日期', null=True, verbose_name='失效日期'),
        ),
        migrations.AlterField(
            model_name='productspricingrule',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='是否激活'),
        ),
        migrations.AlterField(
            model_name='productspricingrule',
            name='max_increment',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='可选：限制最大加价金额', max_digits=10, null=True, verbose_name='最大加价'),
        ),
        migrations.AlterField(
            model_name='productspricingrule',
            name='multiplier',
            field=models.DecimalField(decimal_places=2, default=1.0, help_text='用于倍数计算方式', max_digits=5, verbose_name='倍数'),
        ),
        migrations.AlterField(
            model_name='productspricingrule',
            name='name',
            field=models.CharField(help_text='便于识别的规则名称', max_length=100, verbose_name='规则名称'),
        ),
        migrations.AlterField(
            model_name='productspricingrule',
            name='price_increment',
            field=models.DecimalField(decimal_places=2, help_text='每个单位增量的价格，例如每10mm加收20元', max_digits=10, verbose_name='价格增量'),
        ),
        migrations.AlterField(
            model_name='productspricingrule',
            name='rule_type',
            field=models.CharField(choices=[('height', '高度'), ('width', '宽度'), ('depth', '厚度/深度'), ('weight', '重量'), ('area', '面积'), ('volume', '体积')], help_text='指定这个规则适用于哪种尺寸维度', max_length=20, verbose_name='规则类型'),
        ),
        migrations.AlterField(
            model_name='productspricingrule',
            name='spu',
            field=models.ForeignKey(help_text='规则所属的SPU，当SKU为空时应用于整个SPU', on_delete=django.db.models.deletion.CASCADE, related_name='pricing_rules', to='products.spu', verbose_name='SPU'),
        ),
        migrations.AlterField(
            model_name='productspricingrule',
            name='threshold_value',
            field=models.DecimalField(decimal_places=2, help_text='超过此值开始计费，例如高度超过2335mm', max_digits=10, verbose_name='阈值'),
        ),
        migrations.AlterField(
            model_name='productspricingrule',
            name='unit_increment',
            field=models.DecimalField(decimal_places=2, default=1, help_text='计费单位，例如每10mm', max_digits=10, verbose_name='单位增量'),
        ),
        migrations.AlterField(
            model_name='productspricingrule',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='更新时间'),
        ),
        migrations.AlterUniqueTogether(
            name='productspricingrule',
            unique_together={('spu', 'sku', 'rule_type', 'threshold_value')},
        ),
        migrations.AlterModelTable(
            name='productspricingrule',
            table='products_pricing_rule',
        ),
    ]
