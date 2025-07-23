from typing import Dict, List, Any
import os
from django.conf import settings
from django.http import HttpResponse
from io import StringIO
from products.config.royana_import_template import ROYANA_IMPORT_TEMPLATE
from products.config.ai_import_template import AI_IMPORT_TEMPLATE


class TextTemplateGenerator:
    """
    文本模板生成器

    生成CSV格式的数据导入模板
    """
    
    def __init__(self):
        self.templates = {
            'royana_import': ROYANA_IMPORT_TEMPLATE,
            'ai_data': AI_IMPORT_TEMPLATE,
        }
    
    def generate_template(self, template_type: str, include_sample: bool = True) -> str:
        """
        生成CSV模板

        Args:
            template_type: 模板类型
            include_sample: 是否包含示例数据

        Returns:
            str: CSV格式的模板内容
        """
        if template_type not in self.templates:
            raise ValueError(f"不支持的模板类型: {template_type}")

        template_config = self.templates[template_type]

        # 生成CSV内容
        csv_content = self._generate_csv_content(template_config, include_sample)

        return csv_content
    

    def _generate_csv_content(self, template_config: Dict[str, Any], include_sample: bool) -> str:
        """生成CSV内容"""
        import csv
        from io import StringIO

        output = StringIO()

        # 获取字段名 - 支持新旧两种格式
        field_names = []
        if isinstance(template_config['fields'][0], dict):
            # 新格式：AI数据格式
            field_names = [field['name'] for field in template_config['fields']]
        else:
            # 旧格式：传统格式
            for field_info in template_config['fields']:
                if len(field_info) >= 4:
                    field_names.append(field_info[0])

        writer = csv.writer(output, quoting=csv.QUOTE_ALL)

        # 写入字段说明注释
        template_name = template_config.get('name', 'Royana产品导入模板')
        output.write(f"# {template_name}\n")
        output.write(f"# 描述: {template_config.get('description', '')}\n")
        output.write("# 字段说明:\n")

        # 写入字段说明 - 支持新旧两种格式
        if isinstance(template_config['fields'][0], dict):
            # 新格式：AI数据格式
            for field in template_config['fields']:
                required_text = "必填" if field.get('required', False) else "可选"
                data_type = field.get('data_type', 'text')
                description = field.get('description', '')
                example = field.get('example', '')

                output.write(f"# {field['name']} ({data_type}, {required_text}): {description}\n")
                if example:
                    output.write(f"#   示例: {example}\n")

                # 写入枚举值
                if 'enum_values' in field:
                    output.write(f"#   可选值: {', '.join(field['enum_values'])}\n")
        else:
            # 旧格式：传统格式
            for field_info in template_config['fields']:
                if len(field_info) == 4:
                    field_name, field_type, required, description = field_info
                elif len(field_info) == 5:
                    field_name, field_code, field_type, required, description = field_info
                else:
                    continue

                required_text = "必填" if required else "可选"
                output.write(f"# {field_name} ({field_type}, {required_text}): {description}\n")

        # 写入枚举值说明（旧格式）
        if 'enums' in template_config:
            output.write("# 枚举值说明:\n")
            for enum_name, enum_values in template_config['enums'].items():
                output.write(f"# {enum_name}: {', '.join(enum_values)}\n")

        output.write("#\n")
        output.write("# 使用说明:\n")
        output.write("# 1. 请删除所有以#开头的注释行\n")
        output.write("# 2. 在数据行中填入产品信息\n")
        output.write("# 3. 价格数据可以包含逗号分隔符，如: 4,280\n")
        output.write("# 4. 空值请用 - 表示\n")
        output.write("#\n")

        # 写入表头
        writer.writerow(field_names)

        # 写入示例数据（如果需要）
        if include_sample and 'sample_data' in template_config:
            for sample_row in template_config['sample_data']:
                row_data = []
                for field_name in field_names:
                    row_data.append(sample_row.get(field_name, ''))
                writer.writerow(row_data)

        return output.getvalue()

    def get_template_response(self, template_type: str, include_sample: bool = True) -> HttpResponse:
        """
        生成模板文件的HTTP响应

        Args:
            template_type: 模板类型
            include_sample: 是否包含示例数据

        Returns:
            HttpResponse: 可下载的CSV文件响应
        """
        csv_content = self.generate_template(template_type, include_sample)

        # 生成文件名
        filename = f'{template_type}_导入模板.csv'

        response = HttpResponse(
            csv_content,
            content_type='text/csv; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response