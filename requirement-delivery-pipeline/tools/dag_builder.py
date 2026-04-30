"""DAG 构建器：构建任务依赖图和甘特图"""
import networkx as nx
from typing import Any, Dict, List


class DAGBuilder:
    def build(self, task_graph: Dict[str, Any]) -> nx.DiGraph:
        """从任务字典构建有向无环图"""
        dag = nx.DiGraph()
        tasks = task_graph.get("tasks", [])

        for task in tasks:
            dag.add_node(
                task["id"],
                name=task.get("name", ""),
                estimated_hours=task.get("estimated_hours", 8),
                involved_files=task.get("involved_files", []),
                api_changes=task.get("api_changes", []),
                db_changes=task.get("db_changes", []),
            )

        for task in tasks:
            for dep_id in task.get("dependencies", []):
                if dep_id in dag.nodes:
                    dag.add_edge(dep_id, task["id"])

        return dag

    def find_critical_path(self, dag: nx.DiGraph) -> List[str]:
        """寻找关键路径（基于估算时间的拓扑最长路径）"""
        if not dag.nodes:
            return []

        topo_order = list(nx.topological_sort(dag))
        dist = {node: 0 for node in dag.nodes}
        prev = {node: None for node in dag.nodes}

        for node in topo_order:
            cost = dag.nodes[node].get("estimated_hours", 8)
            for successor in dag.successors(node):
                if dist[node] + cost > dist[successor]:
                    dist[successor] = dist[node] + cost
                    prev[successor] = node

        # 找终点
        end = max(dist, key=dist.get)
        path = []
        while end is not None:
            path.append(end)
            end = prev[end]
        return path[::-1]

    def identify_parallel_groups(self, dag: nx.DiGraph) -> List[List[str]]:
        """识别可并行执行的任务组"""
        groups = []
        remaining = set(dag.nodes)
        group_id = 0

        while remaining:
            # 找出所有入度为零的节点（无未完成的依赖）
            ready = [n for n in remaining if all(
                pred not in remaining for pred in dag.predecessors(n)
            )]
            if not ready:
                break  # 应该有环，但应该已被检测
            groups.append(ready)
            for node in ready:
                dag.nodes[node]["parallel_group"] = group_id
            remaining -= set(ready)
            group_id += 1

        return groups