#!/bin/bash
echo "Starting all OCR Engine services..."

# Start PostgreSQL
echo "Starting PostgreSQL..."
/etc/init.d/postgresql start
sleep 3

# Start Redis
echo "Starting Redis..."
redis-server --daemonize yes
sleep 2

# Restart all supervisor services
echo "Restarting supervisor services..."
supervisorctl restart all

echo "All services started!"
supervisorctl status
