from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import User, Document, DocumentPage, FormSchema, FormField, FieldValue, DocumentStatus, ProcessingLog
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

@router.post("/{document_id}/process")
async def process_document_sync(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process a document synchronously"""
    import sys
    sys.path.insert(0, '/app')
    from workers.tasks import process_document_sync as process_func
    
    # Get document and verify ownership
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.tenant_id == current_user.tenant_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Update status to processing
    document.status = DocumentStatus.PROCESSING
    db.commit()
    
    # Process synchronously (blocks but updates progress via logs)
    result = process_func(document_id)
    
    return {
        "message": "Document processing started",
        "document_id": document_id,
        "status": "processing"
    }

@router.get("/{document_id}/progress")
async def get_processing_progress(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current processing progress for a document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.tenant_id == current_user.tenant_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Get latest log to determine stage
    latest_log = db.query(ProcessingLog).filter(
        ProcessingLog.document_id == document_id
    ).order_by(ProcessingLog.created_at.desc()).first()
    
    # Calculate progress based on stage
    progress = 0
    stage = "starting"
    
    if latest_log:
        stage = latest_log.stage
        if stage == 'processing_start':
            progress = 10
        elif stage == 'ocr':
            progress = 40
        elif stage == 'llm':
            progress = 70
        elif stage == 'validation':
            progress = 85
        elif stage == 'completed':
            progress = 100
        elif stage == 'error':
            progress = 100
    
    return {
        "document_id": document_id,
        "status": document.status.value,
        "progress": progress,
        "stage": stage,
        "processing_started_at": document.processing_started_at.isoformat() if document.processing_started_at else None,
        "processing_completed_at": document.processing_completed_at.isoformat() if document.processing_completed_at else None
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

@router.put("/{document_id}/fields/{field_id}")
async def update_field_value(
    document_id: int,
    field_id: int,
    update_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a field value for a document"""
    # Get document and verify ownership
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.tenant_id == current_user.tenant_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Get field value
    field_value = db.query(FieldValue).filter(
        FieldValue.document_id == document_id,
        FieldValue.field_id == field_id
    ).first()
    
    if not field_value:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field value not found"
        )
    
    # Update field value
    if 'final_value' in update_data:
        field_value.final_value = update_data['final_value']
    if 'needs_review' in update_data:
        field_value.needs_review = update_data['needs_review']
    
    db.commit()
    db.refresh(field_value)
    
    return {
        "message": "Field updated successfully",
        "field_id": field_id,
        "final_value": field_value.final_value
    }

@router.get("/export/schema/{schema_id}")
async def get_documents_by_schema(
    schema_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all documents and their field values for a specific schema"""
    # Verify schema belongs to user's tenant
    schema = db.query(FormSchema).filter(
        FormSchema.id == schema_id,
        FormSchema.tenant_id == current_user.tenant_id
    ).first()
    
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schema not found"
        )
    
    # Get all fields for this schema
    fields = db.query(FormField).filter(FormField.schema_id == schema_id).order_by(FormField.id).all()
    
    # Get all documents for this schema
    documents = db.query(Document).filter(
        Document.form_schema_id == schema_id,
        Document.tenant_id == current_user.tenant_id,
        Document.status == DocumentStatus.COMPLETED
    ).order_by(Document.created_at.desc()).all()
    
    # Build table data - only template fields
    columns = [f.field_label for f in fields]
    
    rows = []
    for doc in documents:
        row = {}
        
        # Get field values for this document
        for field in fields:
            field_value = db.query(FieldValue).filter(
                FieldValue.document_id == doc.id,
                FieldValue.field_id == field.id
            ).first()
            
            if field_value:
                row[field.field_label] = field_value.final_value or field_value.normalized_value or field_value.extracted_value or ''
            else:
                row[field.field_label] = ''
        
        rows.append(row)
    
    return {
        "schema_name": schema.name,
        "schema_id": schema_id,
        "columns": columns,
        "rows": rows,
        "total_documents": len(rows)
    }

@router.get("/export/schema/{schema_id}/csv")
async def export_schema_csv(
    schema_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export documents data as CSV"""
    from fastapi.responses import StreamingResponse
    import io
    import csv
    
    # Get data
    data = await get_documents_by_schema(schema_id, current_user, db)
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(data['columns'])
    
    # Write rows
    for row in data['rows']:
        writer.writerow([row.get(col, '') for col in data['columns']])
    
    # Return as downloadable file
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={data['schema_name']}_export.csv"
        }
    )