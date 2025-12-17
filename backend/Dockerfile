FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libpq-dev \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Copy and setup startup script
COPY app/startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

# Create storage directories
RUN mkdir -p /app/storage/images /app/storage/thumbnails

EXPOSE 8000

CMD ["/app/startup.sh"]

