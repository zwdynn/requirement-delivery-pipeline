"""第一层：需求澄清与结构化 Agent"""
import json
from typing import Any, Dict, List
from agents.base_agent import BaseAgent
from prompts.clarification_prompts import (
    SYSTEM_PROMPT,
    CLARIFICATION_STEP_PROMPTS,
    STRUCTURING_PROMPT,
)
import logging

logger = logging.getLogger(__name__)


class ClarificationAgent(BaseAgent):
    def __init__(self):
        super().__init__("ClarificationAgent")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行需求澄清与结构化"""
        prd_text = input_data.get("prd_text", "")
        product_manager_replies = input_data.get("replies", {})

        logger.info(f"[{self.name}] 开始处理 PRD，长度: {len(prd_text)}")

        # 步骤 1: 将 PRD 拆解为功能点
        feature_points = self._extract_feature_points(prd_text)
        logger.info(f"[{self.name}] 提取到 {len(feature_points)} 个功能点")

        # 步骤 2: 对每个功能点执行五步推理
        all_clarifications = []
        for fp in feature_points:
            if product_manager_replies.get(fp["id"]):
                continue  # 已有回复，跳过
            questions = self._run_five_step_reasoning(fp)
            all_clarifications.append({
                "feature_id": fp["id"],
                "feature_name": fp["name"],
                "questions": questions,
            })

        # 步骤 3: 如果有澄清问题，返回给产品经理
        if all_clarifications and not product_manager_replies:
            return {
                "status": "needs_clarification",
                "feature_points": feature_points,
                "clarifications": all_clarifications,
            }

        # 步骤 4: 融合回复，生成结构化需求
        structured_spec = self._generate_structured_spec(
            prd_text, feature_points, product_manager_replies
        )

        logger.info(f"[{self.name}] 结构化需求生成完成")
        return {
            "status": "structured",
            "structured_spec": structured_spec,
            "feature_points": feature_points,
        }

    def _extract_feature_points(self, prd_text: str) -> List[Dict]:
        """从 PRD 中提取功能点"""
        system_prompt = """你是一个需求分析专家。从给定的 PRD 中提取所有功能点。
返回 JSON 数组，每个元素包含 id, name, description 字段。"""
        response = self.call_llm(system_prompt, prd_text)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # 尝试从文本中提取 JSON
            import re
            match = re.search(r"\[.*\]", response, re.DOTALL)
            if match:
                return json.loads(match.group())
        return [{"id": "FP001", "name": "未知功能", "description": prd_text[:200]}]

    def _run_five_step_reasoning(self, feature: Dict) -> List[str]:
        """执行五步长链推理"""
        questions = []
        for step_key, step_prompt in CLARIFICATION_STEP_PROMPTS.items():
            user_msg = f"功能点：{feature['name']}\n描述：{feature['description']}\n\n{step_prompt}"
            result = self.call_llm(SYSTEM_PROMPT, user_msg)
            q_list = [q.strip() for q in result.split("\n") if q.strip() and "?" in q]
            questions.extend(q_list)
        return questions[:10]  # 限制问题数量

    def _generate_structured_spec(
        self,
        prd_text: str,
        feature_points: List[Dict],
        replies: Dict,
    ) -> Dict:
        """融合回复，生成结构化需求规格说明"""
        system_prompt = STRUCTURING_PROMPT
        user_msg = f"""
## 原始 PRD
{prd_text}

## 功能点
{json.dumps(feature_points, ensure_ascii=False, indent=2)}

## 产品经理回复
{json.dumps(replies, ensure_ascii=False, indent=2)}

请生成结构化需求规格说明，包含状态流转图（Mermaid）、异常分支决策表、验收标准。
"""
        response = self.call_llm(system_prompt, user_msg)
        return {"raw_spec": response, "feature_count": len(feature_points)}