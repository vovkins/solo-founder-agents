# Multi-stage build for Solo Founder Agents

FROM python:3.12-slim as builder

WORKDIR /app

# Install Node.js for React Native development
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js global packages for React Native
RUN npm install -g \
    react-native-cli \
    @react-native-community/cli \
    typescript \
    eslint \
    prettier

RUN pip install poetry==2.3.2

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies only (not the project itself)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

FROM python:3.12-slim as runtime

WORKDIR /app

# Install Node.js in runtime
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    git \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js global packages
RUN npm install -g \
    react-native-cli \
    @react-native-community/cli \
    typescript \
    eslint \
    prettier

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY src/ ./src/
COPY config/ ./config/
COPY templates/ ./templates/
COPY README.md ./

RUN mkdir -p /app/data/artifacts /app/data/state

ENV PYTHONPATH=/app

CMD ["sleep", "infinity"]
