#!/bin/bash

# OCR Engine Platform - Deployment Script
# Run this script on your VPS after cloning the repository

set -e

echo "==========================================="
echo "OCR Engine Platform - Automated Deployment"
echo "==========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Please do not run as root. Run as a regular user with sudo privileges.${NC}"
    exit 1
fi

# Get domain name
read -p "Enter your domain name (e.g., ocrengine.example.com): " DOMAIN_NAME

# Get email for SSL
read -p "Enter your email for SSL certificate: " SSL_EMAIL

# Ask about LLM key
read -p "Do you have an Emergent LLM key? (y/n): " HAS_LLM_KEY
if [ "$HAS_LLM_KEY" = "y" ]; then
    read -p "Enter your Emergent LLM key: " LLM_KEY
else
    LLM_KEY=""
fi

echo ""
echo "=== Step 1: Updating System ==="
sudo apt update && sudo apt upgrade -y

echo ""
echo "=== Step 2: Installing System Dependencies ==="
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
sudo apt install -y build-essential git curl wget unzip
sudo apt install -y libssl-dev libffi-dev libjpeg-dev libpng-dev libtiff-dev
sudo apt install -y nginx certbot python3-certbot-nginx

echo ""
echo "=== Step 3: Installing Node.js ==="
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g yarn

echo ""
echo "=== Step 4: Installing OCR Dependencies ==="
sudo apt install -y tesseract-ocr libtesseract-dev poppler-utils
sudo apt install -y tesseract-ocr-eng tesseract-ocr-fra tesseract-ocr-deu tesseract-ocr-spa
sudo apt install -y libgomp1 libopencv-dev python3-opencv

echo ""
echo "=== Step 5: Installing Ollama (Local LLM) ==="
curl -fsSL https://ollama.com/install.sh | sh

echo ""
echo "=== Step 6: Setting up Backend ==="
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install OCR libraries
pip install paddlepaddle paddleocr easyocr

# Install emergent integrations
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/

# Generate secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Create .env file
cat > .env << EOF
DATABASE_URL=sqlite:///./ocrengine.db
SECRET_KEY=$SECRET_KEY
HOST=0.0.0.0
PORT=8001
EOF

if [ -n "$LLM_KEY" ]; then
    echo "EMERGENT_LLM_KEY=$LLM_KEY" >> .env
fi

# Create uploads directory
mkdir -p uploads

# Initialize database
python3 << PYEOF
from database import engine, Base
from models import *
Base.metadata.create_all(bind=engine)
print("Database initialized!")
PYEOF

# Create initial data
python3 init_db.py

deactivate

echo ""
echo "=== Step 7: Setting up Frontend ==="
cd ../frontend

# Create .env file
echo "REACT_APP_BACKEND_URL=https://$DOMAIN_NAME" > .env

# Install dependencies and build
yarn install
yarn build

echo ""
echo "=== Step 8: Creating Systemd Services ==="
cd ~

# Backend service
sudo tee /etc/systemd/system/ocrengine-backend.service > /dev/null << EOF
[Unit]
Description=OCR Engine Backend API
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PWD/ocrengine-app/backend
Environment="PATH=$PWD/ocrengine-app/backend/venv/bin"
ExecStart=$PWD/ocrengine-app/backend/venv/bin/python -m uvicorn server:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Ollama service
sudo tee /etc/systemd/system/ollama.service > /dev/null << EOF
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3
Environment="OLLAMA_HOST=127.0.0.1:11434"
Environment="OLLAMA_MODELS=$HOME/.ollama/models"

[Install]
WantedBy=default.target
EOF

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable ocrengine-backend
sudo systemctl enable ollama
sudo systemctl start ocrengine-backend
sudo systemctl start ollama

echo ""
echo "=== Step 9: Configuring Nginx ==="
sudo tee /etc/nginx/sites-available/ocrengine > /dev/null << EOF
upstream backend {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name $DOMAIN_NAME;

    location / {
        root $PWD/ocrengine-app/frontend/build;
        try_files \$uri \$uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }

    client_max_body_size 50M;
}
EOF

sudo ln -sf /etc/nginx/sites-available/ocrengine /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

sudo nginx -t
sudo systemctl restart nginx

echo ""
echo "=== Step 10: Setting up SSL Certificate ==="
sudo certbot --nginx -d $DOMAIN_NAME --email $SSL_EMAIL --agree-tos --non-interactive

echo ""
echo "=== Step 11: Downloading LLM Models (Optional) ==="
read -p "Download Qwen2.5-7B model? (recommended, 4.7GB) (y/n): " DOWNLOAD_MODEL
if [ "$DOWNLOAD_MODEL" = "y" ]; then
    ollama pull qwen2.5:7b-instruct
    echo -e "${GREEN}Model downloaded successfully!${NC}"
fi

echo ""
echo "=== Step 12: Setting up Firewall ==="
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow OpenSSH
sudo ufw --force enable

echo ""
echo "==========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "==========================================="
echo ""
echo "Your OCR Engine Platform is now running at:"
echo -e "${GREEN}https://$DOMAIN_NAME${NC}"
echo ""
echo "Default admin credentials:"
echo "  Email: admin@ocrengine.com"
echo "  Password: SecurePass123!"
echo ""
echo "Next steps:"
echo "1. Change admin password"
echo "2. Configure LLM settings in Admin Panel"
echo "3. Test document upload and processing"
echo ""
echo "Useful commands:"
echo "  Check backend status: sudo systemctl status ocrengine-backend"
echo "  View backend logs: sudo journalctl -u ocrengine-backend -f"
echo "  Check Ollama status: sudo systemctl status ollama"
echo "  View Nginx logs: sudo tail -f /var/log/nginx/error.log"
echo ""
echo "Documentation:"
echo "  Deployment Guide: ~/ocrengine-app/DEPLOYMENT_GUIDE.md"
echo "  OCR/LLM Setup: ~/ocrengine-app/OCR_LLM_SETUP_GUIDE.md"
echo ""
