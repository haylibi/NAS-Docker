# --- Stage 1: Build the Frontend ---
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend_build

# Copy frontend package files
COPY frontend/package*.json ./
COPY frontend/tsconfig*.json ./

# Install dependencies and build
RUN npm install
COPY frontend/ ./
# IMPORTANT: Ensure your vite.config.ts or package.json sets the base URL (see below)
RUN npm run build



# Use a slim Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# 1. Copy only the files needed for installation first 
# (This leverages Docker's cache for faster builds)
COPY pyproject.toml .
COPY requirements.txt .
RUN pip install -r requirements.txt


# 2. Copy the actual application code
COPY jellyfin_webhooks/ jellyfin_webhooks/

# 3. Copy the frontend build artifacts
COPY --from=frontend-builder /frontend_build/dist /app/frontend_static

# 3. Use the Entry Point we defined in pyproject.toml
# Instead of "python main.py", we use the command name
CMD ["python", "-m", "jellyfin_webhooks.main"]
