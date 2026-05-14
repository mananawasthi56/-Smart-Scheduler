# Smart Scheduler

An AI-powered container scheduling system using genetic algorithms to optimize resource allocation and minimize energy costs.

## Features

- Genetic Algorithm core for scheduling optimization
- Docker/Kubernetes integration
- Real-time metrics collection
- Energy cost calculation
- Performance visualization

## Project Structure

```
smart-scheduler/
├── scheduler/              # Core scheduling modules and data collectors
│   ├── __init__.py
│   ├── cost_model.py
│   ├── docker_client.py
│   ├── genetic_scheduler.py
│   ├── historical_data_collector.py
│   ├── kubernetes_collector.py
│   ├── metrics_collector.py
│   ├── real_data_collector.py
│   └── visualizer.py
├── tests/                  # Unit tests and workload simulator
│   ├── test_scheduler.py
│   └── workload_simulator.py
├── compare/                # Benchmark comparisons
│   └── default_vs_ai.py
├── docker-compose.yml      # Simulated nodes and container environment
├── requirements.txt        # Python dependencies
├── main.py                 # Entry point for the scheduler
├── real_world_comparison.py # Real data comparison and visualization
├── setup_guide.py          # Automated setup and validation helper
├── START_HERE.txt          # Project onboarding instructions
├── QUICK_START.md          # Quick start guide and summary
├── REAL_DATA_GUIDE.md      # Real data migration guide
├── DUMMY_VS_REAL_EXPLANATION.md # Dummy vs real explanation
├── CHECKLIST.md            # Setup and validation checklist
└── README.md               # This file
```

## Code Structure

- `scheduler/` contains the scheduler logic, data collection, and visualization helpers.
- `main.py` launches the scheduler using the configured modules and policies.
- `real_world_comparison.py` runs the AI vs default scheduler comparison using real metrics.
- `setup_guide.py` automates setup tasks and validates the Docker/Kubernetes environment.
- `compare/default_vs_ai.py` provides benchmark comparison utilities.
- `tests/` contains unit tests and a workload simulator for validating scheduler behavior.

## CI / Automation

- GitHub Actions is already configured in `.github/workflows/ci.yml`.
- A Jenkins pipeline file has been added at `Jenkinsfile` for Jenkins-based CI runs.
- Both workflows install dependencies, run tests, and execute the scheduler comparison.

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the scheduler:
   ```bash
   python main.py
   ```

3. Run tests:
   ```bash
   pytest tests/
   ```

## License

MIT
