# Base image
FROM python:3.9-slim

# Work directory
WORKDIR /app

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Port expose (Render automatically handles this, but for clarity)
EXPOSE 8000

# Start command
CMD ["python", "main.py"]
