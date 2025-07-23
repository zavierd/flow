"""
AI数据质量检测服务
使用统计学方法和规则引擎检测数据质量问题
"""

import statistics
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal, InvalidOperation
from .base_ai_service import BaseAIService
from products.utils.ai_feature_flags import AIFeatureFlags
import logging

logger = logging.getLogger(__name__)


class AIQualityService(BaseAIService):
    """AI数据质量检测服务"""

    def _check_enabled(self) -> bool:
        """检查服务是否启用"""
        return AIFeatureFlags.is_enabled(AIFeatureFlags.QUALITY_DETECTION)

    def process_for_test(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """专门用于测试的处理方法，忽略启用状态"""
        try:
            return self._process_impl(data)
        except Exception as e:
            logger.error(f"{self.__class__.__name__} 处理失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'service': self.__class__.__name__
            }

    def _process_impl(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """实际的质量检测逻辑"""
        issues = []
        suggestions = []

        # 检测价格异常
        price_issues = self._detect_price_anomalies(data)
        issues.extend(price_issues)

        # 检测尺寸异常
        dimension_issues = self._detect_dimension_anomalies(data)
        issues.extend(dimension_issues)

        # 检测编码格式
        code_issues = self._validate_product_code(data)
        issues.extend(code_issues)

        # 检测数据一致性
        consistency_issues = self._check_data_consistency(data)
        issues.extend(consistency_issues)

        # AI智能业务逻辑验证（如果启用DeepSeek）
        ai_validation_issues = self._ai_business_logic_validation(data)
        issues.extend(ai_validation_issues)

        # 生成修复建议
        if issues:
            suggestions = self._generate_suggestions(issues, data)

        return {
            'success': True,
            'quality_score': self._calculate_quality_score(issues),
            'issues': issues,
            'suggestions': suggestions,
            'total_issues': len(issues)
        }

    def _detect_price_anomalies(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检测价格异常"""
        issues = []
        price_fields = ['等级Ⅰ', '等级Ⅱ', '等级Ⅲ', '等级Ⅳ', '等级Ⅴ']

        # 提取价格数据
        prices = []
        for field in price_fields:
            price_str = str(data.get(field, '')).replace(',', '').replace('-', '0')
            try:
                if price_str and price_str != '0':
                    prices.append(float(price_str))
            except (ValueError, TypeError):
                issues.append({
                    'type': 'price_format_error',
                    'field': field,
                    'value': data.get(field, ''),
                    'severity': 'high',
                    'message': f'价格格式错误: {field}'
                })

        if len(prices) < 2:
            return issues

        # 检测价格递增逻辑
        if not all(prices[i] <= prices[i+1] for i in range(len(prices)-1)):
            issues.append({
                'type': 'price_logic_error',
                'field': 'price_levels',
                'value': prices,
                'severity': 'medium',
                'message': '价格等级应该递增'
            })

        # 检测异常值（使用IQR方法）
        if len(prices) >= 3:
            try:
                # 使用更兼容的方式计算分位数
                sorted_prices = sorted(prices)
                n = len(sorted_prices)
                q1 = sorted_prices[n//4]
                q3 = sorted_prices[3*n//4]
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr

                for i, price in enumerate(prices):
                    if price < lower_bound or price > upper_bound:
                        issues.append({
                            'type': 'price_outlier',
                            'field': price_fields[i],
                            'value': price,
                            'severity': 'medium',
                            'message': f'价格异常值: {price}'
                        })
            except Exception as e:
                logger.warning(f"异常值检测失败: {e}")

        return issues

    def _detect_dimension_anomalies(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检测尺寸异常"""
        issues = []
        dimension_fields = {
            '宽度 (Width_cm)': (10, 300),   # 宽度范围
            '高度 (Height_cm)': (50, 250),  # 高度范围
            '深度 (Depth_cm)': (30, 100)   # 深度范围
        }

        for field, (min_val, max_val) in dimension_fields.items():
            value_str = str(data.get(field, '')).strip()
            if not value_str or value_str == '-':
                continue

            try:
                value = float(value_str)
                if value < min_val or value > max_val:
                    issues.append({
                        'type': 'dimension_out_of_range',
                        'field': field,
                        'value': value,
                        'severity': 'high',
                        'message': f'{field.split("(")[0].strip()}超出合理范围 ({min_val}-{max_val}cm)'
                    })
            except (ValueError, TypeError):
                issues.append({
                    'type': 'dimension_format_error',
                    'field': field,
                    'value': value_str,
                    'severity': 'high',
                    'message': f'{field.split("(")[0].strip()}格式错误'
                })

        return issues

    def _validate_product_code(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """验证产品编码格式"""
        issues = []
        code = data.get('产品编码 (Code)', '').strip()

        if not code:
            issues.append({
                'type': 'missing_product_code',
                'field': '产品编码 (Code)',
                'value': code,
                'severity': 'critical',
                'message': '产品编码不能为空'
            })
            return issues

        # 检查编码格式 (例: N-U30-7256-L/R)
        pattern = r'^N-[A-Z]+\d+(-\d+)?(-[A-Z/]+)?$'
        if not re.match(pattern, code):
            issues.append({
                'type': 'invalid_code_format',
                'field': '产品编码 (Code)',
                'value': code,
                'severity': 'high',
                'message': '产品编码格式不符合规范'
            })

        return issues

    def _check_data_consistency(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检查数据一致性"""
        issues = []

        # 检查编码与尺寸的一致性
        code = data.get('产品编码 (Code)', '')
        width = data.get('宽度 (Width_cm)', '')

        if code and width:
            # 从编码中提取宽度信息
            width_match = re.search(r'-(\d+)-', code)
            if width_match:
                code_width = int(width_match.group(1))
                try:
                    actual_width = int(float(str(width)))
                    if code_width != actual_width:
                        issues.append({
                            'type': 'code_dimension_mismatch',
                            'field': 'consistency_check',
                            'value': f'编码宽度:{code_width}, 实际宽度:{actual_width}',
                            'severity': 'medium',
                            'message': '产品编码中的宽度与实际宽度不一致'
                        })
                except (ValueError, TypeError):
                    pass

        return issues

    def _generate_suggestions(self, issues: List[Dict[str, Any]], data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成修复建议"""
        suggestions = []

        for issue in issues:
            suggestion = self._create_suggestion_for_issue(issue, data)
            if suggestion:
                suggestions.append(suggestion)

        return suggestions

    def _create_suggestion_for_issue(self, issue: Dict[str, Any], data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """为特定问题创建修复建议"""
        issue_type = issue['type']

        if issue_type == 'price_format_error':
            return {
                'type': 'fix_price_format',
                'field': issue['field'],
                'current_value': issue['value'],
                'suggested_value': '0',
                'action': 'replace',
                'message': '建议将无效价格设置为0或删除'
            }

        elif issue_type == 'price_logic_error':
            return {
                'type': 'fix_price_logic',
                'field': 'price_levels',
                'current_value': issue['value'],
                'suggested_value': sorted(issue['value']),
                'action': 'reorder',
                'message': '建议按价格等级递增排序'
            }

        elif issue_type == 'dimension_out_of_range':
            # 根据常见尺寸建议修正值
            field = issue['field']
            value = issue['value']
            if '宽度' in field:
                suggested = self._suggest_standard_width(value)
            elif '高度' in field:
                suggested = 72  # 标准高度
            elif '深度' in field:
                suggested = 56  # 标准深度
            else:
                suggested = None

            if suggested:
                return {
                    'type': 'fix_dimension',
                    'field': field,
                    'current_value': value,
                    'suggested_value': suggested,
                    'action': 'replace',
                    'message': f'建议使用标准尺寸: {suggested}cm'
                }

        elif issue_type == 'invalid_code_format':
            return {
                'type': 'fix_code_format',
                'field': issue['field'],
                'current_value': issue['value'],
                'suggested_value': self._suggest_code_format(issue['value']),
                'action': 'replace',
                'message': '建议修正产品编码格式'
            }

        return None

    def _suggest_standard_width(self, current_width: float) -> int:
        """建议标准宽度"""
        standard_widths = [30, 40, 50, 60, 80, 90, 120]
        return min(standard_widths, key=lambda x: abs(x - current_width))

    def _suggest_code_format(self, current_code: str) -> str:
        """建议编码格式"""
        # 简单的格式修正逻辑
        if not current_code.startswith('N-'):
            return f'N-{current_code}'
        return current_code.upper()

    def _calculate_quality_score(self, issues: List[Dict[str, Any]]) -> float:
        """计算数据质量评分 (0-100)"""
        if not issues:
            return 100.0

        # 根据问题严重程度计算扣分
        severity_weights = {
            'critical': 30,
            'high': 20,
            'medium': 10,
            'low': 5
        }

        total_deduction = sum(
            severity_weights.get(issue.get('severity', 'low'), 5)
            for issue in issues
        )

        # 确保分数不低于0
        score = max(0, 100 - total_deduction)
        return round(score, 1)

    def _ai_business_logic_validation(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """AI业务逻辑验证"""
        issues = []

        try:
            # 只有在复杂产品或发现潜在问题时才调用AI
            should_validate = self._should_use_ai_validation(data)
            if not should_validate:
                return issues

            # 导入DeepSeek服务
            from products.utils.ai_feature_flags import is_deepseek_integration_enabled
            if not is_deepseek_integration_enabled():
                return issues

            from .deepseek_service import DeepSeekService
            deepseek_service = DeepSeekService()

            if not deepseek_service.enabled or not deepseek_service.api_key:
                return issues

            # 构建验证请求
            validation_prompt = self._build_validation_prompt(data)
            validation_data = {
                'task_type': 'business_validation',
                'prompt': validation_prompt
            }

            result = deepseek_service.process(validation_data)

            if result and result.get('success'):
                # 解析AI验证结果
                ai_issues = self._parse_ai_validation_result(result, data)
                issues.extend(ai_issues)

        except Exception as e:
            logger.warning(f"AI业务逻辑验证失败: {e}")

        return issues

    def _should_use_ai_validation(self, data: Dict[str, Any]) -> bool:
        """判断是否需要AI验证"""
        # 检查是否有潜在的业务逻辑问题
        description = data.get('产品描述 (Description)', '').lower()

        # 高价值产品需要AI验证
        prices = []
        for level in ['Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ', 'Ⅴ']:
            price_str = str(data.get(f'等级{level}', '')).replace(',', '').replace('-', '0')
            try:
                if price_str and price_str != '0':
                    prices.append(float(price_str))
            except (ValueError, TypeError):
                pass

        max_price = max(prices) if prices else 0

        # 复杂产品特征
        complex_keywords = ['古典', '欧式', '美式', 'led', '恒温', '智能', '定制']
        has_complex_features = any(keyword in description for keyword in complex_keywords)

        return max_price > 10000 or has_complex_features

    def _build_validation_prompt(self, data: Dict[str, Any]) -> str:
        """构建AI验证提示"""
        return f"""请验证以下产品数据的业务逻辑合理性：

产品描述：{data.get('产品描述 (Description)', '')}
产品编码：{data.get('产品编码 (Code)', '')}
尺寸：宽{data.get('宽度 (Width_cm)', '')}cm × 高{data.get('高度 (Height_cm)', '')}cm × 深{data.get('深度 (Depth_cm)', '')}cm
价格等级：{data.get('等级Ⅰ', '')}, {data.get('等级Ⅱ', '')}, {data.get('等级Ⅲ', '')}, {data.get('等级Ⅳ', '')}, {data.get('等级Ⅴ', '')}

请检查：
1. 尺寸与产品类型是否匹配
2. 价格与材质、工艺是否合理
3. 功能描述与产品类型是否一致
4. 是否存在明显的逻辑错误

如发现问题，请返回JSON格式：
{{"issues": [{{"type": "logic_error", "message": "具体问题描述", "severity": "medium"}}]}}

如无问题，返回：{{"issues": []}}"""

    def _parse_ai_validation_result(self, result: Dict[str, Any], data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析AI验证结果"""
        issues = []

        try:
            api_response = result.get('response', {})
            choices = api_response.get('choices', [])

            if choices:
                content = choices[0].get('message', {}).get('content', '')

                # 清理JSON格式
                clean_content = content.strip()
                if clean_content.startswith('```json'):
                    clean_content = clean_content[7:]
                if clean_content.endswith('```'):
                    clean_content = clean_content[:-3]
                clean_content = clean_content.strip()

                validation_result = json.loads(clean_content)
                ai_issues = validation_result.get('issues', [])

                for issue in ai_issues:
                    issues.append({
                        'type': 'ai_business_logic',
                        'field': 'business_logic',
                        'value': '',
                        'severity': issue.get('severity', 'medium'),
                        'message': f"AI业务逻辑检查: {issue.get('message', '')}"
                    })

        except Exception as e:
            logger.error(f"解析AI验证结果失败: {e}")

        return issues