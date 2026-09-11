# Agent Incident Investigation Lab

**工具驱动的事件调查 Agent**  
*评估和改进小模型 Agent 的证据驱动型系统诊断能力*

## 项目概述

本项目基于 **Qwen2.5-7B** 构建了一个轻量级的长周期事件调查 Agent，使用公开的系统日志数据集、工具驱动的调查、验证和轨迹评估。

```text
事件发生
   ↓
观察现象
   ↓
选择调查动作
   ↓
调用工具
   ↓
观察结果
   ↓
更新假设
   ↓
继续 / 重试 / 重新规划
   ↓
验证
   ↓
根因 + 证据
```

## 核心研究问题

1. **Q1**: Qwen2.5-7B 能否完成基础故障调查？
2. **Q2**: 多步骤 Agent 是否优于单轮分析？
3. **Q3**: Verifier / Re-plan 能否减少错误的调查路径？
4. **Q4**: Trace / Evaluation 能否定位 Agent 失败原因？
5. **Q5**: 能否用于 SFT / RL / Credit Assignment？

## 调查示例

```text
事件 BGL-00017
   ↓
search_logs (查找错误事件)
   ↓
get_error_stats (分析错误模式)
   ↓
compare_window (对比正常窗口与异常窗口)
   ↓
假设: 检测到节点故障
   ↓
verify_hypothesis (验证假设)
   ↓
重新规划 (需要更多证据)
   ↓
get_related_events (追踪相关活动)
   ↓
finish_investigation (结束调查)
   ↓
根因分析: node-042 硬件故障
证据: [ev-00123, ev-00145, ev-00167]
置信度: 0.85
```

## 安装

```bash
# 使用 pip
pip install -r requirements.txt

# 或使用 uv（推荐）
uv sync
```

## 快速开始

### 1. 准备 BGL 数据集

从 [LogHub](https://github.com/logpai/loghub) 下载 BGL 数据集，放置到 `data/raw/BGL/BGL.log`。

或者使用合成数据集（已包含在项目中）：

```bash
# 数据集已位于 data/raw/BGL/BGL.log
```

### 2. 构建事件数据集

```bash
python -m scripts.build_incidents --data data --output data/incidents/bgl_incidents.json
```

### 3. 运行调查

```bash
python -m agent.run --incident BGL-00001 --data data --max-steps 12
```

输出示例：

```text
Investigation Complete
Incident: BGL-00001
Steps: 12

Final Answer:
{
  'root_cause': '网络硬件故障，具体为路由器失效...',
  'evidence_ids': ['ev-00008', 'ev-00009', ...],
  'confidence': 0.95
}
```

### 4. 运行评估

```bash
python -m scripts.run_eval --results reports/evaluation_results.json
```

## 项目结构

```text
agent-incident-lab/
├── agent/              # Agent 控制器和状态管理
│   ├── controller.py   # 核心调查循环
│   ├── state.py        # 状态定义
│   ├── context.py      # 上下文构建器
│   └── prompts/        # Prompt 模板
├── tools/              # 调查工具
│   ├── search_logs.py      # 日志搜索
│   ├── error_stats.py      # 错误统计
│   ├── compare_window.py   # 窗口对比
│   ├── related_events.py   # 相关事件
│   ├── service_summary.py  # 服务摘要
│   ├── verifier.py         # 假设验证
│   └── finish.py           # 结束调查
├── environment/        # 数据加载和事件环境
│   ├── parser.py       # BGL 数据集解析器
│   ├── log_store.py    # 日志存储
│   └── incident_env.py # 事件环境
├── providers/          # LLM 提供者抽象
│   └── ollama.py       # Ollama 提供者
├── evaluation/         # 指标和评估
├── experiments/        # 基线实验
├── configs/            # 配置文件
├── data/               # 数据集存储
├── scripts/            # CLI 脚本
└── reports/            # 实验输出
```

## 调查工具

项目实现了 7 个调查工具：

| 工具 | 功能 |
|------|------|
| `search_logs` | 查询指定时间窗口内的日志 |
| `get_error_stats` | 获取错误统计和模式 |
| `compare_window` | 对比正常窗口与异常窗口 |
| `get_related_events` | 查找相关事件 |
| `get_service_summary` | 获取服务摘要 |
| `verify_hypothesis` | 验证假设是否被证据支持 |
| `finish_investigation` | 结束调查并提交结论 |

## 基线实验

| 方法 | 根因准确率 | 平均步骤数 | 恢复率 |
|------|-----------|-----------|--------|
| Direct LLM | - | - | - |
| Tool Agent | - | - | - |
| + Verifier | - | - | - |
| Full Agent | - | - | - |

## 配置

编辑 `configs/agent.yaml` 调整 Agent 参数：

```yaml
agent:
  max_steps: 12        # 最大调查步骤
  max_replans: 3       # 最大重新规划次数
  max_retries: 2       # 最大重试次数
  confidence_threshold: 0.75  # 置信度阈值
```

## 系统要求

- Python 3.11+
- Ollama（运行 Qwen2.5-7B 模型）
- BGL 数据集（来自 LogHub 或使用合成数据）

## 设计原则

1. **Agent 负责决策，工具负责数据处理**  
   Qwen2.5-7B 负责任务理解、调查规划、工具选择、证据理解和假设生成；工具负责日志扫描、统计分析、数据检索。

2. **结构化观测**  
   工具返回结构化的 JSON 结果，而不是大段文本，避免上下文无限增长。

3. **假设驱动调查**  
   Agent 维护多个假设，根据证据更新置信度，最终保留被验证的假设。

4. **可追溯性**  
   完整的调查轨迹被记录，支持后续分析和评估。

## 许可证

本项目使用 LogHub 的公开数据集。请遵守其许可和引用要求。

## 引用

如果在研究中使用本项目，请引用 LogHub 论文和本仓库。
