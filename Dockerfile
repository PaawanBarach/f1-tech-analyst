# 1. Base image
FROM python:3.10-slim

# 2. Install build tools for any pip packages that need compiling
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      gcc \
      libc6-dev \
      python3-dev \
      git \
 && rm -rf /var/lib/apt/lists/*

# 3. Set working dir
WORKDIR /app

# 4. Copy only requirements first (caching layer)
COPY requirements.txt .

# 5. Install Python deps
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your application
COPY . .

# 7. Expose ports
EXPOSE 80 7860

# 8. Default command
CMD ["bash", "-lc", "uvicorn main:app --host 0.0.0.0 --port 80"]
