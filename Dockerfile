# Use the official Python image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy project files
COPY . /app

# Set Python path to structure folder
ENV PYTHONPATH="/app/structure"

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Expose Django's port
EXPOSE 8000

# Run migrations and start Django server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
