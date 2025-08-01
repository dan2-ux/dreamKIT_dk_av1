# Use a base image with Python 3.9
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libglib2.0-dev \
    alsa-utils pulseaudio \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

# Copy the entire local directory (including your script) into the container
COPY . /app/

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application
CMD ["python", "model1.1.py"]