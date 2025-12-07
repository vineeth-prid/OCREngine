from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, FormSchema, FormField
from schemas import FormSchemaCreate, FormSchemaUpdate, FormSchemaResponse, FormFieldCreate
from auth import get_current_user

router = APIRouter(prefix="/api/schemas", tags=["Form Schemas"])

@router.post("/", response_model=FormSchemaResponse, status_code=status.HTTP_201_CREATED)
async def create_schema(
    schema_data: FormSchemaCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Create form schema
    form_schema = FormSchema(
        tenant_id=current_user.tenant_id,
        name=schema_data.name,
        description=schema_data.description,
        created_by=current_user.id,
        version=1,
        is_active=True
    )
    db.add(form_schema)
    db.commit()
    db.refresh(form_schema)
    
    # Create fields
    for field_data in schema_data.fields:
        field = FormField(
            schema_id=form_schema.id,
            field_name=field_data.field_name,
            field_label=field_data.field_label,
            field_type=field_data.field_type,
            is_required=field_data.is_required,
            default_value=field_data.default_value,
            regex_validation=field_data.regex_validation,
            dropdown_options=field_data.dropdown_options,
            cross_field_rules=field_data.cross_field_rules,
            field_group=field_data.field_group,
            display_order=field_data.display_order
        )
        db.add(field)
    
    db.commit()
    db.refresh(form_schema)
    
    # Load fields
    form_schema.fields = db.query(FormField).filter(
        FormField.schema_id == form_schema.id
    ).order_by(FormField.display_order).all()
    
    return form_schema

@router.get("/", response_model=List[FormSchemaResponse])
async def list_schemas(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(FormSchema).filter(FormSchema.tenant_id == current_user.tenant_id)
    
    if active_only:
        query = query.filter(FormSchema.is_active == True)
    
    schemas = query.offset(skip).limit(limit).all()
    
    # Load fields for each schema
    for schema in schemas:
        schema.fields = db.query(FormField).filter(
            FormField.schema_id == schema.id
        ).order_by(FormField.display_order).all()
    
    return schemas

@router.get("/{schema_id}", response_model=FormSchemaResponse)
async def get_schema(
    schema_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    schema = db.query(FormSchema).filter(
        FormSchema.id == schema_id,
        FormSchema.tenant_id == current_user.tenant_id
    ).first()
    
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form schema not found"
        )
    
    # Load fields
    schema.fields = db.query(FormField).filter(
        FormField.schema_id == schema.id
    ).order_by(FormField.display_order).all()
    
    return schema

@router.put("/{schema_id}", response_model=FormSchemaResponse)
async def update_schema(
    schema_id: int,
    schema_update: FormSchemaUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    schema = db.query(FormSchema).filter(
        FormSchema.id == schema_id,
        FormSchema.tenant_id == current_user.tenant_id
    ).first()
    
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form schema not found"
        )
    
    if schema_update.name is not None:
        schema.name = schema_update.name
    if schema_update.description is not None:
        schema.description = schema_update.description
    if schema_update.is_active is not None:
        schema.is_active = schema_update.is_active
    
    db.commit()
    db.refresh(schema)
    
    # Load fields
    schema.fields = db.query(FormField).filter(
        FormField.schema_id == schema.id
    ).order_by(FormField.display_order).all()
    
    return schema

@router.delete("/{schema_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schema(
    schema_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    schema = db.query(FormSchema).filter(
        FormSchema.id == schema_id,
        FormSchema.tenant_id == current_user.tenant_id
    ).first()
    
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form schema not found"
        )
    
    # Soft delete - just mark as inactive
    schema.is_active = False
    db.commit()
    
    return None

@router.post("/{schema_id}/fields", status_code=status.HTTP_201_CREATED)
async def add_field_to_schema(
    schema_id: int,
    field_data: FormFieldCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    schema = db.query(FormSchema).filter(
        FormSchema.id == schema_id,
        FormSchema.tenant_id == current_user.tenant_id
    ).first()
    
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form schema not found"
        )
    
    field = FormField(
        schema_id=schema.id,
        field_name=field_data.field_name,
        field_label=field_data.field_label,
        field_type=field_data.field_type,
        is_required=field_data.is_required,
        default_value=field_data.default_value,
        regex_validation=field_data.regex_validation,
        dropdown_options=field_data.dropdown_options,
        cross_field_rules=field_data.cross_field_rules,
        field_group=field_data.field_group,
        display_order=field_data.display_order
    )
    db.add(field)
    
    # Increment schema version
    schema.version += 1
    
    db.commit()
    db.refresh(field)
    
    return field

@router.delete("/{schema_id}/fields/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_field_from_schema(
    schema_id: int,
    field_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    schema = db.query(FormSchema).filter(
        FormSchema.id == schema_id,
        FormSchema.tenant_id == current_user.tenant_id
    ).first()
    
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form schema not found"
        )
    
    field = db.query(FormField).filter(
        FormField.id == field_id,
        FormField.schema_id == schema_id
    ).first()
    
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found"
        )
    
    db.delete(field)
    
    # Increment schema version
    schema.version += 1
    
    db.commit()
    return None
