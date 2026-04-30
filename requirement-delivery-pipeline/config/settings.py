

### 5. config/settings.py


"""全局配置管理"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
    TASK_BOARD_API_URL: str = os.getenv("TASK_BOARD_API_URL", "")
    TASK_BOARD_API_TOKEN: str = os.getenv("TASK_BOARD_API_TOKEN", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MAX_CLARIFICATION_ROUNDS: int = 5
    TEMPERATURE: float = 0.3
    MAX_TOKENS: int = 4096


settings = Settings()