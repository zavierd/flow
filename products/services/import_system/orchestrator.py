"""
导入编排器
负责协调各个模块的执行顺序和数据流转
"""

import logging
from typing import Dict, List, Any, Optional
from django.db import transaction

from . import ProcessingContext, ImportResult, ProcessingStatus, ProcessingStage
from .processors.data_preprocessor import DataPreprocessor
from .builders.product_builder import ProductBuilder
from .builders.relation_builder import RelationBuilder
from .utils.error_handler import ErrorHandler
from .utils.progress_manager import ProgressManager

logger = logging.getLogger(__name__)


class ImportOrchestrator:
    """导入编排器 - 单一职责：协调各模块执行"""

    def __init__(self, task):
        self.task = task
        self.error_handler = ErrorHandler(task)
        self.progress_manager = ProgressManager(task)

        # 初始化各个模块
        self.data_preprocessor = DataPreprocessor()
        self.product_builder = ProductBuilder()
        self.relation_builder = RelationBuilder()

        # 统计信息
        self.total_rows = 0
        self.success_rows = 0
        self.error_rows = 0
        self.all_errors = []

    def process_import(self, csv_content: str) -> ImportResult:
        """处理导入流程"""
        try:
            # 🚀 阶段1: 系统初始化
            self.progress_manager.start_stage(ProcessingStage.INITIALIZING)

            # 1. 解析CSV数据
            rows = self._parse_csv_data(csv_content)
            if not rows:
                return ImportResult(
                    success=False,
                    total_rows=0,
                    success_rows=0,
                    error_rows=0,
                    errors=[{'message': 'CSV数据解析失败或为空'}]
                )

            self.total_rows = len(rows)
            self.progress_manager.start_import(self.total_rows)
            logger.info(f"🚀 开始处理{self.total_rows}行数据，启动智能导入引擎...")

            # 2. 逐行处理数据
            for index, row in enumerate(rows):
                context = ProcessingContext(
                    row_number=index + 2,  # CSV第一行是标题，从第2行开始
                    original_data=row
                )

                # 处理单行数据
                result_context = self._process_single_row(context)

                # 统计结果
                success = result_context.status == ProcessingStatus.SUCCESS
                if success:
                    self.success_rows += 1
                else:
                    self.error_rows += 1
                    self.all_errors.extend(result_context.errors)

                # 更新进度
                self.progress_manager.complete_row(success, context.row_number)

            # 🎉 阶段9: 完成处理
            self.progress_manager.start_stage(ProcessingStage.FINALIZING)

            # 3. 生成最终结果
            final_result = self._generate_final_result()

            # 完成导入
            self.progress_manager.complete_import(final_result.success, final_result.errors)

            return final_result

        except Exception as e:
            logger.error(f"导入流程执行失败: {str(e)}")
            error_result = ImportResult(
                success=False,
                total_rows=self.total_rows,
                success_rows=self.success_rows,
                error_rows=self.error_rows,
                errors=self.all_errors + [{'message': f'导入流程执行失败: {str(e)}'}]
            )

            # 记录失败
            self.progress_manager.complete_import(False, error_result.errors)
            return error_result

    def _process_single_row(self, context: ProcessingContext) -> ProcessingContext:
        """处理单行数据的完整流程"""
        try:
            with transaction.atomic():
                # 🔧 阶段2: 数据预处理
                stage_info = self.progress_manager.start_stage(ProcessingStage.PREPROCESSING, context.row_number)
                context.stage_info = stage_info

                if self.data_preprocessor.can_process(context):
                    context = self.data_preprocessor.process(context)
                    if context.status == ProcessingStatus.FAILED:
                        return context

                # 🏗️ 阶段6: 产品构建
                stage_info = self.progress_manager.start_stage(ProcessingStage.PRODUCT_BUILDING, context.row_number)
                context.stage_info = stage_info

                if self.product_builder.validate_prerequisites(context):
                    context = self.product_builder.build(context)
                    if context.status == ProcessingStatus.FAILED:
                        return context

                # 🔗 阶段7: 关系构建
                stage_info = self.progress_manager.start_stage(ProcessingStage.RELATION_BUILDING, context.row_number)
                context.stage_info = stage_info

                if self.relation_builder.validate_prerequisites(context):
                    context = self.relation_builder.build(context)
                    if context.status == ProcessingStatus.FAILED:
                        return context

                # 最终状态设置
                context.status = ProcessingStatus.SUCCESS

                # 记录处理指标
                context.processing_metrics['created_objects_count'] = len(context.created_objects)
                context.processing_metrics['processed_fields'] = len(context.processed_data)

                return context

        except Exception as e:
            context.status = ProcessingStatus.FAILED
            context.errors.append({
                'stage': 'orchestration',
                'message': f'行处理失败: {str(e)}',
                'details': str(e)
            })
            logger.error(f"❌ 行{context.row_number}处理失败: {str(e)}")
            return context

    def _parse_csv_data(self, csv_content: str) -> Optional[List[Dict[str, Any]]]:
        """解析CSV数据"""
        try:
            import csv
            from io import StringIO

            # 处理可能的Markdown表格格式
            if '|' in csv_content and ('---' in csv_content or ':---' in csv_content):
                csv_content = self._convert_markdown_to_csv(csv_content)

            # 使用csv.DictReader解析
            reader = csv.DictReader(StringIO(csv_content))
            rows = []
            for row in reader:
                # 清理空值
                cleaned_row = {k: v for k, v in row.items() if k and k.strip()}
                if cleaned_row:  # 跳过空行
                    rows.append(cleaned_row)

            return rows

        except Exception as e:
            logger.error(f"CSV解析失败: {str(e)}")
            return None

    def _convert_markdown_to_csv(self, markdown_content: str) -> str:
        """将Markdown表格转换为CSV格式"""
        lines = markdown_content.strip().split('\n')
        csv_lines = []

        for line in lines:
            line = line.strip()
            if line.startswith('|') and line.endswith('|'):
                # 跳过分隔行
                if '---' in line or ':---' in line:
                    continue

                # 处理表格行
                cells = line[1:-1].split('|')
                cleaned_cells = []

                for cell in cells:
                    cleaned_cell = cell.strip()
                    # 处理HTML标签和换行符
                    cleaned_cell = cleaned_cell.replace('<br>', '\n').replace('<br/>', '\n')
                    # CSV转义
                    if ',' in cleaned_cell or '\n' in cleaned_cell or '"' in cleaned_cell:
                        cleaned_cell = '"' + cleaned_cell.replace('"', '""') + '"'
                    cleaned_cells.append(cleaned_cell)

                csv_lines.append(','.join(cleaned_cells))

        return '\n'.join(csv_lines)

    def _update_task_progress(self, processed_rows: int):
        """更新任务进度"""
        if hasattr(self.task, 'update_progress'):
            self.task.update_progress(processed_rows, self.success_rows, self.error_rows)

    def _generate_final_result(self) -> ImportResult:
        """生成最终结果"""
        success = self.error_rows == 0 or self.success_rows > 0

        return ImportResult(
            success=success,
            total_rows=self.total_rows,
            success_rows=self.success_rows,
            error_rows=self.error_rows,
            errors=self.all_errors
        )