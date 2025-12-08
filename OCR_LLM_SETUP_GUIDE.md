# Complete OCR & LLM Setup Guide

## 🎯 Overview

This guide covers setting up ALL OCR engines and LLM models for maximum reliability and accuracy in production.

---

## 📊 OCR Engines Comparison

| Engine | Speed | Accuracy | Languages | Use Case |
|--------|-------|----------|-----------|----------|
| **Tesseract** | Fast | Good | 100+ | General purpose, good for clean docs |
| **RapidOCR** | Very Fast | Good | Multi | Fast processing, decent accuracy |
| **PaddleOCR** | Fast | Excellent | 80+ | Chinese, multi-language documents |
| **EasyOCR** | Slow | Excellent | 80+ | Handwriting, complex layouts |

---

## 1. Tesseract OCR Setup (Already Installed)

### Installation
```bash
sudo apt install -y tesseract-ocr libtesseract-dev
```

### Install Additional Language Packs
```bash
# European Languages
sudo apt install -y tesseract-ocr-fra  # French
sudo apt install -y tesseract-ocr-deu  # German
sudo apt install -y tesseract-ocr-spa  # Spanish
sudo apt install -y tesseract-ocr-ita  # Italian
sudo apt install -y tesseract-ocr-por  # Portuguese

# Asian Languages
sudo apt install -y tesseract-ocr-chi-sim  # Simplified Chinese
sudo apt install -y tesseract-ocr-chi-tra  # Traditional Chinese
sudo apt install -y tesseract-ocr-jpn  # Japanese
sudo apt install -y tesseract-ocr-kor  # Korean

# Other Languages
sudo apt install -y tesseract-ocr-ara  # Arabic
sudo apt install -y tesseract-ocr-hin  # Hindi
sudo apt install -y tesseract-ocr-rus  # Russian
```

### Verify Languages
```bash
tesseract --list-langs
```

### Test Tesseract
```bash
# Create test image
convert -size 300x100 xc:white \
  -pointsize 24 -fill black \
  -gravity center -annotate +0+0 "Hello World" \
  test.png

# Run OCR
tesseract test.png stdout
```

### Configuration File
```bash
# Create custom Tesseract config
sudo tee /etc/tesseract/configs/ocr_engine << 'EOF'
# OCR Engine Custom Config
tessedit_char_whitelist 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,;:!?-()[]{}/@#$%&*
tessedit_pageseg_mode 3
oem 1
EOF
```

---

## 2. RapidOCR Setup (Already Installed)

### Installation
```bash
pip install rapidocr-onnxruntime
```

### Test RapidOCR
```bash
python3 << 'EOF'
from rapidocr_onnxruntime import RapidOCR

# Initialize
ocr = RapidOCR()

# Test with image
result, elapse = ocr('test.png')

if result:
    for line in result:
        print(f"Text: {line[1]}, Confidence: {line[2]:.2f}")
else:
    print("No text detected")
EOF
```

---

## 3. PaddleOCR Setup

### Step 3.1: Install PaddlePaddle
```bash
# For CPU version
pip install paddlepaddle

# For GPU version (if you have CUDA)
# pip install paddlepaddle-gpu
```

### Step 3.2: Install PaddleOCR
```bash
pip install paddleocr
```

### Step 3.3: Download Models
```bash
# Models are downloaded automatically on first use
# Pre-download to save time
python3 << 'EOF'
from paddleocr import PaddleOCR

# Initialize (downloads models)
ocr = PaddleOCR(use_angle_cls=True, lang='en')
print("English model downloaded")

# Download multilingual model
ocr = PaddleOCR(use_angle_cls=True, lang='ch')
print("Chinese model downloaded")
EOF
```

