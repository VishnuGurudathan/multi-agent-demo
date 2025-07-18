# UI Dockerfile for Streamlit frontend
FROM python:3.11-slim as builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Copy requirements
COPY ui/requirements.txt .

# Install dependencies
RUN uv pip install --system --no-cache -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy packages
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app

# Copy UI source code
COPY ui/src/ ./ui/src/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "ui/src/app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
