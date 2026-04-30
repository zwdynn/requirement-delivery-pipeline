"""上下文管理器：维护需求版本的增量演进"""
from typing import Any, Dict, List
import json
from datetime import datetime


class ContextManager:
    def __init__(self):
        self.session_id = None
        self.prd_versions: List[Dict] = []
        self.clarification_history: List[Dict] = []
        self.current_state: str = "init"

    def init_session(self, prd_text: str) -> str:
        """初始化新会话"""
        import uuid
        self.session_id = str(uuid.uuid4())[:8]
        self.prd_versions.append({
            "version": 1,
            "timestamp": datetime.now().isoformat(),
            "content": prd_text,
            "base_version": None,
        })
        self.current_state = "prd_loaded"
        return self.session_id

    def add_clarification(self, feature_id: str, question: str, answer: str):
        """增量添加澄清记录（不覆盖历史）"""
        self.clarification_history.append({
            "feature_id": feature_id,
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat(),
        })

    def create_new_version(self, updated_prd: str) -> int:
        """创建需求的新版本"""
        version = len(self.prd_versions) + 1
        self.prd_versions.append({
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "content": updated_prd,
            "base_version": version - 1,
        })
        return version

    def get_context(self) -> Dict[str, Any]:
        """获取完整上下文"""
        return {
            "session_id": self.session_id,
            "current_state": self.current_state,
            "latest_version": self.prd_versions[-1] if self.prd_versions else None,
            "clarification_count": len(self.clarification_history),
            "version_history": [v["version"] for v in self.prd_versions],
        }

    def transition_state(self, new_state: str):
        """状态转换"""
        valid_states = [
            "init", "prd_loaded", "clarifying", "structured",
            "orchestrating", "orchestrated", "auditing", "approved", "rejected"
        ]
        if new_state in valid_states:
            self.current_state = new_state
        else:
            raise ValueError(f"无效状态: {new_state}，有效状态: {valid_states}")