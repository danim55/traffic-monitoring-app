# Detector Backend Module

This directory contains the backend component responsible for network traffic detection. 
It is written in Python, managed with [Poetry](https://python-poetry.org/), 
and packaged as a Docker image for deployment in containerized environments.

This module is part of a larger system and is intended to operate as a long-running service that processes network flow data.

---

## 📁 Directory Overview

```

detector/
├── detector/             # Source code (Python package)
│   └── main.py           # Application entry point
├── tests/                # Unit tests
├── pyproject.toml        # Poetry project configuration
├── poetry.lock           # Locked dependency versions
├── Dockerfile            # Docker image definition
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
cd detector
poetry install
````

### Run the Application Locally

```bash
poetry run python -m detector.main
```

### Run Tests

```bash
poetry run pytest
```

---

## 🐳 Docker

The included `Dockerfile` builds a minimal production-ready container image using Poetry for dependency management.

### Build the Image

```bash
docker build -t detector:latest .
```

### Run the Container

```bash
docker run --rm detector:latest
```

This executes:

```bash
python -m detector.main
```

inside the container.

---

## 🔐 Corporate Environment Configuration

If working in a corporate network (e.g., behind an Artifactory proxy):

* The `Dockerfile` is preconfigured to:

  * Use the Artifactory proxy as the Python package index
  * Trust system CA certificates for HTTPS
  * Set `REQUESTS_CA_BUNDLE` and `PIP_CERT` environment variables to avoid SSL issues

Make sure any internal certificates or proxy configurations are correctly mirrored inside your Docker environment.

---

## 🧩 Integration Notes

* This module is expected to be orchestrated within a broader application stack.
* Future deployment will include container orchestration via Kubernetes and Helm.
* Gradle and GitHub Actions will be used to coordinate multi-component builds and CI/CD.

---

```
