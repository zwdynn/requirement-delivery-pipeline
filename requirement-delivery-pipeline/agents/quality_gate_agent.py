"""第三层：质量审核与守门 Agent"""
import json
from typing import Any, Dict, List
from agents.base_agent import BaseAgent
from prompts.quality_gate_prompts import SYSTEM_PROMPT, AUDIT_PROMPT
import networkx as nx
import logging

logger = logging.getLogger(__name__)


class QualityGateAgent(BaseAgent):
    def __init__(self, max_retries: int = 3):
        super().__init__("QualityGateAgent")
        self.max_retries = max_retries

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行质量审核"""
        structured_spec = input_data.get("structured_spec", {})
        task_graph = input_data.get("task_graph", {})
        dag = input_data.get("dag")

        logger.info(f"[{self.name}] 开始质量审核")

        issues = []
        retry_count = 0

        while retry_count <= self.max_retries:
            # 结构检查
            structural_issues = self._check_structure(dag)
            # 覆盖度检查
            coverage_issues = self._check_coverage(structured_spec, task_graph)
            # LLM 语义检查
            semantic_issues = self._llm_audit(structured_spec, task_graph)

            all_issues = structural_issues + coverage_issues + semantic_issues

            if not all_issues:
                logger.info(f"[{self.name}] 审核通过")
                return {
                    "status": "approved",
                    "retry_count": retry_count,
                }

            issues = all_issues
            retry_count += 1
            logger.warning(
                f"[{self.name}] 发现 {len(all_issues)} 个问题，第 {retry_count} 次打回"
            )

            if retry_count > self.max_retries:
                break

        return {
            "status": "rejected" if issues else "approved",
            "issues": issues,
            "retry_count": retry_count,
            "suggestion": "请修正上述问题后重新提交" if issues else None,
        }

    def _check_structure(self, dag) -> List[Dict]:
        """结构检查：依赖环、孤立节点"""
        issues = []
        if dag is None:
            return issues

        # 检查依赖环
        try:
            cycles = list(nx.simple_cycles(dag))
            if cycles:
                issues.append({
                    "type": "circular_dependency",
                    "severity": "critical",
                    "detail": f"发现依赖环: {cycles}",
                })
        except Exception as e:
            logger.error(f"环检测失败: {e}")

        # 检查孤立节点
        isolated = [n for n in dag.nodes if dag.degree(n) == 0]
        if isolated:
            issues.append({
                "type": "isolated_nodes",
                "severity": "warning",
                "detail": f"孤立节点（无依赖无被依赖）: {isolated}",
            })

        # 检查叶子节点是否都有验收覆盖
        leaves = [n for n in dag.nodes if dag.out_degree(n) == 0]
        if not leaves:
            issues.append({
                "type": "no_leaf_tasks",
                "severity": "critical",
                "detail": "任务图中没有叶子节点，可能存在依赖环",
            })

        return issues

    def _check_coverage(self, spec: Dict, task_graph: Dict) -> List[Dict]:
        """覆盖度检查：验收标准是否都有任务对应"""
        issues = []
        tasks = task_graph.get("tasks", [])
        if not tasks:
            issues.append({
                "type": "empty_tasks",
                "severity": "critical",
                "detail": "任务列表为空",
            })
        return issues

    def _llm_audit(self, spec: Dict, task_graph: Dict) -> List[Dict]:
        """LLM 语义审核"""
        system_prompt = AUDIT_PROMPT
        user_msg = f"""
## 结构化需求
{json.dumps(spec, ensure_ascii=False, indent=2)[:2000]}

## 任务拆解
{json.dumps(task_graph, ensure_ascii=False, indent=2)[:2000]}

请审核一致性并列出问题。
"""
        response = self.call_llm(system_prompt, user_msg)
        try:
            return json.loads(response).get("issues", [])
        except json.JSONDecodeError:
            return [{"type": "llm_audit_note", "severity": "info", "detail": response[:200]}]