"""编排 Agent 测试"""
import pytest
from agents.orchestration_agent import OrchestrationAgent


def test_execute_with_empty_spec():
    agent = OrchestrationAgent()
    with pytest.raises(Exception):
        agent.execute({})