"""
AI输出数据格式映射配置
专门用于处理AI模型输出的表格数据格式
"""

# AI数据字段映射到系统字段（严格按照原始15列格式）
AI_DATA_FIELD_MAPPING = {
    # 基础信息映射（直接对应）
    '产品描述 (Description)': '产品描述',
    '产品编码 (Code)': '产品编码',
    '系列 (Series)': '系列',
    '类型代码 (Type_Code)': '类型代码',
    '宽度 (Width_cm)': '宽度',
    '高度 (Height_cm)': '高度',
    '深度 (Depth_cm)': '深度',
    '配置代码 (Config_Code)': '配置代码',
    '开门方向 (Door_Swing)': '开门方向',
    '备注 (Remarks)': '备注',

    # 价格等级映射（完整5级价格体系）
    '等级Ⅰ': '价格等级I',
    '等级Ⅱ': '价格等级II',
    '等级Ⅲ': '价格等级III',
    '等级Ⅳ': '价格等级IV',
    '等级Ⅴ': '价格等级V',
}

# 产品结构定义（正确的SPU/SKU关系）
PRODUCT_STRUCTURE_MAPPING = {
    # SPU提取字段：用于生成标准产品单元（一个SPU对应多个SKU）
    'spu_fields': {
        'primary': '产品描述',    # 主要用于提取SPU名称和描述
        'series': '系列',        # 产品系列，用于SPU分组
        'type_code': '类型代码',  # 柜体类型，用于SPU分类
        # 注意：不包含宽度、高度、深度等具体规格，这些应该是SKU级别的差异
    },

    # SKU基本信息字段：直接对应SKU属性
    'sku_fields': {
        'code': '产品编码',      # SKU唯一编码
        'name': '产品描述',      # SKU名称（从描述提取）
        'description': '备注',   # SKU详细描述
        'price_level': None,     # 价格等级（从5个等级中确定当前SKU的等级）
    },

    # 产品属性字段：存储为产品属性（每个SKU的具体属性）
    'attribute_fields': [
        '系列',           # 产品系列属性
        '类型代码',       # 柜体类型代码属性
        '宽度',           # 尺寸属性
        '高度',           # 尺寸属性
        '深度',           # 尺寸属性
        '配置代码',       # 配置代码属性
        '开门方向',       # 门板方向属性
        '等级',           # 板材等级属性（单一属性，值为等级Ⅰ-Ⅴ中的一个）
    ]
}

# 价格等级处理规则（正确逻辑：一个等级对应一个SKU）
PRICE_LEVEL_PROCESSING = {
    # 从5个价格等级创建5个不同的SKU
    'levels': ['等级Ⅰ', '等级Ⅱ', '等级Ⅲ', '等级Ⅳ', '等级Ⅴ'],
    'level_mapping': {
        '等级Ⅰ': {'display_name': '经济型', 'suffix': '-E'},
        '等级Ⅱ': {'display_name': '标准型', 'suffix': '-S'},
        '等级Ⅲ': {'display_name': '舒适型', 'suffix': '-C'},
        '等级Ⅳ': {'display_name': '豪华型', 'suffix': '-L'},
        '等级Ⅴ': {'display_name': '至尊型', 'suffix': '-P'},
    },
    # 等级属性定义
    'attribute_definition': {
        'name': '等级',
        'display_name': '板材级别',
        'type': 'select',
        'is_required': True,
        'is_filterable': True
    }
}

