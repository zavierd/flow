"""
DeepSeek AI服务
提供与DeepSeek API的集成功能
"""

import json
import logging
from typing import Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class DeepSeekService:
    """DeepSeek AI服务类"""
    
    def __init__(self):
        # 从Django设置中获取DeepSeek配置
        deepseek_config = getattr(settings, 'DEEPSEEK_CONFIG', {})

        self.api_key = deepseek_config.get('api_key')
        self.base_url = deepseek_config.get('base_url', 'https://api.deepseek.com/v1')
        self.model = deepseek_config.get('model', 'deepseek-chat')
        self.max_tokens = deepseek_config.get('max_tokens', 1000)
        self.temperature = deepseek_config.get('temperature', 0.1)
        self.timeout = deepseek_config.get('timeout', 30)
        self.max_retries = deepseek_config.get('max_retries', 3)
        self.retry_delay = deepseek_config.get('retry_delay', 1)
        
    def is_available(self) -> bool:
        """检查DeepSeek服务是否可用"""
        if not self.api_key:
            logger.debug("DeepSeek API密钥未配置")
            return False

        # 可以添加更多检查，如网络连接测试
        return True

    def test_connection(self) -> Dict[str, Any]:
        """测试DeepSeek API连接"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'API密钥未配置',
                'details': 'DEEPSEEK_CONFIG.api_key 未设置'
            }

        try:
            # 发送一个简单的测试请求
            test_prompt = "请回复'连接测试成功'"
            response = self._call_deepseek_api(test_prompt, 50, 0.1)

            return {
                'success': True,
                'message': '连接测试成功',
                'response_length': len(response),
                'api_key_prefix': f"{self.api_key[:8]}..." if self.api_key else None
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'details': 'API连接测试失败'
            }
    
    def generate_response(self, prompt: str, max_tokens: int = None, temperature: float = None) -> str:
        """生成AI响应"""
        if not self.is_available():
            logger.warning("DeepSeek服务不可用，使用默认处理")
            return self._fallback_response(prompt)

        # 使用实例配置或传入参数
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature or self.temperature

        try:
            # 尝试真实的DeepSeek API调用
            response = self._call_deepseek_api(prompt, max_tokens, temperature)
            logger.info("✅ DeepSeek API调用成功")
            return response

        except Exception as e:
            logger.warning(f"DeepSeek API调用失败，降级到模拟模式: {str(e)}")
            # 降级到模拟响应
            return self._simulate_deepseek_response(prompt)

    def _call_deepseek_api(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """调用真实的DeepSeek API"""
        import requests
        import time

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': self.model,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': max_tokens,
            'temperature': temperature,
            'stream': False
        }

        # 重试机制
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🤖 调用DeepSeek API (尝试 {attempt + 1}/{self.max_retries})")

                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    result = response.json()

                    if 'choices' in result and len(result['choices']) > 0:
                        content = result['choices'][0]['message']['content']
                        logger.info(f"✅ DeepSeek API响应成功 (长度: {len(content)})")
                        return content.strip()
                    else:
                        raise ValueError("API响应格式异常：缺少choices字段")

                elif response.status_code == 429:
                    # 速率限制，等待后重试
                    wait_time = self.retry_delay * (2 ** attempt)  # 指数退避
                    logger.warning(f"⏳ API速率限制，等待 {wait_time}s 后重试...")
                    time.sleep(wait_time)
                    continue

                else:
                    error_msg = f"API调用失败: HTTP {response.status_code}"
                    try:
                        error_detail = response.json()
                        error_msg += f" - {error_detail}"
                    except:
                        error_msg += f" - {response.text}"

                    raise requests.RequestException(error_msg)

            except requests.Timeout:
                logger.warning(f"⏰ API调用超时 (尝试 {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                raise

            except requests.RequestException as e:
                logger.warning(f"🔌 API调用网络错误: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                raise

        raise Exception(f"DeepSeek API调用失败，已重试 {self.max_retries} 次")

    def _simulate_deepseek_response(self, prompt: str) -> str:
        """模拟DeepSeek响应（用于开发和测试）"""
        # 分析提示词中的属性信息
        if "属性名:" in prompt and "属性值:" in prompt:
            # 提取属性名和值
            lines = prompt.split('\n')
            attr_name = ""
            attr_value = ""
            
            for line in lines:
                if line.strip().startswith("属性名:"):
                    attr_name = line.split(":", 1)[1].strip()
                elif line.strip().startswith("属性值:"):
                    attr_value = line.split(":", 1)[1].strip()
            
            # 智能分析属性
            return self._analyze_attribute_intelligently(attr_name, attr_value)
        
        return '{"error": "无法解析提示词"}'
    
    def _analyze_attribute_intelligently(self, attr_name: str, attr_value: str) -> str:
        """智能分析属性（模拟AI逻辑）"""
        # 属性类型智能判断
        attr_type = self._determine_attribute_type(attr_name, attr_value)
        
        # 属性名标准化
        display_name = self._standardize_attribute_name(attr_name)
        
        # 属性值标准化
        display_value = self._standardize_attribute_value(attr_name, attr_value)
        
        # 可筛选性判断
        filterable = self._is_filterable_attribute(attr_name, attr_type)
        
        # 重要程度评估
        importance = self._assess_importance(attr_name, attr_type)
        
        result = {
            "display_name": display_name,
            "display_value": display_value,
            "attribute_type": attr_type,
            "filterable": filterable,
            "importance": importance,
            "confidence": 0.85  # 模拟置信度
        }
        
        return json.dumps(result, ensure_ascii=False)
    
    def _determine_attribute_type(self, attr_name: str, attr_value: str) -> str:
        """智能判断属性类型"""
        attr_name_lower = attr_name.lower()
        attr_value_str = str(attr_value).lower()
        
        # 数字类型
        if any(keyword in attr_name_lower for keyword in ['尺寸', '长度', '宽度', '高度', '深度', '厚度', '重量']):
            return 'number'
        
        # 颜色类型
        if any(keyword in attr_name_lower for keyword in ['颜色', '色彩', 'color']):
            return 'color'
        
        # 布尔类型
        if attr_value_str in ['是', '否', 'true', 'false', '有', '无']:
            return 'boolean'
        
        # 选择类型（短文本且常见值）
        if (len(attr_value_str) < 20 and 
            any(keyword in attr_name_lower for keyword in ['材质', '类型', '风格', '等级', '规格', '型号'])):
            return 'select'
        
        # 默认文本类型
        return 'text'
    
    def _standardize_attribute_name(self, attr_name: str) -> str:
        """标准化属性名"""
        # 常见属性名映射
        name_mapping = {
            '材质': '材质类型',
            '颜色': '产品颜色',
            '风格': '设计风格',
            '等级': '产品等级',
            '型号': '产品型号',
            '规格': '产品规格',
            '厚度': '板材厚度',
            '重量': '产品重量',
            '品牌': '品牌名称',
            '产地': '生产地区',
        }
        
        return name_mapping.get(attr_name, attr_name)
    
    def _standardize_attribute_value(self, attr_name: str, attr_value: str) -> str:
        """标准化属性值"""
        attr_value_str = str(attr_value).strip()
        
        # 材质标准化
        if '材质' in attr_name:
            material_mapping = {
                '实木': '实木材质',
                '颗粒板': '实木颗粒板',
                '密度板': '中密度纤维板',
                'MDF': '中密度纤维板',
                'OSB': '定向刨花板',
            }
            for key, value in material_mapping.items():
                if key in attr_value_str:
                    return value
        
        # 颜色标准化
        if '颜色' in attr_name:
            color_mapping = {
                '白': '纯白色',
                '黑': '经典黑',
                '灰': '高级灰',
                '木色': '原木色',
                '胡桃': '胡桃木色',
            }
            for key, value in color_mapping.items():
                if key in attr_value_str:
                    return value
        
        return attr_value_str
    
    def _is_filterable_attribute(self, attr_name: str, attr_type: str) -> bool:
        """判断属性是否应该可筛选"""
        # 重要的筛选属性
        important_filters = ['材质', '颜色', '风格', '等级', '品牌', '系列', '类型']
        
        if any(keyword in attr_name for keyword in important_filters):
            return True
        
        # 选择类型通常可筛选
        if attr_type in ['select', 'boolean', 'color']:
            return True
        
        return False
    
    def _assess_importance(self, attr_name: str, attr_type: str) -> int:
        """评估属性重要程度（1-5）"""
        # 核心属性
        if any(keyword in attr_name for keyword in ['材质', '颜色', '风格', '等级']):
            return 5
        
        # 重要属性
        if any(keyword in attr_name for keyword in ['品牌', '系列', '型号', '规格']):
            return 4
        
        # 一般属性
        if any(keyword in attr_name for keyword in ['厚度', '重量', '产地']):
            return 3
        
        # 次要属性
        return 2
    
    def _fallback_response(self, prompt: str) -> str:
        """降级响应（当AI服务不可用时）"""
        return json.dumps({
            "display_name": "未知属性",
            "display_value": "未知值",
            "attribute_type": "text",
            "filterable": False,
            "importance": 3,
            "confidence": 0.1
        }, ensure_ascii=False)
