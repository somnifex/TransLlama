FROM python:3.12-slim

WORKDIR /app

# Install build dependencies for llama-cpp-python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project metadata and install dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir .

# Copy application source
COPY main.py ./
COPY api/ ./api/
COPY services/ ./services/
COPY models/ ./models/
COPY core/ ./core/
COPY models.yaml ./

# Create model storage directory
RUN mkdir -p /app/storage/models

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
