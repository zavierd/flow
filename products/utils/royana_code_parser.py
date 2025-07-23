"""
Royana 产品编码智能解析器
基于产品编码规则自动解析产品信息
"""

import re
from typing import Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class ParsedProductInfo:
    """解析后的产品信息"""
    brand_code: str
    series: str
    cabinet_type: str
    drawer_config: str
    width: int
    height: int
    depth: int
    drawer_height: Optional[int] = None
    drawer_count: Optional[int] = None
    door_direction: Optional[str] = None
    category_code: str = ''
    spu_code: str = ''
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'brand_code': self.brand_code,
            'series': self.series,
            'cabinet_type': self.cabinet_type,
            'drawer_config': self.drawer_config,
            'width': self.width,
            'height': self.height,
            'depth': self.depth,
            'drawer_height': self.drawer_height,
            'drawer_count': self.drawer_count,
            'door_direction': self.door_direction,
            'category_code': self.category_code,
            'spu_code': self.spu_code
        }


class RoyanaCodeParser:
    """Royana 产品编码解析器"""
    
    # 编码规则映射
    BRAND_MAPPING = {
        'N-': 'ROYANA'
    }
    
    SERIES_MAPPING = {
        'N-': 'NOVO'
    }
    
    CABINET_TYPE_MAPPING = {
        'U': '底柜'
    }
    
    DRAWER_CONFIG_MAPPING = {
        'U': '无抽屉',      # 基础单门底柜
        'US': '外置抽屉',   # 外部抽屉（Schublade）
        'UC': '内置抽屉'    # 隐藏式抽屉（Concealed）
    }
    
    DOOR_DIRECTION_MAPPING = {
        'L': '左开',
        'R': '右开'
    }
    
    def __init__(self):
        # 编码解析正则表达式
        self.code_pattern = re.compile(
            r'^(?P<prefix>N-)'
            r'(?P<type>U[SC]?)'
            r'(?P<width>\d+)'
            r'(?P<drawer_config>-\d+)?'
            r'-(?P<dimensions>\d{4})'
            r'(?P<direction>-[LR])?$'
        )
    
    def parse_code(self, code: str) -> Optional[ParsedProductInfo]:
        """
        解析产品编码
        
        Args:
            code: 产品编码，如 'N-U30-7256' 或 'N-US60-10-7256-L'
            
        Returns:
            ParsedProductInfo: 解析后的产品信息，解析失败返回None
        """
        if not code or not isinstance(code, str):
            return None
            
        match = self.code_pattern.match(code.strip().upper())
        if not match:
            return None
        
        try:
            groups = match.groupdict()
            
            # 解析基础信息
            prefix = groups['prefix']
            type_code = groups['type']
            width = int(groups['width'])
            dimensions = groups['dimensions']
            
            # 解析尺寸（4位数字：前2位高度，后2位深度）
            height = int(dimensions[:2])
            depth = int(dimensions[2:])
            
            # 解析品牌和系列
            brand_code = self.BRAND_MAPPING.get(prefix, 'UNKNOWN')
            series = self.SERIES_MAPPING.get(prefix, 'UNKNOWN')
            
            # 解析柜体类型
            cabinet_type = self.CABINET_TYPE_MAPPING.get(type_code[0], '未知')
            
            # 解析抽屉配置
            drawer_config = self.DRAWER_CONFIG_MAPPING.get(type_code, '未知')
            
            # 解析抽屉特殊配置
            drawer_height = None
            drawer_count = None
            if groups['drawer_config']:
                drawer_value = int(groups['drawer_config'][1:])  # 去掉前面的'-'
                if type_code == 'US':
                    # 外置抽屉：数字表示抽屉面板高度
                    drawer_height = drawer_value
                elif type_code == 'UC':
                    # 内置抽屉：数字表示抽屉数量（30表示3个）
                    drawer_count = drawer_value // 10
            
            # 解析门板方向
            door_direction = None
            if groups['direction']:
                direction_code = groups['direction'][1:]  # 去掉前面的'-'
                door_direction = self.DOOR_DIRECTION_MAPPING.get(direction_code)
            
            # 生成分类编码和SPU编码
            category_code = self._generate_category_code(cabinet_type, drawer_config)
            spu_code = self._generate_spu_code(series, cabinet_type, drawer_config, width)
            
            return ParsedProductInfo(
                brand_code=brand_code,
                series=series,
                cabinet_type=cabinet_type,
                drawer_config=drawer_config,
                width=width,
                height=height,
                depth=depth,
                drawer_height=drawer_height,
                drawer_count=drawer_count,
                door_direction=door_direction,
                category_code=category_code,
                spu_code=spu_code
            )
            
        except (ValueError, KeyError, IndexError) as e:
            return None
    
    def _generate_category_code(self, cabinet_type: str, drawer_config: str) -> str:
        """生成分类编码"""
        type_map = {
            '底柜': 'UNDER',
            '吊柜': 'WALL',
            '高柜': 'TALL'
        }
        
        drawer_map = {
            '无抽屉': 'PLAIN',
            '外置抽屉': 'DRAWER',
            '内置抽屉': 'HIDDEN'
        }
        
        type_code = type_map.get(cabinet_type, 'UNKNOWN')
        drawer_code = drawer_map.get(drawer_config, 'UNKNOWN')
        
        return f"{type_code}_{drawer_code}"
    
    def _generate_spu_code(self, series: str, cabinet_type: str, drawer_config: str, width: int) -> str:
        """生成SPU编码"""
        return f"{series}_{cabinet_type}_{drawer_config}_{width}CM"
    
    def generate_product_name(self, parsed_info: ParsedProductInfo, base_name: str = None) -> str:
        """
        生成产品名称
        
        Args:
            parsed_info: 解析后的产品信息
            base_name: 基础名称，如果不提供则自动生成
            
        Returns:
            str: 生成的产品名称
        """
        if base_name:
            return base_name
        
        # 自动生成产品名称
        name_parts = [parsed_info.series + '系列']
        
        # 添加抽屉配置描述
        if parsed_info.drawer_config == '外置抽屉':
            name_parts.append('门抽组合')
        elif parsed_info.drawer_config == '内置抽屉':
            if parsed_info.drawer_count:
                name_parts.append(f'内置{parsed_info.drawer_count}抽')
            else:
                name_parts.append('内置抽屉')
        else:
            name_parts.append('单门')
        
        # 添加柜体类型
        name_parts.append(parsed_info.cabinet_type)
        
        # 添加宽度
        name_parts.append(f'{parsed_info.width}cm')
        
        # 添加门板方向（如果有）
        if parsed_info.door_direction:
            name_parts.append(parsed_info.door_direction)
        
        return ''.join(name_parts)
    
    def validate_code(self, code: str) -> tuple[bool, str]:
        """
        验证产品编码格式
        
        Args:
            code: 产品编码
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        if not code or not isinstance(code, str):
            return False, "产品编码不能为空"
        
        code = code.strip().upper()
        
        if not self.code_pattern.match(code):
            return False, "产品编码格式不符合Royana规范"
        
        parsed = self.parse_code(code)
        if not parsed:
            return False, "产品编码解析失败"
        
        # 验证尺寸合理性
        if not (10 <= parsed.width <= 300):
            return False, f"产品宽度 {parsed.width}cm 不在合理范围内(10-300cm)"
        
        if not (30 <= parsed.height <= 250):
            return False, f"产品高度 {parsed.height}cm 不在合理范围内(30-250cm)"
        
        if not (20 <= parsed.depth <= 80):
            return False, f"产品深度 {parsed.depth}cm 不在合理范围内(20-80cm)"
        
        return True, ""


# 全局解析器实例
royana_parser = RoyanaCodeParser()