# 智能属性值处理配置（AI智能转换字母代码为显示名称）
INTELLIGENT_ATTRIBUTE_MAPPING = {
    # 柜体类型代码智能映射
    '类型代码': {
        'attribute_name': '柜体类型',
        'display_name': '柜体类型',
        'mapping': {
            'U': '单门底柜',
            'US': '单门单抽底柜',
            'UC': '内置抽屉柜',
            'D': '双门底柜',
            'DS': '双门单抽底柜',
            'DC': '双门内置抽屉柜',
            'T': '三门底柜',
            'W': '吊柜',
            'WS': '单抽吊柜',
        },
        'context_rules': {
            # 可以根据系列、品牌等信息进一步细化
            'NOVO': {'prefix': 'NOVO系列'},
            'CLASSIC': {'prefix': '经典系列'},
            'MODERN': {'prefix': '现代系列'},
        }
    },

    # 门板方向智能映射
    '开门方向': {
        'attribute_name': '门板方向',
        'display_name': '开门方向',
        'mapping': {
            'L': '左开',
            'R': '右开',
            'L/R': '左开/右开',
            'LR': '左开/右开',
            '-': '无门板',
            '': '双开',
        }
    },

    # 配置代码智能映射
    '配置代码': {
        'attribute_name': '产品配置',
        'display_name': '产品配置',
        'mapping': {
            'STD-001': '标准配置A型',
            'STD-002': '标准配置B型',
            'STD-003': '标准配置C型',
            'PRE-001': '高级配置A型',
            'PRE-002': '高级配置B型',
            'CUS-001': '定制配置A型',
        },
        'pattern_rules': {
            # 基于模式的智能识别
            r'STD-\d+': '标准配置',
            r'PRE-\d+': '高级配置',
            r'CUS-\d+': '定制配置',
        }
    },

    # 系列智能映射
    '系列': {
        'attribute_name': '产品系列',
        'display_name': '产品系列',
        'mapping': {
            'NOVO': 'NOVO现代系列',
            'CLASSIC': 'CLASSIC经典系列',
            'MODERN': 'MODERN时尚系列',
            'LUXURY': 'LUXURY奢华系列',
            'SIMPLE': 'SIMPLE简约系列',
        }
    }
}

# AI数据预处理规则（基于您的提示词输出）
AI_DATA_PREPROCESSING_RULES = {
    # 产品描述处理：处理<br>分隔的多行描述
    '产品描述 (Description)': {
        'extract_chinese': True,  # 提取中文部分作为主描述
        'keep_english': True,     # 保留英文作为英文名称
        'split_pattern': r'<br>',  # 使用<br>分割
        'lines_mapping': {
            0: '产品描述',    # 第一行：中文描述
            1: '英文名称',    # 第二行：英文名称
            2: '规格说明'     # 第三行：规格说明
        }
    },

    # 价格处理：处理带逗号的价格数据
    'price_fields': ['等级Ⅰ', '等级Ⅱ', '等级Ⅲ', '等级Ⅳ', '等级Ⅴ'],
    'price_processing': {
        'remove_comma': True,      # 去除千位分隔符
        'convert_to_float': True,  # 转换为浮点数
        'handle_dash': 0.0,        # '-' 转换为 0.0
        'handle_empty': 0.0        # 空值处理
    },

    # 尺寸处理：确保为整数类型
    'dimension_fields': ['宽度 (Width_cm)', '高度 (Height_cm)', '深度 (Depth_cm)'],
    'dimension_processing': {
        'convert_to_int': True,
        'handle_dash': None,       # '-' 转换为 None
        'handle_empty': None
    },

    # 编码处理：标准化格式
    '产品编码 (Code)': {
        'uppercase': True,
        'remove_spaces': True,
        'validate_format': r'^N-[A-Z]+\d+(-\d+)?-\d+(-[A-Z/]+)?$'
    },

    # 备注处理：保持<br>格式
    '备注 (Remarks)': {
        'preserve_br': True,       # 保持<br>换行符
        'handle_empty': '',        # 空值处理
        'inherit_from_above': True # 从上一行继承
    }
}

# 数据验证规则
AI_DATA_VALIDATION_RULES = {
    'required_fields': ['Code', 'Description'],
    'price_validation': {
        'min_value': 0,
        'max_value': 100000,
        'at_least_one_price': True  # 至少需要一个价格等级
    },
    'dimension_validation': {
        'width_range': (10, 300),   # 宽度范围 cm
        'height_range': (50, 250),  # 高度范围 cm  
        'depth_range': (30, 100)    # 深度范围 cm
    }
}

# 自动补全规则
AI_DATA_AUTO_COMPLETION = {
    # 从编码自动解析的字段
    'auto_parse_from_code': [
        '品牌编码',      # 固定为 ROYANA
        '产品系列',      # 从编码前缀解析
        '柜体类型',      # 从类型代码解析
        '宽度',         # 从编码解析
        '高度',         # 从编码解析（默认72）
        '深度',         # 从编码解析（默认56）
        '门板方向',      # 从后缀解析
    ],
    
    # 默认值设置
    'default_values': {
        '品牌编码': 'ROYANA',
        '产品系列': 'NOVO', 
        '高度': 72,
        '深度': 56,
        '产品状态': 'active',
        '库存数量': 0,
        '最小库存': 10
    },
    
    # 智能生成规则
    'smart_generation': {
        '产品名称': 'generate_from_description_and_code',
        '主分类': 'parse_from_cabinet_type',
        '子分类': 'parse_from_door_config',
        '分类编码': 'auto_generate',
        '英文名称': 'extract_from_description'
    }
}
