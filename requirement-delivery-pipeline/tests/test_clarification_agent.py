"""澄清 Agent 测试"""
import pytest
from unittest.mock import Mock, patch
from agents.clarification_agent import ClarificationAgent


@pytest.fixture
def agent():
    return ClarificationAgent()


def test_extract_feature_points(agent):
    prd = "用户登录：输入用户名密码，点击登录按钮。用户注册：填写信息提交。"
    features = agent._extract_feature_points(prd)
    assert len(features) > 0


def test_execute_returns_clarification_without_replies(agent):
    with patch.object(agent, "_extract_feature_points") as mock_extract:
        mock_extract.return_value = [
            {"id": "FP001", "name": "用户登录", "description": "登录功能"}
        ]
        with patch.object(agent, "_run_five_step_reasoning") as mock_reason:
            mock_reason.return_value = ["边界条件是什么？"]
            result = agent.execute({"prd_text": "测试需求"})
            assert result["status"] == "needs_clarification"
            assert len(result["clarifications"]) == 1