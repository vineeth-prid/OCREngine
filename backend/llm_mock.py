import json
from typing import Dict, List, Any
import random
import time

class LLMProcessor:
    """Mock LLM processor - will be replaced with actual models"""
    
    def __init__(self):
        self.models = ['deepseek', 'qwen', 'mistral', 'qwen-vl']
    
    def normalize_text(self, text: str, field_type: str) -> str:
        """Mock text normalization"""
        # Simulate processing time
        time.sleep(0.1)
        
        # Simple mock normalization
        if field_type == 'date':
            return '2025-12-07'
        elif field_type == 'number':
            # Extract numbers
            import re
            numbers = re.findall(r'\d+\.?\d*', text)
            return numbers[0] if numbers else '0'
        elif field_type == 'email':
            # Extract email pattern
            import re
            emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
            return emails[0] if emails else ''
        else:
            return text.strip()
    
    def extract_fields(self, text: str, schema_fields: List[Dict]) -> Dict[str, Any]:
        """Mock field extraction using LLM"""
        time.sleep(0.2)
        
        extracted = {}
        
        for field in schema_fields:
            field_name = field['field_name']
            field_type = field['field_type']
            
            # Mock extraction
            if field_type == 'text':
                extracted[field_name] = f"[Mock extracted: {field_name}]"
            elif field_type == 'number':
                extracted[field_name] = str(random.randint(100, 999))
            elif field_type == 'date':
                extracted[field_name] = '2025-12-07'
            elif field_type == 'email':
                extracted[field_name] = 'mock@example.com'
            else:
                extracted[field_name] = f"[{field_type}]"
            
            extracted[f"{field_name}_confidence"] = random.uniform(0.7, 0.95)
        
        return extracted
    
    def validate_consistency(self, field_values: Dict[str, Any]) -> Dict[str, Any]:
        """Mock consistency validation"""
        time.sleep(0.1)
        
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Mock validation logic
        for field_name, value in field_values.items():
            if not field_name.endswith('_confidence'):
                if not value or value == '':
                    validation_result['warnings'].append(
                        f"Field '{field_name}' is empty"
                    )
        
        return validation_result
    
    def process_with_model(self, model_name: str, text: str, schema_fields: List[Dict]) -> Dict:
        """Process text with specific LLM model (mock)"""
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")
        
        start_time = time.time()
        
        extracted = self.extract_fields(text, schema_fields)
        validation = self.validate_consistency(extracted)
        
        processing_time = time.time() - start_time
        
        return {
            'model': model_name,
            'extracted_fields': extracted,
            'validation': validation,
            'processing_time': processing_time,
            'overall_confidence': random.uniform(0.75, 0.92)
        }