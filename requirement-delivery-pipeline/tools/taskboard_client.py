"""任务看板 API 客户端：自动创建 Epic 和子任务"""
from typing import Any, Dict, List
import httpx
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class TaskBoardClient:
    def __init__(self):
        self.base_url = settings.TASK_BOARD_API_URL
        self.token = settings.TASK_BOARD_API_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def create_epic(self, name: str, description: str) -> Dict[str, Any]:
        """创建 Epic"""
        if not self.base_url:
            logger.info(f"[Mock] 创建 Epic: {name}")
            return {"id": f"epic_mock_{hash(name) % 10000}", "name": name}

        try:
            with httpx.Client() as client:
                resp = client.post(
                    f"{self.base_url}/epics",
                    json={"name": name, "description": description},
                    headers=self.headers,
                    timeout=30,
                )
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error(f"创建 Epic 失败: {e}")
            return {}

    def create_tasks(self, epic_id: str, tasks: List[Dict]) -> List[Dict]:
        """批量创建子任务"""
        results = []
        for task in tasks:
            if not self.base_url:
                logger.info(f"[Mock] 创建任务: {task.get('name')}")
                results.append({"id": f"task_mock_{hash(task.get('name', '')) % 10000}"})
                continue
            try:
                with httpx.Client() as client:
                    resp = client.post(
                        f"{self.base_url}/tasks",
                        json={**task, "epic_id": epic_id},
                        headers=self.headers,
                        timeout=30,
                    )
                    resp.raise_for_status()
                    results.append(resp.json())
            except Exception as e:
                logger.error(f"创建任务失败: {e}")
        return results