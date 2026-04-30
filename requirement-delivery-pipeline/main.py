#!/usr/bin/env python3
"""需求交付流水线主入口"""
import argparse
import logging
import json
from pathlib import Path

from agents import ClarificationAgent, OrchestrationAgent, QualityGateAgent
from core.context_manager import ContextManager
from tools.taskboard_client import TaskBoardClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("Pipeline")


def run_pipeline(prd_path: str, output_path: str = None):
    """运行完整流水线"""
    prd_text = Path(prd_path).read_text(encoding="utf-8")
    logger.info(f"读取 PRD: {prd_path}，长度: {len(prd_text)}")

    # 初始化上下文
    ctx_manager = ContextManager()
    session_id = ctx_manager.init_session(prd_text)
    logger.info(f"会话 ID: {session_id}")

    # 第一层：需求澄清
    ctx_manager.transition_state("clarifying")
    clarification_agent = ClarificationAgent()
    clarification_result = clarification_agent.execute({
        "prd_text": prd_text,
        "replies": {},
    })

    if clarification_result["status"] == "needs_clarification":
        logger.info("需求需要澄清，请产品经理回答以下问题：")
        for item in clarification_result["clarifications"]:
            for q in item["questions"]:
                print(f"\n[需澄清] {item['feature_name']}: {q}")
        logger.info("请将回复填入后重新运行")
        return clarification_result

    structured_spec = clarification_result["structured_spec"]
    ctx_manager.transition_state("structured")
    logger.info("结构化需求生成完成")

    # 第二层：任务编排
    ctx_manager.transition_state("orchestrating")
    orchestration_agent = OrchestrationAgent()
    orchestration_result = orchestration_agent.execute({
        "structured_spec": structured_spec,
        "codebase_context": "示例代码库上下文",
    })
    ctx_manager.transition_state("orchestrated")
    logger.info(
        f"任务拆解完成，共 {orchestration_result['dag'].number_of_nodes()} 个节点"
    )

    # 第三层：质量审核
    ctx_manager.transition_state("auditing")
    quality_agent = QualityGateAgent()
    quality_result = quality_agent.execute({
        "structured_spec": structured_spec,
        "task_graph": orchestration_result["task_graph"],
        "dag": orchestration_result["dag"],
    })

    if quality_result["status"] == "approved":
        ctx_manager.transition_state("approved")
        logger.info("质量审核通过！")

        # 推送到任务看板
        taskboard = TaskBoardClient()
        epic = taskboard.create_epic(
            name="需求交付流水线自动创建",
            description=prd_text[:200],
        )
        if epic:
            tasks = orchestration_result["task_graph"].get("tasks", [])
            taskboard.create_tasks(epic.get("id", ""), tasks)
            logger.info(f"已推送 {len(tasks)} 个任务到看板")
    else:
        ctx_manager.transition_state("rejected")
        logger.warning(f"质量审核未通过，共 {len(quality_result.get('issues', []))} 个问题")
        for issue in quality_result.get("issues", []):
            logger.warning(f"  [{issue['severity']}] {issue['detail']}")

    # 输出结果
    result = {
        "session_id": session_id,
        "context": ctx_manager.get_context(),
        "clarification": {"status": clarification_result["status"]},
        "orchestration": {
            "task_count": orchestration_result["dag"].number_of_nodes(),
            "critical_path": orchestration_result["critical_path"],
            "parallel_groups": len(orchestration_result["parallel_groups"]),
        },
        "quality_gate": {
            "status": quality_result["status"],
            "issues": quality_result.get("issues", []),
        },
    }

    if output_path:
        Path(output_path).write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info(f"结果已保存到: {output_path}")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="需求交付流水线")
    parser.add_argument("--prd", required=True, help="PRD 文件路径")
    parser.add_argument("--output", default="output.json", help="输出文件路径")
    args = parser.parse_args()
    run_pipeline(args.prd, args.output)