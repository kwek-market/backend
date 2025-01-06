# Use the Python Alpine image
FROM python:3.11.11-alpine3.21

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libffi-dev \
    build-base \
    py3-cryptography \
    jpeg-dev \
    zlib-dev

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project into the container
COPY . .

# Expose the port used by Django (default: 8000)
EXPOSE 8000

# Run the application
CMD ["gunicorn", "kwek.wsgi:application", "--bind", "0.0.0.0:8000"]
