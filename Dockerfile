FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose web port
EXPOSE 5000

# Default entrypoint
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
