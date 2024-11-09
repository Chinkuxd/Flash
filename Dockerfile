# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /Flash

# Copy the current directory contents into the container at /app
COPY . .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run the application with gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app"]
