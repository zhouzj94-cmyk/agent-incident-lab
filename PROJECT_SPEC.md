# Agent Incident Investigation Lab - Project Specification

This document contains the complete technical specification for the Agent Incident Investigation Lab project.

## Project Positioning

This is not a traditional "LLM log classifier" or a simple "log Q&A bot". The goal is to build a Tool Agent capable of **autonomous investigation** of system anomalies.

## Core Technical Questions

All code should revolve around these 4 questions:

1. **Action**: What should the Agent do next?
2. **Evidence**: Is the current evidenceufficient?
3. **Recovery**: What to do after going wrong?
4. **Evaluation**: Why did the Agent fail?

## Phase 1 Scope

### In Scope
- Qwen2.5-7B
- Python
- Tool Agent
- LogHub (BGL / HDFS)
- Incident Investigation
- Verifier
- Re-plan
- Langfuse Trace
- Offline Evaluation

### Out of Scope
- Multi-Agent
- MCP
- Browser Agent
- Computer Use
- Large-scale RL
- Custom LLM training
- Distributed training
- Kubernetes
- Production systems

## Implementation Phases

### Phase 1: Core Infrastructure
- Dataset Loader
- Log Store
- Incident Environment
- Qwen Provider
- Tool Registry
- Tool Calling
- Agent State
- Investigation Loop
- Termination

### Phase 2: Advanced Features
- Verifier
- Retry
- Anti-loop
- Re-plan

### Phase 3: Observability
- Langfuse Trace
- Evaluation
- Baseline

### Phase 4: Analysis
- Failure Attribution
- Dataset
- Regression

### Phase 5-7: Training (Future)
- SFT
- Credit Assignment
- GRPO

## Completion Criteria

### Phase 1 MVP
- [ ] Load BGL data
- [ ] Construct incidents
- [ ] Qwen2.5-7B via Ollama
- [ ] Agent calls 5+ tools
- [ ] Agent completes 3+ step investigation
- [ ] Max step limit
- [ ] Retry mechanism
- [ ] Anti-loop
- [ ] Verifier
- [ ] Re-plan
- [ ] Final RCA
- [ ] Evidence list
- [ ] Langfuse trace
- [ ] Baseline comparison
- [ ] Evaluation metrics
- [ ] CSV/JSON output

## Code Constraints

1. Python 3.11+
2. Type annotations
3. Pydantic data models
4. Async-first
5. Tools independently testable
6. Agent-Tool decoupling
7. Replaceable LLM Provider
8. Evaluation independent of Agent internals
9. All experiments reproducible via CLI
10. JSON/CSV output per experiment

## Prohibited Actions

- Fabricate experiment metrics
- Fabricate dataset scale
- Claim LogHub data as original
- Hardcode baseline results
- Write final metrics to README
- Cherry-pick best results via random seed
- Use test set for prompt tuning
- Leak failure cases from test to train
- Use LLM self-evaluation as absolute truth
- Add untested modules for appearance
