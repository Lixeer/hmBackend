#!/bin/bash
# Start backend in background
echo "Starting Patient Monitor Backend..."
cd /app
./PatientMonitor.Api --urls "http://127.0.0.1:8080" &
BACKEND_PID=$!

# Start Nginx in foreground
echo "Starting Nginx..."
nginx -g "daemon off;" &
NGINX_PID=$!

# Handle shutdown signals gracefully
trap "kill -TERM $BACKEND_PID $NGINX_PID" SIGINT SIGTERM

# Wait for both processes
wait
