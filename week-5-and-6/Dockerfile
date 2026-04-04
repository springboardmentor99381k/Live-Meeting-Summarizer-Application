# Use a lightweight Python base image
FROM python:3.11-slim

# Prevent Python from writing pyc files to disk and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies including FFmpeg and PortAudio
# We do this as root before switching users
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    libportaudio2 \
    && rm -rf /var/lib/apt/lists/*

# Set up a new user named "user" with user ID 1000 for Hugging Face Spaces
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set the working directory
WORKDIR $HOME/app

# First, install the CPU-only version of PyTorch to save massive amounts of space & time
# This stops pip from downloading the 3GB GPU version
RUN pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# Copy the requirements file and install the rest of the dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY --chown=user server.py backend.py ./

# Expose the port Hugging Face Spaces uses by default
EXPOSE 7860

# Command to run the FastAPI application on Hugging Face's required port mapping
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860"]
