# Generated by Django 5.0.6 on 2024-07-15 00:00

from django.db import migrations

def create_board_level_attribute(apps, schema_editor):
    """创建板子级别属性和属性值"""
    Attribute = apps.get_model('products', 'Attribute')
    AttributeValue = apps.get_model('products', 'AttributeValue')
    
    # 创建板子级别属性
    board_level_attr, created = Attribute.objects.get_or_create(
        code='BOARD_LEVEL',
        defaults={
            'name': '板子级别',
            'type': 'select',
            'unit': '',
            'description': '产品使用的板子级别，不同级别价格不同',
            'is_required': True,
            'is_filterable': True,
            'order': 10,
            'is_active': True,
        }
    )
    
    # 定义板子级别选项
    board_levels = [
        ('II', 'Ⅱ级板'),
        ('III', 'Ⅲ级板'),
        ('IV', 'Ⅳ级板'),
        ('V', 'Ⅴ级板'),
    ]
    
    # 创建属性值
    for order, (value, display_name) in enumerate(board_levels, 1):
        AttributeValue.objects.get_or_create(
            attribute=board_level_attr,
            value=value,
            defaults={
                'display_name': display_name,
                'order': order,
                'is_active': True,
            }
        )
    
    print(f"板子级别属性创建{'成功' if created else '已存在'}")

def reverse_board_level_attribute(apps, schema_editor):
    """撤销板子级别属性创建"""
    Attribute = apps.get_model('products', 'Attribute')
    AttributeValue = apps.get_model('products', 'AttributeValue')
    
    try:
        # 删除属性值
        board_level_attr = Attribute.objects.get(code='BOARD_LEVEL')
        AttributeValue.objects.filter(attribute=board_level_attr).delete()
        # 删除属性
        board_level_attr.delete()
        print("板子级别属性删除成功")
    except Attribute.DoesNotExist:
        print("板子级别属性不存在")

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_add_remarks_field'),
    ]

    operations = [
        migrations.RunPython(
            create_board_level_attribute,
            reverse_board_level_attribute,
        ),
    ]