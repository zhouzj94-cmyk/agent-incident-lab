# Agent Incident Investigation Lab

**Tool-driven Incident Investigation Agent**  
*Evaluating and improving small-model agents for evidence-driven system diagnosis*

## Overview

This project builds a lightweight long-horizon incident investigation agent on **Qwen2.5-7B**, using public system-log datasets, tool-driven investigation, verification, and trajectory evaluation.

```text
Incident
   ↓
Observe
   ↓
Choose Investigation Action
   ↓
Call Tool
   ↓
Observe Result
   ↓
Update Hypothesis
   ↓
Continue / Retry / Re-plan
   ↓
Verify
   ↓
Root Cause + Evidence
```

## Core Research Questions

1. **Q1**: Can Qwen2.5-7B complete basic fault investigation?
2. **Q2**: Is multi-step Agent superior to single-turn analysis?
3. **Q3**: Can Verifier / Re-plan reduce incorrect investigation paths?
4. **Q4**: Can Trace / Evaluation locate Agent failures?
5. **Q5**: Can this be used for SFT / RL / Credit Assignment?

## Example Investigation

```text
Incident BGL-00017
   ↓
search_logs (find error events)
   ↓
get_error_stats (analyze error patterns)
   ↓
compare_window (compare normal vs incident)
   ↓
hypothesis: Node failure detected
   ↓
verify_hypothesis
   ↓
re-plan (need more evidence)
   ↓
get_related_events (trace related activity)
   ↓
finish_investigation
   ↓
RCA: Hardware failure on node-042
Evidence: [ev-00123, ev-00145, ev-00167]
Confidence: 0.85
```

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Download BGL Dataset

Download the BGL dataset from [LogHub](https://github.com/logpai/loghub) and place it in `data/raw/BGL/BGL.log`.

### 2. Build Incident Dataset

```bash
python -m scripts.build_incidents --data data --output data/incidents/bgl_incidents.json
```

### 3. Run Investigation

```bash
python -m agent.run --incident BGL-00001 --data data --max-steps 12
```

### 4. Run Evaluation

```bash
python -m scripts.run_eval --results reports/evaluation_results.json
```

## Project Structure

```text
agent-incident-lab/
├── agent/              # Agent controller and state management
├── tools/              # Investigation tools
├── environment/        # Data loading and incident environment
├── providers/          # LLM provider abstraction
├── evaluation/         # Metrics and evaluation
├── experiments/        # Baseline experiments
├── configs/            # Configuration files
├── data/               # Dataset storage
├── scripts/            # CLI scripts
└── reports/            # Experiment outputs
```

## Baselines

| Method | RCA Acc. | Avg Steps | Recovery |
|--------|----------|-----------|----------|
| Direct LLM | - | - | - |
| Tool Agent | - | - | - |
| + Verifier | - | - | - |
| Full Agent | - | - | - |

## Configuration

Edit `configs/agent.yaml` to adjust agent parameters:

```yaml
agent:
  max_steps: 12
  max_replans: 3
  max_retries: 2
  confidence_threshold: 0.75
```

## Requirements

- Python 3.11+
- Ollama with Qwen2.5-7B model
- BGL dataset from LogHub

## License

This project uses public datasets from LogHub. Please respect their licensing and citation requirements.

## Citation

If you use this project in your research, please cite the LogHub paper and this repository.
