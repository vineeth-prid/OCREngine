# VPS Deployment Guide - OCR Engine Platform

## 📋 Table of Contents
1. [System Requirements](#system-requirements)
2. [Initial Server Setup](#initial-server-setup)
3. [Install System Dependencies](#install-system-dependencies)
4. [Install OCR Engines](#install-ocr-engines)
5. [Install Local LLMs](#install-local-llms)
6. [Clone & Setup Application](#clone--setup-application)
7. [Database Setup](#database-setup)
8. [Configure Services](#configure-services)
9. [Nginx Configuration](#nginx-configuration)
10. [SSL Setup](#ssl-setup)
11. [Monitoring & Logs](#monitoring--logs)
12. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Specs:
- **OS:** Ubuntu 22.04 LTS or 24.04 LTS
- **RAM:** 16GB (8GB minimum, 32GB recommended for local LLMs)
- **CPU:** 4 cores (8+ recommended)
- **Storage:** 50GB SSD (100GB+ recommended)
- **Network:** Static IP address

### For Local LLMs:
- **RAM:** 32GB+ recommended
- **CPU:** 8+ cores
- **Storage:** 100GB+ (models are 5-10GB each)

---

## 1. Initial Server Setup

### Step 1.1: Connect to Your VPS
```bash
ssh root@YOUR_SERVER_IP
```

### Step 1.2: Update System
```bash
apt update && apt upgrade -y
```

### Step 1.3: Create Non-Root User
```bash
adduser ocrengine
usermod -aG sudo ocrengine
```

### Step 1.4: Setup Firewall
```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### Step 1.5: Switch to New User
```bash
su - ocrengine
```

---

## 2. Install System Dependencies

### Step 2.1: Install Python 3.11+
```bash
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
```

### Step 2.2: Install Node.js 18+
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g yarn
```

### Step 2.3: Install Build Tools
```bash
sudo apt install -y build-essential git curl wget unzip
sudo apt install -y libssl-dev libffi-dev
```

### Step 2.4: Install Image Processing Libraries
```bash
sudo apt install -y libjpeg-dev libpng-dev libtiff-dev
sudo apt install -y libopencv-dev python3-opencv
```

---

## 3. Install OCR Engines

### Step 3.1: Install Tesseract OCR
```bash
sudo apt install -y tesseract-ocr
sudo apt install -y libtesseract-dev

# Install language packs
sudo apt install -y tesseract-ocr-eng  # English
sudo apt install -y tesseract-ocr-fra  # French
sudo apt install -y tesseract-ocr-deu  # German
sudo apt install -y tesseract-ocr-spa  # Spanish

# Verify installation
tesseract --version
```

### Step 3.2: Install Poppler (PDF support)
```bash
sudo apt install -y poppler-utils
pdftoppm -v
```

### Step 3.3: Install PaddleOCR Dependencies
```bash
sudo apt install -y libgomp1
pip3 install paddlepaddle paddleocr
```

### Step 3.4: Install EasyOCR
```bash
pip3 install easyocr
```

### Step 3.5: Verify OCR Installations
```bash
# Test Tesseract
echo "Hello World" | tesseract stdin stdout

# Test with Python
python3 << EOF
import pytesseract
print("Tesseract:", pytesseract.get_tesseract_version())

from rapidocr_onnxruntime import RapidOCR
print("RapidOCR: Installed")

import paddleocr
print("PaddleOCR: Installed")

import easyocr
print("EasyOCR: Installed")
EOF
```

---

## 4. Install Local LLMs (Optional but Recommended)

### Step 4.1: Install Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version
```

### Step 4.2: Start Ollama Service
```bash
# Create systemd service
sudo tee /etc/systemd/system/ollama.service > /dev/null << EOF
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
Type=simple
User=ocrengine
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3
Environment="OLLAMA_HOST=127.0.0.1:11434"
Environment="OLLAMA_MODELS=/home/ocrengine/.ollama/models"

[Install]
WantedBy=default.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama
sudo systemctl status ollama
```

### Step 4.3: Download LLM Models
```bash
# Download Qwen2.5-7B (Recommended - Best for document extraction)
ollama pull qwen2.5:7b-instruct

# Download smaller model for faster processing
ollama pull qwen2.5:3b-instruct

# Download DeepSeek (Alternative)
ollama pull deepseek-r1:7b

# Verify models
ollama list
```

### Step 4.4: Test Local LLM
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:7b-instruct",
  "prompt": "Extract name from: John Smith, Age 30",
  "stream": false
}'
```

---

## 5. Clone & Setup Application

### Step 5.1: Clone Repository
```bash
cd ~
git clone YOUR_GITHUB_REPO_URL ocrengine-app
cd ocrengine-app
```

### Step 5.2: Setup Backend
```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install emergentintegrations
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
```

### Step 5.3: Setup Frontend
```bash
cd ../frontend

# Install dependencies
yarn install

# Build for production
yarn build
```

---

## 6. Database Setup

### Step 6.1: The Application Uses SQLite (No Extra Setup Needed)
```bash
cd ~/ocrengine-app/backend

# Create uploads directory
mkdir -p uploads

# Initialize database
python3 << EOF
from database import engine, Base
from models import *
Base.metadata.create_all(bind=engine)
print("Database initialized!")
EOF

# Create initial data
python3 init_db.py
```

### Step 6.2: Verify Database
```bash
ls -lh ocrengine.db
# Should show the database file
```

---

## 7. Configure Services

### Step 7.1: Create Environment Files

**Backend .env:**
```bash
cd ~/ocrengine-app/backend
cat > .env << 'EOF'
# Database
DATABASE_URL=sqlite:///./ocrengine.db

# JWT Secret (Generate a strong random key)
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# Emergent LLM Key (if using cloud LLMs)
EMERGENT_LLM_KEY=your-emergent-llm-key

# Or OpenAI Key
# OPENAI_API_KEY=your-openai-api-key

# Server
HOST=0.0.0.0
PORT=8001
EOF
```

**Frontend .env:**
```bash
cd ~/ocrengine-app/frontend
cat > .env << 'EOF'
REACT_APP_BACKEND_URL=https://your-domain.com
EOF
```

### Step 7.2: Create Systemd Service for Backend

```bash
sudo tee /etc/systemd/system/ocrengine-backend.service > /dev/null << 'EOF'
[Unit]
Description=OCR Engine Backend API
After=network.target

[Service]
Type=simple
User=ocrengine
WorkingDirectory=/home/ocrengine/ocrengine-app/backend
Environment="PATH=/home/ocrengine/ocrengine-app/backend/venv/bin"
ExecStart=/home/ocrengine/ocrengine-app/backend/venv/bin/python -m uvicorn server:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable ocrengine-backend
sudo systemctl start ocrengine-backend
sudo systemctl status ocrengine-backend
```

---

## 8. Nginx Configuration

### Step 8.1: Install Nginx
```bash
sudo apt install -y nginx
```

### Step 8.2: Configure Nginx
```bash
sudo tee /etc/nginx/sites-available/ocrengine > /dev/null << 'EOF'
upstream backend {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Frontend (React build)
    location / {
        root /home/ocrengine/ocrengine-app/frontend/build;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeouts for processing
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
    }

    # File upload size limit
    client_max_body_size 50M;
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/ocrengine /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

---

## 9. SSL Setup (Let's Encrypt)

### Step 9.1: Install Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Step 9.2: Obtain SSL Certificate
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### Step 9.3: Auto-renewal
```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot auto-renewal is set up via systemd timer
sudo systemctl status certbot.timer
```

---

## 10. Monitoring & Logs

### Step 10.1: View Logs
```bash
# Backend logs
sudo journalctl -u ocrengine-backend -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Ollama logs
sudo journalctl -u ollama -f
```

### Step 10.2: Install Monitoring (Optional)
```bash
# Install htop for system monitoring
sudo apt install -y htop

# Monitor resources
htop
```

---

## 11. Update & Maintenance

### Update Application
```bash
cd ~/ocrengine-app

# Pull latest code
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Update frontend
cd ../frontend
yarn install
yarn build

# Restart services
sudo systemctl restart ocrengine-backend
sudo systemctl reload nginx
```

### Backup Database
```bash
# Create backup script
cat > ~/backup_db.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$HOME/backups"
mkdir -p $BACKUP_DIR

# Backup database
cp ~/ocrengine-app/backend/ocrengine.db $BACKUP_DIR/ocrengine_$DATE.db

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz ~/ocrengine-app/backend/uploads

# Keep only last 7 days
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x ~/backup_db.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * $HOME/backup_db.sh") | crontab -
```

---

## 12. Troubleshooting

### Backend Not Starting
```bash
# Check logs
sudo journalctl -u ocrengine-backend -n 100

# Check if port is in use
sudo netstat -tulpn | grep 8001

# Restart service
sudo systemctl restart ocrengine-backend
```

### Ollama Not Responding
```bash
# Check status
sudo systemctl status ollama

# Check logs
sudo journalctl -u ollama -n 50

# Restart
sudo systemctl restart ollama
```

### Database Errors
```bash
# Check permissions
ls -l ~/ocrengine-app/backend/ocrengine.db

# Fix permissions
chmod 664 ~/ocrengine-app/backend/ocrengine.db
```

### OCR Errors
```bash
# Verify Tesseract
which tesseract
tesseract --version

# Verify Poppler
which pdftoppm
```

---

## 🎯 Quick Start Checklist

- [ ] Server updated and secured
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] Tesseract OCR installed
- [ ] Poppler utils installed
- [ ] PaddleOCR installed
- [ ] EasyOCR installed
- [ ] Ollama installed (optional)
- [ ] LLM models downloaded (optional)
- [ ] Repository cloned
- [ ] Backend dependencies installed
- [ ] Frontend built
- [ ] Database initialized
- [ ] Environment files configured
- [ ] Systemd services created
- [ ] Nginx configured
- [ ] SSL certificate obtained
- [ ] Services running

---

## 🔒 Security Recommendations

1. **Change default secrets** in `.env` files
2. **Setup firewall rules** properly
3. **Keep system updated** regularly
4. **Use strong passwords**
5. **Enable fail2ban** for SSH protection
6. **Regular backups** of database and uploads
7. **Monitor logs** for suspicious activity
8. **Use HTTPS only** (SSL certificate)

---

## 📞 Support

If you encounter issues:
1. Check logs: `sudo journalctl -u ocrengine-backend -f`
2. Verify services: `sudo systemctl status ocrengine-backend`
3. Test endpoints: `curl http://localhost:8001/api/health`
4. Check Nginx: `sudo nginx -t`

---

**Next:** After deployment, test the application and configure LLM preferences in the Admin Panel!
