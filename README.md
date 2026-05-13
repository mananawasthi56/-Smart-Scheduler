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
├── scheduler/              # Core scheduling modules
├── tests/                  # Unit tests and simulators
├── compare/                # Benchmark comparisons
├── docker-compose.yml      # Simulated nodes
├── requirements.txt        # Python dependencies
├── main.py                 # Entry point
└── README.md              # This file
```

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
