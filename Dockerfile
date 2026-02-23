# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (layer caching — reinstall only if requirements change)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Create an empty state.json if it doesn't exist
# This prevents a crash on first run inside the container
RUN test -f state.json || echo "{}" > state.json

# Run the tracker
CMD ["python", "main.py"]