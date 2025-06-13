# Stage 1: Install dependencies with Poetry
FROM python:3.12-slim AS builder

# Install build-time tools
RUN apt-get update && \
    apt-get install --no-install-recommends -y gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Poetry config & project metadata
COPY pyproject.toml poetry.lock ./

# Install Poetry
RUN pip install poetry

# Configure Poetry to skip creating virtualenvs
RUN poetry config virtualenvs.create false

# Install only production dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Stage 2: Build the lean runtime image
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from the builder image
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copy only your application code
COPY detector detector

# Default command
ENTRYPOINT ["python", "-m", "detector.main"]