### Step 3.4: Test PaddleOCR
```bash
python3 << 'EOF'
from paddleocr import PaddleOCR
import cv2

# Initialize
ocr = PaddleOCR(use_angle_cls=True, lang='en')

# Read image
img_path = 'test.png'
result = ocr.ocr(img_path, cls=True)

# Print results
for line in result[0]:
    text = line[1][0]
    confidence = line[1][1]
    print(f"Text: {text}, Confidence: {confidence:.2f}")
EOF
```

### Step 3.5: PaddleOCR Language Support
```bash
# Available languages:
# 'ch', 'en', 'fr', 'german', 'korean', 'japan'
# 'chinese_cht', 'ta', 'te', 'ka', 'latin', 'arabic',
# 'cyrillic', 'devanagari'

# Download specific language
python3 -c "from paddleocr import PaddleOCR; PaddleOCR(lang='french')"
```

---

## 4. EasyOCR Setup

### Step 4.1: Install EasyOCR
```bash
pip install easyocr
```

### Step 4.2: Download Models
```bash
python3 << 'EOF'
import easyocr

# Initialize with languages (downloads models)
reader = easyocr.Reader(['en'])
print("English model downloaded")

# Multi-language
reader = easyocr.Reader(['en', 'fr', 'de', 'es'])
print("Multi-language models downloaded")
EOF
```

### Step 4.3: Test EasyOCR
```bash
python3 << 'EOF'
import easyocr

# Initialize
reader = easyocr.Reader(['en'])

# Read image
result = reader.readtext('test.png')

# Print results
for detection in result:
    bbox, text, confidence = detection
    print(f"Text: {text}, Confidence: {confidence:.2f}")
EOF
```

### Step 4.4: EasyOCR Language Codes
```
Common languages:
- 'en' (English)
- 'fr' (French)
- 'de' (German)
- 'es' (Spanish)
- 'it' (Italian)
- 'pt' (Portuguese)
- 'ru' (Russian)
- 'ar' (Arabic)
- 'hi' (Hindi)
- 'zh' (Chinese Simplified)
- 'ja' (Japanese)
- 'ko' (Korean)
```

---

## 5. Update OCR Engine Code

### Update `/app/backend/ocr_engines.py`

Add methods for PaddleOCR and EasyOCR:

```python
def run_paddleocr(self, image_path: str) -> Dict:
    """Run PaddleOCR"""
    try:
        from paddleocr import PaddleOCR
        start_time = time.time()
        
        # Handle PDF conversion
        if image_path.lower().endswith('.pdf'):
            image_path = self.convert_pdf_to_image(image_path)
        
        # Initialize PaddleOCR
        ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
        
        # Run OCR
        result = ocr.ocr(image_path, cls=True)
        
        # Extract text and confidence
        text_lines = []
        confidences = []
        
        if result and result[0]:
            for line in result[0]:
                text = line[1][0]
                confidence = line[1][1]
                text_lines.append(text)
                confidences.append(confidence)
        
        full_text = '\n'.join(text_lines)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        processing_time = time.time() - start_time
        
        return {
            'engine': 'paddleocr',
            'text': full_text,
            'confidence': avg_confidence,
            'processing_time': processing_time,
            'word_count': len(full_text.split())
        }
        
    except Exception as e:
        print(f"PaddleOCR error: {e}")
        return {
            'engine': 'paddleocr',
            'text': '',
            'confidence': 0.0,
            'processing_time': 0,
            'error': str(e)
        }

def run_easyocr(self, image_path: str) -> Dict:
    """Run EasyOCR"""
    try:
        import easyocr
        start_time = time.time()
        
        # Handle PDF conversion
        if image_path.lower().endswith('.pdf'):
            image_path = self.convert_pdf_to_image(image_path)
        
        # Initialize EasyOCR
        if not hasattr(self, 'easyocr_reader'):
            self.easyocr_reader = easyocr.Reader(['en'])
        
        # Run OCR
        result = self.easyocr_reader.readtext(image_path)
        
        # Extract text and confidence
        text_lines = []
        confidences = []
        
        for detection in result:
            bbox, text, confidence = detection
            text_lines.append(text)
            confidences.append(confidence)
        
        full_text = '\n'.join(text_lines)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        processing_time = time.time() - start_time
        
        return {
            'engine': 'easyocr',
            'text': full_text,
            'confidence': avg_confidence,
            'processing_time': processing_time,
            'word_count': len(full_text.split())
        }
        
    except Exception as e:
        print(f"EasyOCR error: {e}")
        return {
            'engine': 'easyocr',
            'text': '',
            'confidence': 0.0,
            'processing_time': 0,
            'error': str(e)
        }
```

