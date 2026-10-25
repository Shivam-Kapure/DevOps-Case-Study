# ==============================================================================
# Enterprise Payment & Notification Engine - Backend Dockerfile
# ==============================================================================
FROM python:3.12-slim

# Prevent bytecode caching and ensure immediate log output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BACKEND_HOST=0.0.0.0 \
    PORT=28081 \
    BACKEND_PORT=28081

WORKDIR /app

# Install dependencies first for Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application source
COPY . .

# Run as non-privileged user for security best practices
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose the default backend port (can be overridden via -e PORT=...)
EXPOSE 28081

# Container health check on the FastAPI /health endpoint
HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request, os; port=os.getenv('PORT', '28081'); urllib.request.urlopen(f'http://localhost:{port}/health')" || exit 1

# Start the application binding to 0.0.0.0
CMD ["python", "run.py"]
