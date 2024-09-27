# Use the official Python runtime as the base image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot code to the working directory
COPY *.py .
COPY lib lib

# Run the bot when the container starts
CMD ["python", "bot.py"]