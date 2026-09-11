from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel


class ToolResult(BaseModel):
    """工具执行结果的统一结构"""
    tool: str
    status: str
    query: dict
    result: Any
    evidence_ids: list[str] = []


class BaseTool(ABC):
    """
    调查工具的基类。
    
    所有工具必须实现：
    - name: 工具名称（用于 Agent 调用）
    - description: 工具描述（用于 Agent 理解工具用途）
    - input_schema: 输入参数定义
    - execute: 执行逻辑
    """
    name: str
    description: str
    input_schema: dict
    output_schema: dict

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        pass

    def to_openai_schema(self) -> dict:
        """转换为 OpenAI 工具调用格式（预留扩展）"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema,
            },
        }


class ToolRegistry:
    """
    工具注册表，管理所有调查工具。
    
    设计模式：注册表模式（Registry Pattern）
    - 工具在启动时注册
    - Agent 通过名称查找并执行工具
    - 所有工具返回统一的 ToolResult 结构
    """
    
    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """注册工具到注册表"""
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        """根据名称获取工具"""
        return self._tools.get(name)

    def list_tools(self) -> list[BaseTool]:
        """列出所有已注册工具"""
        return list(self._tools.values())

    def get_openai_schemas(self) -> list[dict]:
        """获取所有工具的 OpenAI 格式定义"""
        return [tool.to_openai_schema() for tool in self._tools.values()]

    async def execute(self, name: str, **kwargs) -> ToolResult:
        """执行指定工具，返回统一结果结构"""
        tool = self._tools.get(name)
        if not tool:
            return ToolResult(
                tool=name,
                status="error",
                query=kwargs,
                result={"error": f"Tool {name} not found"},
            )
        return await tool.execute(**kwargs)
