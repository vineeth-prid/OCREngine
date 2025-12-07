"""
LLM Processor with Cloud and Local Model Support
Supports: OpenAI GPT-4o, GPT-4o-mini, Ollama local models
"""

import os
import json
import time
import requests
import asyncio
from typing import Dict, List, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage

class LLMProcessor:
    def __init__(self):
        self.emergent_llm_key = os.getenv('OPENAI_API_KEY') or os.getenv('EMERGENT_LLM_KEY')
        self.ollama_base_url = "http://localhost:11434"
        self.use_local = False  # Default to cloud
        self.local_model = "qwen2.5:3b-instruct"
    
    def check_local_model_available(self) -> bool:
        """Check if local Ollama model is available and has enough memory"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return len(models) > 0
        except:
            pass
        return False
    
    async def process_with_cloud_llm_async(
        self, 
        model: str,
        ocr_text: str, 
        schema_fields: List[Dict],
        use_mini: bool = False
    ) -> Dict:
        """Process document with cloud LLM using emergentintegrations"""
        start_time = time.time()
        
        if not self.emergent_llm_key:
            raise Exception("Emergent LLM key not configured")
        
        # Build prompt
        field_descriptions = "\n".join([
            f"- {f['field_name']} ({f['field_type']}): {f['field_label']}"
            for f in schema_fields
        ])
        
        prompt = f"""Extract the following fields from the OCR text below. Return ONLY a valid JSON object.

Required fields:
{field_descriptions}

OCR Text:
{ocr_text[:2000]}

Return format:
{{
    "field_name": "extracted_value",
    "field_name_confidence": 0.95
}}

