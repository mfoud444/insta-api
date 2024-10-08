# Use Python 3.8 slim base image
FROM python:3.8-slim

# Update package list, install necessary packages and libraries
RUN apt-get update \
    && apt-get install gcc ffmpeg imagemagick -y \
    && apt-get clean

# Modify ImageMagick security policy to allow external file access
RUN sed -i 's|<policy domain="path" rights="none" pattern="@\*"/>|<!--<policy domain="path" rights="none" pattern="@*"/>-->|g' /etc/ImageMagick-6/policy.xml

# Expose port 8000 for the application
EXPOSE 8000

# Set environment variables for Python
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Copy application files to /app directory in the container
COPY . /app/

# Set the working directory
WORKDIR /app

# Install Python dependencies from requirements.txt
RUN pip install -r requirements.txt

# Command to run the application with uvicorn
CMD ["uvicorn", "main:main", "--host", "0.0.0.0", "--port", "8000", "--reload"]
