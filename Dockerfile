# Solo Founder Agents Dockerfile
# Multi-stage build for optimized image

# ===========================================
# Builder stage
# ===========================================
FROM python:3.12-slim as builder

# Install poetry
RUN pip install poetry==2.3.2

# Set poetry config
RUN poetry config virtualenvs.create false

WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-interaction --no-root

# ===========================================
# Runtime stage
# ===========================================
FROM python:3.12-slim as runtime

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY templates/ ./templates/

# Create data directories
RUN mkdir -p /app/data/artifacts /app/data/state

# Set Python path
ENV PYTHONPATH=/app

# Run the application
CMD ["python", "-m", "src.main"]
