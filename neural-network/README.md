# Neural Network Module

This directory contains the neural network component responsible for creating and trainig the neural network that will classify the traffic. 
It is written in Python, managed with [Poetry](https://python-poetry.org/),.

This module is part of a larger system and is intended to be a previous step for the final system to work.

---

## Directory Overview

```

neural-network/
├── neural-network/       # Source code (Python package)
│   └── main.py           # Application entry point
├── tests/                # Unit tests
├── pyproject.toml        # Poetry project configuration
├── poetry.lock           # Locked dependency versions
└── README.md             # This file

````

---

## Development Workflow

### Prerequisites

- Python 3.12+
- [Poetry](https://python-poetry.org/docs/#installation)
- (Optional) `pytest`, `flake8`, `mypy` for testing and linting

### Install Dependencies

```bash
cd neural-network
poetry shell
poetry install
````

### Run the Application Locally

```bash
poetry run python -m neural-network.main
```

### Run Tests

```bash
poetry run pytest
```