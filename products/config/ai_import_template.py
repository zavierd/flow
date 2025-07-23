"""
AI数据格式导入模板配置
基于AI模型输出的15列标准化数据格式
"""

# AI数据格式导入模板配置
AI_IMPORT_TEMPLATE = {
    'name': 'AI数据格式导入模板',
    'template_type': 'ai_data',
    'description': '基于AI模型输出的15列标准化数据格式，完美适配Royana产品导入系统',
    'version': '1.0',
    
    # 15列标准字段定义
    'fields': [
        # 基础信息字段
        {
            'name': '产品描述 (Description)',
            'field_key': 'description',
            'data_type': 'text',
            'required': True,
            'description': '产品完整描述，支持<br>换行符，包含中英文对照',
            'example': '单门底柜<br>1 door base unit<br>H.720 D.560',
            'validation': {
                'max_length': 500,
                'min_length': 5
            }
        },
        {
            'name': '产品编码 (Code)',
            'field_key': 'code',
            'data_type': 'text',
            'required': True,
            'description': '产品唯一编码，遵循Royana编码规范',
            'example': 'N-U30-7256-L/R',
            'validation': {
                'pattern': r'^N-[A-Z]+\d+(-\d+)?-\d+(-[A-Z/]+)?$',
                'max_length': 50
            }
        },
        {
            'name': '系列 (Series)',
            'field_key': 'series',
            'data_type': 'text',
            'required': False,
            'description': '产品系列代码，通常为N',
            'example': 'N',
            'default': 'N'
        },
        {
            'name': '类型代码 (Type_Code)',
            'field_key': 'type_code',
            'data_type': 'text',
            'required': False,
            'description': '柜体类型代码：U=单门底柜, US=单门单抽底柜, UC=内置抽屉柜',
            'example': 'U',
            'enum_values': ['U', 'US', 'UC']
        },
        
        # 尺寸字段
        {
            'name': '宽度 (Width_cm)',
            'field_key': 'width',
            'data_type': 'number',
            'required': False,
            'description': '产品宽度，单位：厘米',
            'example': 30,
            'validation': {
                'min': 10,
                'max': 300
            }
        },
        {
            'name': '高度 (Height_cm)',
            'field_key': 'height',
            'data_type': 'number',
            'required': False,
            'description': '产品高度，单位：厘米',
            'example': 72,
            'default': 72,
            'validation': {
                'min': 50,
                'max': 250
            }
        },
        {
            'name': '深度 (Depth_cm)',
            'field_key': 'depth',
            'data_type': 'number',
            'required': False,
            'description': '产品深度，单位：厘米',
            'example': 56,
            'default': 56,
            'validation': {
                'min': 30,
                'max': 100
            }
        },
        
        # 配置字段
        {
            'name': '配置代码 (Config_Code)',
            'field_key': 'config_code',
            'data_type': 'text',
            'required': False,
            'description': '配置代码，如抽屉高度等',
            'example': '10',
            'default': '-'
        },
        {
            'name': '开门方向 (Door_Swing)',
            'field_key': 'door_swing',
            'data_type': 'text',
            'required': False,
            'description': '门板开启方向',
            'example': 'L/R',
            'enum_values': ['L', 'R', 'L/R', '-'],
            'default': '-'
        },
        
        # 价格字段（5级价格体系）
        {
            'name': '等级Ⅰ',
            'field_key': 'price_level_1',
            'data_type': 'number',
            'required': False,
            'description': '价格等级I，成本价格',
            'example': '3,730',
            'validation': {
                'min': 0,
                'max': 999999
            },
            'format': 'currency'
        },
        {
            'name': '等级Ⅱ',
            'field_key': 'price_level_2',
            'data_type': 'number',
            'required': False,
            'description': '价格等级II',
            'example': '4,280',
            'validation': {
                'min': 0,
                'max': 999999
            },
            'format': 'currency'
        },
        {
            'name': '等级Ⅲ',
            'field_key': 'price_level_3',
            'data_type': 'number',
            'required': False,
            'description': '价格等级III，建议零售价',
            'example': '4,560',
            'validation': {
                'min': 0,
                'max': 999999
            },
            'format': 'currency'
        },
        {
            'name': '等级Ⅳ',
            'field_key': 'price_level_4',
            'data_type': 'number',
            'required': False,
            'description': '价格等级IV',
            'example': '4,870',
            'validation': {
                'min': 0,
                'max': 999999
            },
            'format': 'currency'
        },
        {
            'name': '等级Ⅴ',
            'field_key': 'price_level_5',
            'data_type': 'number',
            'required': False,
            'description': '价格等级V，最高价格',
            'example': '5,600',
            'validation': {
                'min': 0,
                'max': 999999
            },
            'format': 'currency'
        },
        
        # 备注字段
        {
            'name': '备注 (Remarks)',
            'field_key': 'remarks',
            'data_type': 'text',
            'required': False,
            'description': '产品备注说明，支持<br>换行符',
            'example': '一块可调节隔板<br>配四杆高抽',
            'validation': {
                'max_length': 1000
            }
        }
    ],
    
    # 数据验证规则
    'validation_rules': {
        'required_fields': ['产品描述 (Description)', '产品编码 (Code)'],
        'at_least_one_price': True,  # 至少需要一个价格等级
        'code_format_check': True,   # 检查编码格式
        'dimension_consistency': True,  # 检查尺寸一致性
    },
    
    # 自动补全规则
    'auto_completion': {
        'brand_code': 'ROYANA',
        'product_series': 'NOVO',
        'default_height': 72,
        'default_depth': 56,
        'product_status': 'active',
        'stock_quantity': 0,
        'min_stock': 10
    },
    
    # 示例数据
    'sample_data': [
        {
            '产品描述 (Description)': '单门底柜<br>1 door base unit<br>H.720 D.560',
            '产品编码 (Code)': 'N-U30-7256-L/R',
            '系列 (Series)': 'N',
            '类型代码 (Type_Code)': 'U',
            '宽度 (Width_cm)': 30,
            '高度 (Height_cm)': 72,
            '深度 (Depth_cm)': 56,
            '配置代码 (Config_Code)': '-',
            '开门方向 (Door_Swing)': 'L/R',
            '等级Ⅰ': '-',
            '等级Ⅱ': '3,730',
            '等级Ⅲ': '3,970',
            '等级Ⅳ': '4,180',
            '等级Ⅴ': '4,810',
            '备注 (Remarks)': '一块可调节隔板'
        },
        {
            '产品描述 (Description)': '单门单抽底柜<br>1 door 1 drawer base unit<br>H.720 D.560',
            '产品编码 (Code)': 'N-US30-10-7256-L/R',
            '系列 (Series)': 'N',
            '类型代码 (Type_Code)': 'US',
            '宽度 (Width_cm)': 30,
            '高度 (Height_cm)': 72,
            '深度 (Depth_cm)': 56,
            '配置代码 (Config_Code)': '10',
            '开门方向 (Door_Swing)': 'L/R',
            '等级Ⅰ': '-',
            '等级Ⅱ': '4,700',
            '等级Ⅲ': '4,900',
            '等级Ⅳ': '5,080',
            '等级Ⅴ': '5,550',
            '备注 (Remarks)': '一组低抽<br>一块可调节隔板'
        },
        {
            '产品描述 (Description)': '内置抽屉柜<br>Inner drawers base unit<br>H.720 D.560',
            '产品编码 (Code)': 'N-UC30-30-7256',
            '系列 (Series)': 'N',
            '类型代码 (Type_Code)': 'UC',
            '宽度 (Width_cm)': 30,
            '高度 (Height_cm)': 72,
            '深度 (Depth_cm)': 56,
            '配置代码 (Config_Code)': '30',
            '开门方向 (Door_Swing)': '-',
            '等级Ⅰ': '-',
            '等级Ⅱ': '8,890',
            '等级Ⅲ': '9,070',
            '等级Ⅳ': '9,230',
            '等级Ⅴ': '10,160',
            '备注 (Remarks)': '一块抽拉门板<br>配四杆高抽<br>二组内置抽屉'
        }
    ]
}

# 字段映射配置
FIELD_MAPPING = {
    field['name']: field['field_key'] 
    for field in AI_IMPORT_TEMPLATE['fields']
}

# 必填字段列表
REQUIRED_FIELDS = [
    field['name'] for field in AI_IMPORT_TEMPLATE['fields'] 
    if field.get('required', False)
]

# 价格字段列表
PRICE_FIELDS = [
    field['name'] for field in AI_IMPORT_TEMPLATE['fields'] 
    if field['field_key'].startswith('price_level')
]

# 尺寸字段列表
DIMENSION_FIELDS = [
    field['name'] for field in AI_IMPORT_TEMPLATE['fields'] 
    if field['field_key'] in ['width', 'height', 'depth']
]
