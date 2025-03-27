# Dockerfile for SearchAI application
# Using Python 3.10 as the base image
FROM python:3.10-slim

# Install system dependencies
# wkhtmltopdf is required for PDF generation through pdfkit
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Command to run the application
ENTRYPOINT ["python", "main.py"]

