# ============================================================
# BASE IMAGE
# We start from an official Python image
# 3.11-slim means Python 3.11 with minimal OS packages
# slim is smaller than full image — faster to download/deploy
# ============================================================
FROM python:3.11-slim

# ============================================================
# WORKING DIRECTORY
# All subsequent commands run from this folder inside container
# Like doing cd /app inside the container
# ============================================================
WORKDIR /app

# ============================================================
# INSTALL DEPENDENCIES FIRST
# We copy requirements.txt before copying all code
# Why? Docker caches each layer
# If only code changes (not requirements), Docker reuses
# the cached pip install layer — much faster builds
# ============================================================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================
# COPY APPLICATION CODE
# Now copy everything else
# .dockerignore prevents copying venv, .env, __pycache__
# ============================================================
COPY . .

# ============================================================
# EXPOSE PORT
# Tells Docker this container listens on port 8000
# Doesn't actually open the port — just documents it
# ============================================================
EXPOSE 8000

# ============================================================
# STARTUP COMMAND
# Command that runs when container starts
# host 0.0.0.0 = accept connections from anywhere
# not just localhost (critical for Azure to reach your app)
# ============================================================
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]