"""第二层：任务编排与拆解 Agent"""
import json
from typing import Any, Dict
from agents.base_agent import BaseAgent
from prompts.orchestration_prompts import SYSTEM_PROMPT, TASK_DECOMPOSE_PROMPT
from tools.dag_builder import DAGBuilder
from tools.schema_differ import SchemaDiffer
import logging

logger = logging.getLogger(__name__)


class OrchestrationAgent(BaseAgent):
    def __init__(self):
        super().__init__("OrchestrationAgent")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务编排与拆解"""
        structured_spec = input_data.get("structured_spec", {})
        codebase_context = input_data.get("codebase_context", "")

        logger.info(f"[{self.name}] 开始任务拆解")

        # 步骤 1: 调用 LLM 进行任务拆解
        task_graph = self._decompose_tasks(structured_spec, codebase_context)

        # 步骤 2: 构建 DAG 图
        dag_builder = DAGBuilder()
        dag = dag_builder.build(task_graph)
        critical_path = dag_builder.find_critical_path(dag)
        parallel_groups = dag_builder.identify_parallel_groups(dag)

        # 步骤 3: 生成数据库迁移脚本
        schema_diff = SchemaDiffer().analyze(
            structured_spec.get("raw_spec", ""), codebase_context
        )

        # 步骤 4: 生成甘特图数据
        gantt_data = self._generate_gantt(dag, parallel_groups)

        logger.info(
            f"[{self.name}] 拆解完成，共 {len(dag.nodes)} 个任务节点，"
            f"关键路径长度: {len(critical_path)}"
        )

        return {
            "status": "orchestrated",
            "task_graph": task_graph,
            "dag": dag,
            "critical_path": critical_path,
            "parallel_groups": parallel_groups,
            "schema_migration": schema_diff,
            "gantt_data": gantt_data,
        }

    def _decompose_tasks(self, spec: Dict, context: str) -> Dict:
        """调用 LLM 拆解任务"""
        system_prompt = TASK_DECOMPOSE_PROMPT
        user_msg = f"""
## 结构化需求规格说明
{spec.get('raw_spec', '')}

## 代码库上下文
{context}

请按 JSON 格式输出任务拆解结果，每个任务包含：
- id, name, description, dependencies（前置任务ID列表）
- estimated_hours, involved_files, api_changes, db_changes
"""
        response = self.call_llm(system_prompt, user_msg)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            import re
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                return json.loads(match.group())
        return {"tasks": [], "metadata": {"error": "parse_failed"}}

    def _generate_gantt(self, dag, parallel_groups) -> Dict:
        """生成甘特图数据"""
        gantt = {"tasks": []}
        for node_id in dag.nodes:
            node_data = dag.nodes[node_id]
            gantt["tasks"].append({
                "id": node_id,
                "name": node_data.get("name", ""),
                "estimated_hours": node_data.get("estimated_hours", 8),
                "dependencies": list(dag.predecessors(node_id)),
                "parallel_group": node_data.get("parallel_group", 0),
            })
        return gantt