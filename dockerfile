# Use an official lightweight Python image
FROM python:3.12-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies and install them
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . /app/

# Move into backend directory to run manage.py
WORKDIR /app/backend

# Expose port for Django
EXPOSE 8000

# Run migrations and start server automatically
CMD ["bash", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
