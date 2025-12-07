# System Dependencies

This application requires the following system packages to be installed:

## Required Packages

### 1. Tesseract OCR
```bash
apt-get install -y tesseract-ocr
```

**Purpose:** OCR engine for text extraction from images and PDFs
**Location:** `/usr/bin/tesseract`
**Verification:** `tesseract --version`

### 2. Poppler Utils
```bash
apt-get install -y poppler-utils
```

**Purpose:** PDF rendering utilities (converts PDF to images for OCR processing)
**Key Tool:** `pdftoppm`
**Verification:** `which pdftoppm`

## Installation Commands

For a fresh environment, run:
```bash
apt-get update
apt-get install -y tesseract-ocr poppler-utils
```

## Python Dependencies

The following Python packages are required (already in `requirements.txt`):
- `pdf2image==1.17.0` - Python wrapper for poppler
- `pytesseract==0.3.13` - Python wrapper for Tesseract
- `rapidocr-onnxruntime==1.4.4` - Fast OCR alternative

## Troubleshooting

### Issue: "tesseract is not installed or it's not in your PATH"
**Solution:** Install tesseract-ocr package

### Issue: "Unable to get page count. Is poppler installed and in PATH?"
**Solution:** Install poppler-utils package

### Issue: "cannot identify image file"
**Solution:** Ensure both tesseract and poppler-utils are installed, and PDFs are being converted to images before OCR processing
