FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY src/ ./src/

# Set Python path so imports work correctly
ENV PYTHONPATH=/app

EXPOSE 5000

# Run the app via the package entry point
CMD ["python", "src/__init__.py"]