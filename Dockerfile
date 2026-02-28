# Simple Dockerfile for running the Flask application
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set environment defaults (override with actual values at runtime)
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:$PORT"]
