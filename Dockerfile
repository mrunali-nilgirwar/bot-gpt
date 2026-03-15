# Start with Python
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install all packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
