# Use an official Python runtime as a parent image
FROM python:3.11 as base
WORKDIR /app
COPY . /app/

USER root

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make the entrypoint script executable
RUN chmod +x /app/main.py

# Start the Python program
CMD ["python", "-u", "/app/main.py"]
