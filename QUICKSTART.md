# Quick Start Guide

## Prerequisites

1. **Python 3.11+**
2. **Ollama** with Qwen2.5-7B model
3. **BGL Dataset** from LogHub

## Setup Steps

### 1. Install Dependencies

```bash
cd agent-incident-lab
pip install -r requirements.txt
```

### 2. Install Ollama and Download Model

```bash
# Install Ollama (https://ollama.com)
ollama pull qwen2.5:7b
```

### 3. Download BGL Dataset

The BGL dataset must be downloaded manually from LogHub:

1. Visit: https://github.com/logpai/loghub
2. Follow their instructions to download the BGL dataset
3. Place the file at: `data/raw/BGL/BGL.log`

**Important**: LogHub datasets require agreeing to their license terms. Please cite their paper if you use the data in research.

### 4. Build Incident Dataset

```bash
python -m scripts.build_incidents --data data --output data/incidents/bgl_incidents.json
```

This will:
- Parse the BGL log file
- Extract incident windows
- Classify by difficulty (easy/medium/hard)
- Save to JSON

### 5. Run Your First Investigation

```bash
python -m agent.run --incident BGL-00001 --data data --max-steps 12
```

The agent will:
- Load the incident
- Use investigation tools
- Build hypotheses
- Collect evidence
- Generate root cause analysis

### 6. Run Evaluation

After running investigations, evaluate results:

```bash
python -m scripts.run_eval --results reports/evaluation_results.json
```

## Example Output

```text
Investigation Complete
Incident: BGL-00001
Steps: 5

Final Answer:
{
  "root_cause": "Hardware failure detected on node-042...",
  "evidence_ids": ["ev-00123", "ev-00145"],
  "confidence": 0.82
}
```

## Troubleshooting

### Ollama Connection Error

Make sure Ollama is running:
```bash
ollama serve
```

### Dataset Not Found

Verify the BGL dataset is at: `data/raw/BGL/BGL.log`

### Import Errors

Make sure you're in the project root directory and have installed dependencies:
```bash
pip install -r requirements.txt
```

## Next Steps

1. **Explore different incidents**: Try incidents with different difficulty levels
2. **Adjust agent parameters**: Edit `configs/agent.yaml`
3. **Run baseline experiments**: Compare different agent configurations
4. **Analyze trajectories**: Review the investigation process in detail

## Project Structure

```text
agent-incident-lab/
├── agent/              # Core agent logic
│   ├── controller.py   # Investigation controller
│   ├── state.py        # State management
│   └── run.py          # Main entry point
├── tools/              # Investigation tools
│   ├── search_logs.py
│   ├── error_stats.py
│   ├── compare_window.py
│   └── ...
├── environment/        # Data handling
│   ├── parser.py       # BGL parser
│   ├── log_store.py    # Log storage
│   └── incident_env.py # Incident extraction
├── evaluation/         # Metrics and reports
├── configs/            # Configuration files
├── scripts/            # CLI utilities
└── data/               # Dataset storage
```

## Configuration

Edit `configs/agent.yaml` to customize:

```yaml
agent:
  max_steps: 12          # Maximum investigation steps
  max_replans: 3         # Maximum re-planning attempts
  confidence_threshold: 0.75  # Confidence to finish
```

## Research Questions

This project investigates:

1. Can Qwen2.5-7B complete basic fault investigation?
2. Is multi-step Agent superior to single-turn analysis?
3. Can Verifier / Re-plan reduce incorrect paths?
4. Can Trace / Evaluation locate Agent failures?

See `PROJECT_SPEC.md` for complete technical specification.
