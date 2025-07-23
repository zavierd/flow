"""
Royana 整木定制产品导入模板配置
基于产品编码智能解析的一体化导入方案
"""

# Royana 产品导入模板配置
ROYANA_IMPORT_TEMPLATE = {
    'name': 'Royana整木定制产品导入模板',
    'template_type': 'products',
    'description': '基于AI识别数据的Royana产品导入方案，支持批量导入产品信息和多级价格',

    # Excel 表格列定义
    'fields': [
        # 基础产品信息（必填）
        ('产品编码', 'code', 'text', True, '产品的唯一编码，如：N-U30-7256-L/R'),
        ('产品描述', 'description', 'text', True, '产品描述，如：单门底柜 1 door base unit H.720 D.560'),
        ('产品名称', 'name', 'text', False, '产品显示名称，不填写将从描述自动生成'),

        # 价格信息（多级价格体系）
        ('价格等级II', 'price_level_2', 'number', False, '价格等级II，单位：元'),
        ('价格等级III', 'price_level_3', 'number', False, '价格等级III，单位：元'),
        ('价格等级IV', 'price_level_4', 'number', False, '价格等级IV，单位：元'),
        ('价格等级V', 'price_level_5', 'number', False, '价格等级V，单位：元'),
        ('默认销售价格', 'price', 'number', False, '默认销售价格，不填写将使用价格等级III'),

        # 产品特性（从编码自动解析，也可手动填写）
        ('品牌编码', 'brand_code', 'text', False, '品牌编码，默认：ROYANA'),
        ('产品系列', 'series', 'text', False, '产品系列，默认：NOVO'),
        ('柜体类型', 'cabinet_type', 'text', False, '柜体类型：单门底柜、双门底柜、单门单抽底柜、内置抽屉柜等'),
        ('门板数量', 'door_count', 'number', False, '门板数量，如：1、2'),
        ('抽屉数量', 'drawer_count', 'number', False, '抽屉数量，如：0、1、2'),
        ('抽屉类型', 'drawer_type', 'text', False, '抽屉类型：无、外置抽屉、内置抽屉'),

        # 尺寸信息（从编码解析或手动填写）
        ('宽度', 'width', 'number', False, '产品宽度，单位：cm'),
        ('高度', 'height', 'number', False, '产品高度，单位：cm，默认：72'),
        ('深度', 'depth', 'number', False, '产品深度，单位：cm，默认：56'),

        # 门板配置
        ('门板方向', 'door_direction', 'text', False, '门板方向：左开、右开、双开、无门板'),
        ('门板配置', 'door_config', 'text', False, '门板配置说明'),

        # 配件和备注
        ('备注说明', 'remarks', 'text', False, '产品备注，如：一块可调节隔板、配四杆高抽等'),
        ('配件清单', 'accessories', 'text', False, '产品配件清单'),
        ('安装说明', 'installation_notes', 'text', False, '安装注意事项'),

        # 分类信息
        ('主分类', 'main_category', 'text', False, '主分类，如：底柜、吊柜、高柜'),
        ('子分类', 'sub_category', 'text', False, '子分类，如：单门、双门、抽屉柜'),
        ('分类编码', 'category_code', 'text', False, '分类编码，不填写将自动生成'),

        # 业务信息
        ('成本价格', 'cost_price', 'number', False, '产品成本价格，单位：元'),
        ('库存数量', 'stock_quantity', 'number', False, '初始库存数量，默认：0'),
        ('最小库存', 'min_stock', 'number', False, '库存预警线，默认：10'),
        ('产品状态', 'status', 'select', False, '产品状态：active(上架)、inactive(下架)、draft(草稿)'),

        # 扩展信息
        ('英文名称', 'english_name', 'text', False, '产品英文名称'),
        ('规格说明', 'specifications', 'text', False, '详细规格参数'),
        ('使用场景', 'usage_scenario', 'text', False, '适用场景说明'),
        ('产品特色', 'features', 'text', False, '产品特色和卖点'),
    ],
    
    # 示例数据（基于你提供的实际数据格式）
    'sample_data': [
        {
            '产品编码': 'N-U30-7256-L/R',
            '产品描述': '单门底柜 1 door base unit H.720 D.560',
            '产品名称': 'NOVO系列单门底柜30cm',
            '价格等级II': 3730.00,
            '价格等级III': 3970.00,
            '价格等级IV': 4180.00,
            '价格等级V': 4810.00,
            '默认销售价格': 3970.00,
            '品牌编码': 'ROYANA',
            '产品系列': 'NOVO',
            '柜体类型': '单门底柜',
            '门板数量': 1,
            '抽屉数量': 0,
            '抽屉类型': '无',
            '宽度': 30,
            '高度': 72,
            '深度': 56,
            '门板方向': '左开/右开',
            '备注说明': '一块可调节隔板',
            '主分类': '底柜',
            '子分类': '单门',
            '英文名称': '1 door base unit',
            '产品状态': 'active'
        },
        {
            '产品编码': 'N-U90-7256',
            '产品描述': '双门底柜 2 door base unit H.720 D.560',
            '产品名称': 'NOVO系列双门底柜90cm',
            '价格等级II': 6750.00,
            '价格等级III': 7180.00,
            '价格等级IV': 7830.00,
            '价格等级V': 9010.00,
            '默认销售价格': 7180.00,
            '品牌编码': 'ROYANA',
            '产品系列': 'NOVO',
            '柜体类型': '双门底柜',
            '门板数量': 2,
            '抽屉数量': 0,
            '抽屉类型': '无',
            '宽度': 90,
            '高度': 72,
            '深度': 56,
            '门板方向': '双开',
            '备注说明': '一块可调节隔板',
            '主分类': '底柜',
            '子分类': '双门',
            '英文名称': '2 door base unit',
            '产品状态': 'active'
        },
        {
            '产品编码': 'N-US45-10-7256-L/R',
            '产品描述': '单门单抽底柜 1 door 1 drawer base unit H.720 D.560',
            '产品名称': 'NOVO系列单门单抽底柜45cm',
            '价格等级II': 5320.00,
            '价格等级III': 5540.00,
            '价格等级IV': 5810.00,
            '价格等级V': 6350.00,
            '默认销售价格': 5540.00,
            '品牌编码': 'ROYANA',
            '产品系列': 'NOVO',
            '柜体类型': '单门单抽底柜',
            '门板数量': 1,
            '抽屉数量': 1,
            '抽屉类型': '外置抽屉',
            '宽度': 45,
            '高度': 72,
            '深度': 56,
            '门板方向': '左开/右开',
            '备注说明': '一组低抽，一块可调节隔板',
            '主分类': '底柜',
            '子分类': '门抽组合',
            '英文名称': '1 door 1 drawer base unit',
            '产品状态': 'active'
        },
        {
            '产品编码': 'N-UC60-30-7256',
            '产品描述': '内置抽屉柜 Inner drawers base unit H.720 D.560',
            '产品名称': 'NOVO系列内置抽屉柜60cm',
            '价格等级II': 10200.00,
            '价格等级III': 10400.00,
            '价格等级IV': 10690.00,
            '价格等级V': 11760.00,
            '默认销售价格': 10400.00,
            '品牌编码': 'ROYANA',
            '产品系列': 'NOVO',
            '柜体类型': '内置抽屉柜',
            '门板数量': 1,
            '抽屉数量': 2,
            '抽屉类型': '内置抽屉',
            '宽度': 60,
            '高度': 72,
            '深度': 56,
            '门板方向': '无门板',
            '备注说明': '一块抽拉门板，配四杆高抽，二组内置抽屉',
            '主分类': '底柜',
            '子分类': '内置抽屉',
            '英文名称': 'Inner drawers base unit',
            '产品状态': 'active'
        }
    ],
    
    # 字段映射（Excel列名 -> 模型字段名）
    'field_mapping': {
        '产品编码': 'code',
        '产品描述': 'description',
        '产品名称': 'name',
        '价格等级II': 'price_level_2',
        '价格等级III': 'price_level_3',
        '价格等级IV': 'price_level_4',
        '价格等级V': 'price_level_5',
        '默认销售价格': 'price',
        '品牌编码': 'brand_code',
        '产品系列': 'series',
        '柜体类型': 'cabinet_type',
        '门板数量': 'door_count',
        '抽屉数量': 'drawer_count',
        '抽屉类型': 'drawer_type',
        '宽度': 'width',
        '高度': 'height',
        '深度': 'depth',
        '门板方向': 'door_direction',
        '门板配置': 'door_config',
        '备注说明': 'remarks',
        '配件清单': 'accessories',
        '安装说明': 'installation_notes',
        '主分类': 'main_category',
        '子分类': 'sub_category',
        '分类编码': 'category_code',
        '成本价格': 'cost_price',
        '库存数量': 'stock_quantity',
        '最小库存': 'min_stock',
        '产品状态': 'status',
        '英文名称': 'english_name',
        '规格说明': 'specifications',
        '使用场景': 'usage_scenario',
        '产品特色': 'features'
    },

    # 必填字段
    'required_fields': ['code', 'description'],
    
    # 验证规则
    'validation_rules': {
        'code': {
            'pattern': r'^N-U[SC]?\d+(-\d+)?-\d{4}(-[LR])?(/R)?$',
            'message': '产品编码格式不正确，应符合Royana编码规范，如：N-U30-7256-L/R'
        },
        'description': {
            'required': True,
            'message': '产品描述不能为空'
        },
        'price_level_2': {
            'min': 0,
            'max': 999999.99,
            'message': '价格等级II必须在0-999999.99之间'
        },
        'price_level_3': {
            'min': 0,
            'max': 999999.99,
            'message': '价格等级III必须在0-999999.99之间'
        },
        'price_level_4': {
            'min': 0,
            'max': 999999.99,
            'message': '价格等级IV必须在0-999999.99之间'
        },
        'price_level_5': {
            'min': 0,
            'max': 999999.99,
            'message': '价格等级V必须在0-999999.99之间'
        },
        'width': {
            'min': 10,
            'max': 300,
            'message': '宽度必须在10-300cm之间'
        },
        'height': {
            'min': 30,
            'max': 250,
            'message': '高度必须在30-250cm之间'
        },
        'depth': {
            'min': 20,
            'max': 80,
            'message': '深度必须在20-80cm之间'
        },
        'door_count': {
            'min': 0,
            'max': 4,
            'message': '门板数量必须在0-4之间'
        },
        'drawer_count': {
            'min': 0,
            'max': 10,
            'message': '抽屉数量必须在0-10之间'
        }
    },

    # 枚举值定义
    'enums': {
        '产品状态': ['active', 'inactive', 'draft'],
        '柜体类型': ['单门底柜', '双门底柜', '单门单抽底柜', '内置抽屉柜', '吊柜', '高柜'],
        '抽屉类型': ['无', '外置抽屉', '内置抽屉', '混合抽屉'],
        '门板方向': ['左开', '右开', '左开/右开', '双开', '无门板'],
        '主分类': ['底柜', '吊柜', '高柜', '台面柜', '装饰柜'],
        '子分类': ['单门', '双门', '门抽组合', '内置抽屉', '开放式']
    }
}
