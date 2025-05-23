# Example Dockerfile for LogLama (Python-based)
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY ../../.. /app
RUN pip install --upgrade pip \
    && pip install .

# Expose the web interface port (adjust if needed)
EXPOSE 5000

# Set environment variables if needed
ENV LOGLAMA_LOG_DIR=/logs \
    LOGLAMA_CONSOLE_ENABLED=true \
    LOGLAMA_SQLITE_ENABLED=true

# Create logs directory
RUN mkdir -p /logs

# Default command (adjust if LogLama has a different entrypoint)
CMD ["python", "-m", "loglama.web.app"]
