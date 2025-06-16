FROM python:3.12-slim

# Company configuration if needed
ARG ENVIRONMENT
ENV ENVIRONMENT=${ENVIRONMENT}
COPY resources/company-configuration.sh /usr/local/bin/company-configuration.sh
RUN chmod +x /usr/local/bin/company-configuration.sh
RUN /usr/local/bin/company-configuration.sh

# Install Poetry (pinned version)
RUN pip install poetry==1.4.2

WORKDIR /app

# Copy Poetry config & project metadata
COPY pyproject.toml poetry.lock ./
COPY detector ./detector
RUN touch README.md

# Install only production dependencies
RUN poetry install --without dev

# Default command
ENTRYPOINT ["poetry", "run", "python", "-m", "detector.main"]
