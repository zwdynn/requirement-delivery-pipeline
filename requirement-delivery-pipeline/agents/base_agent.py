"""Agent 基类"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from openai import OpenAI
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )

    def call_llm(
        self,
        system_prompt: str,
        user_message: str,
        temperature: Optional[float] = None,
    ) -> str:
        """调用大语言模型"""
        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                temperature=temperature or settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"[{self.name}] LLM 调用失败: {e}")
            raise

    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行 Agent 的核心逻辑"""
        pass