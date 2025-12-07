from celery_app import celery_app
from sqlalchemy.orm import Session
import sys
sys.path.append('/app/backend')

from database import SessionLocal
from models import Document, DocumentPage, OCRResult, LLMResult, FieldValue, ProcessingLog, FormField, DocumentStatus
from ocr_engines import OCREngine
from llm_mock import LLMProcessor
from datetime import datetime

ocr_engine = OCREngine()
llm_processor = LLMProcessor()

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass

@celery_app.task(name='workers.tasks.process_document')
def process_document(document_id: int):
    """Main document processing task"""
    db = SessionLocal()
    
    try:
        # Get document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return {'error': 'Document not found'}
        
        # Log start
        log = ProcessingLog(
            document_id=document.id,
            stage='processing_start',
            message='Started document processing',
            level='INFO'
        )
        db.add(log)
        db.commit()
        
        # Update status
        document.status = DocumentStatus.PROCESSING
        document.processing_started_at = datetime.utcnow()
        db.commit()
        
        # Step 1: OCR Processing
        ocr_result = ocr_engine.process_with_routing(document.file_path)
        
        # Create document page
        page = DocumentPage(
            document_id=document.id,
            page_number=1,
            image_path=document.file_path,
            quality_score=ocr_result['quality_score']
        )
        db.add(page)
        db.commit()
        db.refresh(page)
        
        # Save OCR results
        best_ocr = ocr_result['best_result']
        ocr_record = OCRResult(
            page_id=page.id,
            ocr_engine=best_ocr['engine'],
            extracted_text=best_ocr['text'],
            confidence_score=best_ocr['confidence'],
            bounding_boxes=best_ocr.get('bounding_boxes', []),
            processing_time=best_ocr['processing_time']
        )
        db.add(ocr_record)
        db.commit()
        
        log = ProcessingLog(
            document_id=document.id,
            stage='ocr',
            message=f"OCR completed with {best_ocr['engine']} (confidence: {best_ocr['confidence']:.2f})",
            level='INFO'
        )
        db.add(log)
        db.commit()
        
        # Step 2: LLM Processing (if schema exists)
        if document.form_schema_id:
            from models import FormSchema
            schema = db.query(FormSchema).filter(FormSchema.id == document.form_schema_id).first()
            
            if schema:
                # Get fields
                fields = db.query(FormField).filter(FormField.schema_id == schema.id).all()
                field_dicts = [
                    {
                        'field_name': f.field_name,
                        'field_type': f.field_type.value,
                        'field_label': f.field_label
                    }
                    for f in fields
                ]
                
                # Process with LLM (mock)
                llm_result = llm_processor.process_with_model(
                    'deepseek',
                    best_ocr['text'],
                    field_dicts
                )
                
                # Save LLM result
                llm_record = LLMResult(
                    page_id=page.id,
                    llm_model=llm_result['model'],
                    input_text=best_ocr['text'][:1000],  # Truncate
                    normalized_output=llm_result['extracted_fields'],
                    confidence_score=llm_result['overall_confidence'],
                    processing_time=llm_result['processing_time']
                )
                db.add(llm_record)
                db.commit()
                
                # Create field values
                for field in fields:
                    field_name = field.field_name
                    extracted_value = llm_result['extracted_fields'].get(field_name, '')
                    confidence = llm_result['extracted_fields'].get(f'{field_name}_confidence', 0)
                    
                    field_value = FieldValue(
                        document_id=document.id,
                        field_id=field.id,
                        extracted_value=extracted_value,
                        normalized_value=extracted_value,
                        confidence_score=confidence,
                        needs_review=confidence < 0.8
                    )
                    db.add(field_value)
                
                db.commit()
                
                log = ProcessingLog(
                    document_id=document.id,
                    stage='llm',
                    message=f"LLM processing completed with {llm_result['model']}",
                    level='INFO'
                )
                db.add(log)
                db.commit()
                
                # Calculate overall confidence
                document.overall_confidence = llm_result['overall_confidence']
        else:
            # No schema, just use OCR confidence
            document.overall_confidence = best_ocr['confidence']
        
        # Step 3: Finalize
        document.status = DocumentStatus.COMPLETED
        document.processing_completed_at = datetime.utcnow()
        db.commit()
        
        log = ProcessingLog(
            document_id=document.id,
            stage='completed',
            message='Document processing completed successfully',
            level='INFO'
        )
        db.add(log)
        db.commit()
        
        return {
            'status': 'success',
            'document_id': document.id,
            'confidence': document.overall_confidence
        }
        
    except Exception as e:
        # Handle errors
        if document:
            document.status = DocumentStatus.FAILED
            document.error_message = str(e)
            db.commit()
            
            log = ProcessingLog(
                document_id=document.id,
                stage='error',
                message=f'Processing failed: {str(e)}',
                level='ERROR'
            )
            db.add(log)
            db.commit()
        
        return {
            'status': 'error',
            'message': str(e)
        }
    
    finally:
        db.close()
