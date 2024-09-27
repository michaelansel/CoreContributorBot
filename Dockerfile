# Use the official Python runtime as the base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the entire repository to the working directory
COPY . .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Run the bot when the container starts
CMD ["python", "bot.py"]