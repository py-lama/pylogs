FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml poetry.lock ./
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir poetry structlog rich click sqlalchemy python-dotenv

# Copy the package files
COPY . .

# Install the package in development mode
RUN pip install -e .

# Create logs directory
RUN mkdir -p /app/logs

# Expose the web interface port
EXPOSE 5001

# Command to run the web interface
CMD ["python", "-m", "loglama.cli.main", "web", "--host", "0.0.0.0", "--port", "5001", "--db", "/app/logs/loglama.db"]
