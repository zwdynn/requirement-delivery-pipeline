"""质量审核 Agent 测试"""
import pytest
import networkx as nx
from agents.quality_gate_agent import QualityGateAgent


def test_check_structure_no_issues():
    agent = QualityGateAgent()
    dag = nx.DiGraph()
    dag.add_node("T001")
    dag.add_node("T002")
    dag.add_edge("T001", "T002")
    issues = agent._check_structure(dag)
    assert len(issues) == 0


def test_check_structure_detects_cycle():
    agent = QualityGateAgent()
    dag = nx.DiGraph()
    dag.add_edge("T001", "T002")
    dag.add_edge("T002", "T001")
    issues = agent._check_structure(dag)
    assert any(i["type"] == "circular_dependency" for i in issues)


def test_check_structure_isolated_node():
    agent = QualityGateAgent()
    dag = nx.DiGraph()
    dag.add_node("T001")
    dag.add_node("T002")
    dag.add_node("T003")
    dag.add_edge("T001", "T002")
    issues = agent._check_structure(dag)
    assert any(i["type"] == "isolated_nodes" for i in issues)