# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
# We selectively copy to avoid unnecessary files if .dockerignore isn't present, 
# but for simplicity in this project structure, we can copy the relevant folders.
COPY backend/ ./backend/
COPY frontend/ ./frontend/
# COPY database.json . (Removed: Database is auto-created or persistent volume used)

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run gunicorn
# Note: We run from /app, so 'backend.server' is the module path.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "backend.server:app"]