Update `process_with_routing` to include all engines:

```python
def process_with_routing(self, file_path: str) -> Dict:
    """Process with intelligent routing across all OCR engines"""
    
    # Run all OCR engines
    results = {
        'tesseract': self.run_tesseract(file_path),
        'rapidocr': self.run_rapidocr(file_path),
        'paddleocr': self.run_paddleocr(file_path),
        'easyocr': self.run_easyocr(file_path)
    }
    
    # Select best result based on confidence
    best_result = max(results.values(), key=lambda x: x['confidence'])
    
    return {
        'best_result': best_result,
        'all_results': results
    }
```

---

## 6. Local LLM Setup (Ollama)

### Step 6.1: Install Ollama (Already Done)
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 6.2: Download Recommended Models

**For Document Extraction (Recommended):**
```bash
# Qwen2.5-7B - Best for structured data extraction
ollama pull qwen2.5:7b-instruct

# Smaller, faster version
ollama pull qwen2.5:3b-instruct

# Larger, more accurate version
ollama pull qwen2.5:14b-instruct
```

**For Reasoning & Complex Documents:**
```bash
# DeepSeek R1 - Excellent reasoning
ollama pull deepseek-r1:7b

# Mistral - Good general purpose
ollama pull mistral:7b-instruct
```

**For Multilingual Documents:**
```bash
# Qwen supports 29 languages including Chinese
ollama pull qwen2.5:7b-instruct

# LLaMA 3 with multilingual support
ollama pull llama3:8b-instruct
```

### Step 6.3: Test Models
```bash
# Test Qwen
ollama run qwen2.5:7b-instruct "Extract name and amount from: Invoice to John Smith for $500"

# Test DeepSeek
ollama run deepseek-r1:7b "Extract invoice number from: Invoice #INV-2025-001"
```

### Step 6.4: Model Comparison

| Model | Size | Speed | Accuracy | Best For |
|-------|------|-------|----------|----------|
| **Qwen2.5-3B** | 1.9GB | Very Fast | 82-88% | Simple forms, fast processing |
| **Qwen2.5-7B** | 4.7GB | Fast | 85-90% | **Recommended** - General purpose |
| **Qwen2.5-14B** | 8.5GB | Medium | 88-93% | Complex documents, high accuracy |
| **DeepSeek-R1** | 4.7GB | Fast | 87-92% | Reasoning, validation |
| **Mistral-7B** | 4.1GB | Fast | 83-89% | General purpose |

---

## 7. Configure Application to Use All Engines

### Update Admin Panel LLM Config

In Admin Panel → LLM Management:

1. **Local Model Selection:**
   - Primary: `qwen2.5:7b-instruct`
   - Fallback: `qwen2.5:3b-instruct`

2. **OCR Engine Priority:**
   - High quality: EasyOCR
   - Fast processing: RapidOCR
   - General: Tesseract
   - Multilingual: PaddleOCR

### Create Configuration File

```bash
cat > ~/ocrengine-app/backend/config.yml << 'EOF'
ocr_engines:
  enabled:
    - tesseract
    - rapidocr
    - paddleocr
    - easyocr
  
  routing:
    high_quality: easyocr
    fast: rapidocr
    general: tesseract
    multilingual: paddleocr
  
  confidence_thresholds:
    minimum: 0.7
    high: 0.9

llm_models:
  local:
    enabled: true
    primary: "qwen2.5:7b-instruct"
    fallback: "qwen2.5:3b-instruct"
  
  cloud:
    enabled: true
    simple_docs: "gpt-4.1-mini"
    complex_docs: "gpt-4.1"
  
  routing:
    use_local_first: true
    cloud_fallback_on_low_confidence: true
    confidence_threshold: 0.8
EOF
```

