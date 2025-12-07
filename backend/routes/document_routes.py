from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import User, Document, DocumentPage, FormSchema, DocumentStatus, ProcessingLog
from schemas import DocumentUploadResponse, DocumentResponse
from auth import get_current_user
import os
import uuid
from datetime import datetime
import aiofiles
from pathlib import Path

router = APIRouter(prefix="/api/documents", tags=["Documents"])

UPLOAD_DIR = "/app/uploads"
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    form_schema_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate file type
    allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not supported. Only PDF, JPEG, PNG allowed."
        )
    
    # Validate schema if provided
    if form_schema_id:
        schema = db.query(FormSchema).filter(
            FormSchema.id == form_schema_id,
            FormSchema.tenant_id == current_user.tenant_id
        ).first()
        if not schema:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form schema not found"
            )
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    file_size = len(content)
    
    # Create document record
    document = Document(
        tenant_id=current_user.tenant_id,
        form_schema_id=form_schema_id,
        uploaded_by=current_user.id,
        original_filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type,
        num_pages=1,  # Will be updated by processing
        status=DocumentStatus.UPLOADED
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Create processing log
    log = ProcessingLog(
        document_id=document.id,
        stage="upload",
        message=f"Document uploaded: {file.filename}",
        level="INFO"
    )
    db.add(log)
    db.commit()
    
    return document

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Document).filter(Document.tenant_id == current_user.tenant_id)
    
    if status_filter:
        query = query.filter(Document.status == status_filter)
    
    documents = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    return documents

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.tenant_id == current_user.tenant_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document

@router.post("/{document_id}/process", status_code=status.HTTP_202_ACCEPTED)
async def process_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.tenant_id == current_user.tenant_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Update status
    document.status = DocumentStatus.PROCESSING
    document.processing_started_at = datetime.utcnow()
    db.commit()
    
    # Process synchronously (more reliable than Celery in container environments)
    try:
        import sys
        sys.path.append('/app/workers')
        sys.path.append('/app/backend')
        from tasks import process_document as sync_process
        
        # Process in background thread to not block API
        import threading
        thread = threading.Thread(target=sync_process, args=(document_id,))
        thread.daemon = True
        thread.start()
        
    except Exception as e:
        print(f"Error starting processing: {e}")
        document.status = DocumentStatus.FAILED
        document.error_message = str(e)
        db.commit()
    
    return {
        "message": "Document processing started",
        "document_id": document_id,
        "status": "processing"
    }

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.tenant_id == current_user.tenant_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete file if exists
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    db.delete(document)
    db.commit()
    
    return None

@router.get("/{document_id}/logs")
async def get_document_logs(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.tenant_id == current_user.tenant_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    logs = db.query(ProcessingLog).filter(
        ProcessingLog.document_id == document_id
    ).order_by(ProcessingLog.created_at.desc()).all()
    
    return logs

@router.get("/{document_id}/fields")
async def get_document_fields(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.tenant_id == current_user.tenant_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Get field values with field details
    from models import FieldValue, FormField
    field_values = db.query(FieldValue, FormField).join(
        FormField, FieldValue.field_id == FormField.id
    ).filter(
        FieldValue.document_id == document_id
    ).all()
    
    result = []
    for field_value, form_field in field_values:
        result.append({
            "field_id": form_field.id,
            "field_name": form_field.field_name,
            "field_label": form_field.field_label,
            "field_type": form_field.field_type.value,
            "extracted_value": field_value.extracted_value,
            "normalized_value": field_value.normalized_value,
            "final_value": field_value.final_value,
            "confidence_score": field_value.confidence_score,
            "needs_review": field_value.needs_review
        })
    
    return result