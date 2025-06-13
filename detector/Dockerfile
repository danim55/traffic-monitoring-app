FROM python:3.12-slim

RUN pip install poetry==1.4.2

WORKDIR /app

# Copy Poetry config & project metadata
COPY pyproject.toml poetry.lock ./
COPY detector ./detector
RUN touch README.md

# Install only production dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Default command
ENTRYPOINT ["poetry", "run", "python", "-m", "detector.main"]