---

## 8. Performance Optimization

### GPU Acceleration (If Available)

```bash
# Check for NVIDIA GPU
nvidia-smi

# Install CUDA-enabled versions
pip install paddlepaddle-gpu
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Memory Optimization

```bash
# For systems with limited RAM, use smaller models
ollama pull qwen2.5:3b-instruct  # Only 1.9GB

# Set Ollama memory limit
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_NUM_PARALLEL=1
```

---

## 9. Testing All Engines

### Create Comprehensive Test Script

```bash
cat > ~/test_ocr_llm.py << 'EOF'
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/ocrengine/ocrengine-app/backend')

from ocr_engines import OCREngine
from llm_processor import LLMProcessor
import time

def test_ocr():
    print("=" * 60)
    print("Testing OCR Engines")
    print("=" * 60)
    
    ocr = OCREngine()
    test_file = 'test.png'
    
    # Test all engines
    engines = ['tesseract', 'rapidocr', 'paddleocr', 'easyocr']
    
    for engine_name in engines:
        try:
            print(f"\n{engine_name.upper()}:")
            method = getattr(ocr, f'run_{engine_name}')
            result = method(test_file)
            print(f"  Confidence: {result['confidence']*100:.1f}%")
            print(f"  Time: {result['processing_time']:.2f}s")
            print(f"  Text: {result['text'][:50]}...")
        except Exception as e:
            print(f"  ❌ Error: {e}")

def test_llm():
    print("\n" + "=" * 60)
    print("Testing LLM Models")
    print("=" * 60)
    
    llm = LLMProcessor()
    
    # Test local model
    if llm.check_local_model_available():
        print("\n✅ Local LLM Available")
    else:
        print("\n❌ Local LLM Not Available")
    
    # Test cloud model
    if llm.emergent_llm_key:
        print("✅ Cloud LLM Configured")
    else:
        print("❌ Cloud LLM Not Configured")

if __name__ == "__main__":
    test_ocr()
    test_llm()
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
EOF

chmod +x ~/test_ocr_llm.py
python3 ~/test_ocr_llm.py
```

---

## 10. Production Recommendations

### For Maximum Reliability:

1. **OCR Strategy:**
   - Use **RapidOCR** for initial processing (fast)
   - Fall back to **EasyOCR** if confidence < 80%
   - Use **PaddleOCR** for Asian languages

2. **LLM Strategy:**
   - Use **Qwen2.5-7B** locally for 70% of documents
   - Fall back to **GPT-4.1-mini** for low confidence
   - Use **GPT-4.1** only for complex documents

3. **Cost Optimization:**
   - Local LLM: $0/doc (uses server resources)
   - Cloud mini: ~$0.001/doc
   - Cloud full: ~$0.01/doc
   - **Target:** 70% local, 20% mini, 10% full = ~$0.003/doc average

---

## 📊 Summary

**OCR Engines Installed:**
- ✅ Tesseract (100+ languages)
- ✅ RapidOCR (fast, decent accuracy)
- ✅ PaddleOCR (excellent for Chinese)
- ✅ EasyOCR (best for handwriting)

**LLM Models Available:**
- ✅ Qwen2.5-7B (recommended)
- ✅ DeepSeek-R1 (reasoning)
- ✅ Cloud LLMs (fallback)

**Next Steps:**
1. Test all engines with your documents
2. Configure routing in Admin Panel
3. Monitor accuracy and costs
4. Adjust thresholds as needed

---

**🎯 Result:** Your OCR Engine platform now has 4 OCR engines and multiple LLM options for maximum reliability and accuracy!
