# Start with Python 3.11
FROM python:3.11-slim

# Install Node.js (needed to build React)
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy and build frontend
COPY frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm install
COPY frontend/ ./
RUN npm run build

# Copy backend code
WORKDIR /app
COPY backend/ ./backend/

# Expose port 5000
EXPOSE 5000

# Run Flask
CMD ["python", "backend/backend.py"]
