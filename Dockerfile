FROM python:3.12-slim
# Use the = format to fix those warnings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*
# Now this will work because the file exists!
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Start the app
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]