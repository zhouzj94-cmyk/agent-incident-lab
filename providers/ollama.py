from abc import ABC, abstractmethod
from typing import Any
import httpx


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass

    @abstractmethod
    async def generate_with_tools(
        self, prompt: str, tools: list[dict], **kwargs
    ) -> dict[str, Any]:
        pass


class OllamaProvider(LLMProvider):
    """
    Ollama LLM 提供者，通过 HTTP API 与本地 Ollama 服务通信。
    
    注意：
    - trust_env=False 是必需的，防止 Windows 系统代理设置干扰 localhost 连接
    - 超时设置为 300 秒，因为 7B 模型生成调查响应可能需要较长时间
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2.5:7b"):
        self.base_url = base_url
        self.model = model
        # trust_env=False 防止 httpx 读取系统代理设置（Windows 上会导致 "Relay failed" 错误）
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(300.0, connect=10.0),
            trust_env=False,
        )

    async def generate(self, prompt: str, **kwargs) -> str:
        response = await self.client.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                **kwargs,
            },
        )
        response.raise_for_status()
        return response.json()["response"]

    async def generate_with_tools(
        self, prompt: str, tools: list[dict], **kwargs
    ) -> dict[str, Any]:
        messages = [{"role": "user", "content": prompt}]

        response = await self.client.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "tools": tools,
                "stream": False,
                **kwargs,
            },
        )
        response.raise_for_status()
        result = response.json()

        message = result["message"]

        if "tool_calls" in message and message["tool_calls"]:
            tool_call = message["tool_calls"][0]
            return {
                "type": "tool_call",
                "tool_name": tool_call["function"]["name"],
                "tool_args": tool_call["function"]["arguments"],
                "content": message.get("content", ""),
            }

        return {
            "type": "response",
            "content": message.get("content", ""),
        }

    async def close(self):
        await self.client.aclose()
