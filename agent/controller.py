import asyncio
from typing import Any
from datetime import datetime

from agent.state import Incident, Hypothesis, Evidence
from agent.context import InvestigationState
from agent.prompts.system import SYSTEM_PROMPT, INCIDENT_PROMPT_TEMPLATE
from providers.ollama import OllamaProvider
from tools.registry import ToolRegistry, ToolResult


class InvestigationController:
    """
    核心调查控制器，实现多步骤事件调查循环。
    
    设计原则：
    - Agent 负责决策和推理，工具负责数据处理
    - 通过假设驱动的方式进行调查
    - 支持重新规划（re-plan）以应对调查停滞
    """
    
    def __init__(
        self,
        llm: OllamaProvider,
        tools: ToolRegistry,
        max_steps: int = 12,
        max_replans: int = 3,
        max_retries: int = 2,
        confidence_threshold: float = 0.75,
    ):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps  # 防止无限循环
        self.max_replans = max_replans  # 重新规划次数限制
        self.max_retries = max_retries
        self.confidence_threshold = confidence_threshold  # 置信度阈值，达到后可结束调查

        self.state: InvestigationState | None = None
        self.trajectory: list[dict] = []  # 记录完整调查轨迹，用于后续评估

    async def investigate(self, incident: Incident) -> dict:
        """
        执行完整的调查流程。
        
        调查循环：
        1. 加载事件信息
        2. 规划调查步骤
        3. 选择并执行工具
        4. 观察结果并更新假设
        5. 验证是否需要重新规划
        6. 重复直到达到结束条件
        """
        self.state = self._init_state(incident)
        self.trajectory = []

        step = 0
        while step < self.max_steps:
            step += 1

            # 让 LLM 决定下一步行动
            action = await self._decide_action()

            # 如果 LLM 决定结束调查，跳出循环
            if action["type"] == "finish":
                break

            # 执行工具调用并更新状态
            if action["type"] == "tool_call":
                result = await self._execute_tool(action)
                self._update_state(result)

                # 检查是否需要重新规划（调查停滞时触发）
                should_replan = self._check_replan_condition()
                if should_replan and self.state["replan_count"] < self.max_replans:
                    await self._replan()
                    self.state["replan_count"] += 1

            # 记录当前步骤到轨迹
            self.trajectory.append({
                "step": step,
                "action": action,
                "state_snapshot": self._snapshot_state(),
            })

        # 生成最终调查报告
        final_answer = await self._generate_final_answer()
        self.state["final_answer"] = final_answer

        return {
            "incident_id": incident.incident_id,
            "trajectory": self.trajectory,
            "final_answer": final_answer,
            "steps": step,
        }

    def _init_state(self, incident: Incident) -> InvestigationState:
        return {
            "incident_id": incident.incident_id,
            "user_goal": f"Investigate incident {incident.incident_id}",
            "current_time_window": {
                "start": incident.start_time.isoformat(),
                "end": incident.end_time.isoformat(),
            },
            "observations": [],
            "hypotheses": [],
            "evidence": [],
            "available_tools": [t.name for t in self.tools.list_tools()],
            "plan": ["search_logs", "get_error_stats"],
            "completed_steps": [],
            "confidence": 0.0,
            "retry_count": 0,
            "replan_count": 0,
            "verification_result": {},
            "final_answer": {},
        }

    async def _decide_action(self) -> dict:
        prompt = self._build_prompt()

        response = await self.llm.generate(prompt)

        action = self._parse_action(response)
        return action

    def _parse_action(self, response: str) -> dict:
        """
        解析 LLM 响应，提取要执行的动作。
        
        当前实现：基于关键词匹配（简单但有效）
        未来可升级为：结构化输出或工具调用 API
        """
        response_lower = response.lower()

        # 检查是否决定结束调查
        if "finish_investigation" in response_lower or "conclude" in response_lower:
            return {
                "type": "finish",
                "reasoning": response,
            }

        # 工具关键词映射表
        # 优先级：按顺序匹配，第一个匹配的工具会被选中
        tool_keywords = {
            "search_logs": ["search", "find", "query", "logs"],
            "get_error_stats": ["error", "stats", "statistics", "count"],
            "compare_window": ["compare", "baseline", "window"],
            "get_related_events": ["related", "trace", "pattern"],
            "get_service_summary": ["service", "node", "summary"],
            "verify_hypothesis": ["verify", "hypothesis", "check"],
        }

        for tool_name, keywords in tool_keywords.items():
            if any(kw in response_lower for kw in keywords):
                time_window = self.state["current_time_window"]
                return {
                    "type": "tool_call",
                    "tool_name": tool_name,
                    "tool_args": {
                        "start_time": time_window["start"],
                        "end_time": time_window["end"],
                    },
                }

        # 默认行为：如果无法解析，结束调查
        return {
            "type": "finish",
            "reasoning": response,
        }

    def _build_prompt(self) -> str:
        incident_id = self.state["incident_id"]
        time_window = self.state["current_time_window"]

        context = f"""
Current Investigation State:
- Step {len(self.state['completed_steps']) + 1}
- Confidence: {self.state['confidence']:.2f}
- Hypotheses: {len(self.state['hypotheses'])}
- Evidence collected: {len(self.state['evidence'])}

Recent observations:
"""
        for obs in self.state["observations"][-3:]:
            context += f"- {obs}\n"

        if self.state["hypotheses"]:
            context += "\nActive hypotheses:\n"
            for h in self.state["hypotheses"][-2:]:
                context += f"- {h.statement} (confidence: {h.confidence:.2f})\n"

        prompt = INCIDENT_PROMPT_TEMPLATE.format(
            incident_id=incident_id,
            start_time=time_window["start"],
            end_time=time_window["end"],
            alert="Anomalous activity detected",
        )

        return f"{SYSTEM_PROMPT}\n\n{prompt}\n\n{context}"

    async def _execute_tool(self, action: dict) -> ToolResult:
        tool_name = action["tool_name"]
        tool_args = action["tool_args"]

        result = await self.tools.execute(tool_name, **tool_args)
        return result

    def _update_state(self, result: ToolResult) -> None:
        self.state["completed_steps"].append({
            "tool": result.tool,
            "status": result.status,
            "timestamp": datetime.now().isoformat(),
        })

        observation = f"Called {result.tool}: {result.status}"
        self.state["observations"].append(observation)

        if result.evidence_ids:
            for eid in result.evidence_ids:
                evidence = Evidence(
                    evidence_id=eid,
                    source=result.tool,
                    content=str(result.result),
                )
                self.state["evidence"].append(evidence)

    def _check_replan_condition(self) -> bool:
        if len(self.state["completed_steps"]) < 2:
            return False

        last_two = self.state["completed_steps"][-2:]
        if all(step["status"] == "error" for step in last_two):
            return True

        if len(self.state["observations"]) >= 2:
            last_two_obs = self.state["observations"][-2:]
            if last_two_obs[0] == last_two_obs[1]:
                return True

        return False

    async def _replan(self) -> None:
        prompt = f"""
Investigation is not progressing effectively.

Current state:
- Steps completed: {len(self.state['completed_steps'])}
- Evidence: {len(self.state['evidence'])}
- Confidence: {self.state['confidence']:.2f}

Generate a new investigation plan using different tools or approaches.

Available tools: {', '.join(self.state['available_tools'])}
"""

        response = await self.llm.generate(prompt)

        self.state["plan"] = ["search_logs", "compare_window", "get_related_events"]

    async def _generate_final_answer(self) -> dict:
        prompt = f"""
Based on the investigation, provide your final conclusion.

Evidence collected: {len(self.state['evidence'])}
Steps taken: {len(self.state['completed_steps'])}

Summarize:
1. Root cause
2. Supporting evidence
3. Confidence level (0.0 to 1.0)
"""

        response = await self.llm.generate(prompt)

        return {
            "root_cause": response,
            "evidence_ids": [e.evidence_id for e in self.state["evidence"]],
            "confidence": self.state["confidence"],
        }

    def _snapshot_state(self) -> dict:
        return {
            "step": len(self.state["completed_steps"]),
            "confidence": self.state["confidence"],
            "evidence_count": len(self.state["evidence"]),
            "hypotheses_count": len(self.state["hypotheses"]),
        }
