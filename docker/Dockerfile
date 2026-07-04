FROM mcr.microsoft.com/dotnet/runtime-deps:8.0-bookworm-slim

# Install Nginx and other utilities
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx curl unzip tar && \
    rm -rf /var/lib/apt/lists/*

# Set up working directory for backend
WORKDIR /app

# Download and extract C# backend Release v1.0.1
RUN curl -L -o backend.tar.gz https://github.com/Lixeer/hmBackend/releases/download/v1.0.1/patient-monitor-backend-linux-x64.tar.gz && \
    tar -xzvf backend.tar.gz && \
    rm backend.tar.gz && \
    chmod +x PatientMonitor.Api

# Download and extract Frontend Release v1.0.1
RUN mkdir -p /usr/share/nginx/html && \
    curl -L -o frontend.zip https://github.com/Lixeer/hmFront/releases/download/v1.0.1/patient-monitor-frontend.zip && \
    unzip frontend.zip -d /usr/share/nginx/html && \
    rm frontend.zip

# Copy configuration files
COPY default.nginx /etc/nginx/sites-available/default
COPY entrypoint.sh /app/entrypoint.sh

# Ensure script is executable and uses Unix line endings (in case built on Windows)
RUN sed -i 's/\r$//' /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Expose standard HTTP port
EXPOSE 80

# Start backend and frontend
ENTRYPOINT ["/app/entrypoint.sh"]
