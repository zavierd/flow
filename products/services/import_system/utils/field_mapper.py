"""
字段映射工具
负责将原始字段名映射为标准字段名
"""

from typing import Dict, Any


class FieldMapper:
    """字段映射器 - 单一职责：字段名标准化"""

    def __init__(self, field_mapping: Dict[str, str]):
        self.field_mapping = field_mapping
        # 创建反向映射以支持双向查找
        self.reverse_mapping = {v: k for k, v in field_mapping.items()}

    def map_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """将原始字段映射为标准字段"""
        mapped_data = {}

        for original_field, value in data.items():
            # 查找映射的标准字段名
            standard_field = self.field_mapping.get(original_field, original_field)
            mapped_data[standard_field] = value

        return mapped_data

    def reverse_map_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """将标准字段映射回原始字段"""
        reverse_mapped_data = {}

        for standard_field, value in data.items():
            # 查找原始字段名
            original_field = self.reverse_mapping.get(standard_field, standard_field)
            reverse_mapped_data[original_field] = value

        return reverse_mapped_data

    def get_standard_field(self, original_field: str) -> str:
        """获取标准字段名"""
        return self.field_mapping.get(original_field, original_field)

    def get_original_field(self, standard_field: str) -> str:
        """获取原始字段名"""
        return self.reverse_mapping.get(standard_field, standard_field)

    def is_mapped_field(self, field_name: str) -> bool:
        """检查字段是否在映射中"""
        return field_name in self.field_mapping or field_name in self.reverse_mapping