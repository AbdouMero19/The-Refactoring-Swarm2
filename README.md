# The Refactoring Swarm

## Overview

The Refactoring Swarm repository is a collection of small refactoring exercises, sample projects, and tests used to detect and fix issues such as circular imports and to validate refactoring changes.

This workspace is primarily intended for automated analysis, experiments, and unit tests that exercise refactorings and dependency fixes.

## Repository layout

- `sandbox/` — snapshots of test cases and variants (copies of `circular_test_*` and `real_test4_*`) used for running isolated tests.
- `src/` — (internal) source for analysis tooling and utilities.
- `logs/` — experiment outputs, e.g. `experiment_data.json`.
- `.langgraph_api/` and checkpoints — local caches and artifacts used by tooling in this workspace.

## Requirements

- Python 3.8+ recommended
- Install dependencies from `requirements.txt`:

```
pip install -r requirements.txt
```

## Running the main analysis script

The repository includes a `main.py` that can be used to run analysis against a target directory. Example (from repository root):

```
python main.py --target_dir ".\real_test4\"
```

Adjust `--target_dir` to point to any folder you want to analyze or test (for example a sandbox snapshot).

## Running tests

Many sandbox subfolders include pytest-based tests. From the repository root you can run:

```
pytest -q
```

Or run pytest inside an individual sandbox folder to restrict scope, e.g. `sandbox/real_test4_393db1a8`.

## Logs and experiment data

Experiment outputs are stored under `logs/`, e.g. `logs/experiment_data.json`.

## Notes

- This repo contains multiple snapshots of example projects used for experiments; edit or run them in `sandbox/` when you want isolated test runs.
- No license is specified in this repository — add one if you plan to redistribute.

If you'd like, I can run the test suite, create a git commit for this README, or expand the README with architecture diagrams or examples.
