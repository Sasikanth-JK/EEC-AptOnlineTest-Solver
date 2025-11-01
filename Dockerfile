# Use Python 3.13 slim image as base
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright and uv
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create and activate a virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy dependencies first (for better caching)
COPY requirements.txt .

# Install Python dependencies using uv inside the venv
RUN uv pip install --no-cache -r requirements.txt || \
    uv pip install --no-cache .

# Install Playwright and dependencies
RUN playwright install chromium && \
    playwright install-deps chromium

# Copy the application code
COPY . .

# Default command
CMD ["python3", "main.py"]
