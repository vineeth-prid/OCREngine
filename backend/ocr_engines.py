import pytesseract
from rapidocr_onnxruntime import RapidOCR
from PIL import Image
import cv2
import numpy as np
from typing import Dict, Tuple, List
import time
import os
from pdf2image import convert_from_path

class OCREngine:
    def __init__(self):
        self.rapid_ocr = RapidOCR()
    
    def convert_pdf_to_image(self, pdf_path: str) -> str:
        """Convert PDF first page to image"""
        try:
            # Convert with higher DPI for better OCR quality
            images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=300)
            if images:
                # Save as temporary image
                image_path = pdf_path.replace('.pdf', '_page1.jpg')
                images[0].save(image_path, 'JPEG', quality=95)
                return image_path
            else:
                raise Exception("No images extracted from PDF")
        except Exception as e:
            print(f"PDF conversion error: {e}")
            raise Exception(f"Failed to convert PDF to image: {str(e)}")
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for better OCR results"""
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # Binarization
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def assess_quality(self, image_path: str) -> float:
        """Assess image quality (0-1 score)"""
        try:
            # Convert PDF to image if needed
            if image_path.lower().endswith('.pdf'):
                return 0.75  # Default quality for PDFs
            
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            
            if img is None or img.size == 0:
                return 0.5  # Default medium quality if can't read
            
            # Calculate variance of Laplacian (blur detection)
            laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
            
            # Normalize to 0-1 scale (higher is better)
            quality_score = min(laplacian_var / 1000, 1.0)
            
            return quality_score
        except Exception as e:
            print(f"Quality assessment error: {e}")
            return 0.5  # Default medium quality on error
    
    def run_tesseract(self, image_path: str) -> Dict:
        """Run Tesseract OCR"""
        start_time = time.time()
        
        # Set tesseract path
        pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
        
        img = Image.open(image_path)
        
        # Get text with confidence
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        
        # Extract text and calculate average confidence
        texts = []
        confidences = []
        bounding_boxes = []
        
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 0:
                texts.append(data['text'][i])
                confidences.append(int(data['conf'][i]))
                bounding_boxes.append({
                    'x': data['left'][i],
                    'y': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i],
                    'text': data['text'][i]
                })
        
        full_text = ' '.join(texts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        processing_time = time.time() - start_time
        
        return {
            'engine': 'tesseract',
            'text': full_text,
            'confidence': avg_confidence / 100,  # Normalize to 0-1
            'bounding_boxes': bounding_boxes,
            'processing_time': processing_time
        }
    
    def run_rapidocr(self, image_path: str) -> Dict:
        """Run RapidOCR"""
        start_time = time.time()
        
        result, elapse = self.rapid_ocr(image_path)
        
        if result:
            texts = [item[1] for item in result]
            confidences = [item[2] for item in result]
            bounding_boxes = [{
                'points': item[0],
                'text': item[1],
                'confidence': item[2]
            } for item in result]
            
            full_text = ' '.join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        else:
            full_text = ''
            avg_confidence = 0
            bounding_boxes = []
        
        processing_time = time.time() - start_time
        
        return {
            'engine': 'rapidocr',
            'text': full_text,
            'confidence': avg_confidence,
            'bounding_boxes': bounding_boxes,
            'processing_time': processing_time
        }
    
    def run_paddleocr(self, image_path: str) -> Dict:
        """Run PaddleOCR (mock for now to save resources)"""
        # Mock implementation - in production, use actual PaddleOCR
        return {
            'engine': 'paddleocr',
            'text': '[PaddleOCR - Not initialized to save resources]',
            'confidence': 0.0,
            'bounding_boxes': [],
            'processing_time': 0.0
        }
    
    def process_with_routing(self, image_path: str) -> Dict:
        """Process image with intelligent OCR routing"""
        # Convert PDF to image if needed
        if image_path.lower().endswith('.pdf'):
            image_path = self.convert_pdf_to_image(image_path)
        
        quality_score = self.assess_quality(image_path)
        
        results = []
        
        if quality_score > 0.85:
            # High quality: use RapidOCR + Tesseract
            results.append(self.run_rapidocr(image_path))
            results.append(self.run_tesseract(image_path))
        elif quality_score > 0.60:
            # Medium quality: use Tesseract + RapidOCR
            results.append(self.run_tesseract(image_path))
            results.append(self.run_rapidocr(image_path))
        else:
            # Low quality: use all engines
            results.append(self.run_tesseract(image_path))
            results.append(self.run_rapidocr(image_path))
            results.append(self.run_paddleocr(image_path))
        
        # Select best result
        best_result = max(results, key=lambda x: x['confidence'])
        
        return {
            'quality_score': quality_score,
            'engines_used': [r['engine'] for r in results],
            'best_result': best_result,
            'all_results': results
        }