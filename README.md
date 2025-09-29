# se-ml-test — Reproducible hybrid SE+ML test-generation pipeline (skeleton)

This repository contains minimal artifacts for the paper:
**Integrating Symbolic Execution and Machine Learning for Automated Test Generation in System-Level Programming Languages**.

It provides:
- a minimal C target (`replication/c_parser.c`) and a small Rust parser,
- simple harness (`replication/c_target.c`) to run inputs,
- scripts to execute inputs and collect runtime metadata (`executor.sh`),
- scripts to featurize inputs (`featurize.py`) and train/rank via RandomForest (`ranker.py`),
- a runbook orchestrator: `replication/experiments/run_experiment.sh`,
- a Dockerfile skeleton to help set up an environment.

## Quickstart (local, minimal)

Requirements:
- Linux (bash)
- clang (or gcc)
- python3, pip
- pandas, scikit-learn

Install python deps:
```bash
pip3 install pandas scikit-learn numpy
```

## Notes on AI Assistance
Some parts of this repository (e.g., documentation text, initial code scaffolding, and experiment orchestration) were drafted with the help of AI models.  
All code, scripts, and results included here have been manually reviewed and validated by the authors.
