"""
DeepSeek API集成服务
提供与DeepSeek API的集成功能，用于智能属性提取
"""

import json
import time
import requests
from typing import Dict, List, Any, Optional
from django.conf import settings
from .base_ai_service import BaseAIService
from products.utils.ai_feature_flags import AIFeatureFlags
import logging

logger = logging.getLogger(__name__)


class DeepSeekService(BaseAIService):
    """DeepSeek API集成服务"""

    def __init__(self):
        super().__init__()
        self.config = getattr(settings, 'DEEPSEEK_CONFIG', {})
        self.api_key = self.config.get('api_key', '')
        self.base_url = self.config.get('base_url', 'https://api.deepseek.com/v1')
        self.model = self.config.get('model', 'deepseek-chat')

        if not self.api_key:
            logger.warning("DeepSeek API密钥未配置")

    def _check_enabled(self) -> bool:
        """检查服务是否启用"""
        return AIFeatureFlags.is_enabled('ai_deepseek_integration')

    def _process_impl(self, data: Any) -> Dict[str, Any]:
        """实际的API调用逻辑"""
        if not self.api_key:
            return {
                'success': False,
                'error': 'DeepSeek API密钥未配置'
            }

        try:
            # 构建请求
            messages = self._build_messages(data)
            response = self._call_api(messages)

            if response:
                return {
                    'success': True,
                    'response': response,
                    'usage': response.get('usage', {}),
                    'model': self.model
                }
            else:
                return {
                    'success': False,
                    'error': 'API调用失败'
                }

        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _build_messages(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """构建API请求消息"""
        # 这里可以根据不同的任务类型构建不同的消息
        if isinstance(data, dict) and 'task_type' in data:
            if data['task_type'] == 'attribute_extraction':
                return self._build_attribute_extraction_messages(data)
            elif data['task_type'] == 'business_validation':
                return self._build_business_validation_messages(data)
            elif data['task_type'] == 'data_completion':
                return self._build_data_completion_messages(data)

        # 默认消息格式
        return [
            {
                "role": "user",
                "content": str(data)
            }
        ]

    def _build_attribute_extraction_messages(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """构建属性提取任务的消息"""
        system_prompt = """你是一个专业的产品属性提取专家。请根据提供的产品信息，提取出标准化的产品属性和属性值。

要求：
1. 返回JSON格式的结果
2. 属性名称使用中文，简洁明确
3. 属性值要准确、标准化
4. 只提取确定的属性，不要猜测
5. 优先提取：尺寸、材质、颜色、功能、规格等核心属性

返回格式示例：
{
  "attributes": [
    {"name": "宽度", "value": "30", "unit": "cm", "confidence": 0.95},
    {"name": "材质", "value": "实木", "confidence": 0.90}
  ]
}"""

        user_content = f"""请分析以下产品信息并提取属性：

品牌：{data.get('brand', '未知')}
产品描述：{data.get('description', '')}
产品编码：{data.get('code', '')}
系列：{data.get('series', '')}

请提取这个产品的标准化属性和属性值。"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

    def _build_business_validation_messages(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """构建业务验证任务的消息"""
        system_prompt = """你是一个专业的产品数据验证专家。请检查产品数据的业务逻辑合理性。

要求：
1. 返回JSON格式的结果
2. 检查尺寸、价格、功能的合理性
3. 识别明显的逻辑错误
4. 只标记确定的问题，不要过度解读

返回格式：
{
  "issues": [
    {"type": "logic_error", "message": "具体问题描述", "severity": "medium"}
  ]
}

如果没有问题，返回：{"issues": []}"""

        user_content = data.get('prompt', str(data))

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

    def _build_data_completion_messages(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """构建数据补全任务的消息"""
        system_prompt = """你是一个专业的产品数据补全专家。请根据现有产品信息，智能推断缺失的属性。

要求：
1. 返回JSON格式的结果
2. 只补全有把握的属性，不确定的不要包含
3. 每个属性都要有置信度评分
4. 基于产品描述和常识进行推断

返回格式：
{
  "completed_attributes": [
    {"name": "材质", "value": "推断的材质", "confidence": 0.8},
    {"name": "颜色", "value": "推断的颜色", "confidence": 0.7}
  ]
}"""

        user_content = data.get('prompt', str(data))

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

    def _call_api(self, messages: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        """调用DeepSeek API"""
        url = f"{self.base_url}/chat/completions"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': self.model,
            'messages': messages,
            'max_tokens': self.config.get('max_tokens', 1000),
            'temperature': self.config.get('temperature', 0.1),
            'stream': False
        }

        max_retries = self.config.get('max_retries', 3)
        retry_delay = self.config.get('retry_delay', 1)
        timeout = self.config.get('timeout', 30)

        for attempt in range(max_retries):
            try:
                logger.debug(f"DeepSeek API调用尝试 {attempt + 1}/{max_retries}")

                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=timeout
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"DeepSeek API调用成功，使用tokens: {result.get('usage', {})}")
                    return result

                elif response.status_code == 429:  # 速率限制
                    logger.warning(f"DeepSeek API速率限制，等待重试...")
                    time.sleep(retry_delay * (attempt + 1))
                    continue

                else:
                    logger.error(f"DeepSeek API调用失败: {response.status_code} - {response.text}")
                    if attempt == max_retries - 1:
                        return None
                    time.sleep(retry_delay)

            except requests.exceptions.Timeout:
                logger.warning(f"DeepSeek API调用超时，尝试 {attempt + 1}/{max_retries}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(retry_delay)

            except Exception as e:
                logger.error(f"DeepSeek API调用异常: {str(e)}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(retry_delay)

        return None

    def extract_attributes(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取产品属性的便捷方法"""
        request_data = {
            'task_type': 'attribute_extraction',
            'brand': product_data.get('brand', ''),
            'description': product_data.get('description', ''),
            'code': product_data.get('code', ''),
            'series': product_data.get('series', '')
        }

        result = self.process(request_data)

        if result and result.get('success'):
            # 解析API响应
            api_response = result.get('response', {})
            choices = api_response.get('choices', [])

            if choices:
                content = choices[0].get('message', {}).get('content', '')
                try:
                    # 清理响应内容，移除可能的markdown格式
                    clean_content = content.strip()
                    if clean_content.startswith('```json'):
                        clean_content = clean_content[7:]  # 移除 ```json
                    if clean_content.endswith('```'):
                        clean_content = clean_content[:-3]  # 移除 ```
                    clean_content = clean_content.strip()

                    # 尝试解析JSON响应
                    attributes_data = json.loads(clean_content)
                    return {
                        'success': True,
                        'attributes': attributes_data.get('attributes', []),
                        'usage': result.get('usage', {}),
                        'raw_response': content
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"DeepSeek响应JSON解析失败: {e}")
                    logger.error(f"原始响应: {content}")
                    return {
                        'success': False,
                        'error': 'API响应格式错误',
                        'raw_response': content
                    }

        return result or {'success': False, 'error': '未知错误'}