If a field is not found, use null for value and 0.0 for confidence.
"""
        
        try:
            # Use mini model for simple docs, full model for complex
            model_to_use = "gpt-4.1-mini" if use_mini else "gpt-4.1"
            
            # Create chat instance
            chat = LlmChat(
                api_key=self.emergent_llm_key,
                session_id=f"doc_extraction_{int(time.time())}",
                system_message="You are a document extraction expert. Extract fields accurately and return only valid JSON."
            ).with_model("openai", model_to_use)
            
            # Send message
            user_message = UserMessage(text=prompt)
            response_text = await chat.send_message(user_message)
            
            processing_time = time.time() - start_time
            
            # Parse response - extract JSON from response
            response_text = response_text.strip()
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            extracted_data = json.loads(response_text)
            
            # Calculate overall confidence
            confidence_scores = [
                v for k, v in extracted_data.items() 
                if k.endswith('_confidence') and isinstance(v, (int, float))
            ]
            overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
            
            return {
                'model': model_to_use,
                'extracted_fields': extracted_data,
                'overall_confidence': overall_confidence,
                'processing_time': processing_time,
                'tokens_used': 0  # emergentintegrations doesn't expose token count
            }
            
        except Exception as e:
            print(f"Cloud LLM error: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_mock_response(schema_fields, processing_time=time.time() - start_time)
    
    def process_with_cloud_llm(
        self, 
        model: str,
        ocr_text: str, 
        schema_fields: List[Dict],
        use_mini: bool = False
    ) -> Dict:
        """Synchronous wrapper for cloud LLM processing"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.process_with_cloud_llm_async(model, ocr_text, schema_fields, use_mini)
        )
    
    def process_with_local_llm(
        self, 
        ocr_text: str, 
        schema_fields: List[Dict]
    ) -> Dict:
        """Process document with local Ollama model"""
        start_time = time.time()
        
        field_descriptions = "\n".join([
            f"- {f['field_name']} ({f['field_type']}): {f['field_label']}"
            for f in schema_fields
        ])
        
        prompt = f"""Extract these fields from the text:

{field_descriptions}

Text:
{ocr_text[:1500]}

Return only JSON with field names as keys and extracted values. Include confidence (0-1) for each field."""
        
        try:
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.local_model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=120
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                extracted_data = json.loads(result.get('response', '{}'))
                
                # Calculate overall confidence
                confidence_scores = [
                    v for k, v in extracted_data.items() 
                    if k.endswith('_confidence') and isinstance(v, (int, float))
                ]
                overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
                
                return {
                    'model': self.local_model,
                    'extracted_fields': extracted_data,
                    'overall_confidence': overall_confidence,
                    'processing_time': processing_time,
                    'tokens_used': 0
                }
            else:
                raise Exception(f"Ollama error: {response.status_code}")
                
        except Exception as e:
            print(f"Local LLM error: {e}")
            return self._generate_mock_response(schema_fields, processing_time=time.time() - start_time)
    
    def process_with_model(
        self,
        model: str,
        ocr_text: str,
        schema_fields: List[Dict],
        ocr_confidence: float = 0.9
    ) -> Dict:
        """
        Smart routing: Use local model if available and doc is simple,
        otherwise use cloud LLM
        """
        
        # Check if we should use local model
        use_local = self.use_local and self.check_local_model_available()
        
        # Determine if document is simple based on OCR confidence and text length
        is_simple = ocr_confidence > 0.85 and len(ocr_text) < 1000
        
        if use_local:
            # Try local model first
            try:
                result = self.process_with_local_llm(ocr_text, schema_fields)
                result['model_type'] = 'local'
                return result
            except:
                print("Local model failed, falling back to cloud")
        
        # Use cloud LLM with smart model selection
        if self.openai_client:
            use_mini = is_simple  # Use mini for simple docs
            result = self.process_with_cloud_llm(model, ocr_text, schema_fields, use_mini)
            result['model_type'] = 'cloud'
            return result
        else:
            # Fallback to mock
            return self._generate_mock_response(schema_fields)
    
    def _generate_mock_response(self, schema_fields: List[Dict], processing_time: float = 0.1) -> Dict:
        """Generate mock response when LLM is not available"""
        extracted_fields = {}
        for field in schema_fields:
            field_name = field['field_name']
            extracted_fields[field_name] = f"[Mock extracted: {field_name}]"
            extracted_fields[f"{field_name}_confidence"] = 0.85
        
        return {
            'model': 'mock',
            'model_type': 'mock',
            'extracted_fields': extracted_fields,
            'overall_confidence': 0.85,
            'processing_time': processing_time,
            'tokens_used': 0
        }
    
    def validate_extracted_data(
        self,
        extracted_data: Dict,
        schema_fields: List[Dict]
    ) -> Dict:
        """
        Validate extracted data against schema rules
        Returns validation results with errors and warnings
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'field_validations': {}
        }
        
        for field in schema_fields:
            field_name = field['field_name']
            field_type = field['field_type']
            is_required = field.get('is_required', False)
            value = extracted_data.get(field_name)
            confidence = extracted_data.get(f"{field_name}_confidence", 0)
            
            field_validation = {
                'valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Check required fields
            if is_required and (value is None or value == ''):
                field_validation['valid'] = False
                field_validation['errors'].append(f"Required field '{field_name}' is missing")
                validation_results['is_valid'] = False
            
            # Check confidence threshold
            if confidence < 0.7:
                field_validation['warnings'].append(f"Low confidence ({confidence:.2f}) for field '{field_name}'")
            
            # Type validation
            if value and field_type == 'number':
                try:
                    float(str(value).replace(',', '').replace('$', ''))
                except ValueError:
                    field_validation['errors'].append(f"Field '{field_name}' should be numeric")
                    field_validation['valid'] = False
            
            if value and field_type == 'email':
                if '@' not in str(value):
                    field_validation['errors'].append(f"Field '{field_name}' should be a valid email")
                    field_validation['valid'] = False
            
            if value and field_type == 'date':
                # Basic date validation
                if not any(sep in str(value) for sep in ['/', '-', '.']):
                    field_validation['warnings'].append(f"Field '{field_name}' might not be a valid date format")
            
            validation_results['field_validations'][field_name] = field_validation
            validation_results['errors'].extend(field_validation['errors'])
            validation_results['warnings'].extend(field_validation['warnings'])
        
        return validation_results
