# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY gunicorn.conf.py .

# Expose port 5555
EXPOSE 5555

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=5555

# Use gunicorn for production
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]