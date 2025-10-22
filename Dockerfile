# Use official Python image
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app code into container
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Command to run the app
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
