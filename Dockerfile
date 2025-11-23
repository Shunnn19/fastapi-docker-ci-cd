FROM python:3.11-slim

# Create a non-root user for safety
RUN groupadd -r app && useradd --no-log-init -r -g app app

WORKDIR /app

# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt ./

# Install build dependencies, install runtime packages, then clean up
RUN apt-get update \
	&& apt-get install -y --no-install-recommends gcc libffi-dev \
	&& pip install --upgrade pip \
	&& pip install --no-cache-dir -r requirements.txt \
	&& apt-get purge -y --auto-remove gcc \
	&& rm -rf /var/lib/apt/lists/*

# Copy the application
COPY . /app

# Run as non-root user
USER app

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
