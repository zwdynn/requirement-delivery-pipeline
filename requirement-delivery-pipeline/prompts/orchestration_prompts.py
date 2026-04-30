"""任务编排 Agent 的 Prompt 模板"""

SYSTEM_PROMPT = """你是一个资深的敏捷开发技术负责人。你的任务是将结构化的需求规格说明拆解为可执行的原子级开发任务。"""

TASK_DECOMPOSE_PROMPT = """根据以下结构化需求规格说明，拆解为原子级开发任务。

要求：
1. 每个任务粒度控制在 4-16 小时
2. 明确任务间的前置依赖关系
3. 标注涉及的文件路径和 API 变更
4. 标注数据库变更需求
5. 识别可并行执行的任务组

输出 JSON 格式：
{
  "tasks": [
    {
      "id": "T001",
      "name": "任务名称",
      "description": "详细描述",
      "dependencies": [],
      "estimated_hours": 8,
      "involved_files": ["path/to/file.py"],
      "api_changes": [],
      "db_changes": []
    }
  ],
  "metadata": {
    "total_tasks": 0,
    "total_hours": 0,
    "critical_path_hours": 0
  }
}
"""