# Use a base image with Python
FROM python:3.8

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy the application code to the container
COPY . /app/

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-dev \
    libpq-dev 

# Create and activate a virtual environment and define variables for next stage
RUN python -m venv venv
RUN . venv/bin/activate

ARG DATABASE_URL
ARG PGDATABASE
ARG PGHOST
ARG PGPASSWORD
ARG PGPORT
ARG PGUSER
ARG PORT


    
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt



# Run database migrations and collect static files
RUN python manage.py makemigrations && \
    python manage.py migrate && \      
    python manage.py collectstatic --noinput
    
    



# Run migrations and collect static files
CMD gunicorn mysite.wsgi  --bind 0.0.0.0:$PORT




