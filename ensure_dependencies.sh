#!/bin/bash
echo "Ensuring all dependencies are installed..."

# Check and install Tesseract
if ! command -v tesseract &> /dev/null; then
    echo "Installing Tesseract OCR..."
    apt-get update -qq && apt-get install -y tesseract-ocr tesseract-ocr-eng > /dev/null 2>&1
    echo "✅ Tesseract installed"
else
    echo "✅ Tesseract already installed"
fi

# Check and install Poppler (for PDF processing)
if ! command -v pdftoppm &> /dev/null; then
    echo "Installing Poppler utilities..."
    apt-get install -y poppler-utils > /dev/null 2>&1
    echo "✅ Poppler installed"
else
    echo "✅ Poppler already installed"
fi

echo "All dependencies ready!"
