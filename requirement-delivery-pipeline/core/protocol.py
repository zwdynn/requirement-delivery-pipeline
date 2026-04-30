"""人机交互协议：定义 Agent 与产品经理、开发人员的交互格式"""
from typing import Dict, List, Any
from pydantic import BaseModel
from enum import Enum


class QuestionType(str, Enum):
    BOUNDARY = "boundary_condition"
    EXCEPTION = "exception_scenario"
    STATE_TRANSITION = "state_transition"
    PERMISSION = "permission_granularity"
    CONSISTENCY = "data_consistency"


class ClarificationQuestion(BaseModel):
    feature_id: str
    feature_name: str
    question_type: QuestionType
    question: str
    context: str = ""
    example_answer: str = ""


class ProductManagerReply(BaseModel):
    feature_id: str
    question: str
    answer: str


class ClarificationFormat(BaseModel):
    """返回给产品经理的澄清格式"""
    title: str = "需求澄清问题"
    feature_name: str
    questions: List[ClarificationQuestion]
    instruction: str = "请在下方填写您的回答："


class TaskConfirmFormat(BaseModel):
    """返回给开发人员的任务确认格式"""
    epic_name: str
    tasks: List[Dict[str, Any]]
    dependency_graph_url: str = ""
    instruction: str = "请确认以上任务拆解，如有异议请标注："